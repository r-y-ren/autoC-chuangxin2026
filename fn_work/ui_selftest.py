#!/usr/bin/env python3
# Web 操控台无头自检（蓝图验收 sw-ui-boot）：serve_console(selftest=True) 四点
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.serve_console.serve_console import serve_console  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(serve_console(selftest=True))
