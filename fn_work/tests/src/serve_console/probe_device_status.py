# probe_device_status 单测：清单形状/枚举/物理件占位/单点故障隔离/超时降级
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.serve_console import probe_device_status as mod  # noqa: E402
from src.serve_console.probe_device_status import probe_device_status  # noqa: E402

IDS = {"b210", "esp32_serial", "nrf24", "deps", "toolbox", "platformio",
       "shield_box", "antenna_geometry", "power_hub"}


def test_shape_and_enums():
    devs = probe_device_status()
    assert {e["id"] for e in devs} == IDS and len(devs) == 9
    for e in devs:
        assert e["status"] in mod.STATUS_ENUM
        assert isinstance(e["detail"], str) and e["detail"]
        assert isinstance(e["ts"], int)


def test_manual_items_pending():
    devs = {e["id"]: e for e in probe_device_status()}
    for pid in ("shield_box", "antenna_geometry", "power_hub"):
        assert devs[pid]["status"] == "pending_manual"


def test_single_probe_fault_isolated(monkeypatch):
    def boom(_timeout):
        raise RuntimeError("爆炸")
    monkeypatch.setattr(mod, "_probe_b210", boom)
    devs = {e["id"]: e for e in probe_device_status()}
    assert devs["b210"]["status"] == "missing" and "探测异常" in devs["b210"]["detail"]
    assert devs["deps"]["status"] in mod.STATUS_ENUM  # 其余不受影响


def test_timeout_degrades(monkeypatch):
    def slow(_timeout):
        import time
        time.sleep(0.5)
        return "ok", "不应到达"
    monkeypatch.setattr(mod, "_probe_pio", lambda t: mod._timed(lambda: slow(t), 0.05))
    devs = {e["id"]: e for e in probe_device_status()}
    assert devs["platformio"]["status"] == "missing" and "超时" in devs["platformio"]["detail"]
