# 接口契约：software ↔ hardware（chuangxin2026）

> 蓝图 interface_contracts 指向本文件；并发分发前钉死，变更须 JOURNAL 留痕。固件细节见 `../fn_docs/requirements.md` R3。

## 1. 部件与目录

| 部件 | 目录 | 说明 |
|---|---|---|
| ESP32 WiFi 被测链路固件 | `workspace/chuangxin2026/hardware/firmware/esp32_link/` | PlatformIO 工程，Arduino 框架 |
| NRF24 被测链路固件 | `workspace/chuangxin2026/hardware/firmware/nrf24_link/` | PlatformIO 工程（宿主板按实际定，RF24 库） |
| B210 射频链 | 无固件 | 由 software 侧 GNU Radio/UHD 直接驱动；30dB 衰减器=物理粗档，scenario 中显式标注 |

## 2. 串口数据协议（DUT → 上位机）

- 物理：USB 串口，115200 8N1；每链路 1Hz JSON 行（`\n` 结尾）。
- 字段：`{"link":"wifi|nrf24","seq":<单调递增>,"ts_ms":<固件毫秒时钟>,"per":<0-1>,"tx_n":<包数>,"err_n":<错包数>,"rssi_dbm":<仅 wifi>,"arc_avg":<仅 nrf24>,"plos_cnt":<仅 nrf24>,"fw":"<版本>"}`
- 异常语义：串口断连=KPI gap 事件（记录不中断注入）；`seq` 回退/跳变必须上报为事件。
- 安全：上位机任何异常退出路径必须先向 B210 发停止发射再退出（软件侧责任，固件无 TX）。

## 3. 构建与烧录

- 统一入口：`python3 -m platformio run -d workspace/chuangxin2026/hardware/firmware`（蓝图 hw-fw 验收项）。
- 固件版本号进每帧 `fw` 字段；runs/ 目录随 scenario 副本记录当日固件版本。

## 4. 变更流程

改协议字段/速率 → 修改本文件 → JOURNAL 记一行 → software/hardware 两侧回归（sw-test + hw-fw）。
