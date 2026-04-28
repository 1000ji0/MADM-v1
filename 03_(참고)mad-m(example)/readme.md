# MAS-based Meal Recommendation System – Implementation Guide
사용하는 프레임워크: Google ADK(agent development kit)

## 1. System Overview

This project implements a Multi-Agent System (MAS) for personalized meal recommendation. It addresses complex, real-world decision-making tasks such as user preference analysis, health condition filtering, and budget-aware meal planning through distributed intelligent agents, designed using the MAD-M methodology.

---

## 2. Problem Context and Goals

### ❑ Problem Definition
Users face decision overload when selecting meals due to:
- Recipe overabundance (information overload)
- Lack of consideration for health conditions and preferences
- Budget and nutritional balancing complexity

Traditional keyword-based search systems fail to offer holistic and contextual recommendations. Our MAS aims to provide:
- Health-aware, preference-matching meal recommendations
- Automated constraint balancing (health, budget, culture)
- Adaptive and scalable agent-based architecture

---

## 3. Agent Architecture

### ❑ Agent Hierarchy

| Level | Agent ID | Agent Name                          | Core Role                              |
|-------|----------|--------------------------------------|----------------------------------------|
| Lv0   | A001     | System Orchestrator                 | Top-level planner and decision maker   |
| Lv1   | A101     | Menu Planner & Mediator             | Conflict resolver and menu generator   |
| Lv2   | A201     | User Preference & Health Analyzer   | Health info interpreter                |
| Lv2   | A202     | Budget & Market Analyzer            | Cost evaluator and market fetcher      |
| Lv3   | A301     | Korean Chef                         | Korean recipe generator                |
| Lv3   | A302     | Japanese Chef                       | Japanese recipe generator              |
| Lv3   | A303     | Chinese Chef                        | Chinese recipe generator               |

---

## 4. Agent Specifications (Example: A001)

| Item              | Description                                                       |
|-------------------|-------------------------------------------------------------------|
| Agent ID          | A001                                                              |
| Agent Name        | System Orchestrator                                               |
| Hierarchy Level   | Lv0                                                               |
| Core Function     | Interpret user requests, delegate tasks, and make final decisions |
| Input             | Natural language input, sub-agent results                         |
| Output            | Task coordination instructions, final decisions                   |
| Autonomy Level    | L4 (ReAct-based self-improvement capable)                         |
| Memory Access     | Full (STM + LTM admin)                                            |
| Tools             | N/A                                                               |

---

## 5. Agent Roles – RACIN + Autonomy Mapping

| Agent ID | Name                          | Lv | R | A | C | I | N | Autonomy | Rationale                                     |
|----------|-------------------------------|----|---|---|---|---|---|----------|-----------------------------------------------|
| A001     | System Orchestrator           | 0  | - | ● | ○ | ● | ● | L4       | Oversees arbitration & planning               |
| A101     | Menu Planner & Mediator       | 1  | ● | - | ● | ○ | ○ | L3       | Menu generation + constraint mediation        |
| A201     | Preference & Health Analyzer  | 2  | ● | - | ○ | - | ● | L3       | Detect health risks + analyze preference      |
| A202     | Budget & Market Analyzer      | 2  | ● | - | ○ | - | ● | L3       | Optimize menu within budget                   |
| A301–303 | Chef Agents                   | 3  | ● | - | ● | - | - | L2       | Recipe execution only (template-based)        |

---

## 6. Memory Architecture

| Memory Type | Content                          | Access Control                        | Lifecycle            |
|-------------|----------------------------------|----------------------------------------|-----------------------|
| STM         | Dialogue context                 | Readable by all agents                 | Deleted at session end|
| STM         | Temporary menu list              | RW by A001, A101                       | Deleted at session end|
| LTM         | User profile                     | A001 (full), A201 (RW)                 | Persisted             |
| LTM         | Preference history               | A001 (full), A201 (RW)                 | Persisted             |
| LTM         | Budget pattern                   | A001 (full), A202 (RW)                 | Persisted             |
| LTM         | Recipe database                  | All agents (Read), Admin (Write)       | Persisted             |

