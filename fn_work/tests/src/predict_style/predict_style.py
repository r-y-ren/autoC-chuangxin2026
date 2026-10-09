# predict_style 单测：手工模型分频半区→预测与真值并列
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.predict_style.predict_style import predict_style  # noqa: E402
from src.shared.write_sigmf import write_sigmf  # noqa: E402

SR = 1_000_000
NFFT, SEG, POOL = 128, 2048, 8


def _model(tmp_path):
    W = np.zeros((2, POOL))
    W[0, 4:] = 1.0    # up：正频在 fftshift 上半区
    W[1, :4] = 1.0    # down：负频在下半区
    b = np.zeros(2)
    m = {"W": W, "b": b, "classes": np.array(["up", "down"]),
         "nfft": NFFT, "seg_n": SEG, "pool": POOL}
    p = tmp_path / "model.npz"
    np.savez(p, **m)
    return p


def _rec(tmp_path, offset):
    t = np.arange(8192) / SR
    iq = np.exp(2j * np.pi * offset * t).astype(np.complex64)
    write_sigmf(tmp_path / ("rec_%d" % offset), iq,
                [{"style": "cw", "power_db": -5}])
    return tmp_path / ("rec_%d" % offset)


def test_predict_up_down_with_truth(tmp_path):
    m = _model(tmp_path)
    up = predict_style(str(m), str(_rec(tmp_path, 200_000)))
    down = predict_style(str(m), str(_rec(tmp_path, -200_000)))
    assert up and up[0]["predicted"] == "up" and up[0]["truth"] == "cw"
    assert down[0]["predicted"] == "down"
    assert 0 <= up[0]["probabilities"]["up"] <= 1
