# write_sigmf 单测：写文件对+真值字段强制
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.write_sigmf import write_sigmf  # noqa: E402

import numpy as np  # noqa: E402

IQ = np.exp(2j * np.pi * 0.1 * np.arange(4096)).astype(np.complex64)


def test_write_pair(tmp_path):
    meta_path = write_sigmf(tmp_path / "rec", IQ,
                            [{"style": "cw", "power_db": -5}])
    assert meta_path.exists()
    assert Path(str(tmp_path / "rec") + ".sigmf-data").exists()


def test_reject_missing_truth(tmp_path):
    with pytest.raises(ValueError, match="真值"):
        write_sigmf(tmp_path / "rec", IQ, [{"style": "cw"}])
    with pytest.raises(ValueError, match="真值"):
        write_sigmf(tmp_path / "rec", IQ, [])


def test_reject_empty_iq(tmp_path):
    with pytest.raises(ValueError, match="IQ 为空"):
        write_sigmf(tmp_path / "rec", np.array([], dtype=np.complex64),
                    [{"style": "cw", "power_db": 0}])
