# generate_jamming 单测：dry-run 不发射；mock 全路径落 SigMF 真值
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.generate_jamming.generate_jamming import generate_jamming  # noqa: E402
from src.create_instrument_backend.backends import MockJammer  # noqa: E402
from src.shared.load_scenario import InjectionSpec  # noqa: E402
from src.shared.read_sigmf import read_sigmf  # noqa: E402


def _spec():
    return InjectionSpec(styles=["cw", "noise_bandlimited"], freq_hz=2422000000,
                          bandwidth_hz=20e6, params={"seed": 1},
                          power_start_db=-20, power_step_db=5, power_stop_db=-15,
                          step_duration_s=0.05)


def test_dry_run_no_emission(tmp_path):
    res = generate_jamming(_spec(), dry_run=True, out_dir=tmp_path, backend="mock")
    assert res["ok"] and res["dry_run"]
    assert len(res["param_table"]) == 2 and not res["sigmf_paths"]


def test_mock_full_path_writes_sigmf(tmp_path):
    res = generate_jamming(_spec(), dry_run=False, out_dir=tmp_path, backend="mock")
    assert res["ok"], res["errors"]
    assert len(res["sigmf_paths"]) == 2
    for p in res["sigmf_paths"]:
        _iq, meta = read_sigmf(p.with_suffix(""))  # base
        assert meta["annotations"][0]["core:description"].find("power_db") >= 0
