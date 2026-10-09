# execute_scenario 端到端：合成链路双卡（国标失效电平 + 对照不误报）
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.execute_scenario import execute_scenario  # noqa: E402

GB = """meta: {name: mini_gb, version: 1}
dut: {links: [wifi]}
injection:
  styles: [noise_bandlimited]
  freq_hz: 2422000000
  bandwidth_hz: 20000000
  params: {seed: 3}
  power_start_db: -5
  power_step_db: 5
  power_stop_db: 15
  step_duration_s: 0.3
criteria: {per_threshold: 0.5, sustain_s: 0.04, disconnect_s: 30}
safety: {max_tx_gain_db: 0}
record: {sigmf: true, ch2_monitor: true}
"""
CTRL = """meta: {name: mini_ctrl, version: 1}
dut: {links: [wifi]}
injection: null
criteria: {per_threshold: 0.5, sustain_s: 0.04, disconnect_s: 30}
safety: {max_tx_gain_db: 0}
record: {sigmf: false, ch2_monitor: false}
"""


@pytest.fixture(autouse=True)
def _fast(monkeypatch, tmp_path):
    monkeypatch.setenv("LINKBENCH_SPEED", "30")
    monkeypatch.chdir(tmp_path)  # runs/ 落临时目录


def test_gb_card_finds_fail_level(tmp_path):
    p = tmp_path / "mini.yaml"; p.write_text(GB, encoding="utf-8")
    res = execute_scenario(p)
    fl = res["fail_levels"]
    assert "noise_bandlimited" in fl and fl["noise_bandlimited"] <= 15
    assert res["nojam_false_alarm"] is False
    assert (res["run_dir"] / "report.md").exists()
    steps = [json.loads(ln) for ln in
             (res["run_dir"] / "steps.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(s["failed"] for s in steps)


def test_control_card_no_false_alarm(tmp_path):
    p = tmp_path / "ctrl.yaml"; p.write_text(CTRL, encoding="utf-8")
    res = execute_scenario(p)
    assert res["nojam_false_alarm"] is False
    assert res["fail_levels"] == {}


# ---- 演进轮一集成（R14 加速判据 / R15 断点+标定） ----
FWROOT = Path(__file__).resolve().parents[3]


def test_r14_fast_speed_still_finds_fail_level(tmp_path, monkeypatch):
    # 40 倍速跑标准国标卡：判据同步缩放后必须仍能报出失效电平+报告脚注
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKBENCH_SPEED", "40")
    from src.execute_scenario.execute_scenario import execute_scenario
    res = execute_scenario(FWROOT / "scenarios" / "gb42590_noise.yaml")
    assert res["fail_levels"], "40 倍速下失效电平为空=假阴性"
    text = res["report_path"].read_text(encoding="utf-8")
    assert "加速倍率 40" in text and "同步缩放" in text


def test_r15_resume_half_run(tmp_path, monkeypatch):
    # 全量跑 mini 卡→截断 steps 至 1 行→以 run 目录重入=断点续跑补齐
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKBENCH_SPEED", "60")
    from src.execute_scenario.execute_scenario import execute_scenario
    card = tmp_path / "mini.yaml"
    card.write_text(GB, encoding="utf-8")
    res1 = execute_scenario(card)
    steps_p = res1["run_dir"] / "steps.jsonl"
    lines = [ln for ln in steps_p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    steps_p.write_text(lines[0] + "\n", encoding="utf-8")
    res2 = execute_scenario(res1["run_dir"])
    assert res2["resumed"] is True
    new_lines = [ln for ln in steps_p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) >= 3                        # 全量跑=失效即停前的 3 步
    assert len(new_lines) == len(lines)           # 续跑补齐到同样终点
    assert new_lines[0] == lines[0]               # 已完成首步原样保留
    assert (res1["run_dir"] / "report.md").exists()


def test_r15_calibration_applied_line(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKBENCH_SPEED", "60")
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "calibration.json").write_text(json.dumps({"entries": [
        {"freq_hz": 2422000000, "gain_db": p + 10, "power_db": p}
        for p in range(-5, 16, 5)]}), encoding="utf-8")
    from src.execute_scenario.execute_scenario import execute_scenario
    card = tmp_path / "mini.yaml"
    card.write_text(GB, encoding="utf-8")
    res = execute_scenario(card)
    text = res["report_path"].read_text(encoding="utf-8")
    assert "标定表已应用" in text
