# 样式插槽：样式名→注册表分发→复基带 IQ（责任文档：synthesize_style ← R1）
# 分类学锚点：IEEE COMST 2022 综述（六类危害形态，docs 补充 §4.2）
from __future__ import annotations

import numpy as np

STYLE_BUILDERS: dict = {}  # 样式插槽注册表：新样式=注册新构建器


def _t(params, sample_rate_sps):
    dur = float(params.get("duration_s", 0.1))
    n = max(8, int(dur * sample_rate_sps))
    return np.arange(n) / sample_rate_sps


def _build_cw(params, sr):
    t = _t(params, sr)
    off = float(params.get("tone_offset_hz", 0.0))
    iq = np.exp(2j * np.pi * off * t)
    return iq, {"tone_offset_hz": off}


def _build_sweep(params, sr):
    t = _t(params, sr)
    bw = float(params.get("bandwidth_hz", 1e6))
    rate = float(params.get("sweep_rate_hz_per_s", bw / max(t[-1], 1e-6) / 4))
    f = bw / 2 * np.sin(2 * np.pi * rate / bw * t)  # 来回扫频
    iq = np.exp(2j * np.pi * np.cumsum(f) / sr)
    return iq, {"sweep_rate_hz_per_s": rate}


def _build_chirp(params, sr):
    t = _t(params, sr)
    bw = float(params.get("bandwidth_hz", 1e6))
    period = float(params.get("chirp_period_s", 0.001))
    f = bw * (np.mod(t, period) / period - 0.5)  # 锯齿线性调频
    iq = np.exp(2j * np.pi * np.cumsum(f) / sr)
    return iq, {"chirp_period_s": period}


def _build_noise_bandlimited(params, sr):
    t = _t(params, sr)
    bw = min(float(params.get("bandwidth_hz", sr / 2)), sr / 2 * 0.99)
    rng = np.random.default_rng(int(params.get("seed", 0)))
    x = rng.standard_normal(t.size) + 1j * rng.standard_normal(t.size)
    X = np.fft.fft(x)
    mask = np.zeros(t.size)
    keep = max(1, int(t.size * bw / sr))
    mask[: keep // 2] = 1
    mask[-(keep // 2):] = 1
    iq = np.fft.ifft(X * mask)
    return iq.astype(np.complex64), {"noise_bandwidth_hz": bw}


def _build_partial_band(params, sr):
    iq, meta = _build_noise_bandlimited(params, sr)
    frac = float(params.get("partial_band_frac", 0.25))
    n = iq.size
    keep = max(1, int(n * frac))
    X = np.fft.fft(iq)
    Y = np.zeros(n, dtype=complex)
    Y[: keep] = X[: keep]  # 只占一段（低段）
    return np.fft.ifft(Y).astype(np.complex64), {"partial_band_frac": frac}


def _build_pulse(params, sr):
    base, meta = _build_cw(params, sr)
    period = float(params.get("pulse_period_s", 0.01))
    duty = float(params.get("duty", 0.3))
    t = np.arange(base.size) / sr
    gate = (np.mod(t, period) / period) < duty
    return (base * gate).astype(np.complex64), {"duty": duty, "pulse_period_s": period}


for _name, _fn in (("cw", _build_cw), ("sweep", _build_sweep), ("chirp", _build_chirp),
                   ("noise_bandlimited", _build_noise_bandlimited),
                   ("partial_band", _build_partial_band), ("pulse", _build_pulse)):
    STYLE_BUILDERS[_name] = _fn


def synthesize_style(style: str, params: dict):
    # 返回 (复基带 IQ complex64, 样式元数据 dict)；未知样式明确报错
    if style not in STYLE_BUILDERS:
        raise ValueError("未知干扰样式 %r，已注册: %s" % (style, sorted(STYLE_BUILDERS)))
    sr = float(params.get("sample_rate_sps", 1e6))
    iq, extra = STYLE_BUILDERS[style](params, sr)
    meta = {"style": style, "sample_rate_sps": sr,
            "duration_s": float(params.get("duration_s", 0.1)),
            "freq_hz": params.get("freq_hz"), "bandwidth_hz": params.get("bandwidth_hz")}
    meta.update(extra)
    return np.asarray(iq, dtype=np.complex64), meta
