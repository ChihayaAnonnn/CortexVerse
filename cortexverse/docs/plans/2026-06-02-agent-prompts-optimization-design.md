# Agent Prompts Optimization Design

## 1. 架构目标 (Goals)
基于 `prompt-optimization` 技能中的 7 层架构（Role, Context, Task, Format, Examples, Reasoning, Constraints），将现有的极简 Prompt 重构为高信息密度、强类型约束、带 Few-Shot 示例的系统指令，完美映射 `macro.py` 和 `micro.py` 中的 Schema 字段描述。

## 2. 核心架构设计 (Core Prompt Architecture)
所有的 Agent `system_instructions` 统一遵循以下 7 层映射（`CONTEXT` 和 `FORMAT` 层由 `instructor` 后端及 User Prompt 隐式或显式处理，YAML 中重点强化其他 5 层）：

- **[角色 | ROLE]**: 极具代入感的专家人设定义。
- **[任务 | TASK]**: 结合 Schema 的精确字段填充指南。
- **[推演法则 | REASONING]**: 分步骤的 Chain-of-Thought（思维链）。
- **[约束 | CONSTRAINTS]**: 硬性的 DO/DON'T 规则（含外键约束与数值约束）。
- **[示例 | EXAMPLES]**: Few-Shot 输入输出对照，锁定文风、格式与思考过程。

## 3. 各 Agent 详细设计 (Agent Specifications)

### 3.1 宏观架构师 (Macro Architect)
- **Role**: 顶级商业网文总编、游戏世界观架构师。
- **Task**: 填充 `MacroPhilosophy`, `MacroHistory`, `MacroGrowthOverview`。
- **Reasoning**: 剖析爽点 -> 推演前史 -> 设计阶级晋升代价。
- **Constraints**: 必须有戏剧冲突，语言具有压迫感，严禁平铺直叙。
- **Examples**:
  - *Input*: "废土, 赛博朋克"
  - *Output*: 展示一段极致情绪张力的核心精神（如 "血肉苦弱，机械飞升的尽头是彻底的资本奴役..."）。

### 3.2 地理精算师 (Geography SubAgent)
- **Role**: 关卡设计专家与多模态视觉工程师。
- **Task**: 填充 `MicroLocationNode`（包含 danger_coefficient, visual_sd_prompt）。
- **Reasoning**: 地貌侵蚀推演 -> 幸存者聚集地分析 -> 节点生成。
- **Constraints**: 危险系数 0.0-1.0，视觉提示词纯英文且必须为画面元素。
- **Examples**:
  - *Input*: "被辐射摧毁的巨型城市"
  - *Output*: 展示 `loc_slum_01` 的数据格式，强调 `danger_coefficient: 0.85` 与 `visual_sd_prompt: "neon signs, toxic green smog, rusted cybernetic debris"`。

### 3.3 阶级与社会精算师 (Economy SubAgent)
- **Role**: 残酷的社会工程学专家与地缘政治分析师。
- **Task**: 填充阶层大表、稀缺资源、割据势力、初始角色，通过 `validate_internal_economy` 外键自洽验证。
- **Reasoning**: 生产力基础分析 -> 阶级剥削模型推演 -> 资源分配。
- **Constraints**: 资源稀缺度 >=8 必有垄断，角色必须归属存在的势力，控制资源必须存在。
- **Examples**:
  - *Input*: 极度缺水的沙漠废土宏观背景。
  - *Output*: 展示 `MicroPowerTier` 阶层划分、被垄断的 `res_pure_water` (scarcity: 9)、以及属于某个帮派的主角。

### 3.4 冲突编排师 (Conflict SubAgent)
- **Role**: 精通戏剧冲突与“爽点钩子”的编剧大师。
- **Task**: 填充 `MicroConflictNode`（关联势力A/B与资源，编写爽点导火索）。
- **Reasoning**: 利益对立面剖析 -> 导火索动机设计。
- **Constraints**: 势力与资源ID必须 100% 存在，导火索必须有极强画面爆发力。
- **Examples**:
  - *Input*: 两个对立的帮派和稀缺水资源大表。
  - *Output*: 展示 `conf_water_war`，完美的外键引用，以及导火索："净水阀门开启之日，帮派首领遭暗杀"。
