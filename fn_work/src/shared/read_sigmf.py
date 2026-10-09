# SigMF 文件对→(IQ, meta)，校验不过报原因（责任文档：shared/read_sigmf）
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def read_sigmf(base_path):
    # 读 <base>.sigmf-data/.sigmf-meta → (complex64 IQ, meta dict)
    base = Path(base_path)
    data_path = Path(str(base) + ".sigmf-data")
    meta_path = Path(str(base) + ".sigmf-meta")
    if not data_path.exists():
        raise FileNotFoundError("缺 %s" % data_path.name)
    if not meta_path.exists():
        raise FileNotFoundError("缺 %s" % meta_path.name)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("meta 非法 JSON: %s" % exc) from exc
    for key in ("global", "captures", "annotations"):
        if key not in meta:
            raise ValueError("meta 缺字段 %s" % key)
    if meta["global"].get("core:datatype") != "cf32_le":
        raise ValueError("不支持的 datatype: %s" % meta["global"].get("core:datatype"))
    iq = np.fromfile(data_path, dtype=np.complex64)
    return iq, meta