Memory access is *preemptively* managed — A001 auto-loads profiles before user prompts. A201 prepares health data and past preferences at session start.

---

## 7. External Tools & MCP Servers

| MCP Server     | Agents Involved     | Purpose                              |
|----------------|---------------------|--------------------------------------|
| Filesystem     | A201, A301–A303     | Access to recipe DB and profile data |
| Google Drive   | A001, A201           | Long-term memory storage             |
| Fetch          | A201, A202           | External API integration (nutrition, price) |

---

## 8. LAMT Design – Implementation Details

- **LLM**: All agents use *Gemini 2.5 Flash* for consistency, speed, and cost.
- **Inference Strategy**:
  - A001: ReAct
  - A101: Chain of Thought (CoT)
  - A201/A202: CoT + Self-Refine
  - A301–303: Few-shot Prompting
- **Tool Invocation**: via Google ADK’s Function Calling API with structured schema.
- **Memory Management**: Vector embedding for preference recall, relational DB for structured data.

---

## 9. Orchestration (CPDE Approach)

The system adopts Centralized Planning, Decentralized Execution:
[User Request]
↓
[A001 interprets → loads memory → plans task]
↓
[A201 + A202 → parallel analysis]
↓
[Conflict? → A001 arbitrates]
↓
[A101 creates menu]
↓
[Chef agent selected]
↓
[Final menu presented]


---

## 10. Agent Interaction Protocol

- Protocol: MCP (Memory Communication Protocol)
- Structured JSON exchanges (API outputs)
- Status: Stateless & modular communication

---

## 11. Example Scenarios

1. **First-time user**:
   - "Recommend dinner"
   - A001 loads defaults → A201/A202 analyze → A101 proposes → recipe provided

2. **Health-constrained user**:
   - "Lunch good for diabetes"
   - A201 filters → A101/A202 adapt → blood sugar index displayed

3. **Budget-constrained user**:
   - "Dinner for 3 under ₩10,000"
   - A202 fetches market data → menu cost & ingredients shown

---

## 12. Framework Justification

Google ADK was selected due to:
1. Native Gemini model integration → cost & speed efficiency
2. Enterprise-grade scalability and fault tolerance
3. Seamless connection with Vertex AI, BigQuery, etc.
4. Flexible hierarchy/memory customization for MAS design

Alternatives (LangGraph, AutoGen, CrewAI) had limitations in either scalability, Gemini support, or hierarchy design.

---

## 13. Directory & File Notes

If implementing with Cursor, use this structure:
MAD-M(EXAMple)/
├── agents/
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── agent.py               # A001: System Orchestrator
│   │
│   ├── menu_planner/
│   │   ├── __init__.py
│   │   └── agent.py               # A101: Menu Planner & Mediator
│   │
│   └── analyzers/
│       ├── preference_health/
│       │   ├── __init__.py
│       │   ├── agent.py           # A201: User Preference & Health Analyzer
│       │   └── chefs/
│       │       ├── korean_chef/
│       │       │   ├── __init__.py
│       │       │   └── agent.py   # A301: Korean Chef (Health-Aware)
│       │       ├── japanese_chef/
│       │       │   ├── __init__.py
│       │       │   └── agent.py   # A302
│       │       └── chinese_chef/
│       │           ├── __init__.py
│       │           └── agent.py   # A303
│
│       ├── budget_market/
│       │   ├── __init__.py
│       │   ├── agent.py           # A202: Budget & Market Analyzer
│       │   └── chefs/
│       │       ├── korean_chef/
│       │       │   ├── __init__.py
│       │       │   └── agent.py   # A311: Budget-Aware Korean Chef
│       │       ├── japanese_chef/
│       │       │   ├── __init__.py
│       │       │   └── agent.py   # A312
│       │       └── chinese_chef/
│       │           ├── __init__.py
│       │           └── agent.py   # A313
├── memory/
│   ├── __init__.py
│   ├── memory_manager.py
│   └── vector_db.py
├── tools/
│   ├── __init__.py
│   ├── nutrition_api.py
│   └── price_api.py
├── config/
│   └── config.yaml
├── main.py
└── .env
└── requirements.txt
