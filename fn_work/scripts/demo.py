#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.run_demo.run_demo import run_demo
try:
    res = run_demo(quick="--full" not in sys.argv); print(res); sys.exit(0)
except NotImplementedError as e:
    print(f"[scaffold] {e}"); sys.exit(3)
