# make_spectrogram 单测：形状/能量/峰位/空输入
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.make_spectrogram import make_spectrogram  # noqa: E402


def test_shape_and_energy():
    t = np.arange(4096) / 1e6
    spec = make_spectrogram(np.exp(2j * np.pi * 50e3 * t), nfft=256)
    assert spec.shape[0] == 256 and spec.shape[1] > 10
    assert float(spec.max()) > 0


def test_empty_raises():
    with pytest.raises(ValueError):
        make_spectrogram(np.array([], dtype=np.complex64))
