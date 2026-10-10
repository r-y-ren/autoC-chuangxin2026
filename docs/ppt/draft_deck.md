---
marp: true
theme: default
paginate: true
title: "无人机通信链路电磁干扰测试平台 · 答辩初稿"
---

<!-- 模板雏形（PPT 资产层 v2）：由 scripts/ppt/build_draft_deck.py 以取材器数据填充。
     标记 @cover/@goals/@method/@measured/@compare/@summary 为注入点，勿删。 -->

# 无人机通信链路电磁干扰测试平台 · 答辩初稿

- 项目：**chuangxin2026**｜日期：2026-10-10
- 性质：答辩初稿（产稿段自动生成；数字均带来源标注，见各页脚注）
- 标题：无人机通信链路电磁干扰测试平台 · 答辩初稿

---

# 一、作品（目标与价值）

- **R1** 六类干扰样式生成引擎 [P0]　`fn_docs/requirements.md`
- **R2** 功率标定与步进 [P0]　`fn_docs/requirements.md`
- **R3** 被测双链路采集（真实+合成源） [P0]　`fn_docs/requirements.md`
- **R4** 三路统一采集与时间对齐 [P0]　`fn_docs/requirements.md`
- **R5** 国标步进执行器 [P0]　`fn_docs/requirements.md`
- **R6** SigMF 真值数据集 [P0]　`fn_docs/requirements.md`
- **R7** AI 干扰样式识别 [P0]　`fn_docs/requirements.md`
- **R8** 一键演示与自动报告 [P0]　`fn_docs/requirements.md`
- **R9** 插件式扩展层 [P0]（模块化硬约束的落点）　`fn_docs/requirements.md`
- **R10** Web 操控台 [P0]　`fn_docs/requirements.md`
- **R11** SITL 链路退化注入预研 [P1]　`fn_docs/requirements.md`
- **R12** 2D 示意动画（非重点，不阻塞验收） [P1]　`fn_docs/requirements.md`
- **R13** 产品最后一公里（fn-analyze P2，演进轮 2026-10-03） [P0]　`fn_docs/requirements.md`
- **R14** 加速判据解耦（P3） [P0]　`fn_docs/requirements.md`
- **R15** 标定消费+断点续跑（P4，fn-implement 评审遗留两项） [P0]　`fn_docs/requirements.md`
- **R16** 中期材料编译线（P5） [P0]　`fn_docs/requirements.md`
- **R17** 设备状态面板（演进轮二，2026-10-06） [P0]　`fn_docs/requirements.md`
- **R18** 界面精修·深色驾驶舱（演进轮二） [P0]　`fn_docs/requirements.md`
- **R19** 模拟数据实时接入（演进轮三，2026-10-06） [P0]　`fn_docs/requirements.md`
- **R20** 交互增强包·原生画布（演进轮三） [P0]　`fn_docs/requirements.md`
- **R21** 结果仪表盘（演进轮四，2026-10-06） [P0]　`fn_docs/requirements.md`

---

# 二、方法（结构与实现）

```
# 责任文档：无人机链路抗干扰测评台（STITP 一期）

> 由 fn-divide 产出与独占更新；fn-implement 只读。进度与状态见 implementation.md。
> 职责字段是**重写规约**：凭职责详述 + 签名意图（输入/输出），必须能完美复现该函数功能。
> **实现期发现结构性变化（函数增/删/拆/并/职责或调用关系变化）必须回到本阶段改本文档**（快速确认通道除外，须留变更说明）。
> 产出依据：fn_docs/requirements.md（2026-10-03 严格重跑版，R1–R12，用户门口确认）。

## 结构概览（纯结构，不带职责）

- generate_jamming ← R1
  - synthesize_style
- calibrate_power ← R2
```
- `load_scenario`：**tested**　`fn_docs/implementation/functions.md`
- `write_sigmf`：**tested**　`fn_docs/implementation/functions.md`
- `read_sigmf`：**tested**　`fn_docs/implementation/functions.md`
- `EstopManager`：**tested**　`fn_docs/implementation/functions.md`
- `make_spectrogram`：**tested**　`fn_docs/implementation/functions.md`
- `create_instrument_backend`：**wired**　`fn_docs/implementation/functions.md`
- `synthesize_style`：**tested**　`fn_docs/implementation/functions.md`
- `generate_jamming`：**wired**　`fn_docs/implementation/functions.md`
- `parse_serial_line`：**tested**　`fn_docs/implementation/functions.md`
- `start_dut_source`：**tested**　`fn_docs/implementation/functions.md`
- `collect_dut_samples`：**wired**　`fn_docs/implementation/functions.md`
- `compute_spectrum_stats`：**tested**　`fn_docs/implementation/functions.md`
- `record_run_streams`：**wired**　`fn_docs/implementation/functions.md`
- `plot_triple_curves`：**tested**　`fn_docs/implementation/functions.md`
- `build_report`：**wired**　`fn_docs/implementation/functions.md`
- `plan_steps`：**tested**　`fn_docs/implementation/functions.md`
- `check_failure`：**tested**　`fn_docs/implementation/functions.md`
- `execute_scenario`：**wired**　`fn_docs/implementation/functions.md`
- `index_dataset`：**wired**　`fn_docs/implementation/functions.md`
- `grouped_cv_split`：**tested**　`fn_docs/implementation/functions.md`
- `train_classifier`：**wired**　`fn_docs/implementation/functions.md`
- `predict_style`：**wired**　`fn_docs/implementation/functions.md`
- `run_demo`：**wired**　`fn_docs/implementation/functions.md`
- `serve_console`：**wired**　`fn_docs/implementation/functions.md`
- `bridge_to_sitl`：**wired**　`fn_docs/implementation/functions.md`
- `animate_link_state`：**wired**　`fn_docs/implementation/functions.md`

