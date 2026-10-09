#!/usr/bin/env python3
# gen 入口：--scenario 必填；--dry-run 只产参数表；--run 秒数>0 才真发射（默认 dry）
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generate_jamming.generate_jamming import generate_jamming  # noqa: E402
from src.shared.load_scenario import load_scenario  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(prog="gen")
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", type=float, default=0.0)
    ap.add_argument("--out", default="runs")
    ap.add_argument("--backend", default="mock")
    a = ap.parse_args()
    sc = load_scenario(a.scenario)
    res = generate_jamming(sc.injection, dry_run=(a.dry_run or a.run <= 0),
                           out_dir=Path(a.out), backend=a.backend)
    for row in res.get("param_table", []):
        print(row)
    print("ok=", res["ok"], "errors=", res["errors"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
