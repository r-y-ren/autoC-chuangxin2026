# 纯函数：按倍速返回同步缩放判据（sustain/disconnect÷speed，等效真实时间口径）（R14）
from __future__ import annotations

from src.shared.load_scenario import CriteriaSpec


def scaled_criteria(criteria, speed: float):
    # 返回 (缩放后判据, {speed, note})；speed<=0 拒绝
    if speed <= 0:
        raise ValueError("speed 必须>0， got %r" % speed)
    eff = CriteriaSpec(per_threshold=criteria.per_threshold,
                       sustain_s=criteria.sustain_s / speed,
                       disconnect_s=criteria.disconnect_s / speed)
    info = {"speed": speed,
            "note": "加速倍率 %g×（判据 sustain/disconnect 已同步缩放，等效真实时间口径）" % speed}
    return eff, info