---

# 三、实测（数据与图表）

| 指标 | 值 | 来源 |
|---|---|---|
| speed | 40.0 | `fn_work/runs/demo_mini-1791264217344/speed.json` |
| speed | 40.0 | `fn_work/runs/gb42590_noise-1791029196237/speed.json` |
| speed | 40.0 | `fn_work/runs/gb42590_noise-1791264194379/speed.json` |
| speed | 1.0 | `fn_work/runs/gb42590_noise-1791451883123/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791456846527/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791456877199/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791456906256/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791456928984/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791456973647/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791458783709/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791459033510/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791459059896/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791459296762/speed.json` |
| speed | 80.0 | `fn_work/runs/gb42590_noise-1791459661310/speed.json` |
| speed | 1.0 | `fn_work/runs/nojam_control-1791451881563/speed.json` |
| speed | 40.0 | `fn_work/runs/smoke_loop-1791264185153/speed.json` |
| RC | 0.0 | `fn_docs/results/2026-10-03-demo-report.md:4` |
| step1_demo.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step1_demo.return_dict.fail_levels.noise_bandlimited | 5.0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step1_demo.report_fail_level_table.fail_level_db | 5.0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step1_demo.report_kpi_samples | 480 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step2_gb42590_noise.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step3_check_dataset.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step3_check_dataset.recordings | 4 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step4_macro_f1.value | 1.0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step5_latest_gb42590_run.kpi_csv_lines | 24001 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step5_latest_gb42590_run.steps_jsonl_lines | 10 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step5_latest_gb42590_run.steps_failed_count | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step5_latest_gb42590_run.figs_count | 3 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step5_latest_gb42590_run.report_md_size_bytes | 620 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step6_three_checks.ui_selftest.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step6_three_checks.fn_check_default.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |
| step6_three_checks.fn_check_with_venv.rc | 0 | `fn_docs/results/2026-10-03-runs-summary.json` |

---

# 四、对比（基准与优劣）

| 目标 | 对应实测 | 来源 |
|---|---|---|
| R1 六类干扰样式生成引擎 [P0] | （无同名实测项） | — |
| R2 功率标定与步进 [P0] | （无同名实测项） | — |
| R3 被测双链路采集（真实+合成源） [P0] | （无同名实测项） | — |
| R4 三路统一采集与时间对齐 [P0] | （无同名实测项） | — |
| R5 国标步进执行器 [P0] | （无同名实测项） | — |
| R6 SigMF 真值数据集 [P0] | （无同名实测项） | — |
| R7 AI 干扰样式识别 [P0] | （无同名实测项） | — |
| R8 一键演示与自动报告 [P0] | （无同名实测项） | — |
| R9 插件式扩展层 [P0]（模块化硬约束的落点） | （无同名实测项） | — |
| R10 Web 操控台 [P0] | （无同名实测项） | — |
| R11 SITL 链路退化注入预研 [P1] | （无同名实测项） | — |
| R12 2D 示意动画（非重点，不阻塞验收） [P1] | （无同名实测项） | — |
| R13 产品最后一公里（fn-analyze P2，演进轮 2026-10-03） [P0] | （无同名实测项） | — |
| R14 加速判据解耦（P3） [P0] | （无同名实测项） | — |
| R15 标定消费+断点续跑（P4，fn-implement 评审遗留两项） [P0] | （无同名实测项） | — |
| R16 中期材料编译线（P5） [P0] | （无同名实测项） | — |
| R17 设备状态面板（演进轮二，2026-10-06） [P0] | （无同名实测项） | — |
| R18 界面精修·深色驾驶舱（演进轮二） [P0] | （无同名实测项） | — |
| R19 模拟数据实时接入（演进轮三，2026-10-06） [P0] | （无同名实测项） | — |
| R20 交互增强包·原生画布（演进轮三） [P0] | （无同名实测项） | — |
| R21 结果仪表盘（演进轮四，2026-10-06） [P0] | （无同名实测项） | — |
| — 其他实测 — | speed=40.0、RC=0.0、step1_demo.rc=0、step1_demo.return_dict.fail_levels.noise_bandlimited=5.0、step1_demo.report_fail_level_table.fail_level_db=5.0、step1_demo.report_kpi_samples=480 | 见实测页 |

---

# 五、总结（结论与展望）

- （终检缺失：fn_docs/acceptance.md）
- **缺失注记**（不得用占位数字顶替）：
  - fn_docs/acceptance.md
