# collect_dut_samples 单测：双源收集+失联 gap 不中断+回调
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.collect_dut_samples.collect_dut_samples import collect_dut_samples  # noqa: E402


def test_collect_two_links_with_gap():
    links = [
        {"type": "fake", "link": "wifi", "rate_hz": 300, "dead_at_s": 0.05},
        {"type": "fake", "link": "nrf24", "rate_hz": 300},
    ]
    seen = []
    samples, events = collect_dut_samples(links, 0.15, on_sample=lambda s: seen.append(s.link))
    links_seen = {s.link for s in samples}
    assert links_seen == {"wifi", "nrf24"}
    assert any(e["type"] == "gap" and e["link"] == "wifi" for e in events)
    nrf = [s for s in samples if s.link == "nrf24"]
    assert len(nrf) > 5          # 失联后另一条继续
    assert seen                  # 回调触发过
    assert all(s.seq >= 1 for s in samples)


def test_no_sources_fatal_event():
    _samples, events = collect_dut_samples([], 0.05)
    assert events and events[0]["type"] == "fatal"
