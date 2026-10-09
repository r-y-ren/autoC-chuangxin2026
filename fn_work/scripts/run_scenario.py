#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.execute_scenario.execute_scenario import execute_scenario
arg = sys.argv[-1] if len(sys.argv) > 1 else "scenarios/smoke_loop.yaml"
try:
    res = execute_scenario(arg); print(res); sys.exit(0)
except NotImplementedError as e:
    print(f"[scaffold] {e}"); sys.exit(3)
