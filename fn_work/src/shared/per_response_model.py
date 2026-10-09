# 功率→PER 响应唯一模型（责任文档演进轮三：滑杆预览=实测口径的保证）
from __future__ import annotations

import math


def per_response_model(power_db: float, fail_power_db: float, base_per: float = 0.0) -> float:
    # 线性响应：fail_power_db-15dB 起爬升，fail_power_db 处 PER≈1；base_per 为本底下限
    if not math.isfinite(float(fail_power_db)):
        raise ValueError("fail_power_db 必须为有限数值， got %r" % (fail_power_db,))
    p = float(power_db)
    resp = (p - (float(fail_power_db) - 15.0)) / 15.0
    return float(max(float(base_per), min(1.0, max(0.0, resp))))
