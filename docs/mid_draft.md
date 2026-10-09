# STITP 中期材料稿（自动汇编）

- 运行：demo_mini-1791264217344
- KPI 样本数：480
- 步进记录：3 步（失效 1 步）

## 失效电平（GB 42590 §5.11 口径）

| 样式 | 失效电平 dB | 类型 |
|---|---|---|
| noise_bandlimited | 5.0 | per_sustained |

## 三元曲线

![fail_timeline](../fn_work/runs/demo_mini-1791264217344/figs/fail_timeline.png)
![per_vs_jsr](../fn_work/runs/demo_mini-1791264217344/figs/per_vs_jsr.png)
![throughput_latency](../fn_work/runs/demo_mini-1791264217344/figs/throughput_latency.png)

## 干扰识别（分组 CV）

- - **分组 CV Macro-F1：1.000**（只记录，不设通过门）

## 仪器局限与口径

声明：本平台非 CISPR 16-1-1 意义上的 EMI 测量接收机；测试采用 GB 42590-2023 §5.11 方法学预研 + EN 300 328 传导等效口径；一切数字仅出自本 run 实测产物。

## 数字来源

- steps.jsonl
- /mnt/data/Code/autoC/workspace/chuangxin2026/fn_work/runs/demo/models/train_report.md
