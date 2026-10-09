# RuntimeFeed→WebSocket 帧流（责任文档演进轮三）
from __future__ import annotations

import asyncio
import time


async def ws_stream_feed(ws, feed):
    # 快照续推→增量 ≤10Hz 节流→空闲 1s 心跳；发送失败静默摘除该连接
    try:
        for m in feed.snapshot():
            await ws.send_json(m)
        sub = feed.subscribe()
        last_data = time.monotonic()
        while True:
            batch = []
            while True:
                m = sub.get_nowait()
                if m is None:
                    break
                batch.append(m)
            if batch:
                last_data = time.monotonic()
                for m in batch[-8:]:   # 节流合并：每拍最多补发 8 帧
                    await ws.send_json(m)
            elif time.monotonic() - last_data > 1.0:
                await ws.send_json({"type": "idle"})
                last_data = time.monotonic()
            await asyncio.sleep(0.1)
    except Exception:  # noqa: BLE001 —— 断连/发送失败静默退出
        return
    finally:
        if "sub" in locals():
            sub.close()
