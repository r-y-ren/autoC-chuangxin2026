#!/usr/bin/env python3
# 启动器入口（start.sh/start.bat 包装；--selfcheck 供验收）
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.launch_console.launch_console import launch_console  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog="launch")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    raise SystemExit(launch_console(selftest=a.selfcheck, no_browser=a.no_browser,
                                    port=a.port))
