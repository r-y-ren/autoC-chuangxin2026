# build_mid_material 单测：汇编+溯源+无 run 兜底
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.build_mid_material.build_mid_material import build_mid_material  # noqa: E402


def _fixture(runs: Path):
    r = runs / "runX"
    (r / "figs").mkdir(parents=True)
    (r / "figs" / "per_vs_jsr.png").write_bytes(b"png")
    steps = [{"style": "noise_bandlimited", "power_db": 5, "failed": True,
              "failure_kind": "per_sustained", "t_start_ms": 0, "t_end_ms": 1}]
    (r / "steps.jsonl").write_text("\n".join(json.dumps(s) for s in steps),
                                   encoding="utf-8")
    (r / "kpi.csv").write_text("ts_ms,link,seq,per\n" + "\n".join(
        f"{i},wifi,{i},0.5" for i in range(10)), encoding="utf-8")
    (r / "report.md").write_text("# r", encoding="utf-8")
    return r


def test_build(tmp_path):
    _fixture(tmp_path)
    out = build_mid_material(mode="mid", runs_dir=str(tmp_path),
                             out_path=tmp_path / "out" / "mid_draft.md")
    assert out and out.exists()
    text = out.read_text(encoding="utf-8")
    assert "noise_bandlimited" in text and "5" in text      # 失效电平行
    assert "CISPR" in text                                   # 固定声明
    assert "runX/figs/per_vs_jsr.png" in text                # 图相对链接
    assert "数字来源" in text


def test_no_run_returns_none(tmp_path):
    assert build_mid_material(mode="mid", runs_dir=str(tmp_path),
                              out_path=tmp_path / "x.md") is None
