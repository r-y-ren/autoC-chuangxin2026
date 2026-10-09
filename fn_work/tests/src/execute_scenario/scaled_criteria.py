# scaled_criteria 单测：缩放口径/边界拒绝
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.scaled_criteria import scaled_criteria  # noqa: E402
from src.shared.load_scenario import CriteriaSpec  # noqa: E402


def test_scaling():
    eff, info = scaled_criteria(CriteriaSpec(per_threshold=0.1, sustain_s=10.0,
                                             disconnect_s=30.0), 40)
    assert eff.sustain_s == pytest.approx(0.25)
    assert eff.disconnect_s == pytest.approx(0.75)
    assert eff.per_threshold == 0.1            # 阈值不缩
    assert info["speed"] == 40 and "加速倍率" in info["note"]


def test_speed_rejected():
    with pytest.raises(ValueError):
        scaled_criteria(CriteriaSpec(), 0)
