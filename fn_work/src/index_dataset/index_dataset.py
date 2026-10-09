# R6 顶层：扫描 runs→逐录制校验→按录制分组产 dataset_index.json（责任文档：index_dataset）
from __future__ import annotations

import json
from pathlib import Path

from src.shared.read_sigmf import read_sigmf


def _truth_of(meta) -> tuple:
    # 真值=annotations 内含 style/power_db；返回 (ok, style, power_db)
    anns = meta.get("annotations") or []
    if not anns:
        return False, None, None
    try:
        labels = json.loads(anns[0].get("core:description", "{}"))
    except Exception:  # noqa: BLE001
        return False, None, None
    if "style" not in labels or "power_db" not in labels:
        return False, None, None
    return True, labels["style"], labels["power_db"]


def index_dataset(runs_dir: str):
    # 返回 {recordings, groups, errors, index_path}；坏录制点名但不中断
    root = Path(runs_dir)
    recordings, groups, errors = [], [], []
    for meta_path in sorted(root.rglob("*.sigmf-meta")):
        base = meta_path.with_suffix("")  # 去掉 .sigmf-meta
        try:
            _iq, meta = read_sigmf(base)
            ok, style, power = _truth_of(meta)
            if not ok:
                raise ValueError("真值标注缺失（style/power_db）")
            group = base.parent.name
            recordings.append({"base": str(base), "group": group,
                               "style": style, "power_db": power,
                               "samples": int(_iq.size)})
            if group not in groups:
                groups.append(group)
        except Exception as exc:  # noqa: BLE001
            errors.append("%s: %s" % (meta_path, exc))
    index = {"recordings": recordings, "groups": groups, "errors": errors}
    index_path = Path(runs_dir) / "dataset_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"recordings": len(recordings), "groups": groups,
            "errors": errors, "index_path": str(index_path)}
