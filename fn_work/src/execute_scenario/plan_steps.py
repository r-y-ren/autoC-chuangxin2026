# 注入段→有序步进清单（样式外层×功率内层），纯函数（责任文档：plan_steps ← R5）
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Step:
    index: int
    style: str
    power_db: float
    duration_s: float


def plan_steps(injection):
    # GB 42590 §5.11：自 power_start 起按 step 递增至 power_stop（含端点）；注入为 None→空表
    if injection is None:
        return []
    steps, idx = [], 0
    n_steps = int((injection.power_stop_db - injection.power_start_db) // injection.power_step_db) + 1
    for style in injection.styles:
        for k in range(max(1, n_steps)):
            power = injection.power_start_db + k * injection.power_step_db
            if power > injection.power_stop_db + 1e-9:
                break
            steps.append(Step(index=idx, style=style, power_db=round(power, 3),
                              duration_s=injection.step_duration_s))
            idx += 1
    return steps
