# R8 顶层：一键演示编排——短场景→小样本推理→报告（UI 演示按钮同底层）（责任文档：run_demo）
from __future__ import annotations

import os
from pathlib import Path

from src.execute_scenario.execute_scenario import execute_scenario
from src.generate_jamming.generate_jamming import generate_jamming
from src.index_dataset.index_dataset import index_dataset
from src.predict_style.predict_style import predict_style
from src.shared.load_scenario import InjectionSpec
from src.train_classifier.train_classifier import train_classifier

MINI = """meta: {name: demo_mini, version: 1}
dut: {links: [wifi, nrf24]}
injection:
  styles: [noise_bandlimited]
  freq_hz: 2422000000
  bandwidth_hz: 20000000
  params: {seed: 5}
  power_start_db: -5
  power_step_db: 5
  power_stop_db: 15
  step_duration_s: 0.3
criteria: {per_threshold: 0.5, sustain_s: 0.04, disconnect_s: 30}
safety: {max_tx_gain_db: 0}
record: {sigmf: false, ch2_monitor: false}
"""


def run_demo(*, quick: bool = True):
    # 返回 {report_path, fail_levels, predictions}；quick=合成数据全链路（无硬件可演示）
    if quick:
        os.environ.setdefault("LINKBENCH_SPEED", "40")
    demo_dir = Path("runs") / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    card = demo_dir / "mini.yaml"
    card.write_text(MINI, encoding="utf-8")

    res = execute_scenario(card)

    # 小样本识别支路：两组×两样式合成录制→索引→训练→预测并列真值（分组 CV 需 ≥2 组）
    preds = []
    first_base = None
    ok_all = True
    for grp, seed in (("g1", 9), ("g2", 13)):
        spec = InjectionSpec(styles=["cw", "partial_band"], freq_hz=2422000000,
                             bandwidth_hz=200_000,
                             params={"seed": seed, "tone_offset_hz": 180_000,
                                     "partial_band_frac": 0.2, "duration_s": 8192 / 1e6},
                             power_start_db=-5, power_step_db=5, power_stop_db=-5,
                             step_duration_s=8192 / 1e6)
        gen = generate_jamming(spec, dry_run=False, out_dir=demo_dir / "gen" / grp,
                               backend="mock")
        ok_all = ok_all and gen["ok"]
        if first_base is None and gen["sigmf_paths"]:
            first_base = gen["sigmf_paths"][0].with_suffix("")
    if ok_all and first_base is not None:
        idx = index_dataset(str(demo_dir / "gen"))
        if len(idx["groups"]) >= 2:
            tr = train_classifier(str(demo_dir / "gen"), str(demo_dir / "models"))
            preds = predict_style(tr["model_path"], str(first_base))
    return {"report_path": res["report_path"], "fail_levels": res["fail_levels"],
            "predictions": preds}
