# compute_spectrum_stats 单测：峰位/占用/平坦度
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.record_run_streams.compute_spectrum_stats import compute_spectrum_stats  # noqa: E402

SR = 1_000_000


def test_peak_offset_of_sine():
    t = np.arange(8192) / SR
    iq = np.exp(2j * np.pi * 100_000 * t).astype(np.complex64)
    st = compute_spectrum_stats(iq, SR)
    assert abs(st["peak_offset_hz"] - 100_000) < SR / 8192 * 2
    assert 0 < st["occupied_pct"] <= 1


def test_flatness_noise_less_than_sine():
    rng = np.random.default_rng(0)
    noise = (rng.standard_normal(8192) + 1j * rng.standard_normal(8192)).astype(np.complex64)
    t = np.arange(8192) / SR
    sine = np.exp(2j * np.pi * 100_000 * t).astype(np.complex64)
    assert compute_spectrum_stats(noise, SR)["flatness_db"] < \
           compute_spectrum_stats(sine, SR)["flatness_db"]


def test_empty_raises():
    import pytest
    with pytest.raises(ValueError):
        compute_spectrum_stats(np.array([], dtype=np.complex64), SR)
