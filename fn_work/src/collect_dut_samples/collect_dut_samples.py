# R3 顶层：链路清单→启动样本源持续收集（异常记 gap 不中断）
from __future__ import annotations

import time


def collect_dut_samples(links, duration_s: float, on_sample=None):
    # links=配置列表；返回 (samples, events)；全部失联→报错返回已收内容
    from src.collect_dut_samples.start_dut_source import start_dut_source
    sources = {}
    errors = []
    for cfg in links or []:
        try:
            src = start_dut_source(dict(cfg))
            sources[src.link] = src
        except Exception as exc:  # noqa: BLE001
            errors.append("链路启动失败 %s: %s" % (cfg.get("link"), exc))
    if not sources:
        return [], [{"type": "fatal", "error": "无可用链路源", "detail": errors}]

    samples, events = [], []
    t0 = time.monotonic()
    while time.monotonic() - t0 < duration_s:
        for link in list(sources):
            try:
                s = sources[link].next_sample()
                samples.append(s)
                if on_sample:
                    on_sample(s)
            except ConnectionError as exc:
                events.append({"type": "gap", "link": link, "error": str(exc),
                               "ts_ms": int((time.monotonic() - t0) * 1000)})
                sources[link].close()
                del sources[link]
                if not sources:
                    return samples, events
            except Exception as exc:  # noqa: BLE001
                events.append({"type": "gap", "link": link, "error": repr(exc),
                               "ts_ms": int((time.monotonic() - t0) * 1000)})
        time.sleep(0)
    for src in sources.values():
        src.close()
    return samples, events
