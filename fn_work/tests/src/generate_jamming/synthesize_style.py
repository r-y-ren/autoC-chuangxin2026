# synthesize_style 单测：六样式/注册表一致/未知拒
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.generate_jamming.synthesize_style import STYLE_BUILDERS, synthesize_style  # noqa: E402
from src.shared.load_scenario import KNOWN_STYLES  # noqa: E402

P = {"freq_hz": 2422000000, "bandwidth_hz": 20e6, "duration_s": 0.05, "sample_rate_sps": 1e6,
     "seed": 7}


@pytest.mark.parametrize("style", list(KNOWN_STYLES))
def test_six_styles_produce_iq(style):
    iq, meta = synthesize_style(style, dict(P))
    assert iq.dtype == np.complex64 and iq.size >= 8
    assert float(np.abs(iq).max()) > 0
    assert meta["style"] == style


def test_registry_matches_known_styles():
    assert set(STYLE_BUILDERS) == set(KNOWN_STYLES)


def test_unknown_style():
    with pytest.raises(ValueError, match="未知干扰样式"):
        synthesize_style("laser", dict(P))


def test_deterministic_seed():
    a, _ = synthesize_style("noise_bandlimited", dict(P))
    b, _ = synthesize_style("noise_bandlimited", dict(P))
    assert np.array_equal(a, b)
