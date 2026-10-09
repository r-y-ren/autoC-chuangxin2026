# 串口 JSON 行→DutSample（契约：contracts/sw-hw-interface.md §2）
from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class DutSample:
    link: str
    seq: int
    ts_ms: int
    per: float
    tx_n: int
    err_n: int
    rssi_dbm: float | None = None   # 仅 wifi
    arc_avg: float | None = None    # 仅 nrf24
    plos_cnt: int | None = None     # 仅 nrf24
    fw: str = ""


def parse_serial_line(raw: bytes) -> DutSample:
    # 字段缺失/seq 回退跳变→ValueError（含字段名），上层转 gap 事件
    try:
        d = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ValueError("非法 JSON 行: %s" % exc) from exc
    if not isinstance(d, dict):
        raise ValueError("行必须是 JSON 对象")
    parse_serial_line._last_seq = getattr(parse_serial_line, "_last_seq", {})
    link = d.get("link")
    if not link:
        raise ValueError("缺字段 link")
    for f in ("seq", "ts_ms", "per", "tx_n", "err_n"):
        if f not in d:
            raise ValueError("缺字段 %s" % f)
    seq = int(d["seq"])
    prev = parse_serial_line._last_seq.get(link)
    if prev is not None and seq < prev:
        raise ValueError("seq 回退: %s %d<%d" % (link, seq, prev))
    parse_serial_line._last_seq[link] = seq
    return DutSample(link=str(link), seq=seq, ts_ms=int(d["ts_ms"]),
                     per=float(d["per"]), tx_n=int(d["tx_n"]), err_n=int(d["err_n"]),
                     rssi_dbm=(float(d["rssi_dbm"]) if d.get("rssi_dbm") is not None else None),
                     arc_avg=(float(d["arc_avg"]) if d.get("arc_avg") is not None else None),
                     plos_cnt=(int(d["plos_cnt"]) if d.get("plos_cnt") is not None else None),
                     fw=str(d.get("fw", "")))


def reset_seq_tracking() -> None:
    # 每次采集会话开始时清空链内 seq 记忆
    parse_serial_line._last_seq = {}
