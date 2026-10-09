# index_dataset 单测：分组索引+坏录制点名
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.index_dataset.index_dataset import index_dataset  # noqa: E402
from src.shared.write_sigmf import write_sigmf  # noqa: E402

IQ = np.exp(2j * np.pi * 0.1 * np.arange(2048)).astype(np.complex64)


def test_index_with_bad_recording(tmp_path):
    for grp in ("runA", "runB"):
        write_sigmf(tmp_path / grp / "rec1", IQ,
                    [{"style": "cw", "power_db": -5}])
    (tmp_path / "runBad").mkdir()
    (tmp_path / "runBad" / "rec2.sigmf-meta").write_text("{}", encoding="utf-8")
    res = index_dataset(str(tmp_path))
    assert res["recordings"] == 2
    assert sorted(res["groups"]) == ["runA", "runB"]
    assert len(res["errors"]) == 1 and "rec2" in res["errors"][0]
    assert Path(res["index_path"]).exists()
