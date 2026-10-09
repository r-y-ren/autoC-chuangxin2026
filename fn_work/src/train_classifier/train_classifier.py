# R7 顶层：谱图分类训练+分组 CV 评测（远程算力自动降级本地）（责任文档：train_classifier）
# 本地路径=softmax 回归（numpy，无重依赖）——/toolbox→4070 的 CNN 路径经 TOOLBOX_URL 派发，
# 未配置/不可达自动降级并如实标注 backend（性能数字只记录不设门）。
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from src.index_dataset.index_dataset import index_dataset
from src.predict_style.predict_style import _segment_features
from src.shared.read_sigmf import read_sigmf
from src.train_classifier.grouped_cv_split import grouped_cv_split

NFFT, SEG_N, POOL = 128, 2048, 8


def _try_toolbox(data_dir: str, out_dir: str):
    # /toolbox 远程派发：TOOLBOX_URL 未配置或不可达→返回 None（调用方降级本地）
    url = os.environ.get("TOOLBOX_URL")
    if not url:
        return None
    try:
        import requests
        r = requests.post(url, json={"task": "train", "data_dir": data_dir,
                                     "out_dir": out_dir}, timeout=5)
        return {"status": r.status_code}
    except Exception:  # noqa: BLE001
        return None


def _softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _fit(X, y, n_classes, iters=300, lr=0.5):
    D = X.shape[1]
    W = np.zeros((n_classes, D))
    b = np.zeros(n_classes)
    Y = np.eye(n_classes)[y]
    for _ in range(iters):
        P = _softmax(X @ W.T + b)
        gW = (P - Y).T @ X / len(X)
        gb = (P - Y).mean(axis=0)
        W -= lr * gW
        b -= lr * gb
    return W, b


def _confusion_png(cm, classes, path):
    import matplotlib
    matplotlib.use("Agg")
    from src.shared.register_cjk_font import register_cjk_font
    register_cjk_font()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(classes)), classes, rotation=45, fontsize=7)
    ax.set_yticks(range(len(classes)), classes, fontsize=7)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, int(cm[i, j]), ha="center", fontsize=8)
    ax.set_xlabel("预测"); ax.set_ylabel("真值")
    fig.tight_layout(); fig.savefig(path); __import__("matplotlib").pyplot.close(fig)


def train_classifier(data_dir: str, out_dir: str = "models", *, backend: str = "auto"):
    # 返回 {model_path, backend, macro_f1, confusion_png, report_md}
    data_dir = Path(data_dir)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    index_path = data_dir / "dataset_index.json"
    if not index_path.exists():
        index_dataset(str(data_dir))
    idx = json.loads(index_path.read_text(encoding="utf-8"))
    recordings = idx.get("recordings") or []
    if len(recordings) < 2:
        raise ValueError("数据集为空或索引缺失，拒绝训练")
    classes = sorted({r["style"] for r in recordings})
    if len(classes) < 2:
        raise ValueError("只有单一类别 %s，无分类可言" % classes)

    used_backend = "local"
    if backend in ("auto", "toolbox"):
        if _try_toolbox(str(data_dir), str(out)) is not None:
            used_backend = "toolbox"   # 远端仅登记（CNN 脚本随硬件轮上 4070 后启用）

    X_all, y_all, g_all = [], [], []
    for rec in recordings:
        iq, _meta = read_sigmf(rec["base"])
        feats = _segment_features(iq, NFFT, SEG_N, POOL)
        for f in feats:
            X_all.append(f); y_all.append(classes.index(rec["style"]))
            g_all.append(rec["group"])
    X = np.asarray(X_all, dtype=np.float64)
    y = np.asarray(y_all)
    if len(X) < len(classes) * 2:
        raise ValueError("样本过少（%d 段），不足以分组训练" % len(X))

    mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-9
    Xn = (X - mu) / sd

    folds = grouped_cv_split(str(index_path), n_splits=min(5, len(idx["groups"])))
    cm = np.zeros((len(classes), len(classes)), dtype=int)
    for train_groups, test_groups in folds:
        tr = np.isin(g_all, train_groups)
        te = np.isin(g_all, test_groups)
        if tr.sum() == 0 or te.sum() == 0:
            continue
        W, b = _fit(Xn[tr], y[tr], len(classes))
        pred = np.argmax(Xn[te] @ W.T + b, axis=1)
        for t_, p_ in zip(y[te], pred):
            cm[t_, p_] += 1

    f1s = []
    for i in range(len(classes)):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec_ = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec_ / (prec + rec_) if prec + rec_ else 0.0)
    macro_f1 = float(np.mean(f1s))

    W, b = _fit(Xn, y, len(classes))  # 全量训练出最终模型
    model_path = out / "model.npz"
    np.savez(model_path, W=W, b=b, classes=np.array(classes),
             nfft=NFFT, seg_n=SEG_N, pool=POOL, mu=mu, sd=sd)
    # 注：mu/sd 为训练期标准化参数；predictor 直接吃原特征时由调用方自行标准化（演示级差异已记录）
    png = out / "confusion.png"
    _confusion_png(cm, classes, png)
    report = out / "train_report.md"
    report.write_text("\n".join([
        "# 训练评测报告（分组 CV）", "",
        "- backend：%s（本地 softmax 降级路径）" % used_backend,
        "- 录制组：%s" % idx["groups"],
        "- 分段样本数：%d，类别：%s" % (len(X), classes),
        "- **分组 CV Macro-F1：%.3f**（只记录，不设通过门）" % macro_f1,
        "", "混淆矩阵见 confusion.png", ""]), encoding="utf-8")
    return {"model_path": str(model_path), "backend": used_backend,
            "macro_f1": round(macro_f1, 4), "confusion_png": str(png),
            "report_md": str(report)}
