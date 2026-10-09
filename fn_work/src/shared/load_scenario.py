# 场景 YAML 唯一入口→强类型场景对象+语义校验拒载（责任文档：shared/load_scenario）
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

KNOWN_STYLES = ("cw", "sweep", "chirp", "noise_bandlimited", "partial_band", "pulse")
BAND_HZ = (2_400_000_000, 2_483_500_000)  # 2.4G ISM（一期被测与注入频段）


@dataclass
class CriteriaSpec:
    per_threshold: float = 0.10
    sustain_s: float = 10.0
    disconnect_s: float = 30.0


@dataclass
class SafetySpec:
    max_tx_gain_db: float = 0.0


@dataclass
class RecordSpec:
    sigmf: bool = True
    ch2_monitor: bool = True


@dataclass
class InjectionSpec:
    styles: list = field(default_factory=list)
    freq_hz: int = 0
    bandwidth_hz: int = 0
    params: dict = field(default_factory=dict)
    power_start_db: float = -5.0
    power_step_db: float = 5.0
    power_stop_db: float = 40.0
    step_duration_s: float = 30.0


@dataclass
class ScenarioSpec:
    meta: dict
    dut_links: list
    injection: InjectionSpec | None
    criteria: CriteriaSpec
    safety: SafetySpec
    record: RecordSpec

    @property
    def name(self) -> str:
        return str(self.meta.get("name", "unnamed"))


def load_scenario(path) -> ScenarioSpec:
    # 读场景卡→ScenarioSpec；schema/语义不合法→ValueError（逐条列出字段名）
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("场景卡不存在: %s" % p)
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("场景卡必须是映射结构")
    errors = []

    meta = raw.get("meta")
    if not isinstance(meta, dict) or not meta.get("name"):
        errors.append("meta.name 缺失")

    dut = raw.get("dut", {}) or {}
    links = dut.get("links", []) if isinstance(dut, dict) else []
    if not isinstance(links, list):
        errors.append("dut.links 必须是列表")

    inj_raw = raw.get("injection")
    injection = None
    if inj_raw is not None:
        if not isinstance(inj_raw, dict):
            errors.append("injection 必须是映射或 null")
        else:
            styles = inj_raw.get("styles", [])
            freq = int(inj_raw.get("freq_hz", 0))
            bw = int(inj_raw.get("bandwidth_hz", 0))
            bad = [s for s in styles if s not in KNOWN_STYLES]
            if not styles:
                errors.append("injection.styles 为空")
            if bad:
                errors.append("injection.styles 含未知样式: %s" % bad)
            if not (BAND_HZ[0] <= freq <= BAND_HZ[1]):
                errors.append("injection.freq_hz=%s 超出 2.4G 频段" % freq)
            if bw <= 0:
                errors.append("injection.bandwidth_hz 必须>0")
            ps = float(inj_raw.get("power_start_db", -5))
            pw = float(inj_raw.get("power_stop_db", 40))
            step = float(inj_raw.get("power_step_db", 5))
            dur = float(inj_raw.get("step_duration_s", 30))
            if ps > pw:
                errors.append("power_start_db > power_stop_db")
            if step <= 0 or dur <= 0:
                errors.append("power_step_db / step_duration_s 必须>0")
            injection = InjectionSpec(styles=list(styles), freq_hz=freq, bandwidth_hz=bw,
                                      params=dict(inj_raw.get("params", {}) or {}),
                                      power_start_db=ps, power_step_db=step,
                                      power_stop_db=pw, step_duration_s=dur)

    cr = raw.get("criteria", {}) or {}
    criteria = CriteriaSpec(per_threshold=float(cr.get("per_threshold", 0.10)),
                            sustain_s=float(cr.get("sustain_s", 10.0)),
                            disconnect_s=float(cr.get("disconnect_s", 30.0)))
    if not (0 < criteria.per_threshold <= 1):
        errors.append("criteria.per_threshold 须在 (0,1]")

    sf = raw.get("safety", {}) or {}
    safety = SafetySpec(max_tx_gain_db=float(sf.get("max_tx_gain_db", 0.0)))
    if safety.max_tx_gain_db > 0:
        errors.append("safety.max_tx_gain_db 硬顶 0dB，不许为正")

    rc = raw.get("record", {}) or {}
    record = RecordSpec(sigmf=bool(rc.get("sigmf", True)),
                        ch2_monitor=bool(rc.get("ch2_monitor", True)))

    if errors:
        raise ValueError("场景卡不合法: " + "; ".join(errors))
    return ScenarioSpec(meta=meta or {"name": "unnamed"}, dut_links=list(links),
                        injection=injection, criteria=criteria, safety=safety,
                        record=record)
