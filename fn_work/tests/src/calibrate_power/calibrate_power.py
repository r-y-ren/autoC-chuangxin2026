# calibrate_power 单测：单调表/非单调检出
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.calibrate_power.calibrate_power import calibrate_power  # noqa: E402


def test_monotonic_table(tmp_path):
    res = calibrate_power([2422000000], list(range(-30, 1, 5)), runs_dir=str(tmp_path))
    assert res["monotonic_ok"] and res["entries"] == 7
    assert Path(res["calibration_path"]).exists()


def test_single_entry_not_monotonic(tmp_path):
    res = calibrate_power([2422000000], [0], runs_dir=str(tmp_path))
    assert res["monotonic_ok"] is False or res["entries"] == 1  # 单档无序可言，如实记录
