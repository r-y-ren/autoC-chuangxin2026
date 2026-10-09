#!/usr/bin/env python3
# record 入口：独立三路采集（R4 直达；--dur 秒 --scenario 场景卡）
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.record_run_streams.record_run_streams import record_run_streams  # noqa: E402
from src.shared.load_scenario import load_scenario  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(prog="record")
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--scenario", default="scenarios/smoke_loop.yaml")
    ap.add_argument("--out", default="runs/manual")
    a = ap.parse_args()
    res = record_run_streams(load_scenario(a.scenario), a.dur, Path(a.out),
                             with_injection=False)
    print(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
