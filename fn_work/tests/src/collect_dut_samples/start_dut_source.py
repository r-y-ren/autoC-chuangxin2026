# start_dut_source 单测：合成源台阶/jammer 响应/未知类型拒/串口缺驱动提示
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.collect_dut_samples.start_dut_source import start_dut_source  # noqa: E402
from src.create_instrument_backend.backends import MockJammer  # noqa: E402


def test_fake_profile_steps():
    src = start_dut_source({"type": "fake", "link": "wifi", "rate_hz": 500,
                            "jam_profile": [(0.0, 0.0), (0.02, 0.5)]})
    a = src.next_sample()
    assert a.per <= 0.05
    b = a
    for _ in range(40):  # 推进时间到台阶之后（500Hz×40≈80ms>20ms）
        b = src.next_sample()
        if b.ts_ms >= 25:
            break
    assert b.ts_ms >= 20 and b.per >= 0.4  # 台阶生效


def test_fake_reacts_to_jammer_power():
    j = MockJammer()
    src = start_dut_source({"type": "fake", "link": "nrf24", "rate_hz": 500,
                            "jammer": j, "fail_power_db": 10.0})
    j.set_power_db(-20); j.on()
    low = src.next_sample().per
    j.set_power_db(10)
    high = src.next_sample().per
    j.off()
    after = src.next_sample().per
    assert low <= 0.05 and high >= 0.9 and after <= 0.05


def test_dead_link_raises_after_dead_at():
    src = start_dut_source({"type": "fake", "link": "wifi", "rate_hz": 500,
                            "dead_at_s": 0.01})
    src.next_sample()
    time.sleep(0.02)
    with pytest.raises(ConnectionError):
        src.next_sample()


def test_unknown_type_rejected():
    with pytest.raises(ValueError, match="未知链路类型"):
        start_dut_source({"type": "magic"})


def test_serial_missing_port_or_driver():
    with pytest.raises(Exception):
        start_dut_source({"type": "serial", "link": "wifi"})
