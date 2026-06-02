这一层要完成的是世界观的定义：世界规则、资源系统、冲突机制、生存逻辑、社会结构。
常见的例如：“末日堡垒” -> 资源稀缺 + 外部威胁 + 内部权力斗争

**文档状态：** 核心架构冻结 / 待开发
**所属产品线：** CortexVerse (Content World OS)
**核心负责人：** AI 架构组

---

## 一、 产品愿景与定位

**1.1 业务背景**
传统的“一句话生成剧本”模式无法支撑高质量、长生命周期的内容衍生。为实现“一次创世，无限内容涌现”的商业闭环，系统必须在剧情推演前，构筑一个逻辑自洽、具备成长数值且能激发多巴胺的底层世界。

**1.2 核心定位**
世界观构筑模块不是一个单纯的文本生成器，而是一个**分层式多智能体图谱（Hierarchical Multi-Agent DAG）**。它负责将用户稀疏的标签输入，转化为包含“宏观叙事灵魂”与“微观原子数值”的双层结构化数据资产（Dual-Layer World Asset），为下游的【角色引擎】和【剧情状态机】提供绝对的运行法则与资源约束。

---

## 二、 核心领域模型 (Domain Data Model)

本模块的唯一数据输出标准为 `WorldAsset`，采用“宏观定调 + 微观计算”的双层 Pydantic 结构。

### 2.1 宏观上下文层 (Macro Layer)

提供世界的叙事风味与前史厚度，作为系统级 Prompt 约束所有下游 Agent。

| 数据模块 | 核心字段 | 商业价值 |
| --- | --- | --- |
| **宏观哲学 (`MacroPhilosophy`)** | `theme_statement`, `narrative_tone`, `world_drive_force` | 锁定整个世界的文风基调与人群集体欲望。 |
| **宏观前史 (`MacroHistory`)** | `epoch_name`, `pre_history_legacy` | 解释当前世界奇观的来源，提供遗迹/神器的合理性。 |
| **宏观成长 (`MacroGrowthOverview`)** | `ladder_philosophy`, `desire_anchor` | 建立观众/玩家的长期目标感（如阶级跨越）。 |

### 2.2 微观原子数据层 (Micro Layer)

提供下游状态机可直接读取、扣减和触发冲突的数值化实体。

| 数据模块 | 核心字段 | 商业价值 |
| --- | --- | --- |
| **物理区域 (`MicroLocationNode`)** | `location_id`, `danger_coefficient`, `visual_sd_prompt` | 决定事件致死率；为多模态层(ComfyUI)提供精准的场景一致性视觉标签。 |
| **经济与资源 (`MicroResource`)** | `resource_id`, `scarcity_scale`, `monopolizer` | 限制人物行为，资源稀缺度直接关联剧情引擎的背叛触发概率。 |
| **战力/阶级 (`MicroPowerTier`)** | `rank`, `title`, `hard_cost` | 明确跨越阶级的硬性代价，制造升级爽点。 |
| **冲突节点 (`MicroConflictNode`)** | `faction_a`, `faction_b`, `contested_resource`, `climax_trigger` | 剧情引擎提取冲突的直接原料库。 |

---

## 三、 系统架构与工作流 (Supervisor-Worker DAG)

为解决单一 LLM 的“认知过载”与“上下文遗忘”问题，本模块采用基于 `asyncio` 的主从式（Supervisor-SubAgent）编排架构。

### 3.1 核心角色定义

* **The Director (Supervisor):** 路由节点。负责接收用户输入，编排各 SubAgent 的执行顺序与依赖关系。
* **Macro Architect (Worker):** 宏观建筑师。生成 `Macro` 层数据。
* **Geography SubAgent (Worker):** 地理精算师。生成 `MicroLocationNode`。
* **Economy SubAgent (Worker):** 经济精算师。生成 `MicroResource` 和 `MicroPowerTier`。
* **Conflict SubAgent (Worker):** 冲突剧作家。生成 `MicroConflictNode`。
* **The Inspector (Critic):** 靶向质检员。进行数据审核并输出局部重试指令。

### 3.2 核心执行流水线 (The Pipeline)

1. **节点 A (宏观奠基 - 阻塞执行):**
* Director 唤醒 Macro Architect。
* 输入：用户标签（如“赛博、底层逆袭”）。
* 输出：`Macro` 层数据并锁定。


2. **节点 B (微观推演 I - 并发执行):**
* Director 并行唤醒 Geography 和 Economy SubAgent。
* 依赖注入：将 `Macro` 数据作为全局 `System Prompt` 强行植入。


3. **节点 C (微观推演 II - 强依赖执行):**
* 等待节点 B 完毕。
* Director 唤醒 Conflict SubAgent。
* 依赖注入：强行传入刚刚生成的【区域表】和【资源表】，确保冲突不脱离现有资源。


4. **节点 D (靶向质检 - 循环拦截):**
* Aggregator 组装完整 `WorldAsset` 交由 Inspector 质检。
* 若发现逻辑断层（例：冲突节点抢夺的资源不存在于资源表中），Inspector 返回 `failed_modules: ["conflict"]` 及具体修改意见。
* Director **仅重启** Conflict SubAgent 进行局部重修，最多重试 3 次。



---

## 四、 接口与数据交互设计 (API & I/O)

**4.1 核心创世 API**

* **Endpoint:** `POST /api/v1/world/generate`
* **Payload:**
```json
{
  "theme": "废土修仙",
  "tags": ["高魔", "资源极度匮乏", "阶级固化"],
  "user_custom_notes": "男主初始在一个名为垃圾镇的地方"
}

```


* **Response:** 标准化 `WorldAsset` JSON 结构，或返回需人工干预的 `TargetedReflection` 提问清单。

**4.2 靶向修复 API (前端微调接口)**

* **Endpoint:** `POST /api/v1/world/regenerate-module`
* **Payload:**
```json
{
  "world_id": "w_12345",
  "target_module": "economy",
  "user_feedback": "晋升代价太低了，改成需要消耗寿命"
}

```



---

## 五、 异常处理与性能约束

1. **LLM 幻觉控制：** 所有 SubAgent 必须通过 `instructor` 库强制反序列化 Pydantic 模型。若解析失败，底层网关（LLM Gateway）需自动触发格式重试，不上报至 Director。
2. **并发超时机制：** 节点 B 的并发执行（Geography 和 Economy）需设置总超时时间（如 45 秒）。任意一个挂起超时，需走降级通道或重试该单一子任务。
3. **Token 消耗优化：** Inspector 在进行质检时，不传入整个系统的思考过程（Chain of Thought），仅传入最终生成的 `WorldAsset` JSON，减少不必要的 Context 长度。

---

## 六、 验收标准 (Acceptance Criteria)

1. **解耦性：** 单独修改 Economy SubAgent 的 Prompt，不会影响 Geography SubAgent 的代码流转。
2. **一致性测试：** 输入端设定“水资源稀缺”，生成的微观设定中，水资源的 `scarcity_scale` 必须大于 8，且必然出现在 `MicroConflictNode` 的争夺列表中。
3. **视觉可读性：** 所有的 `visual_sd_prompt` 必须只包含英文 Tag（不含长句描述），且直接复制到 ComfyUI 中能够跑通。