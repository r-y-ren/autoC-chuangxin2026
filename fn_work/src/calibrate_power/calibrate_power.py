# R2 顶层：频点×增益档→注入功率标定表+单调性检查（责任文档：calibrate_power）
from __future__ import annotations

import json
from pathlib import Path

from src.create_instrument_backend.create_instrument_backend import create_instrument_backend


def calibrate_power(freq_hz_list: list, gain_list: list, runs_dir: str = "runs",
                    *, backend: str = "mock"):
    # mock 后端=恒等映射（增益即功率）；真机路径在硬件轮接 UHD 实测
    # 返回 {calibration_path, monotonic_ok, max_deviation_db, entries}
    jammer, _ = create_instrument_backend(backend)
    entries = []
    for freq in freq_hz_list:
        for g in sorted(gain_list):
            jammer.set_power_db(g)
            entries.append({"freq_hz": freq, "gain_db": g, "power_db": g})
    powers = [e["power_db"] for e in entries]
    devs = [abs(powers[i] - powers[i - 1]) for i in range(1, len(powers))] or [0.0]
    monotonic = all(powers[i] > powers[i - 1] for i in range(1, len(powers)))
    import statistics
    med = statistics.median(devs) if devs else 0.0
    warnings = ["档%d 步距偏差 %.2fdB>1dB" % (i + 1, d)
                for i, d in enumerate(devs) if abs(d - med) > 1.0]
    out = Path(runs_dir); out.mkdir(parents=True, exist_ok=True)
    path = out / "calibration.json"
    path.write_text(json.dumps({"entries": entries,
                                "monotonic_ok": monotonic,
                                "max_deviation_db": max(devs),
                                "warnings": warnings}, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    return {"calibration_path": str(path), "monotonic_ok": monotonic,
            "max_deviation_db": max(devs), "entries": len(entries),
            "warnings": warnings}
