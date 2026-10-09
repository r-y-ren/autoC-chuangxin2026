#!/usr/bin/env python3
# sitl_bridge 入口：PER 台阶→SITL 注入计划（R10 直达）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.bridge_to_sitl.bridge_to_sitl import bridge_to_sitl  # noqa: E402

if __name__ == "__main__":
    run_dir = sys.argv[1] if len(sys.argv) > 1 else "runs/demo"
    print(bridge_to_sitl(run_dir))
