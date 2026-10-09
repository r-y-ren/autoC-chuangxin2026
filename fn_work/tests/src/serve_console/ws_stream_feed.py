# ws_stream_feed 集成：快照续推+增量流+idle 心跳（经 TestClient WS）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.serve_console.serve_console import create_app  # noqa: E402
from src.shared.runtime_feed import RuntimeFeed  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


def test_ws_streams_kpi_and_idle():
    app = create_app()
    feed: RuntimeFeed = app.state.feed
    for i in range(12):
        feed.publish({"type": "kpi", "link": "wifi", "seq": i,
                      "per": 0.1 + 0.01 * i, "ts_ms": i * 100})
    with TestClient(app) as c:
        with c.websocket_connect("/ws") as ws:
            got = [ws.receive_json() for _ in range(12)]
    kpis = [m for m in got if m.get("type") == "kpi"]
    assert len(kpis) >= 5
    pers = [m["per"] for m in kpis]
    assert len(set(pers)) > 1                      # 非常数（R19 验收核心）


def test_ws_idle_heartbeat():
    app = create_app()
    with TestClient(app) as c:
        with c.websocket_connect("/ws") as ws:
            msgs = [ws.receive_json() for _ in range(3)]
    assert any(m.get("type") == "idle" for m in msgs)
