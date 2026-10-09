# check_failure 单测：四分支
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.check_failure import check_failure  # noqa: E402
from src.shared.load_scenario import CriteriaSpec  # noqa: E402

C = CriteriaSpec(per_threshold=0.10, sustain_s=10.0, disconnect_s=30.0)


def test_sustained_fail():
    win = [{"ts_ms": i * 1000, "per": 0.6} for i in range(12)]
    assert check_failure(win, C) == (True, "per_sustained")


def test_not_sustained():
    win = [{"ts_ms": i * 1000, "per": 0.6} for i in range(5)]  # 5s < 10s
    ok, kind = check_failure(win, C)
    assert ok is False and kind == ""


def test_disconnect():
    win = [{"ts_ms": i * 1000, "per": 0.0, "connected": False} for i in range(31)]
    assert check_failure(win, C) == (True, "disconnect")


def test_empty():
    assert check_failure([], C) == (False, "")
