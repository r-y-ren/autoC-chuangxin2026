# KPI CSV→标准三图 PNG（责任文档：plot_triple_curves ← R8）
# ①PER-vs-JSR ②吞吐(相对)/误码-vs-时间 ③失效事件时间线；数据不足则跳过并说明
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from src.shared.register_cjk_font import register_cjk_font  # noqa: E402
register_cjk_font()
import matplotlib.pyplot as plt  # noqa: E402


def _load_kpi(kpi_csv):
    with open(kpi_csv, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_steps(run_dir):
    p = Path(run_dir) / "steps.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _power_at(steps, ts_ms):
    for st in steps:
        if st.get("t_start_ms", -1) <= ts_ms <= st.get("t_end_ms", 1 << 60):
            return st.get("power_db")
    return None


def plot_triple_curves(kpi_csv, out_dir):
    kpi_csv = Path(kpi_csv)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _load_kpi(kpi_csv)
    steps = _load_steps(kpi_csv.parent)
    produced, skipped = [], []

    if rows:
        # ① PER vs 功率档（有 steps 则 JSR 轴，否则时间轴兜底）
        fig, ax = plt.subplots(figsize=(6, 4))
        if steps:
            for style in sorted({st.get("style", "?") for st in steps}):
                xs, ys = [], []
                for r in rows:
                    p = _power_at(steps, int(r["ts_ms"]))
                    if p is not None:
                        xs.append(p); ys.append(float(r["per"]))
                if xs:
                    ax.scatter(xs, ys, s=8, label=style)
            ax.set_xlabel("干扰功率档 power_db（JSR 标称轴）")
        else:
            ax.plot([int(r["ts_ms"]) for r in rows], [float(r["per"]) for r in rows])
            ax.set_xlabel("时间 ms（无步进表，时间轴兜底）")
        ax.set_ylabel("PER")
        ax.set_title("① PER vs 干扰电平")
        if ax.get_legend_handles_labels()[0]:
            ax.legend(fontsize=7)
        fig.tight_layout(); p1 = out_dir / "per_vs_jsr.png"; fig.savefig(p1); plt.close(fig)
        produced.append(p1)

        # ② 吞吐(相对)=1-PER 与误码 vs 时间
        fig, ax = plt.subplots(figsize=(6, 4))
        ts = [int(r["ts_ms"]) for r in rows]
        ax.plot(ts, [1 - float(r["per"]) for r in rows], label="吞吐(相对)")
        ax.plot(ts, [float(r["per"]) for r in rows], label="PER", ls="--")
        if "latency_ms" in rows[0] and rows[0]["latency_ms"] not in ("", None):
            ax.plot(ts, [float(r["latency_ms"]) for r in rows], label="时延 ms", ls=":")
        ax.set_xlabel("时间 ms"); ax.set_title("② 吞吐/误码（真实时延列就绪后自动叠加）")
        if ax.get_legend_handles_labels()[0]:
            ax.legend(fontsize=8)
        fig.tight_layout(); p2 = out_dir / "throughput_latency.png"; fig.savefig(p2); plt.close(fig)
        produced.append(p2)

        # ③ 失效/注入事件时间线
        fig, ax = plt.subplots(figsize=(6, 3))
        ev_path = kpi_csv.parent / "events.jsonl"
        events = []
        if ev_path.exists():
            events = [json.loads(ln) for ln in ev_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        ax.plot(ts, [float(r["per"]) for r in rows], lw=1)
        for ev in events:
            kind = ev.get("type", "?")
            if kind in ("injection", "fail", "gap"):
                ax.axvline(int(ev.get("ts_ms", 0)), color="r" if kind == "fail" else "gray",
                           ls="--", lw=0.8)
                ax.annotate(kind, (int(ev.get("ts_ms", 0)), 0.5 + 0.2 * (len(str(kind)) % 3)),
                            fontsize=7)
        ax.set_xlabel("时间 ms"); ax.set_ylabel("PER"); ax.set_title("③ 事件时间线（注入/失效/断连）")
        fig.tight_layout(); p3 = out_dir / "fail_timeline.png"; fig.savefig(p3); plt.close(fig)
        produced.append(p3)
    else:
        skipped = ["kpi.csv 无数据行，三图全跳过"]

    for st in steps:
        if st.get("failed"):
            pass  # 失效电平在 build_report 汇总（本函数只画图）
    return {"produced": [str(p) for p in produced], "skipped": skipped}
