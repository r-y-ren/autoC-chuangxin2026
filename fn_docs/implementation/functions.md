# functions.md —— 函数级实现清单（唯一状态真值）

> fn-implement 独占更新。**代码是真值，本表只是导航。**
> **改任何状态前必须先跑核验命令、在对话中贴出输出，绿了才许改。**

| 函数 | 批次 | 状态(日期) | 核验命令+摘要 | commit |
|---|---|---|---|---|
| load_scenario | B1 | tested (10-03) | pytest tests/src/shared → 15 passed | 0c62831c |
| write_sigmf | B1 | tested (10-03) | pytest tests/src/shared → 15 passed | 0c62831c |
| read_sigmf | B1 | tested (10-03) | pytest tests/src/shared → 15 passed | 0c62831c |
| EstopManager | B1 | tested (10-03) | pytest tests/src/shared → 15 passed | 0c62831c |
| make_spectrogram | B1 | tested (10-03) | pytest tests/src/shared → 15 passed | 0c62831c |
| create_instrument_backend | B2 | wired (10-03) | pytest tests/src/create_instrument_backend → 5 passed；mock 对偶实跑+b210 缺驱动提示断言 | fa9bf5f8 |
| synthesize_style | B3 | tested (10-03) | pytest tests/src/generate_jamming → 11 passed | acdfbcab |
| generate_jamming | B3 | wired (10-03) | 同批 9 passed + gen 入口 dry-run 实跑 rc=0 | acdfbcab |
| parse_serial_line | B4 | tested (10-03) | pytest tests/src/collect_dut_samples → 11 passed | 08b08193 |
| start_dut_source | B4+B19 | tested (10-06) | 响应模型共用后原测仍绿 | 58635d6d |
| collect_dut_samples | B4 | wired (10-03) | 同批 11 passed（双源+gap 续采+回调） | 08b08193 |
| compute_spectrum_stats | B5 | tested (10-03) | pytest tests/src/record_run_streams → 4 passed | 2c987515 |
| record_run_streams | B5 | wired (10-03) | 同批 4 passed（三路落盘+覆盖率≥0.9+extra_events） | 2c987515 |
| plot_triple_curves | B6 | tested (10-03) | pytest tests/src/build_report → 4 passed | 55e2edc6 |
| build_report | B6+B16 | wired (10-03) | 脚注/标定行断言随集成测 | 2ee701e6 |
| plan_steps | B7 | tested (10-03) | pytest tests/src/execute_scenario → 8 passed | f413bed5 |
| check_failure | B7 | tested (10-03) | 同批 8 passed（四分支） | f413bed5 |
| execute_scenario | B7+B16+B19 | wired (10-06) | 发流改造后全量回归绿 | 58635d6d |
| index_dataset | B8 | wired (10-03) | pytest tests/src/index_dataset → 1 passed | 7c9c19d0 |
| grouped_cv_split | B9 | tested (10-03) | pytest tests/src/train_classifier → 3 passed | fc810971 |
| train_classifier | B9 | wired (10-03) | 同批 3 passed——8 录制 4 组 F1≥0.9+模型被 predictor 消费 | fc810971 |
| predict_style | B10 | wired (10-03) | pytest tests/src/predict_style → 1 passed | 7c9c19d0 |
| run_demo | B11 | wired (10-03) | pytest tests/src/run_demo → 1 passed（报告+失效电平+识别样例三件齐） | b61b442f |
| serve_console | B12+B18+B19+B20 | wired (10-06) | dashboard 两端点+网格四卡+dashboard.js | fe0d547b |
| bridge_to_sitl | B13 | wired (10-03) | pytest tests/src/bridge_to_sitl → 1 passed（时间线+模拟标注） | 390bd607 |
| animate_link_state | B14 | wired (10-03) | pytest tests/src/animate_link_state → 2 passed（分级+波纹全覆盖） | 390bd607 |

（状态：stub / implemented / tested / wired 日期 / blocked: 一句原因；全函数按依赖序平铺）
