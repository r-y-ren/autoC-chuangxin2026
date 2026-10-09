# IQ+真值标注→SigMF v1.2.0 文件对（责任文档：shared/write_sigmf）
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def write_sigmf(base_path, iq, annotations, sample_rate_sps=None):
    # 写 <base>.sigmf-data/.sigmf-meta（cf32_le）；标注逐条须含 style/power_db 真值
    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    data = np.asarray(iq, dtype=np.complex64)
    if data.size == 0:
        raise ValueError("IQ 为空，拒绝写空录制")
    if not annotations or not isinstance(annotations, list):
        raise ValueError("annotations 必须是非空列表（真值标注缺失）")
    for i, a in enumerate(annotations):
        if "style" not in a or "power_db" not in a:
            raise ValueError("annotations[%d] 缺真值字段 style/power_db" % i)

    data_path = Path(str(base) + ".sigmf-data")
    data.tofile(data_path)

    anns = []
    for a in annotations:
        labels = {k: v for k, v in a.items()
                  if k not in ("core:sample_start", "core:sample_count")}
        anns.append({"core:sample_start": int(a.get("core:sample_start", 0)),
                     "core:sample_count": int(a.get("core:sample_count", data.size)),
                     "core:description": json.dumps(labels, ensure_ascii=False)})
    g = {"core:datatype": "cf32_le", "core:version": "1.2.0"}
    if sample_rate_sps:
        g["core:sample_rate"] = float(sample_rate_sps)
    meta = {"global": g, "captures": [{"core:sample_start": 0}], "annotations": anns}
    meta_path = Path(str(base) + ".sigmf-meta")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta_path
