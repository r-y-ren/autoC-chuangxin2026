# parse_serial_line 单测：三分支（合法/缺字段/seq 回退）
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.collect_dut_samples.parse_serial_line import parse_serial_line, reset_seq_tracking  # noqa: E402

OK = b'{"link":"wifi","seq":1,"ts_ms":100,"per":0.02,"tx_n":100,"err_n":2,"rssi_dbm":-61.5,"fw":"t"}'


def test_parse_ok():
    reset_seq_tracking()
    s = parse_serial_line(OK)
    assert s.link == "wifi" and s.per == 0.02 and s.rssi_dbm == -61.5 and s.err_n == 2


def test_missing_field():
    reset_seq_tracking()
    with pytest.raises(ValueError, match="缺字段"):
        parse_serial_line(b'{"link":"wifi","seq":1,"per":0.0}')


def test_seq_regress():
    reset_seq_tracking()
    parse_serial_line(OK)
    bad = OK.replace(b'"seq":1', b'"seq":0')
    with pytest.raises(ValueError, match="seq 回退"):
        parse_serial_line(bad)


def test_nrf24_fields():
    reset_seq_tracking()
    s = parse_serial_line(b'{"link":"nrf24","seq":1,"ts_ms":1,"per":0.1,"tx_n":50,"err_n":5,"arc_avg":2.5,"plos_cnt":5}')
    assert s.rssi_dbm is None and s.arc_avg == 2.5 and s.plos_cnt == 5
