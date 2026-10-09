# 起操控台服务+健康就绪后开浏览器；selfcheck 只验证服务/健康/URL（R13）
from __future__ import annotations

import threading
import time


def launch_console(*, host: str = "0.0.0.0", port: int = 8000,
                   selftest: bool = False, no_browser: bool = False) -> int:
    # 返回退出码：0=拉起成功（selftest）或服务正常退出；1=起不来（附可操作提示）
    import httpx
    import uvicorn

    from src.serve_console.serve_console import create_app
    app = create_app()
    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    url = "http://127.0.0.1:%d/" % port
    ok, deadline = False, time.time() + 10
    while time.time() < deadline and not server.should_exit:
        try:
            if httpx.get(url + "api/health", timeout=1).status_code == 200:
                ok = True
                break
        except Exception:  # noqa: BLE001
            time.sleep(0.2)
    if not ok:
        print("启动失败：服务 10s 内未就绪。排查：端口占用（lsof -i:%d）或依赖"
              "（fn_work/.venv/bin/pip install -r requirements.txt）" % port)
        server.should_exit = True
        return 1
    print("CONSOLE READY:", url)
    if selftest:
        try:
            devs = httpx.get(url + "api/devices", timeout=5.0).json().get("devices", [])
        except Exception as exc:  # noqa: BLE001
            print("SELFTEST FAIL: /api_devices 不可达：%s" % exc)
            server.should_exit = True
            return 1
        if len(devs) < 6 or not any(e.get("id") == "b210" for e in devs):
            print("SELFTEST FAIL: /api_devices 条目不足（%d）" % len(devs))
            server.should_exit = True
            return 1
        b210_st = [e["status"] for e in devs if e["id"] == "b210"][0]
        print("DEVICES OK: %d 项（B210=%s）" % (len(devs), b210_st))
        server.should_exit = True
        return 0
    if not no_browser:
        import webbrowser
        webbrowser.open(url)
    try:
        while not server.should_exit:
            time.sleep(0.5)
    except KeyboardInterrupt:
        server.should_exit = True
    return 0
