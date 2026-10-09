# 设备状态探测：异构探测→同构状态清单（责任文档演进轮二：probe_device_status）
from __future__ import annotations

import glob
import importlib.util
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout

STATUS_ENUM = ("ok", "missing", "pending_manual", "manual_ok")

_DEPS = {"pyyaml": "yaml", "numpy": "numpy", "matplotlib": "matplotlib",
         "pyserial": "serial", "sigmf": "sigmf", "fastapi": "fastapi",
         "uvicorn": "uvicorn", "websockets": "websockets", "requests": "requests"}

# (id, 名称, 探测函数名)——函数名延迟解析，便于单点故障注入测试
PROBES = (
    ("b210", "USRP B210", "_probe_b210"),
    ("esp32_serial", "ESP32 串口", "_probe_serial"),
    ("nrf24", "NRF24 数传链路", "_probe_nrf24"),
    ("deps", "Python 依赖", "_probe_deps"),
    ("toolbox", "4070 远程算力", "_probe_toolbox"),
    ("platformio", "PlatformIO 编译环境", "_probe_pio"),
)

# 物理件：机器不可测，人工确认占位（勾选状态由前端 localStorage 维护）
MANUAL = (
    ("shield_box", "金属屏蔽箱", "物理件，机器不可测——请人工确认已到位"),
    ("antenna_geometry", "天线几何固定", "物理件，机器不可测——请人工确认已标定固定"),
    ("power_hub", "供电 Hub", "物理件，机器不可测——请人工确认已接入"),
)


def _timed(fn, timeout_s: float):
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(fn).result(timeout=timeout_s)


def _probe_b210(timeout_s: float):
    try:
        import uhd  # noqa: F401 —— 惰性探测
    except Exception:  # noqa: BLE001
        return "missing", "UHD 未安装（pacman -S uhd 或 PothosSDR）"

    def scan():
        u = uhd.usrp.MultiUSRP("")
        return "ok", "检测到 %d 台 USRP" % u.get_num_mboards()

    try:
        return _timed(scan, timeout_s)
    except FuturesTimeout:
        return "missing", "B210 探测超时（%.1fs）" % timeout_s
    except Exception as exc:  # noqa: BLE001
        return "missing", "未检测到 B210：%s" % exc


def _probe_serial(timeout_s: float):
    ports = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
    if not ports:
        return "missing", "未检测到串口（插入 ESP32 后自动亮灯）"
    return "ok", "串口 %d 个：%s" % (len(ports), ", ".join(ports[:4]))


def _probe_nrf24(timeout_s: float):
    ports = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
    if not ports:
        return "missing", "无宿主串口（NRF24 需 ESP32 驱动）"
    for port in ports:
        try:
            import serial
            with serial.Serial(port, 115200, timeout=0.4) as s:
                line = s.readline().decode("utf-8", "ignore")
            if "nrf24" in line:
                return "ok", "nrf24_link 固件在线（%s）" % port
        except Exception:  # noqa: BLE001
            continue
    return "pending_manual", "串口在位，待 nrf24_link 固件上报确认"


def _probe_deps(timeout_s: float):
    missing = [pip for pip, mod in _DEPS.items()
               if importlib.util.find_spec(mod) is None]
    if missing:
        return "missing", "缺依赖：%s（pip install -r requirements.txt）" % ", ".join(missing)
    return "ok", "Python 依赖齐（%d 项）" % len(_DEPS)


def _probe_toolbox(timeout_s: float):
    url = os.environ.get("TOOLBOX_URL", "").strip()
    if not url:
        return "pending_manual", "未配置 TOOLBOX_URL（配置后自动探测；当前本地 CPU 降级可用）"
    try:
        import requests
        r = requests.get(url, timeout=timeout_s)
        if r.status_code < 500:
            return "ok", "远程算力连通（HTTP %d）" % r.status_code
        return "missing", "远程算力 HTTP %d" % r.status_code
    except Exception as exc:  # noqa: BLE001
        return "missing", "远程算力不可达：%s" % exc


def _probe_pio(timeout_s: float):
    path = shutil.which("pio") or shutil.which("platformio")
    if path:
        return "ok", "PlatformIO：%s" % path
    return "missing", "PlatformIO 未安装（固件编译需要）"


def probe_device_status(timeout_s: float = 2.0) -> list:
    # 一轮探测→统一状态清单；单项异常只降级该项，绝不抛全局错误
    ts = int(time.time())
    out = []
    for pid, name, fn_name in PROBES:
        fn = globals().get(fn_name)
        try:
            status, detail = fn(timeout_s) if callable(fn) else ("missing", "探测函数缺失")
        except FuturesTimeout:
            status, detail = "missing", "探测超时（%.1fs）" % timeout_s
        except Exception as exc:  # noqa: BLE001
            status, detail = "missing", "探测异常：%s" % exc
        out.append({"id": pid, "name": name, "status": status,
                    "detail": str(detail), "ts": ts})
    for pid, name, detail in MANUAL:
        out.append({"id": pid, "name": name, "status": "pending_manual",
                    "detail": detail, "ts": ts})
    return out
