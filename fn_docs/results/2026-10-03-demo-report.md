# demo 产出 report.md 拷贝

- 拷贝时间：2026-10-03
- 源文件：`fn_work/runs/demo_mini-1791026388950/report.md`（demo.py 本日运行产物，RC=0）
- 源文件共 25 行，未超过 200 行，无截断。

---

# 测评报告

- 场景：demo_mini

## 三元曲线

![per_vs_jsr](figs/per_vs_jsr.png)

![throughput_latency](figs/throughput_latency.png)

![fail_timeline](figs/fail_timeline.png)

## 失效电平表（GB 42590 §5.11）

| 样式 | 失效电平 dB | 失效类型 |
|---|---|---|
| noise_bandlimited | 5.0 | per_sustained |

## 样本量

- KPI 样本数：480

## 仪器局限与口径

声明：本平台非 CISPR 16-1-1 意义上的 EMI 测量接收机；测试采用 GB 42590-2023 §5.11 方法学预研 + EN 300 328 传导等效口径；一切数字仅出自本 run 实测产物。
