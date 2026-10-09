#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.index_dataset.index_dataset import index_dataset
arg = sys.argv[1] if len(sys.argv) > 1 else "runs/"
try:
    res = index_dataset(arg); print(res); sys.exit(0)
except NotImplementedError as e:
    print(f"[scaffold] {e}"); sys.exit(3)
