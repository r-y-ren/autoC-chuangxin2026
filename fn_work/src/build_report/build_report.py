# run 目录→report.md（数字全部本 run 实测可溯源）（责任文档：build_report ← R8）
from __future__ import annotations

import json
from pathlib import Path

from src.build_report.plot_triple_curves import plot_triple_curves

DISCLAIMER = ("声明：本平台非 CISPR 16-1-1 意义上的 EMI 测量接收机；"
              "测试采用 GB 42590-2023 §5.11 方法学预研 + EN 300 328 传导等效口径；"
              "一切数字仅出自本 run 实测产物。")


def build_report(run_dir):
    run_dir = Path(run_dir)
    figs = plot_triple_curves(run_dir / "kpi.csv", run_dir / "figs")
    steps = []
    sp = run_dir / "steps.jsonl"
    if sp.exists():
        steps = [json.loads(ln) for ln in sp.read_text(encoding="utf-8").splitlines() if ln.strip()]

    lines = ["# 测评报告", ""]
    scen = run_dir / "scenario.yaml"
    if scen.exists():
        try:
            meta = json.loads(scen.read_text(encoding="utf-8"))
            lines += ["- 场景：%s" % meta.get("name"), ""]
        except Exception:  # noqa: BLE001
            lines += ["- 场景：（scenario.yaml 不可解析）", ""]
    cal = run_dir / "calibration.json"
    if cal.exists():
        lines += ["## 标定表", "", "见 `%s`（本 run 引用）。" % cal.name, ""]

    spd = run_dir / "speed.json"
    if spd.exists():
        try:
            info = json.loads(spd.read_text(encoding="utf-8"))
            if float(info.get("speed", 1.0)) != 1.0:
                lines += ["> 脚注：%s" % info.get("note", "加速运行"), ""]
        except Exception:  # noqa: BLE001
            pass
    calst = run_dir / "calibration_state.json"
    if calst.exists():
        try:
            src = json.loads(calst.read_text(encoding="utf-8")).get("source")
            lines += ["> 标定：%s" % ("标定表已应用（calibration.json）" if src == "calibrated"
                                     else "未标定（恒等映射）"), ""]
        except Exception:  # noqa: BLE001
            pass

    lines += ["## 三元曲线", ""]
    if figs["produced"]:
        lines += ["![per_vs_jsr](figs/per_vs_jsr.png)", "",
                  "![throughput_latency](figs/throughput_latency.png)", "",
                  "![fail_timeline](figs/fail_timeline.png)", ""]
    else:
        lines += ["（数据不足：%s）" % "; ".join(figs["skipped"]), ""]

    fail_rows = [st for st in steps if st.get("failed")]
    lines += ["## 失效电平表（GB 42590 §5.11）", "",
              "| 样式 | 失效电平 dB | 失效类型 |", "|---|---|---|"]
    for st in fail_rows:
        lines.append("| %s | %s | %s |" % (st.get("style"), st.get("power_db"),
                                           st.get("failure_kind", "-")))
    if not fail_rows:
        lines.append("| （无失效记录——对照运行或未达失效） | - | - |")

    kpi = run_dir / "kpi.csv"
    if kpi.exists():
        n = sum(1 for _ in kpi.open(encoding="utf-8")) - 1
        lines += ["", "## 样本量", "", "- KPI 样本数：%d" % max(n, 0)]
    lines += ["", "## 仪器局限与口径", "", DISCLAIMER, ""]
    out = run_dir / "report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
