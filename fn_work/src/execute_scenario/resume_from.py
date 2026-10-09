# 纯函数：读 steps.jsonl 进度→(起跑索引, 已完成记录, finished)（R15）
from __future__ import annotations

import json
from pathlib import Path


def resume_from(run_dir, plan):
    # 进度按 (style, power_db) 对齐计划；文件损坏→从 0 重跑（事件由调用方记）
    p = Path(run_dir) / "steps.jsonl"
    if not p.exists() or not plan:
        return 0, [], False
    done = []
    try:
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                done.append(json.loads(ln))
    except Exception:  # noqa: BLE001
        return 0, [], False
    keys = {(st.style, round(float(st.power_db), 3)) for st in plan}
    matched = [d for d in done
               if (d.get("style"), round(float(d.get("power_db")), 3)) in keys]
    start = len(matched)
    return start, matched, start >= len(plan)
