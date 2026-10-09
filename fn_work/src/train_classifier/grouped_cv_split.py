# 索引→n 折分组划分（同组同侧，杜绝段级泄漏），纯函数（责任文档：grouped_cv_split ← R7）
from __future__ import annotations

import json
from pathlib import Path


def grouped_cv_split(index_path: str, n_splits: int = 5):
    # 返回 [(train_groups, test_groups)]×n_splits；组数<折数→ValueError
    idx = json.loads(Path(index_path).read_text(encoding="utf-8"))
    groups = list(idx.get("groups") or [])
    if len(groups) < n_splits:
        raise ValueError("组数 %d < 折数 %d（分组 CV 不可行，需更多录制组）" % (len(groups), n_splits))
    folds = []
    for k in range(n_splits):
        test = [g for i, g in enumerate(groups) if i % n_splits == k]
        train = [g for g in groups if g not in test]
        folds.append((train, test))
    return folds
