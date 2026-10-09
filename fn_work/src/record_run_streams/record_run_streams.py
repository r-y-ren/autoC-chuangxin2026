# R4 顶层：三路（DUT∥监测谱∥注入事件）统一时间戳采集落 run 目录
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from src.collect_dut_samples.collect_dut_samples import collect_dut_samples
from src.create_instrument_backend.backends import MockAnalyzer


def record_run_streams(scenario, duration_s: float, run_dir, with_injection: bool = False,
                        *, jammer=None, extra_events=None):
    # 签名微调（batches.md 登记）：kw jammer/extra_events 供执行器注入事件与监测联动
    # 返回 {run_dir, kpi_csv, events_jsonl, monitor_csv, coverage_ratio}
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "scenario.yaml").write_text(
        json.dumps({"name": getattr(scenario, "name", "unnamed")}, ensure_ascii=False),
        encoding="utf-8")

    kpi_csv = run_dir / "kpi.csv"
    events_jsonl = run_dir / "events.jsonl"
    monitor_csv = run_dir / "monitor.csv"

    host0 = time.monotonic()

    def host_ms() -> int:
        return int((time.monotonic() - host0) * 1000)

    first_ms, last_ms = None, None
    with kpi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts_ms", "link", "seq", "per", "tx_n", "err_n",
                    "rssi_dbm", "arc_avg", "plos_cnt"])

        def on_sample(s):
            nonlocal first_ms, last_ms
            ts = host_ms()
            first_ms = ts if first_ms is None else first_ms
            last_ms = ts
            w.writerow([ts, s.link, s.seq, s.per, s.tx_n, s.err_n,
                        s.rssi_dbm, s.arc_avg, s.plos_cnt])

        links = [{"type": "fake", "link": name, "rate_hz": 200,
                  "jammer": jammer} for name in (scenario.dut_links or ["wifi"])]
        samples, gap_events = collect_dut_samples(links, duration_s, on_sample=on_sample)

    events = list(extra_events or []) + gap_events
    with events_jsonl.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    analyzer = MockAnalyzer(jammer) if jammer is not None else None
    with monitor_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts_ms", "occupied", "power_dbfs"])
        if with_injection and analyzer is not None:
            for _ in range(max(1, int(duration_s * 2))):
                spec = analyzer.get_spectrum(0, 0)
                w.writerow([host_ms(), spec["occupied"], spec["power_dbfs"]])
                time.sleep(min(0.05, duration_s / 4))

    span = 0 if (first_ms is None or last_ms is None) else (last_ms - first_ms)
    coverage = 0.0 if duration_s <= 0 else min(1.0, span / (duration_s * 1000))
    return {"run_dir": run_dir, "kpi_csv": kpi_csv, "events_jsonl": events_jsonl,
            "monitor_csv": monitor_csv, "coverage_ratio": round(coverage, 4),
            "n_samples": len(samples)}
