# collect_dashboard 单测+集成：形状/可溯源/seed 端到端/DOM（演进轮四 R21）
import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.serve_console.collect_dashboard import collect_dashboard  # noqa: E402
from src.serve_console.serve_console import create_app  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


def _fixture_runs(root: Path):
    r = root / "runX"
    (r / "figs").mkdir(parents=True)
    (r / "figs" / "per_vs_jsr.png").write_bytes(b"png")
    steps = [{"style": "cw", "power_db": 5, "failed": True,
              "failure_kind": "per_sustained", "t_start_ms": 0, "t_end_ms": 1}]
    (r / "steps.jsonl").write_text(json.dumps(steps[0]), encoding="utf-8")
    (r / "kpi.csv").write_text("h\n" + "\n".join("r" for _ in range(10)),
                               encoding="utf-8")
    (r / "report.md").write_text("# r", encoding="utf-8")
    (r / "scenario.yaml").write_text('{"name": "t"}', encoding="utf-8")
    (r / "speed.json").write_text('{"speed": 40, "note": "加速倍率 40×"}',
                                  encoding="utf-8")
    return r, steps


def test_shape_and_traceability(tmp_path):
    _fixture_runs(tmp_path)
    d = collect_dashboard(str(tmp_path))
    assert d["empty"] is False
    assert d["latest"]["scenario"] == "t" and d["latest"]["kpi_n"] == 10
    assert d["latest"]["fail_levels"] == {"cw": 5}          # 可溯源：出自 steps
    assert d["latest"]["synthetic"] is True and "40" in d["latest"]["speed_note"]
    assert d["capability"]["total_runs"] == 1
    st = json.loads((tmp_path / "runX" / "steps.jsonl").read_text(encoding="utf-8"))
    assert d["latest"]["fail_levels"]["cw"] == st["power_db"] == 5   # 等值溯源（非子串）


def test_empty_runs(tmp_path):
    d = collect_dashboard(str(tmp_path))
    assert d["empty"] is True and d["latest"] is None
    assert d["capability"]["styles"] == 6                     # 能力恒可报


def test_r21_dashboard_endpoint_and_dom(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = create_app()
    with TestClient(app) as c:
        d = c.get("/api/dashboard").json()
        assert d["empty"] is True                             # 空 runs 环境
        js = c.get("/dashboard.js").text
        html = c.get("/").text
    for m in ("card-latest", "card-model", "card-capability", "card-history",
              "id=\"dashboard\""):
        assert m in html, m
    assert "compare-chart" in js and "seed_demo" in js         # 对比画布+自动播逻辑
    assert "合成数据" in js and "实测数据" in js                # R21 验收：合成角标


def test_r21_seed_demo_end_to_end(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKBENCH_SPEED", "120")
    app = create_app()
    with TestClient(app) as c:
        assert c.get("/api/dashboard").json()["empty"] is True
        assert c.post("/api/seed_demo").json()["started"] is True
        deadline = time.monotonic() + 90
        d = {}
        while time.monotonic() < deadline:
            d = c.get("/api/dashboard").json()
            if not d["empty"]:
                break
            time.sleep(2)
    assert d.get("empty") is False, "seed_demo 超时未产出"
    assert d["latest"]["kpi_n"] > 0
    fl = d["latest"]["fail_levels"]
    assert fl, "演示轮应产生失效电平"
    # 可溯源：失效电平出现在该 run 的 steps.jsonl
    steps = (tmp_path / "runs" / d["latest"]["name"] / "steps.jsonl").read_text(
        encoding="utf-8")
    for v in fl.values():
        assert str(v) in steps
