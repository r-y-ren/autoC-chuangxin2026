# plan_steps 单测：展开/对照空表
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.plan_steps import plan_steps  # noqa: E402
from src.shared.load_scenario import InjectionSpec  # noqa: E402


def test_expansion():
    spec = InjectionSpec(styles=["cw", "noise_bandlimited"], power_start_db=-5,
                         power_step_db=5, power_stop_db=10, step_duration_s=1.0)
    steps = plan_steps(spec)
    assert len(steps) == 8  # 2 样式 × (-5,0,5,10)
    assert steps[0].power_db == -5 and steps[3].power_db == 10
    assert steps[4].style == "noise_bandlimited"


def test_none_returns_empty():
    assert plan_steps(None) == []
