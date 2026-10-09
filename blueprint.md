---
campaign:
  competition_id: stitp-njupt-2026    # KB 条目待建（慢循环补录）；规则实抓见 references/STITP规则要点.md（S1–S5 官方）
  name: 无人机链路抗干扰测评台（《无人机通信链路电磁干扰测试平台》B210 实操版，队名可改）
  theme: 大学生创新创业训练计划（原 STITP）· 2026 届 · A 类（硬件+软件）

scope:
  deliverables:
    - 测评台实物（B210+衰减链+自建双链路 DUT+屏蔽盒夹具，A 类"做出实物并调测"口径，S5）
    - 平台软件 platform 包（六层：干扰生成/功率步进/跨层测量/GB 42590 §5.11 协议执行器/SigMF 归档/AI 识别/一键报告——关键模块自制）
    - Web 操控台（驾驶舱操控+实时看板+场景卡片一键测+2D 示意动画层；浏览器操作，演示零代码——2026-10-03 用户需求，R11–R13）
    - 受控干扰 SigMF 真值数据集 v1（样式×功率档真值标注，可发布）
    - AI 干扰样式识别模型 + 分组 CV 评测报告（一期核心，2026-10-03 用户决策）
    - STITP 中期材料（~2026-12）与结题材料（~2027 秋）：报告数字全部出自 metrics.json 实测
    - 过程资产：软著申请材料 ×2（省级门槛项，S5"软著 2 项"）；仪表申报技术论证材料（M1 后）
    - 人机分工记录（结题归档，诚信条款佐证）
  out_of_scope:
    - EMC/EMI 合规测试（无 EMI 接收机；B210 非 CISPR 16-1-1 测量接收机，报告明示局限）
    - 13GHz 扩展与高频混频（无混频器；仪表到位后另立需求）
    - 真实无人机黑盒测试与私有协议解析；开放空间（非屏蔽/非受控）辐射注入
    - 任何"反制设备"功能与叙事（《无人驾驶航空器飞行管理暂行条例》第 43 条红线）
    - 5.8GHz 被测链路（现有 DUT 均为 2.4G 器件；5.8G 仅保留注入+监测能力验证）
    - 多智能体 RL 抗干扰纯仿真方向（调研判断创新性价比低，docs/前沿技术与实现方案补充.md §4.3）
    - 安航云盾战役的材料代写（互借件不互欠件，单向输出 SITL 注入源）

