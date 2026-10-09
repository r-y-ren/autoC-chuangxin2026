# EstopManager 单测：按序触发/幂等/单点失败不阻断/状态只升
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.estop import EstopManager  # noqa: E402


def test_order_and_idempotent():
    calls = []
    m = EstopManager()
    m.arm(lambda: calls.append("a"))
    m.arm(lambda: calls.append("b"))
    assert m.state == "armed"
    m.fire("设备失联")
    m.fire("再来一次")
    assert calls == ["a", "b"]  # 幂等：各只一次
    assert m.state.startswith("fired")


def test_callback_error_does_not_block():
    calls = []
    m = EstopManager()
    m.arm(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    m.arm(lambda: calls.append("survived"))
    m.fire("x")
    assert calls == ["survived"]
