# R7 推理：单条录制分段预测样式并与真值并列（责任文档：predict_style）
# 模型 npz 契约键：W, b, classes, nfft, seg_n, pool（与 train_classifier 写出格式一致）
from __future__ import annotations

import json

import numpy as np

from src.shared.make_spectrogram import make_spectrogram
from src.shared.read_sigmf import read_sigmf


def _segment_features(iq, nfft, seg_n, pool):
    feats = []
    for k in range(0, max(1, iq.size // seg_n)):
        seg = iq[k * seg_n:(k + 1) * seg_n]
        if seg.size < seg_n:
            break
        spec = make_spectrogram(seg, nfft=nfft)          # (freq, time)
        prof = spec.mean(axis=1)                          # 频率轮廓
        n = prof.size // pool
        feats.append(prof[: n * pool].reshape(pool, n).mean(axis=1))
    return np.asarray(feats, dtype=np.float64)


def predict_style(model_path: str, sigmf_base: str) -> list:
    # 返回 [{segment, predicted, truth, probabilities}]；truth 取自标注（无则 None）
    m = np.load(model_path, allow_pickle=False)
    W, b = m["W"], m["b"]
    classes = [str(c) for c in m["classes"].tolist()]
    nfft, seg_n, pool = int(m["nfft"]), int(m["seg_n"]), int(m["pool"])

    iq, meta = read_sigmf(sigmf_base)
    truth = None
    anns = meta.get("annotations") or []
    if anns:
        try:
            truth = json.loads(anns[0].get("core:description", "{}")).get("style")
        except Exception:  # noqa: BLE001
            truth = None

    feats = _segment_features(iq, nfft, seg_n, pool)
    out = []
    for i, x in enumerate(feats):
        logits = W @ x + b
        p = np.exp(logits - logits.max())
        p = p / p.sum()
        out.append({"segment": i, "predicted": classes[int(np.argmax(p))],
                    "truth": truth,
                    "probabilities": {c: float(p[j]) for j, c in enumerate(classes)}})
    return out
