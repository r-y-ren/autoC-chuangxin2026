# load_scenario 单测：四卡真实载入 + 四类非法卡拒载
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.load_scenario import load_scenario  # noqa: E402

SCEN = Path(__file__).resolve().parents[3] / "scenarios"


def test_four_fixture_cards_load():
    for name in ("smoke", "smoke_loop", "gb42590_noise", "nojam_control"):
        sc = load_scenario(SCEN / (name + ".yaml"))
        assert sc.meta["name"] == name
    assert load_scenario(SCEN / "nojam_control.yaml").injection is None
    inj = load_scenario(SCEN / "gb42590_noise.yaml").injection
    assert inj.power_start_db == -5 and inj.power_step_db == 5  # GB 42590 口径


def _bad(tmp_path, text):
    p = tmp_path / "bad.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_reject_unknown_style(tmp_path):
    p = _bad(tmp_path, "meta: {name: x}\ndut: {links: []}\ninjection: {styles: [laser], freq_hz: 2422000000, bandwidth_hz: 1000}\n")
    with pytest.raises(ValueError, match="未知样式"):
        load_scenario(p)


def test_reject_out_of_band(tmp_path):
    p = _bad(tmp_path, "meta: {name: x}\ndut: {links: []}\ninjection: {styles: [cw], freq_hz: 5800000000, bandwidth_hz: 1000}\n")
    with pytest.raises(ValueError, match="频段"):
        load_scenario(p)


def test_reject_positive_gain(tmp_path):
    p = _bad(tmp_path, "meta: {name: x}\ndut: {links: []}\ninjection: null\nsafety: {max_tx_gain_db: 3}\n")
    with pytest.raises(ValueError, match="硬顶"):
        load_scenario(p)


def test_reject_missing_meta(tmp_path):
    p = _bad(tmp_path, "dut: {links: []}\n")
    with pytest.raises(ValueError, match="meta.name"):
        load_scenario(p)
