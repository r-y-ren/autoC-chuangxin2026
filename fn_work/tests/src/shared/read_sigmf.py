# read_sigmf 单测：往返一致+缺失/损坏报因
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.read_sigmf import read_sigmf  # noqa: E402
from src.shared.write_sigmf import write_sigmf  # noqa: E402

IQ = np.exp(2j * np.pi * 0.1 * np.arange(1024)).astype(np.complex64)


def test_roundtrip(tmp_path):
    write_sigmf(tmp_path / "rec", IQ, [{"style": "noise_bandlimited", "power_db": -10}])
    iq, meta = read_sigmf(tmp_path / "rec")
    assert iq.size == IQ.size
    assert meta["annotations"][0]["core:description"].find("noise_bandlimited") >= 0


def test_missing_data_file(tmp_path):
    (tmp_path / "rec.sigmf-meta").write_text("{}", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        read_sigmf(tmp_path / "rec")


def test_broken_meta(tmp_path):
    write_sigmf(tmp_path / "rec", IQ, [{"style": "cw", "power_db": 0}])
    (tmp_path / "rec.sigmf-meta").write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON"):
        read_sigmf(tmp_path / "rec")
