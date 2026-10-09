#!/usr/bin/env python3
# 中期/结题材料编译入口（蓝图验收 doc-mid/doc-final）——桥接 fn_work 包
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fn_work"))
from src.build_mid_material.build_mid_material import build_mid_material  # noqa: E402

if __name__ == "__main__":
    mode = "final" if "--final" in sys.argv else "mid"
    out = None
    if "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]
    fw = Path(__file__).resolve().parent.parent / "fn_work"
    res = build_mid_material(mode=mode, runs_dir=str(fw / "runs"), out_path=out)
    print(res)
    raise SystemExit(0 if res else 1)
