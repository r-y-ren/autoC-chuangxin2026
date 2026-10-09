# EstopManager：全局急停管理器（注册回调→按序触发→状态只升不降）
from __future__ import annotations


class EstopManager:
    def __init__(self) -> None:
        self._callbacks = []
        self._fired = False
        self._reason = None

    def arm(self, callback) -> None:
        # 注册停发射回调；fire 时按注册序同步调用
        self._callbacks.append(callback)

    def fire(self, reason: str) -> None:
        # 触发急停（幂等）；单个回调抛错不阻断其余
        if self._fired:
            return
        self._fired = True
        self._reason = reason
        for cb in self._callbacks:
            try:
                cb()
            except Exception:  # noqa: BLE001 —— 急停链不许被单点失败打断
                continue

    @property
    def state(self) -> str:
        # 'armed' | 'fired: 原因'
        if not self._fired:
            return "armed"
        return "fired: %s" % self._reason
