# 监测 IQ→谱统计（峰值/占用/平坦度/总功率）（责任文档：compute_spectrum_stats ← R4）
from __future__ import annotations

import numpy as np


def compute_spectrum_stats(iq, sample_rate_sps: float) -> dict:
    # 输出：peak_offset_hz（相对中心）/occupied_pct/flatness_db/total_power_dbfs
    x = np.asarray(iq, dtype=np.complex64)
    if x.size == 0:
        raise ValueError("IQ 为空")
    spec = np.abs(np.fft.fftshift(np.fft.fft(x))) ** 2
    freqs = np.fft.fftshift(np.fft.fftfreq(x.size, d=1.0 / sample_rate_sps))
    peak_idx = int(np.argmax(spec))
    peak_offset = float(freqs[peak_idx])
    peak = float(spec[peak_idx])
    occupied = float(np.mean(spec >= peak * 10 ** (-20 / 10)))  # 峰下 20dB 计占用
    band = spec[spec > 0]
    flatness = float(10 * np.log10(band.max() / band.min())) if band.min() > 0 else float("inf")
    total_dbfs = float(10 * np.log10(float(spec.sum()) + 1e-30))
    return {"peak_offset_hz": peak_offset, "occupied_pct": occupied,
            "flatness_db": flatness, "total_power_dbfs": total_dbfs}
