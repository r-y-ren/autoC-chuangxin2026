# per_response_model 单测：单调/钳位/下限/非法参
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.per_response_model import per_response_model  # noqa: E402


def test_monotonic_and_clamps():
    vals = [per_response_model(p, 10.0) for p in range(-20, 41, 5)]
    assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
    assert vals[0] == 0.0 and vals[-1] == 1.0
    assert per_response_model(10.0, 10.0) == pytest.approx(1.0)   # 失效基准处≈1


def test_base_per_floor():
    assert per_response_model(-20.0, 10.0, base_per=0.05) == 0.05


def test_invalid_fail_power():
    with pytest.raises(ValueError):
        per_response_model(0.0, float("nan"))
