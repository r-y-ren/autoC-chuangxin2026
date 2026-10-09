# 接口契约：software ↔ document（chuangxin2026）

> 蓝图 interface_contracts 指向本文件；并发分发前钉死，变更须 JOURNAL 留痕。

## 1. 数据流（software → document）

| 交付物 | 来源 | 格式 | 消费方 |
|---|---|---|---|
| 性能数字 | `workspace/chuangxin2026/metrics.json`（merge_metrics 唯一入口） | JSON 键值 | 中期/结题报告技术节、软著材料、创新大赛 2027 材料 |
| 图表素材 | `fn_work/runs/<时间戳>/figs/`（三元曲线/混淆矩阵/瀑布图 PNG） | PNG（命名 `m<里程碑>-<内容>.png`） | 报告、PPT |
| 结题证据 | `fn_work/runs/<时间戳>/report.md` + `dataset_index.json` | Markdown/JSON | 结题报告附录（A 类"实物并调测"佐证） |
| 操控台截图 | `fn_work/runs/<时间戳>/figs/ui-<内容>.png`（操控台在线导出或演示时截取） | PNG | 中期/结题报告的"零代码演示"配图、软著材料界面页 |

## 2. metrics 键清单（m0 冻结，增删须 JOURNAL 留痕）

`cal_monotonic_pass`（标定单调性）、`loop_curves_count`（竖切三元曲线产出数）、`gb42590_fail_levels_found`（失效电平样点数）、`gb42590_nojam_falsealarm`（无干扰对照误报=0）、`dataset_recordings_total`（SigMF 录制组数）、`jamming_cls_macro_f1`（分组 CV Macro-F1，仅实测）、`demo_exit_code`（一键演示退出码）、`scenario_switch_seconds`（样式切换耗时实测）、`kpi_period_seconds`（KPI 采集周期实测）。

## 3. 硬约束

1. document 角色只允许消费上表路径的数字/素材；对外文档出现任何表外数字 = 验收失败（铁律 4）。
2. 对外材料固定声明（仪器局限+口径）："本平台非 CISPR 16-1-1 测量接收机；采用 GB 42590-2023 §5.11 方法学预研 + EN 300 328 传导等效口径"。
3. 中期/结题材料源文件放 `workspace/chuangxin2026/docs/`，构建入口 `docs/build.py`（--mid/--final）。

## 4. 变更流程

software 改 metrics 键或素材路径 → 修改本文件 → `lint_kb.py --file workspace/chuangxin2026/blueprint.md` 复验 → JOURNAL 记一行。