tech_stack:
  - name: GB 42590-2023 §5.11 协议执行器 + ETSI EN 300 328/301 893 传导等效测评框架
    kb_tech_ids: [gb-42590-2023, etsi-en-300-328]
    rationale: 平台锚=强制国标测法（噪声/单音/多音、-5dB 起 5dB 步进至失效记失效电平）——不自造协议；ETSI 注 4 认可传导测量，绕开暗室/重型仪表短板。差异化=国标方法学的低成本实验室实现
    reuse_cost: 低
  - name: 六类干扰样式生成引擎（GNU Radio 3.10 + UHD → B210 双通道）
    kb_tech_ids: [comst-2022-jamming-survey]
    rationale: 样式分类学与可引用危害锚点（SJR 4dB/-19dB 等）出自 IEEE COMST 2022 综述；无维护中 jamming OOT，自带块+自写 Python 块实现（关键模块自制）
    reuse_cost: 低
  - name: 自建双链路被测对象（ESP32 WiFi + NRF24L01，PlatformIO 固件）
    kb_tech_ids: [esp-idf-esp-wifi, rf24-lib]
    rationale: 白盒可控+合规风险最低（用户 2026-10-03 决策）；NRF24 走 ARC_CNT/PLOS_CNT 丢包统计（无 RSSI），ESP32 走上层 PER 自统计
    reuse_cost: 低
  - name: SigMF 真值数据集与防泄漏评测协议
    kb_tech_ids: [sigmf-1.2.0, arxiv-2607.01025]
    rationale: 公开数据集普遍缺受控 JSR/样式真值——衰减器精确控 JSR 是本科生实验室独有能力；按录制分组 CV 防段级泄漏（2607.01025 实证教训）
    reuse_cost: 低
  - name: AI 干扰样式识别（谱图 CNN 基线 → 双流门控进阶）
    kb_tech_ids: [arxiv-2205.15001, arxiv-2602.00042, arxiv-2301.08403]
    rationale: 七类标签体系复现（2205.15001）+JSR 门控双流（2602.00042，控 JSR 恰是其卖点）+小样本增广（2301.08403）；训练经 /toolbox 远程 4070（用户已接入）
    reuse_cost: 中
  - name: 仪表程控抽象层（PyVISA 预留）
    kb_tech_ids: [pyvisa]
    rationale: >-
      "先现有设备、雏形后申报仪表"（用户决策）——B210 与未来 1433D/RSA513A 同接口，scenario 体系不翻修
    reuse_cost: 低
  - name: SITL 链路退化注入（安航云盾联动，单向输出）
    kb_tech_ids: [pymavlink, ardupilot-sitl]
    rationale: 实测"PER-功率台阶"映射为 ArduPilot SITL 丢包/时延注入，为姊妹战役链路风险通道供受控数据源
    reuse_cost: 低
  - name: Web 操控台（FastAPI+WebSocket+Vue3 CDN 单页+Canvas 动画，无 Node 构建链）
    kb_tech_ids: [fastapi, vue3]
    rationale: 演示零代码+游戏感操控（2026-10-03 用户需求 fn-grill 演进轮）：驾驶舱/场景卡片/2D 实测驱动动画；排期=m1 只读实时页、m2 全量；演示级产品化（一键起服务+浏览器）
    reuse_cost: 中
  # 注：以上 ID 为 2026-10-03 战役内实抓调研的引用（docs/前沿技术与实现方案补充.md §四/§5.1，逐条带源）；
  # KB-2 卡片化排队慢循环，入库后回填规范卡片 ID。

interface_contracts:
  - between: [software, hardware]
    contract_file: workspace/chuangxin2026/contracts/sw-hw-interface.md
  - between: [software, document]
    contract_file: workspace/chuangxin2026/contracts/sw-doc-interface.md

milestones:
  - id: m0-skeleton
    task: 工程骨架（platform 包结构/scenario schema/串口契约实体化/metrics 键清单冻结/远程算力烟测）；含两日冒烟栈（干扰波形瀑布+无干扰链路基线）
    owner_role: software
    depends_on: []
  - id: m1-vertical
    task: 端到端竖切（R1–R4）：六类样式生成→衰减链→双链路 KPI→时间对齐→首张三元曲线+标定表；附只读实时曲线页（R11 首 installment）；"雏形"达成→启动仪表申报材料
    owner_role: software
    depends_on: [m0-skeleton]
  - id: m2-full
    task: 全量实现（R5 协议执行器+R6 数据集+R7 AI 识别+R8 一键报告+R11–R13 Web 操控台全量：驾驶舱/场景卡片/2D 动画）＋ **STITP 中期材料**（中期检查 ~2026-12，硬节点）
    owner_role: software
    depends_on: [m1-vertical]
  - id: m3-polish
    task: 结题冲刺：结题报告成稿（数字回填 metrics）、软著申请材料×2、人机分工记录、（二站）创新大赛 2027 参赛材料复用改造
    owner_role: document
    depends_on: [m2-full]

