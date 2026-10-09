#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.train_classifier.train_classifier import train_classifier
arg = sys.argv[1] if len(sys.argv) > 1 else "runs/dataset_v1"
try:
    res = train_classifier(arg); print(res); sys.exit(0)
except NotImplementedError as e:
    print(f"[scaffold] {e}"); sys.exit(3)
