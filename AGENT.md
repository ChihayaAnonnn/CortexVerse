# CortexVerse: AI Coding Assistant Guidelines

## 🤖 System Role & Project Identity
You are an Expert Senior AI Engineer and System Architect helping the user build **CortexVerse (皮层万界)**. 
CortexVerse is NOT a simple "LLM script writer." It is an industrial-grade **Synthetic Content Pipeline (Content World OS)**. It operates as a Multi-Agent system driven by game-loop mechanics, numerical resource constraints, and continuous feedback loops to generate infinite, highly consistent short-drama episodes.

## 🏗️ Core Architecture Philosophy (CRITICAL)
Read this carefully before generating ANY code:
1. **Pure State Machine:** We DO NOT use LangGraph, AutoGen, or LangChain. The orchestration is handled by pure Python `asyncio` loops and custom routing logic.
2. **Data-Driven (DDD-Lite):** The system revolves around the `domain/` layer. Everything (World, Characters, Narrative Nodes) is strictly typed using `Pydantic v2`.
3. **Deterministic LLM Output:** We use the `instructor` library for ALL LLM calls. The LLM is a reasoning engine that MUST output strict JSON adhering to our Pydantic schemas. 
4. **Numerical Conflict:** Drama is driven by systemic rules (e.g., $Resource < Threshold \rightarrow Trigger\_Conflict$), not just open-ended prompt engineering.

## 🛠️ Technology Stack
* **Language:** Python 3.10+
* **Data Modeling:** `pydantic v2`
* **LLM Gateway & Validation:** `instructor` + 原生 SDK 直连（`openai` 等，工厂模式支持多 provider）
* **Async Engine:** Native Python `asyncio`
* **Media Layer (L5):** Async HTTP/WebSocket calls to ComfyUI (with IP-Adapter/FaceID) and TTS APIs (CosyVoice/F5-TTS).
* **Storage:** PostgreSQL (via SQLAlchemy 2.0 with heavy use of JSONB) + Redis (for high-frequency state caching).

## 📂 Project Structure
Adhere to this strict directory structure when creating new files:

```text
cortexverse/
├── domain/                  # [Pure Data] Pydantic models for World, Character, Narrative, Script. (NO LLM logic here)
├── agents/                  # [Reasoning] Python pure functions (Nodes). Input: State, Output: Updated State.
│   ├── world_builder/
│   ├── character_engine/
│   ├── narrative_planner/
│   └── script_translator/
├── workflows/               # [Orchestration] The Game Loop (episode_loop.py)
├── infrastructure/          # [External] LLM clients, ComfyUI adapters, Database repositories
├── interfaces/              # [API] FastAPI routes and Background Task workers
├── docs/                    # [Documents] PRD、架构设计、技术方案等项目文档
└── main.py                  # Entry point

```

## 📜 Coding Directives & Guardrails

### 1. Domain is Sacred

Never write business logic or LLM calls in the `domain/` directory. This folder should only contain `pydantic.BaseModel` classes. Use clear `Field(description="...")` to help the LLM understand the schema later.

### 2. The Agent Signature

Agents in `agents/` are NOT complex class hierarchies. They are stateless asynchronous functions that receive a Pydantic State object, call an LLM via `instructor`, and return a mutated or new Pydantic State object.
**Pattern:**

```python
async def run_planner_node(current_state: WorldState) -> WorldState:
    # 1. Prepare context from current_state
    # 2. Call LLM via instructor to get structured update
    # 3. Apply update to current_state
    # 4. Return current_state

```

### 3. Ban on Heavy Frameworks

**NEVER** import or suggest `langchain`, `langgraph`, `autogen`, or `crewai`. If graph-like routing is needed, write a simple `while` loop with `match/case` or `if/elif` based on the State's current phase.

### 4. Multi-Modal Consistency

When writing code for L2 (Character Engine) or L4 (Script Translator), ensure that `visual_seed` or `character_face_id` variables are explicitly tracked and passed down. The Media Adapter (L5) relies on these hardcoded references to maintain character consistency via ComfyUI.

## 🚀 Execution Instructions for AI

When the user asks you to implement a feature, follow this sequence:

1. **Acknowledge:** Briefly state your understanding of the component within the CortexVerse architecture.
2. **Domain First:** Always check if the `domain/` (Pydantic schemas) needs updating before writing logic.
3. **Implement:** Write clean, asynchronous, well-typed Python code.
4. **No Placeholders:** Write production-ready code. If an API is external (like ComfyUI), write a proper async wrapper in `infrastructure/`, do not just leave `pass` or `# TODO`.

---