# RuntimeFeed 单测：保序/快照/订阅/满丢最旧/close 摘除
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.runtime_feed import RuntimeFeed  # noqa: E402


def test_publish_snapshot_order():
    f = RuntimeFeed(maxlen=3)
    for i in range(5):
        f.publish({"type": "kpi", "n": i})
    snap = f.snapshot()
    assert [m["n"] for m in snap] == [2, 3, 4]   # 满丢最旧


def test_subscribe_receives_and_close():
    f = RuntimeFeed()
    sub = f.subscribe()
    f.publish({"type": "event", "k": 1})
    m = sub.get_nowait()
    assert m and m["k"] == 1 and sub.get_nowait() is None
    sub.close()
    f.publish({"type": "event", "k": 2})
    assert sub.get_nowait() is None               # close 后不再收到


def test_subscriber_queue_drops_oldest_when_full():
    f = RuntimeFeed()
    sub = f.subscribe()
    sub._q.maxsize = 2
    for i in range(5):
        f.publish({"n": i})
    got = []
    while True:
        m = sub.get_nowait()
        if m is None:
            break
        got.append(m["n"])
    assert got[-1] == 4 and len(got) <= 2          # 只保最新的尾巴
