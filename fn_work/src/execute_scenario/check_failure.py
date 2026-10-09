# KPI 窗口按判据判失效并给类型，纯函数（责任文档：check_failure ← R5）
from __future__ import annotations


def check_failure(kpi_window: list, criteria):
    # 失效类型："per_sustained" | "disconnect" | ""；窗口元素 {ts_ms, per, connected?}
    if not kpi_window:
        return False, ""
    win = sorted(kpi_window, key=lambda r: r["ts_ms"])

    def span(rows):
        return (rows[-1]["ts_ms"] - rows[0]["ts_ms"]) / 1000.0

    # 断连分支：连续失联时长 ≥ disconnect_s
    run = []
    for r in win:
        if r.get("connected", True) is False:
            run.append(r)
        else:
            if run and span(run) >= criteria.disconnect_s:
                return True, "disconnect"
            run = []
    if run and span(run) >= criteria.disconnect_s:
        return True, "disconnect"

    # PER 分支：连续 per≥阈值 且时间跨度 ≥ sustain_s
    run = []
    for r in win:
        if float(r["per"]) >= criteria.per_threshold:
            run.append(r)
        else:
            if run and span(run) >= criteria.sustain_s:
                return True, "per_sustained"
            run = []
    if run and span(run) >= criteria.sustain_s:
        return True, "per_sustained"
    return False, ""
