# R5 顶层：国标步进执行器——装载→步进→判失效→失效电平→产物与报告（责任文档：execute_scenario）
from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

from src.build_report.build_report import build_report
from src.collect_dut_samples.collect_dut_samples import collect_dut_samples
from src.create_instrument_backend.create_instrument_backend import create_instrument_backend
from src.execute_scenario.apply_calibration import apply_calibration
from src.execute_scenario.check_failure import check_failure
from src.execute_scenario.resume_from import resume_from
from src.execute_scenario.scaled_criteria import scaled_criteria
from src.execute_scenario.plan_steps import plan_steps
from src.shared.estop import EstopManager
from src.shared.load_scenario import load_scenario


def _host_ms() -> int:
    return int(time.monotonic() * 1000)


def execute_scenario(scenario_path, *, estop=None, feed=None):
    # 返回 {run_dir, outcomes, fail_levels, nojam_false_alarm, report_path}
    # [改造←R14/R15] 支持传 run 目录=断点续跑；判据同步缩放；标定换算
    sp = Path(scenario_path)
    resuming = sp.is_dir()
    card = (sp / "scenario_card.yaml") if resuming else sp
    if resuming and not card.exists():
        raise ValueError("断点续跑目录缺 scenario_card.yaml: %s" % sp)
    sc = load_scenario(card)
    speed = max(0.1, float(os.environ.get("LINKBENCH_SPEED", "1.0")))
    crit_eff, speed_info = scaled_criteria(sc.criteria, speed)
    backend = os.environ.get("LINKBENCH_BACKEND", "mock")
    run_dir = sp if resuming else Path("runs") / ("%s-%d" % (sc.name, int(time.time() * 1000)))
    run_dir.mkdir(parents=True, exist_ok=True)
    if not resuming:
        (run_dir / "scenario_card.yaml").write_text(
            Path(scenario_path).read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "speed.json").write_text(
        json.dumps(speed_info, ensure_ascii=False), encoding="utf-8")

    jammer, analyzer = create_instrument_backend(backend)
    if estop is None:
        estop = EstopManager()
    estop.arm(jammer.off)

    links = [{"type": "fake", "link": n,
              "rate_hz": max(10.0, 40.0 * speed),
              "jammer": jammer} for n in (sc.dut_links or ["wifi"])]

    _t_boot = _host_ms()
    plan_all = plan_steps(sc.injection)
    start_index, done_records, already_finished = (resume_from(run_dir, plan_all)
                                                   if resuming else (0, [], False))
    pre_events = []
    if resuming and start_index == 0 and (run_dir / "steps.jsonl").exists():
        _rr = {"type": "resume_reset", "msg": "进度损坏或无可匹配步，从 0 重跑",
               "ts_ms": _host_ms()}
        pre_events.append(_rr)
        emit(_rr)
    cal_path = Path("runs") / "calibration.json"
    cal_state = {"source": None}
    kpi_rows, events, step_records = [], list(pre_events), list(done_records)

    def emit(msg: dict) -> None:
        if feed is not None:
            try:
                feed.publish(msg)
            except Exception:  # noqa: BLE001 —— 发流不阻断执行
                pass

    def add_event(e: dict) -> None:
        events.append(e)
        emit(e)

    def on_sample(s):
        row = {"ts_ms": _host_ms(), "link": s.link, "seq": s.seq,
               "per": s.per, "tx_n": s.tx_n, "err_n": s.err_n,
               "rssi_dbm": s.rssi_dbm, "arc_avg": s.arc_avg,
               "plos_cnt": s.plos_cnt}
        kpi_rows.append(row)
        emit({"type": "kpi", **row})

    try:
        if sc.injection is None:
            dur = max(0.2, 1.0 / speed)
            _samples, gaps = collect_dut_samples(links, dur, on_sample=on_sample)
            [add_event(g) for g in gaps]
            window = kpi_rows
            failed, kind = check_failure(window, crit_eff)
            nojam_false_alarm = bool(failed)
            step_records.append({"style": "nojam", "power_db": None,
                                 "t_start_ms": 0, "t_end_ms": _host_ms(),
                                 "failed": failed, "failure_kind": kind})
        else:
            nojam_false_alarm = False
            if already_finished:
                jammer.off()
                return {"run_dir": run_dir, "outcomes": step_records,
                        "fail_levels": _fail_levels(step_records),
                        "nojam_false_alarm": False,
                        "report_path": build_report(run_dir),
                        "resumed_finished": True}
            for st in plan_all[start_index:]:
                t0 = _host_ms()
                emit({"type": "progress",
                      "index": st.index + 1, "total": len(plan_all),
                      "style": st.style, "power_db": st.power_db,
                      "elapsed_s": round((t0 - _t_boot) / 1000.0, 2)})
                jammer.set_style(st.style, dict(sc.injection.params or {}))
                gain, src, warn = apply_calibration(st.power_db, sc.injection.freq_hz,
                                                    cal_path)
                if cal_state["source"] is None:
                    cal_state["source"] = src
                    (run_dir / "calibration_state.json").write_text(
                        json.dumps(cal_state), encoding="utf-8")
                if warn:
                    events.append({"type": "calibration_warn", "msg": warn,
                                   "ts_ms": _host_ms()})
                jammer.set_power_db(gain)
                jammer.on()
                add_event({"type": "injection", "style": st.style,
                           "power_db": st.power_db, "ts_ms": t0})
                eff = max(0.05, st.duration_s / speed)
                _s, gaps = collect_dut_samples(links, eff, on_sample=on_sample)
                [add_event(g) for g in gaps]
                jammer.off()
                add_event({"type": "injection_off", "style": st.style,
                           "power_db": st.power_db, "ts_ms": _host_ms()})
                t1 = _host_ms()
                window = [r for r in kpi_rows if t0 <= r["ts_ms"] <= t1]
                failed, kind = check_failure(window, crit_eff)
                rec = {"style": st.style, "power_db": st.power_db,
                       "t_start_ms": t0, "t_end_ms": t1,
                       "failed": failed, "failure_kind": kind}
                step_records.append(rec)
                if failed:
                    add_event({"type": "fail", "style": st.style,
                               "power_db": st.power_db, "kind": kind,
                               "ts_ms": t1})
                    break  # 该样式已失效，进下一样式
    except Exception:  # noqa: BLE001 —— 任何异常先急停再抛
        estop.fire("execute_scenario 异常")
        raise

    (run_dir / "scenario.yaml").write_text(
        json.dumps({"name": sc.name}, ensure_ascii=False), encoding="utf-8")
    with (run_dir / "kpi.csv").open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not resuming:
            w.writerow(["ts_ms", "link", "seq", "per", "tx_n", "err_n",
                        "rssi_dbm", "arc_avg", "plos_cnt"])
        for r in kpi_rows:
            w.writerow([r["ts_ms"], r["link"], r["seq"], r["per"], r["tx_n"],
                        r["err_n"], r["rssi_dbm"], r["arc_avg"], r["plos_cnt"]])
    old_events = []
    ev_path = run_dir / "events.jsonl"
    if resuming and ev_path.exists():
        old_events = [ln for ln in ev_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    with ev_path.open("w", encoding="utf-8") as f:
        for e in old_events:
            f.write(e + "\n")
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with (run_dir / "steps.jsonl").open("w", encoding="utf-8") as f:
        for st in step_records:
            f.write(json.dumps(st, ensure_ascii=False) + "\n")

    def _fail_levels(recs):
        fl = {}
        for st in recs:
            if st.get("failed") and st.get("power_db") is not None:
                fl.setdefault(st["style"], st["power_db"])
        return fl

    report = build_report(run_dir)
    return {"run_dir": run_dir, "outcomes": step_records,
            "fail_levels": _fail_levels(step_records),
            "nojam_false_alarm": nojam_false_alarm,
            "report_path": report, "resumed": bool(resuming)}
