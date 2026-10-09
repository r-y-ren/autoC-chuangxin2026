# RuntimeFeed：运行数据扇入扇出缓冲（责任文档演进轮三）
from __future__ import annotations

import threading
from collections import deque
from queue import Empty, Full, Queue


class _Subscription:
    def __init__(self, feed, q: Queue) -> None:
        self._feed = feed
        self._q = q

    def get_nowait(self):
        try:
            return self._q.get_nowait()
        except Empty:
            return None

    def close(self) -> None:
        self._feed._drop(self._q)


class RuntimeFeed:
    # 发布端→订阅端缓冲中转：多线程安全、限长防爆、三类消息透传
    def __init__(self, maxlen: int = 500) -> None:
        self._buf: deque = deque(maxlen=maxlen)
        self._subs: list[Queue] = []
        self._lock = threading.Lock()

    def publish(self, msg: dict) -> None:
        with self._lock:
            self._buf.append(msg)
            for q in list(self._subs):
                try:
                    q.put_nowait(msg)
                except Full:  # 满丢最旧，保实时性
                    try:
                        q.get_nowait()
                    except Empty:
                        pass
                    try:
                        q.put_nowait(msg)
                    except Full:
                        pass

    def snapshot(self) -> list:
        with self._lock:
            return list(self._buf)

    def subscribe(self):
        q: Queue = Queue(maxsize=1000)
        with self._lock:
            self._subs.append(q)
        return _Subscription(self, q)

    def _drop(self, q: Queue) -> None:
        with self._lock:
            if q in self._subs:
                self._subs.remove(q)
