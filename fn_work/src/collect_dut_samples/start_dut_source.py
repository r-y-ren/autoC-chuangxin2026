# 链路插槽工厂：真实串口源/合成源同接口（责任文档：start_dut_source ← R3）
from __future__ import annotations

import json
import time

from src.collect_dut_samples.parse_serial_line import DutSample, parse_serial_line, reset_seq_tracking
from src.shared.per_response_model import per_response_model


class FakeDutSource:
    # 合成链路：jam_profile=[(时刻s, PER)] 显式台阶；或挂 jammer 由功率响应曲线推 PER
    def __init__(self, config: dict):
        self.link = str(config.get("link", "wifi"))
        self.rate_hz = float(config.get("rate_hz", 1.0))
        self.profile = list(config.get("jam_profile", []) or [])
        self.jammer = config.get("jammer")            # MockJammer 等可读状态对象
        self.fail_power_db = float(config.get("fail_power_db", 10.0))
        self.seed = int(config.get("seed", 0))
        self._t0 = time.monotonic()
        self._seq = 0
        self._dead_at = config.get("dead_at_s")       # 模拟失联时刻
        self._base = config.get("base_per", 0.0)

    def _per_now(self, t: float) -> float:
        if self.dead(t):
            return 1.0
        per = self._base
        if self.jammer is not None and getattr(self.jammer, "emitting", False):
            p = float(self.jammer.power_db or 0.0)
            per = per_response_model(p, self.fail_power_db, base_per=self._base)
        for t_k, per_k in self.profile:
            if t >= t_k:
                per = float(per_k)
        return min(1.0, per)

    def dead(self, t: float) -> bool:
        return self._dead_at is not None and t >= self._dead_at

    def next_sample(self) -> DutSample:
        # 按速率节拍出一个样本（测试用高 rate_hz 压缩等待）
        self._seq += 1
        t = time.monotonic() - self._t0
        target = self._seq / max(self.rate_hz, 1e-6)
        while t < target:
            time.sleep(min(0.005, max(0.0, target - t)))
            t = time.monotonic() - self._t0
        per = self._per_now(t)
        tx = 100
        s = DutSample(link=self.link, seq=self._seq,
                      ts_ms=int(t * 1000), per=per, tx_n=tx,
                      err_n=int(per * tx),
                      rssi_dbm=(-60.0 - 10.0 * per) if self.link == "wifi" else None,
                      arc_avg=(per * 5) if self.link == "nrf24" else None,
                      plos_cnt=(int(per * 100)) if self.link == "nrf24" else None,
                      fw="fake-0.1")
        if self.dead(t):
            raise ConnectionError("链路 %s 失联（合成 dead_at）" % self.link)
        return s

    def close(self) -> None:
        return None


class SerialDutSource:
    # 真实串口源：pyserial 惰性导入，115200 8N1 逐行解析
    def __init__(self, config: dict):
        try:
            import serial  # noqa: F401
        except Exception as exc:
            raise RuntimeError("真实串口源需要 pyserial（pip install pyserial）") from exc
        import serial as _serial
        reset_seq_tracking()  # 会话级清一次，保住逐行 seq 回退检测
        port = config.get("port")
        if not port:
            raise ValueError("串口源配置缺 port")
        self.link = str(config.get("link", port))
        self._ser = _serial.Serial(port, 115200, timeout=1.0)

    def next_sample(self) -> DutSample:
        line = self._ser.readline().strip()
        return parse_serial_line(line)

    def close(self) -> None:
        self._ser.close()


def start_dut_source(config: dict):
    # type=fake|serial；未知类型拒绝
    t = str(config.get("type", "fake"))
    if t == "fake":
        return FakeDutSource(config)
    if t == "serial":
        return SerialDutSource(config)
    raise ValueError("未知链路类型 %r（可用: fake/serial）" % t)
