# apply_calibration 单测：三分支（缺表恒等/查表内插/损坏降级）
import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.apply_calibration import apply_calibration  # noqa: E402


def test_no_table_identity(tmp_path):
    gain, src, warn = apply_calibration(-5.0, 2422000000, tmp_path / "none.json")
    assert gain == -5.0 and src == "identity" and warn is None


def test_table_interp(tmp_path):
    p = tmp_path / "calibration.json"
    p.write_text(json.dumps({"entries": [
        {"freq_hz": 2422000000, "gain_db": g, "power_db": g}
        for g in range(-30, 1, 5)]}), encoding="utf-8")
    gain, src, warn = apply_calibration(-22.5, 2422000000, p)
    assert src == "calibrated" and gain == pytest.approx(-22.5)  # 恒等表内插=自身
    gain2, src2, _ = apply_calibration(-100, 2422000000, p)
    assert gain2 == -30 and src2 == "calibrated"  # 低端钳位


def test_corrupt_falls_back(tmp_path):
    p = tmp_path / "calibration.json"
    p.write_text("{broken", encoding="utf-8")
    gain, src, warn = apply_calibration(7.0, 2422000000, p)
    assert gain == 7.0 and src == "identity" and warn
