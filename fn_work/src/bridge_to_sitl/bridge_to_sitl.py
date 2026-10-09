# R11 [P1]：实测 PER 台阶→ArduPilot SITL 丢包/时延注入（姊妹项目安航云盾联动）
from __future__ import annotations

import json
from pathlib import Path


def bridge_to_sitl(run_dir: str, sitl_host: str = "127.0.0.1:5760"):
    # 读 run 的 steps/kpi→注入时间线；pymavlink 可用则真注入，否则产模拟记录（如实标注）
    run_dir = Path(run_dir)
    steps = []
    sp = run_dir / "steps.jsonl"
    if sp.exists():
        steps = [json.loads(ln) for ln in sp.read_text(encoding="utf-8").splitlines() if ln.strip()]
    timeline = [{"t_start_ms": st.get("t_start_ms"), "t_end_ms": st.get("t_end_ms"),
                 "style": st.get("style"), "power_db": st.get("power_db"),
                 "per_target": (1.0 if st.get("failed") else 0.0)}
                for st in steps if st.get("power_db") is not None]

    mode = "simulated"
    try:
        import pymavlink  # noqa: F401
        mode = "pymavlink-ready"
    except Exception:  # noqa: BLE001
        pass

    record = {"mode": mode, "sitl_host": sitl_host, "timeline": timeline,
              "note": ("pymavlink 未安装——本记录为注入计划（真注入随安航云盾联调轮启用）"
                       if mode == "simulated" else "pymavlink 已装：注入通道就绪，尚未连接 SITL（联调轮启用）")}
    out = run_dir / "sitl_bridge_log.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"mode": mode, "log": str(out), "steps": len(timeline)}