acceptance:
  checklist:
    - {id: sw-boot, category: software, item: 一键启动冒烟（gen dry-run+DUT 空跑+远程算力连通）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/smoke_boot.py"}
    - {id: sw-test, category: software, item: 测试套件全过, method: 自动,
       cmd: "python -m pytest workspace/chuangxin2026/fn_work/tests -q"}
    - {id: sw-loop, category: software, item: 注入-测量闭环出三元曲线（R1–R4）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/scripts/run_scenario.py --scenario scenarios/smoke_loop.yaml"}
    - {id: sw-gb42590, category: software, item: GB 42590 §5.11 执行器产出失效电平表且无干扰对照不误报（R5）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/scripts/run_scenario.py --scenario scenarios/gb42590_noise.yaml"}
    - {id: sw-dataset, category: software, item: SigMF 数据集校验+分组索引（R6）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/scripts/check_dataset.py runs/"}
    - {id: sw-ai, category: software, item: AI 识别端到端（训练→分组 CV→预测并列真值）（R7）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/scripts/eval_jamming_cls.py"}
    - {id: sw-demo, category: software, item: 一键演示报告（R8，数字可溯源到本 run）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/scripts/demo.py --quick"}
    - {id: sw-ui-boot, category: software, item: Web 操控台无头自检（服务起/健康检查/WS 推送/急停生效）（R11–R13）, method: 自动,
       cmd: "python workspace/chuangxin2026/fn_work/ui_selftest.py"}
    - {id: hw-fw, category: hardware, item: ESP32/NRF24 固件编译烧录+串口 JSON 上报, method: 自动,
       cmd: "python3 workspace/chuangxin2026/hardware/firmware/build_all.py"}
    - {id: doc-mid, category: document, item: STITP 中期材料编译通过, method: 自动,
       cmd: "python workspace/chuangxin2026/docs/build.py --mid"}
    - {id: doc-final, category: document, item: 结题报告编译通过（数字与 metrics.json 一致）, method: 自动,
       cmd: "python workspace/chuangxin2026/docs/build.py --final"}
    - {id: man-bench, category: manual, item: 台架物理装配与固定几何标定（屏蔽盒+衰减链+天线位）, method: 人工手册}
    - {id: man-ui-demo, category: manual, item: 浏览器零代码演示走查（开浏览器→选场景→出报告全程无命令行）, method: 人工手册}
    - {id: man-lab, category: manual, item: 实干扰物理实测（各样式三元曲线补测与复核）, method: 人工手册}
    - {id: man-instrument, category: manual, item: 重型仪表申报与到位跟进（M1 后，导师渠道）, method: 人工手册}
    - {id: man-cy2027, category: manual, item: 创新大赛 2027 报名与参赛（S5 强制条款）, method: 人工手册}

workflow:
  auto_chain: false   # 2026-10-03 确认闸门用户改为关：交付期走原波次编排（逐波推进逐波汇报），不跑自动规格链

compliance:
  ai_policy_reviewed: true
  mode: apply
  policy_basis: >-
    S1–S5 五份官方文件均未见 AI 专项条款（2026-10-03 实抓核对，references/STITP规则要点.md）。
    唯一诚信条款："弄虚作假、工作无明显进展的项目，一经查实将终止其运行，追回项目资助经费"（S4《管理办法》）；
    A 类结题要求"做出实物并调测、关键模块自制"（S5）。
  notes: 按"AI 辅助原创"从严执行——AI 限脚手架/检索/润色，协议执行器与识别模型等核心自研，人机分工记录随战役归档（结题佐证）；2026 届任务书原文到手后与本蓝图验收清单对齐回填。
---

# 蓝图：无人机链路抗干扰测评台（STITP 2026 届·A 类）

# 正文（人读）

## 选型依据摘要

见 strategy.md 六节（方向锁定=导师课题已申报；执行口径=GB 42590-2023 §5.11 国标锚 + B210 传导等效台架 + 受控真值数据集差异化；证据链全部 2026-10-03 实抓，docs/前沿技术与实现方案补充.md）。

## 里程碑展开

- m0（第 1 周）：骨架+两日冒烟栈——干扰波形瀑布图、无干扰链路基线曲线、远程算力连通三件先行；metrics 键清单冻结。
- m1（第 2–3 周）：竖切一条线出**首张三元曲线**与标定表；此即"雏形"，触发仪表申报。落后则砍 AI 先保 m1（中期演示主件）。
- m2（第 4–8 周，**12 月上中期检查为硬节点**）：国标执行器自动化+数据集 v1+AI 识别+一键报告；中期材料同步成稿。
- m3（结题期 ~2027 秋，与创新大赛 2027 报名窗 ~04 月重叠）：结题报告数字回填、软著×2、2027 参赛材料改造。

## 风险与缓解

见 strategy.md 第五节（中期时间紧/电磁合规/任务书未知/双战役精力/仪表滞后/省级门槛六项，各附缓解）。
