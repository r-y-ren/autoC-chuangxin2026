# record_run_streams 单测：三路落盘+覆盖率+extra_events
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.create_instrument_backend.backends import MockJammer  # noqa: E402
from src.record_run_streams.record_run_streams import record_run_streams  # noqa: E402
from src.shared.load_scenario import load_scenario  # noqa: E402

FW = Path(__file__).resolve().parents[3]


def _scenario():
    return load_scenario(FW / "scenarios" / "smoke_loop.yaml")


def test_record_three_streams(tmp_path):
    j = MockJammer(); j.set_power_db(5); j.on()
    res = record_run_streams(_scenario(), 0.3, tmp_path / "run1", with_injection=True,
                             jammer=j,
                             extra_events=[{"type": "injection", "style": "cw",
                                            "power_db": 5, "ts_ms": 1}])
    assert res["kpi_csv"].exists() and res["events_jsonl"].exists() and res["monitor_csv"].exists()
    assert res["n_samples"] > 20
    assert res["coverage_ratio"] >= 0.9
    lines = res["events_jsonl"].read_text(encoding="utf-8").strip().splitlines()
    assert any('"injection"' in ln for ln in lines)
    mon = res["monitor_csv"].read_text(encoding="utf-8").strip().splitlines()
    assert len(mon) >= 2  # 表头+至少一行（occupied=1）
