# 仪表插槽工厂：按名返回(干扰源, 分析仪)，接口固定（责任文档：create_instrument_backend ← R9）
from __future__ import annotations

from src.create_instrument_backend.backends import REGISTRY


def create_instrument_backend(name: str, *, params: dict | None = None):
    # mock/b210/pyvisa；未知名或驱动缺失→异常含可操作提示
    if name not in REGISTRY:
        raise ValueError("未知后端 %r，可用: %s" % (name, sorted(REGISTRY)))
    return REGISTRY[name](params)
