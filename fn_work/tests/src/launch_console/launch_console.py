# launch_console 单测：selfcheck 拉起服务+健康检查过（无浏览器）
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.launch_console.launch_console import launch_console  # noqa: E402


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def test_selfcheck_rc0(capsys):
    rc = launch_console(selftest=True, port=_free_port())
    out = capsys.readouterr().out
    assert rc == 0 and "CONSOLE READY" in out and "http://" in out
