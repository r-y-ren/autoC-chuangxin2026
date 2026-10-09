# grouped_cv_split 单测：同组同侧/全覆盖/组数不足拒
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.train_classifier.grouped_cv_split import grouped_cv_split  # noqa: E402


def _idx(tmp_path, groups):
    p = tmp_path / "dataset_index.json"
    import json
    p.write_text(json.dumps({"groups": groups}), encoding="utf-8")
    return str(p)


def test_no_overlap_full_cover(tmp_path):
    folds = grouped_cv_split(_idx(tmp_path, ["a", "b", "c", "d", "e", "f"]), 3)
    all_test = []
    for tr, te in folds:
        assert not (set(tr) & set(te))
        all_test += te
    assert sorted(all_test) == ["a", "b", "c", "d", "e", "f"]


def test_too_few_groups(tmp_path):
    with pytest.raises(ValueError, match="组数"):
        grouped_cv_split(_idx(tmp_path, ["a"]), 3)
