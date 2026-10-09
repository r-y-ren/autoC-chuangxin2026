# 纯函数：标定表查表/内插换算后端增益；缺表=恒等；表损坏降级并告警（R15）
from __future__ import annotations

import json
from pathlib import Path


def apply_calibration(power_db: float, freq_hz: int, calibration_path=None):
    # 返回 (后端增益 dB, 来源 "calibrated"|"identity", 告警 str|None)
    p = Path(calibration_path) if calibration_path else Path("runs") / "calibration.json"
    if not p.exists():
        return power_db, "identity", None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = [e for e in data.get("entries", [])
                   if int(e.get("freq_hz", freq_hz)) == freq_hz] or \
                  [e for e in data.get("entries", [])]
        pts = sorted((float(e["power_db"]), float(e["gain_db"])) for e in entries)
        if not pts:
            return power_db, "identity", "标定表为空，按恒等映射"
        lo, hi = pts[0], pts[-1]
        x = float(power_db)
        if x <= lo[0]:
            gain = lo[1]
        elif x >= hi[0]:
            gain = hi[1]
        else:
            for a, b in zip(pts, pts[1:]):
                if a[0] <= x <= b[0]:
                    t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
                    gain = a[1] + t * (b[1] - a[1])
                    break
        return round(gain, 3), "calibrated", None
    except Exception as exc:  # noqa: BLE001
        return power_db, "identity", "标定表损坏（%s），按恒等映射" % exc
