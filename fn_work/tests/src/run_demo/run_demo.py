# run_demo 单测：quick 合成路径一条命令（报告+失效电平+识别样例）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.run_demo.run_demo import run_demo  # noqa: E402


def test_demo_quick(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKBENCH_SPEED", "60")
    res = run_demo(quick=True)
    assert Path(res["report_path"]).exists()
    assert res["fail_levels"].get("noise_bandlimited") is not None
    assert res["predictions"] and res["predictions"][0]["truth"] in ("cw", "partial_band")
