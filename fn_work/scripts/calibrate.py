#!/usr/bin/env python3
# calibrate 入口：功率标定表（R2 直达）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.calibrate_power.calibrate_power import calibrate_power  # noqa: E402

if __name__ == "__main__":
    res = calibrate_power([2422000000], list(range(-30, 1, 5)),
                          runs_dir=Path("runs") / "manual")
    print(res)
