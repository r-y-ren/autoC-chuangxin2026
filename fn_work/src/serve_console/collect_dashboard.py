# 产物→仪表盘四组数据包（责任文档演进轮四：collect_dashboard）
from __future__ import annotations

import json
from pathlib import Path


def _fails_of(run_dir: Path) -> list:
    p = run_dir / "steps.jsonl"
    if not p.exists():
        return []
    out = []
    try:
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                st = json.loads(ln)
                if st.get("failed"):
                    out.append(st)
    except Exception:  # noqa: BLE001
        pass
    return out


def _run_entry(run_dir: Path) -> dict:
    fails = _fails_of(run_dir)
    fail_levels = {}
    for st in fails:
        fail_levels.setdefault(st.get("style"), st.get("power_db"))
    kpi_n = 0
    kp = run_dir / "kpi.csv"
    if kp.exists():
        kpi_n = sum(1 for _ in kp.open(encoding="utf-8")) - 1
    return {"name": run_dir.name, "mtime": int(run_dir.stat().st_mtime),
            "fails": len(fails), "fail_levels": fail_levels, "kpi_n": max(kpi_n, 0)}


def collect_dashboard(runs_dir: str = "runs") -> dict:
    # 四组：latest/history/model/capability；数字一律取自产物文件；单项缺失→空值不抛错
    runs = Path(runs_dir)
    out = {"empty": True, "latest": None, "history": [], "model": None,
           "capability": {}}

    # capability（不依赖 runs 存在）
    try:
        from src.generate_jamming.synthesize_style import STYLE_BUILDERS
        styles_n = len(STYLE_BUILDERS)
    except Exception:  # noqa: BLE001
        styles_n = 0
    scen_dir = Path(__file__).resolve().parents[2] / "scenarios"
    scen_n = len(list(scen_dir.glob("*.yaml"))) if scen_dir.exists() else 0
    cands = []
    if runs.exists():
        cands = [d for d in runs.iterdir()
                 if d.is_dir() and (d / "report.md").exists()
                 and (d / "steps.jsonl").exists()]
    out["capability"] = {"styles": styles_n, "scenarios": scen_n,
                         "plugin_slots": 3, "total_runs": len(cands)}
    if not cands:
        return out

    cands.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    out["history"] = [_run_entry(d) for d in cands[:30]]

    latest = cands[0]
    entry = out["history"][0]
    scen_name = ""
    try:
        scen_name = json.loads(
            (latest / "scenario.yaml").read_text(encoding="utf-8")).get("name", "")
    except Exception:  # noqa: BLE001
        pass
    figs = ["/runs-media/%s/figs/%s" % (latest.name, p.name)
            for p in sorted((latest / "figs").glob("*.png"))] \
        if (latest / "figs").exists() else []
    speed_note = cal_note = ""
    try:
        sp = json.loads((latest / "speed.json").read_text(encoding="utf-8"))
        if float(sp.get("speed", 1.0)) != 1.0:
            speed_note = sp.get("note", "加速运行")
            entry["synthetic"] = True
    except Exception:  # noqa: BLE001
        pass
    try:
        cs = json.loads((latest / "calibration_state.json").read_text(encoding="utf-8"))
        cal_note = "标定表已应用" if cs.get("source") == "calibrated" else "未标定（恒等）"
    except Exception:  # noqa: BLE001
        pass
    out["latest"] = {"name": latest.name, "scenario": scen_name,
                     "fail_levels": entry["fail_levels"], "kpi_n": entry["kpi_n"],
                     "figs": figs, "speed_note": speed_note,
                     "cal_note": cal_note,
                     "synthetic": entry.get("synthetic", False)}

    # model：最新 train_report + 最新 dataset_index
    try:
        reps = sorted(runs.glob("*/models/train_report.md"),
                      key=lambda p: p.stat().st_mtime)
        if reps:
            for ln in reps[-1].read_text(encoding="utf-8").splitlines():
                if "Macro-F1" in ln:
                    out["model"] = {"f1_line": ln.strip(),
                                    "run": reps[-1].parts[-3]}
                    break
    except Exception:  # noqa: BLE001
        pass
    try:
        idxs = sorted(runs.glob("*/dataset_index.json"),
                      key=lambda p: p.stat().st_mtime)
        if idxs:
            idx = json.loads(idxs[-1].read_text(encoding="utf-8"))
            m = out["model"] or {}
            m["recordings"] = len(idx.get("recordings", []))
            m["groups"] = len(idx.get("groups", []))
            out["model"] = m
    except Exception:  # noqa: BLE001
        pass

    out["empty"] = False
    return out
