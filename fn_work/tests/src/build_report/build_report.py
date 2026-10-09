# build_report 单测：报告生成+失效电平行+固定声明
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.build_report.build_report import build_report  # noqa: E402


def test_report_contains_disclaimer_and_fails(tmp_path):
    rows = ["ts_ms,link,seq,per,tx_n,err_n,rssi_dbm,arc_avg,plos_cnt"]
    for i in range(20):
        rows.append(f"{i*100},nrf24,{i},0.05,50,2,,1.0,2")
    (tmp_path / "kpi.csv").write_text("\n".join(rows), encoding="utf-8")
    import json
    (tmp_path / "steps.jsonl").write_text(json.dumps(
        {"style": "noise_bandlimited", "power_db": 10, "failed": True,
         "failure_kind": "per_sustained", "t_start_ms": 0, "t_end_ms": 1999}),
        encoding="utf-8")
    (tmp_path / "scenario.yaml").write_text('{"name": "t"}', encoding="utf-8")
    out = build_report(tmp_path)
    text = out.read_text(encoding="utf-8")
    assert out.exists()
    assert "CISPR" in text and "GB 42590" in text          # 固定声明
    assert "noise_bandlimited" in text and "10" in text    # 失效电平行
    assert (tmp_path / "figs" / "per_vs_jsr.png").exists()
