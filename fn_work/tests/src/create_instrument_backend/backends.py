# backends 单测：mock 行为/接口完备
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.create_instrument_backend.backends import MockJammer, MockAnalyzer  # noqa: E402


def test_mock_jammer_records_and_toggles():
    j = MockJammer()
    j.set_style("cw", {})
    j.set_power_db(-5)
    j.on()
    assert j.emitting and j.power_db == -5 and j.style == "cw"
    j.off()
    assert not j.emitting
    assert j.calls[0][0] == "set_style" and j.calls[-1] == ("off",)


def test_mock_analyzer_reflects_jammer():
    j = MockJammer()
    a = MockAnalyzer(j)
    assert not a.get_spectrum(2422000000, 20e6)["occupied"]
    j.set_power_db(3); j.on()
    spec = a.get_spectrum(2422000000, 20e6)
    assert spec["occupied"] and spec["power_dbfs"] == 3
