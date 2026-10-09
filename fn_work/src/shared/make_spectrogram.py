# 复基带 IQ→幅度谱图（训练/推理共用唯一口径）（责任文档：shared/make_spectrogram）
from __future__ import annotations

import numpy as np


def make_spectrogram(iq, nfft: int = 256, hop: int | None = None):
    # complex IQ → float32 谱图 (freq=nfft, time=帧数)；fftshift 后频率轴关于 0 对称
    x = np.asarray(iq).astype(np.complex64)
    if x.size == 0:
        raise ValueError("IQ 为空")
    hop = int(hop or max(1, nfft // 2))
    if x.size < nfft:
        x = np.concatenate([x, np.zeros(nfft - x.size, dtype=np.complex64)])
    frames = np.lib.stride_tricks.sliding_window_view(x, nfft)[::hop]
    spec = np.abs(np.fft.fftshift(np.fft.fft(frames, nfft, axis=1), axes=1)).T
    return spec.astype(np.float32)
