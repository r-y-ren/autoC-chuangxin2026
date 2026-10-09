#!/usr/bin/env python3
# 一键启动冒烟（蓝图验收 sw-boot）——桩阶段：编译/导入/场景卡/桩标记四查
import compileall, importlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOPS = ["generate_jamming", "calibrate_power", "collect_dut_samples", "record_run_streams",
        "execute_scenario", "index_dataset", "train_classifier", "predict_style", "run_demo",
        "build_report", "create_instrument_backend", "serve_console", "bridge_to_sitl",
        "animate_link_state", "shared"]
fail = []

if sys.version_info < (3, 10):
    fail.append("need Python>=3.10")

print("[1/4] compileall src + scripts ...")
for d in ("src", "scripts"):
    if compileall.compile_dir(str(ROOT / d), quiet=1) is not True:
        fail.append(f"compileall {d}")

print("[2/4] import packages ...")
sys.path.insert(0, str(ROOT))
for t in TOPS:
    try:
        importlib.import_module("src." + t)
    except Exception as exc:
        fail.append(f"import src.{t}: {exc}")

print("[3/4] scenario fixtures ...")
try:
    import yaml
    for y in sorted((ROOT / "scenarios").glob("*.yaml")):
        yaml.safe_load(y.read_text(encoding="utf-8")); print("      ok", y.name)
except Exception as exc:
    fail.append(f"scenario parse: {exc}")

print("[4/4] stub markers ...")
_m = "unimplemented" + ":fn:"  # 运行时拼接，避免本文件自计入
marks = sum(p.read_text(encoding="utf-8").count(_m) for p in (ROOT / "src").rglob("*.py"))
print("      残留桩计数 x", marks, "(实现期递减，fn-close 期应为 0)")

if fail:
    print("SMOKE BOOT FAIL:"); [print("  -", f) for f in fail]; sys.exit(1)
print("SMOKE BOOT OK"); sys.exit(0)
