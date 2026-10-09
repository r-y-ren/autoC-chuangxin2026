# create_instrument_backend 单测：工厂三分支
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.create_instrument_backend.create_instrument_backend import create_instrument_backend  # noqa: E402


def test_mock_factory_pair():
    jammer, analyzer = create_instrument_backend("mock")
    jammer.set_style("noise_bandlimited", {})
    jammer.set_power_db(-5)
    jammer.on(); jammer.off()
    assert callable(analyzer.get_spectrum)


def test_unknown_backend_rejected():
    with pytest.raises(ValueError, match="未知后端"):
        create_instrument_backend("hackrf")


def test_b210_missing_driver_hint():
    # 本机未装 UHD——必须给出可操作提示而非裸 ImportError
    with pytest.raises(RuntimeError, match="UHD"):
        create_instrument_backend("b210")
