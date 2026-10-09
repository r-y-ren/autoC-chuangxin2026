# plot_triple_curves 单测：三图产出/无 steps 兜底
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.build_report.plot_triple_curves import plot_triple_curves  # noqa: E402


def _write_fixture(d: Path, with_steps: bool):
    rows = ["ts_ms,link,seq,per,tx_n,err_n,rssi_dbm,arc_avg,plos_cnt"]
    for i in range(30):
        per = 0.02 if i < 15 else 0.6
        rows.append(f"{i*100},wifi,{i},{per},100,{int(per*100)},-61,,")
    (d / "kpi.csv").write_text("\n".join(rows), encoding="utf-8")
    if with_steps:
        sts = [{"style": "cw", "power_db": -5, "t_start_ms": 0, "t_end_ms": 1499},
               {"style": "cw", "power_db": 0, "t_start_ms": 1500, "t_end_ms": 99999, "failed": True}]
        (d / "steps.jsonl").write_text("\n".join(
            json.dumps(s) for s in sts), encoding="utf-8")
        (d / "events.jsonl").write_text(
            json.dumps({"type": "fail", "ts_ms": 2000}), encoding="utf-8")


import json  # noqa: E402


def test_three_figures_with_steps(tmp_path):
    _write_fixture(tmp_path, with_steps=True)
    res = plot_triple_curves(tmp_path / "kpi.csv", tmp_path / "figs")
    assert sorted(Path(p).name for p in res["produced"]) == \
        ["fail_timeline.png", "per_vs_jsr.png", "throughput_latency.png"]
    assert not res["skipped"]


def test_fallback_without_steps(tmp_path):
    _write_fixture(tmp_path, with_steps=False)
    res = plot_triple_curves(tmp_path / "kpi.csv", tmp_path / "figs")
    assert len(res["produced"]) == 3  # 时间轴兜底仍出三图
