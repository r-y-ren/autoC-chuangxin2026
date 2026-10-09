# train_classifier 端到端：合成可分数据集→分组 CV 高分→模型可被 predictor 消费
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.generate_jamming.synthesize_style import synthesize_style  # noqa: E402
from src.index_dataset.index_dataset import index_dataset  # noqa: E402
from src.predict_style.predict_style import predict_style  # noqa: E402
from src.shared.write_sigmf import write_sigmf  # noqa: E402
from src.train_classifier.train_classifier import train_classifier  # noqa: E402


def _build_dataset(root: Path):
    for grp in ("g1", "g2", "g3", "g4"):
        for k, style in enumerate(("cw", "partial_band")):
            params = {"freq_hz": 2422000000, "bandwidth_hz": 200_000,
                      "duration_s": 8192 / 1e6, "sample_rate_sps": 1e6,
                      "seed": 11 + k, "tone_offset_hz": 180_000,
                      "partial_band_frac": 0.2}
            iq, _ = synthesize_style(style, params)
            write_sigmf(root / grp / ("%s_%d" % (style, k)), iq,
                        [{"style": style, "power_db": -5.0}])
    return index_dataset(str(root))


def test_train_end_to_end(tmp_path):
    root = tmp_path / "runs"
    res_idx = _build_dataset(root)
    assert res_idx["recordings"] == 8 and not res_idx["errors"]
    res = train_classifier(str(root), str(tmp_path / "models"))
    assert res["backend"] == "local"          # TOOLBOX_URL 未配置→降级如实标注
    assert res["macro_f1"] >= 0.9             # 可分合成集（数字只记录；此为回归断言）
    assert Path(res["model_path"]).exists() and Path(res["confusion_png"]).exists()
    m = np.load(res["model_path"])
    assert set(m["classes"].tolist()) == {"cw", "partial_band"}
    # 模型可被 predictor 直接消费（跨模块契约）
    preds = predict_style(res["model_path"], str(root / "g1" / "cw_0"))
    assert preds and preds[0]["predicted"] == "cw" and preds[0]["truth"] == "cw"
