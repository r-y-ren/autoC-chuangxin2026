# 仪表后端实现集（create_instrument_backend 的子树文件）：mock / b210 / pyvisa
# 接口契约（R9）：干扰源 set_style/set_power_db/on/off；分析仪 get_spectrum
from __future__ import annotations


class BaseJammer:
    # 仪表插槽固定接口——新仪表=新子类注册进 backends.REGISTRY，场景与执行器零改动
    def set_style(self, style: str, params: dict) -> None:
        raise NotImplementedError

    def set_power_db(self, power_db: float) -> None:
        raise NotImplementedError

    def on(self) -> None:
        raise NotImplementedError

    def off(self) -> None:
        # 急停路径必经
        raise NotImplementedError


class BaseAnalyzer:
    def get_spectrum(self, freq_hz: int, bandwidth_hz: int) -> dict:
        raise NotImplementedError


class MockJammer(BaseJammer):
    # 无硬件测试/演示后端：记录调用序列，不触真设备
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.emitting = False
        self.style = None
        self.power_db = None

    def set_style(self, style, params):
        self.style, _ = style, params
        self.calls.append(("set_style", style))

    def set_power_db(self, power_db):
        self.power_db = power_db
        self.calls.append(("set_power_db", power_db))

    def on(self):
        self.emitting = True
        self.calls.append(("on",))

    def off(self):
        self.emitting = False
        self.calls.append(("off",))


class MockAnalyzer(BaseAnalyzer):
    def __init__(self, jammer: MockJammer | None = None) -> None:
        self._jammer = jammer

    def get_spectrum(self, freq_hz, bandwidth_hz):
        # 合成谱：注入开启时给出与样式/功率相关的占用度，供监测链路与自校演示
        emitting = bool(self._jammer and self._jammer.emitting)
        return {"freq_hz": freq_hz, "bandwidth_hz": bandwidth_hz,
                "occupied": emitting,
                "power_dbfs": (self._jammer.power_db if emitting else None)}


class B210Jammer(BaseJammer):
    # 真实 B210：UHD 惰性导入（本机未装时构造失败并给可操作提示）
    def __init__(self, serial: str | None = None, tx_gain_db: float = 0.0) -> None:
        try:
            import uhd  # noqa: F401 —— 仅探测
        except Exception as exc:
            raise RuntimeError(
                "B210 后端需要 UHD（Arch: pacman -S uhd；Windows: PothosSDR）") from exc
        self._serial = serial
        self._tx_gain_db = tx_gain_db
        import uhd  # 已确认可导入
        self._usrp = uhd.usrp.MultiUSRP(",".join(filter(None, ["", serial or ""])))
        self.emitting = False

    def set_style(self, style, params):
        raise NotImplementedError("B210 波形下发在 fn-implement 硬件轮补全（当前用 mock/gnuradio 路径）")

    def set_power_db(self, power_db):
        self._usrp.set_normalized_gain(power_db)

    def on(self):
        self.emitting = True

    def off(self):
        self.emitting = False


class PyVisaJammer(BaseJammer):
    # 未来 SCPI 仪表（如 1433D）：PyVISA 惰性导入
    def __init__(self, resource_str: str) -> None:
        try:
            import pyvisa  # noqa: F401
        except Exception as exc:
            raise RuntimeError("PyVISA 后端需要 pyvisa（pip install pyvisa pyvisa-py）") from exc
        raise NotImplementedError("SCPI 后端随仪表到位补全（R9 插槽已预留）")


REGISTRY = {
    "mock": lambda params: (MockJammer(), MockAnalyzer()),
    "b210": lambda params: (B210Jammer(**(params or {})), MockAnalyzer()),
    "pyvisa": lambda params: (PyVisaJammer((params or {}).get("resource_str", "")), MockAnalyzer()),
}
