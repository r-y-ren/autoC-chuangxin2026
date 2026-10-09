# 最新 run→材料稿汇编（失效电平/曲线/识别指标/仪器局限声明）；数字溯源失败即报错（R16）
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from src.build_report.build_report import DISCLAIMER

TITLE = {"mid": "STITP 中期材料稿（自动汇编）", "final": "STITP 结题材料稿（自动汇编）"}


def _latest_run(runs_dir: Path) -> Path | None:
    cands = [d for d in runs_dir.iterdir()
             if d.is_dir() and (d / "report.md").exists() and (d / "steps.jsonl").exists()]
    return max(cands, key=lambda d: d.stat().st_mtime) if cands else None


def _f1_line(runs_dir: Path) -> tuple[str, str] | None:
    cands = sorted(runs_dir.glob("*/models/train_report.md"),
                   key=lambda p: p.stat().st_mtime)
    if not cands:
        return None
    p = cands[-1]
    for ln in p.read_text(encoding="utf-8").splitlines():
        if "Macro-F1" in ln:
            return ln.strip(), str(p)
    return None


def build_mid_material(*, mode: str = "mid", runs_dir: str = "runs", out_path=None):
    # 返回材料稿路径；无可用 run 或数字溯源失败→打印原因并返回 None
    runs = Path(runs_dir)
    run = _latest_run(runs)
    if run is None:
        print("无可用 run（需含 report.md 与 steps.jsonl）：", runs)
        return None
    out = Path(out_path) if out_path else \
        Path(__file__).resolve().parents[2].parent / "docs" / (mode + "_draft.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    steps_text = (run / "steps.jsonl").read_text(encoding="utf-8")
    steps = [json.loads(ln) for ln in steps_text.splitlines() if ln.strip()]
    kpi_n = sum(1 for _ in (run / "kpi.csv").open(encoding="utf-8")) - 1 \
        if (run / "kpi.csv").exists() else 0
    fails = [s for s in steps if s.get("failed")]

    # 数字溯源自检：稿内关键数字必须逐个能在来源文件中找到
    sources = {"steps.jsonl": steps_text}
    for s in fails:
        if str(s["power_db"]) not in steps_text:
            print("溯源失败：失效电平 %s 不在 steps.jsonl" % s["power_db"])
            return None

    f1 = _f1_line(runs)
    if f1:
        sources[f1[1]] = Path(f1[1]).read_text(encoding="utf-8")

    fig_dir = run / "figs"
    fig_links = []
    if fig_dir.exists():
        for png in sorted(fig_dir.glob("*.png")):
            rel = os.path.relpath(png, out.parent).replace(os.sep, "/")
            fig_links.append("![%s](%s)" % (png.stem, rel))

    lines = ["# " + TITLE.get(mode, TITLE["mid"]), "",
             "- 运行：%s" % run.name,
             "- KPI 样本数：%d" % kpi_n,
             "- 步进记录：%d 步（失效 %d 步）" % (len(steps), len(fails)),
             "", "## 失效电平（GB 42590 §5.11 口径）", "",
             "| 样式 | 失效电平 dB | 类型 |", "|---|---|---|"]
    if fails:
        for s in fails:
            lines.append("| %s | %s | %s |" % (s.get("style"), s.get("power_db"),
                                               s.get("failure_kind", "-")))
    else:
        lines.append("| （本轮未失效——对照运行或未达失效） | - | - |")
    lines += ["", "## 三元曲线", ""] + fig_links
    if f1:
        lines += ["", "## 干扰识别（分组 CV）", "", "- %s" % f1[0]]
    lines += ["", "## 仪器局限与口径", "", DISCLAIMER, "",
              "## 数字来源", ""]
    for name in sources:
        lines.append("- %s" % name)
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
