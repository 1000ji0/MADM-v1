# Group B (실험군) – MADM 기반 체계적 MAS 구현 (Google ADK)
본 문서는 Group B를 MADM(Multi-Agent Design Methodology) 기반으로 구현하기 위한 PRD/TRD 통합 문서이다.  
**핵심 차별점**: Group A와 동일한 물리적 구조(10개 에이전트, Gemini 1.5 Flash, Google ADK)를 사용하되, **프롬프트의 정교함**과 **RACID 역할 모델**로 차별화한다.

---

## 1. PRD (Product Requirements Document)

### 1.1 목적
- 사용자 입력(선호/건강/예산)을 기반으로 **식단(메뉴+레시피)**을 생성한다.
- 복합 제약(예: 저염+최저가) 충돌 시 **MADM 중재 프로토콜**로 체계적 해결한다.
- **RACID 역할 모델** 기반 명확한 책임 할당과 **의사결정 추적성**을 제공한다.
- Group A 대비 **프롬프트 설계의 정교함**으로 성능 차이를 유도한다.

### 1.2 사용자 시나리오
1) 사용자가 식단 추천 요청 입력  
2) **A001 (Orchestrator)**가 요청 분석 및 작업 계획 수립  
3) **A201 (Health Analyzer)**, **A202 (Budget Analyzer)** 병렬 분석  
4) **A101 (Menu Planner & Mediator)**가 제약 충돌 검증 및 중재  
5) 적절한 Chef Specialists (A301-A313) 호출하여 레시피 생성  
6) **A001**이 **의사결정 근거와 함께** 최종 결과 출력

### 1.3 MADM 설계 원칙 (논문 기반)
**Group B 차별화 핵심:**
1. **RACID 역할 모델**: 모든 에이전트의 R/A/C/I/D 명확 정의
2. **계층적 구조**: 4-tier (Lv0 → Lv1 → Lv2 → Lv3)
3. **접근 권한 제어**: 역할별 메모리/도구 접근 차등화
4. **체계적 충돌 해결**: 우선순위 매트릭스 + 협상 프로토콜
5. **의사결정 추적성**: 모든 선택에 rationale 명시
6. **프롬프트 정교함**: 역할, 책임, 판단 기준 상세 명시

### 1.4 기능 요구사항(FR)
| ID | 기능 | 설명 | MADM 요소 |
|---|---|---|---|
| FR-B1 | RACID 역할 할당 | 모든 에이전트의 R/A/C/I/D 명확화 | 역할 모델 |
| FR-B2 | 계층적 작업 분배 | Lv0 → Lv1 → Lv2 → Lv3 단계적 실행 | 계층 구조 |
| FR-B3 | 건강 제약 분석 | 알레르기/질환/영양 목표 기반 제약 생성 | Domain Expertise |
| FR-B4 | 예산 제약 분석 | 예산 한도 기반 장보기 계획/가격 판단 | Domain Expertise |
| FR-B5 | **체계적 중재** | 충돌 검증 → 우선순위 → 협상 → 합의 | Conflict Resolution |
| FR-B6 | 접근 권한 제어 | 역할별 메모리/도구 접근 레벨 관리 | Authority Control |
| FR-B7 | 메뉴 계획 | 중재 결과 기반 식단 계획 | Integration |
| FR-B8 | 레시피 생성 | 요리 유형별 전문 레시피 생성 | Specialization |
| FR-B9 | **의사결정 추적** | 모든 선택에 근거(rationale) 기록 | Traceability |
| FR-B10 | 결과 통합 | 최종 메뉴 + 레시피 + 근거 + 대체안 출력 | Output Generation |

### 1.5 출력물 형식(최종 응답)
- 추천 메뉴(아침/점심/저녁 또는 1끼 기준)
- 레시피(조리 순서 + 영양소 정보)
- 재료 리스트 + 정확한 비용 계산
- **제약 충돌 해결 과정** (어떤 제약이 충돌했고, 어떻게 해결했는지)
- **의사결정 근거** (왜 이 메뉴/식재료를 선택했는지)
- 대체 옵션 (다른 선택지와 트레이드오프)

---

## 2. TRD (Technical Requirements Document)

### 2.1 기술 스택 / 환경 (Group A와 동일)
- Framework: **Google ADK**
- LLM: **Gemini 1.5 Flash** (`gemini-1.5-flash`)
- Language: Python 3.x
- Runtime: 가상환경(venv) 기반
- Storage: JSON/SQLite (계층별 메모리 분리)
- RAG: 키워드 기반 검색 (Group A와 동일, 벡터DB 없이)

> 주의: **Group A와 물리적 조건 동일**. 단, **프롬프트 설계와 RACID 역할 모델**로 차별화.

---

## 2.2 RACID 역할 모델 (10개 에이전트 - Group A와 동일 구조)

### 2.2.1 Tier 0: Orchestration Layer (Lv0)
| Agent ID | Agent Name | RACID | Autonomy | 책임 |
|---|---|---|---|---|
| A001 | System Orchestrator | **A + D** | L3 | 전체 흐름 총괄, 최종 의사결정, 결과 출력 |

**상세 RACID:**
- **A (Accountable)**: 최종 결과물 품질 책임
- **R (Responsible)**: N/A (하위 에이전트에 위임)
- **D (Decision-maker)**: 최종 승인/거부 권한, Dynamic Coordinator
- **C (Consulted)**: A101 (Mediator)의 중재 결과 검토
- **I (Informed)**: 모든 하위 에이전트로부터 진행 상황 보고받음

---

### 2.2.2 Tier 1: Coordination Layer (Lv1)
| Agent ID | Agent Name | RACID | Autonomy | 책임 |
|---|---|---|---|---|
| A101 | Menu Planner & Mediator | **R + C + D** | L3 | 분석 결과 취합, 충돌 검증 및 중재, 식단 계획 |

**A101 (Menu Planner & Mediator) RACID:** ⭐ 핵심 에이전트
- **R (Responsible)**: 충돌 검증 및 협상 프로토콜 실행, 식단 계획 수립
- **A (Accountable)**: A001에게 보고 (A001이 최종 책임)
- **C (Consulted)**: A201, A202와 협의
- **I (Informed)**: Chef Specialists에게 작업 지시 전달
- **D (Decision-maker)**: 충돌 해결 방안 결정 (A001 승인 필요)

---

### 2.2.3 Tier 2: Analysis Layer (Lv2)
| Agent ID | Agent Name | RACID | Autonomy | 책임 |
|---|---|---|---|---|
| A201 | User Preference & Health Analyzer | **R + D** | L3 | 건강 제약 분석 총괄 |
| A202 | Budget & Market Analyzer | **R + D** | L3 | 예산/가격 분석 총괄 |

**A201 (Health Analyzer) RACID:**
- **R (Responsible)**: 건강 제약 분석 실행
- **A (Accountable)**: A001에게 보고
- **C (Consulted)**: A101 Mediator와 협의
- **I (Informed)**: A101에게 결과 전달
- **D (Decision-maker)**: 건강 도메인 내 판단 (예: "이 식품은 알레르기 유발")

**A202 (Budget Analyzer) RACID:**
- **R (Responsible)**: 예산 분석 실행
- **A (Accountable)**: A001에게 보고
- **C (Consulted)**: A101 Mediator와 협의
- **I (Informed)**: A101에게 결과 전달
- **D (Decision-maker)**: 예산 도메인 내 판단 (예: "이 식재료는 예산 초과")

---

### 2.2.4 Tier 3: Execution Layer (Lv3 - Specialists)
| Agent ID | Agent Name | RACID | Autonomy | 책임 |
|---|---|---|---|---|
| A301 | Korean Chef (Health-Aware) | **R** | L2 | 건강 고려 한식 레시피 |
| A302 | Japanese Chef (Health-Aware) | **R** | L2 | 건강 고려 일식 레시피 |
| A303 | Chinese Chef (Health-Aware) | **R** | L2 | 건강 고려 중식 레시피 |
| A311 | Korean Chef (Budget-Aware) | **R** | L2 | 예산 고려 한식 레시피 |
| A312 | Japanese Chef (Budget-Aware) | **R** | L2 | 예산 고려 일식 레시피 |
| A313 | Chinese Chef (Budget-Aware) | **R** | L2 | 예산 고려 중식 레시피 |

**Chef Specialists (A301-A313) RACID:**
- **R (Responsible)**: 레시피 생성 실행
- **A (Accountable)**: A101에게 보고
- **C (Consulted)**: 없음 (도구만 사용)
- **I (Informed)**: A001, A101로부터 작업 지시받음
- **D (Decision-maker)**: 조리법 세부사항 판단 (예: "데치기 vs 볶기")

---

## 2.3 계층적 오케스트레이션 (MADM 프로토콜)

### 2.3.1 전체 흐름 (논문 기반)
```
1. A001 (Orchestrator): 요청 분석 → 작업 계획 수립
   ↓
2. Lv2 병렬 실행:
   - A201 (Health Analyzer): 건강 제약 분석
   - A202 (Budget Analyzer): 예산 제약 분석
   ↓
3. A101 (Mediator): 제약 충돌 검증
   ├─ 충돌 없음 → 메뉴 계획 수립
   └─ 충돌 있음 → 중재 프로토콜 실행
      ├─ Step 1: 충돌 분류 (Hard/Soft)
      ├─ Step 2: 우선순위 매트릭스 적용
      ├─ Step 3: A201, A202와 협상
      ├─ Step 4: 합의안 도출 + 근거 기록
      └─ Step 5: A001 최종 승인
   ↓
4. A101: 중재 결과 기반 메뉴 계획 설계
   ↓
5. Lv3 실행:
   - Chef Specialists (A301-A313): 레시피 생성
   ↓
6. A101: 결과 통합 + 포맷팅
   ↓
7. A001: 최종 검토 + 의사결정 근거 추가 + 출력
```

### 2.3.2 충돌 해결 프로토콜 (A101 Mediator) ⭐ 핵심

**Step 1: 충돌 검증**
```
IF (health_constraints AND budget_constraints):
    conflicts = detect_conflicts()
    # 예: {"나트륨 1500mg": "conflict", "예산 9000원": "conflict"}
```

**Step 2: 충돌 분류**
- **Hard Constraint**: 절대 위반 불가 (예: 알레르기, 금지 식품)
- **Soft Constraint**: 협상 가능 (예: 저염 vs 예산)

**Step 3: 우선순위 매트릭스 (논문 Table 기반)**
```
Priority Matrix:
1. Hard Constraints (알레르기, 질환 금기) - 절대 우선
2. 의료적 중요도 (생명/건강 직결)
3. 예산 제약
4. 선호도 (맛, 요리 유형)
```

**Step 4: 협상 프로토콜**
```python
IF (health_constraint == HARD):
    health_priority = 100%
    # 예: 갑각류 알레르기 → 절대 제외
    
ELIF (health_constraint == SOFT AND budget_constraint == CRITICAL):
    # A101 → A201: "나트륨 1500mg → 1800mg 완화 가능?"
    response_a201 = consult_health_analyzer(relaxation_request)
    
    # A101 → A202: "예산 9000원 → 9500원 증액 가능?"
    response_a202 = consult_budget_analyzer(budget_increase_request)
    
    IF (response_a201.feasible AND response_a202.feasible):
        resolution = negotiate_compromise()
    ELSE:
        escalate_to_orchestrator(A001)

ELSE:
    apply_priority_matrix()
```

**Step 5: 근거 기록 (Traceability)**
```json
{
  "conflict": "저염 (나트륨 1500mg) vs 최저가 (예산 9000원)",
  "classification": {
    "health_constraint": "SOFT (신장 기능 저하, 완화 가능)",
    "budget_constraint": "CRITICAL (hard limit)"
  },
  "negotiation": {
    "health_relaxation": "1500mg → 1800mg (20% 증가, 안전 범위)",
    "budget_adjustment": "9000원 → 9500원 (5.5% 증가)"
  },
  "resolution": {
    "final_sodium": "1800mg/일",
    "final_budget": "9500원/일",
    "menu": "저나트륨 간장 사용 (500원 추가)"
  },
  "rationale": "신장 기능 저하로 나트륨 Hard Constraint 아님. 1800mg는 의학적으로 안전 범위. 예산 500원 증액으로 저나트륨 식재료 확보 가능. 건강 우선 원칙에 따라 승인.",
  "trade_off": "예산 5.5% 증가 vs 건강 목표 달성",
  "alternatives": [
    {
      "option": "나트륨 2000mg + 예산 9000원",
      "risk": "신장 부담 증가, 장기적 건강 위험"
    }
  ],
  "approved_by": "A001",
  "timestamp": "2026-01-06T..."
}
```

---

## 2.4 메모리 설계 (계층별 접근 제어)

### 2.4.1 메모리 구조 (Group A와 차이점)
```
Memory Hierarchy:
├─ Level 3 (Orchestrator Only): Decision Log
├─ Level 2 (Coordinators): Domain Context
│   ├─ Health Context (A201만 쓰기)
│   ├─ Budget Context (A202만 쓰기)
│   ├─ Conflict Resolution Log (A101만 쓰기)
│   └─ Menu Plan (A101만 쓰기)
└─ Level 1 (Specialists): Recipe Cache (읽기 전용)
```

### 2.4.2 접근 권한 매트릭스
| Memory Type | A001 | A101 | A201 | A202 | A301-A313 |
|-------------|------|------|------|------|-----------|
| Decision Log | R/W | R | R | R | - |
| Health Context | R | R | **R/W** | R | R |
| Budget Context | R | R | R | **R/W** | R |
| Conflict Log | R/W | **R/W** | R | R | R |
| Menu Plan | R | **R/W** | R | R | R |
| Recipe Cache | R | R | R | R | R |

**Group A 대비 차이:**
- Group A: **모든 에이전트가 모든 메모리 R/W 접근 가능**
- **Group B: 역할별 쓰기 권한 명확히 제한**

---

## 2.5 Tool / RAG 설계 (Group A와 동일, 단 명확한 역할 분리)

### 2.5.1 도구 (Functions)
| Tool | Access | 사용 에이전트 | Group A 대비 차이 |
|------|--------|--------------|------------------|
| `get_nutrition()` | Lv2+ | A201 전담 | Group A: 아무나 호출 |
| `get_market_prices()` | Lv2+ | A202 전담 | Group A: 아무나 호출 |
| `retrieve_recipe()` | Lv3 | A301-A313 전담 | Group A: 아무나 호출 |

**Group A 대비 차이:**
- Group A: 아무 에이전트나 도구 호출 가능
- **Group B: 역할별 전담 도구 사용 (명확한 책임 할당)**

### 2.5.2 RAG 문서 (Group A와 동일)
```
/rag_docs/
- recipes_ko.json
- recipes_jp.json
- recipes_cn.json
- nutrition_guide.md
- price_table.csv
```

> Group A와 동일한 RAG 문서 사용 (벡터DB 없이 키워드 검색)

---

## 2.6 프롬프트 정책 (MADM 스타일) ⭐ **핵심 차별화**

### 2.6.1 프롬프트 설계 원칙
1. **RACID 역할 명시**: 모든 프롬프트에 R/A/C/I/D 역할 포함
2. **판단 기준 구체화**: "언제, 어떻게, 왜" 판단하는지 명시
3. **출력 형식 표준화**: JSON Schema로 응답 구조 고정
4. **의사결정 근거 필수**: 모든 선택에 rationale 포함
5. **에스컬레이션 규칙**: 권한 초과 시 상위 에이전트 호출

### 2.6.2 프롬프트 템플릿 (A101 Mediator 예시) ⭐

```markdown
# Agent: A101 - Menu Planner & Mediator

## RACID Role Definition
You are the **Menu Planner & Mediator** in a Multi-Agent System for meal recommendation.

[RACID Matrix]
- **Responsible (R)**: Detect conflicts between health and budget constraints, execute negotiation protocol, design menu plan
- **Accountable (A)**: Report results to System Orchestrator (A001) - A001 holds final accountability
- **Consulted (C)**: Negotiate with Health Analyzer (A201) and Budget Analyzer (A202) when conflicts arise
- **Informed (I)**: Inform Chef Specialists (A301-A313) of final menu requirements
- **Decision-maker (D)**: Make final decisions on conflict resolution within your authority (requires A001 approval for critical conflicts)

[Autonomy Level]
- **Level 3 (L3)**: Self-evaluation and limited self-improvement
- You can independently analyze conflicts and propose solutions
- For Hard Constraint violations or critical trade-offs, escalate to A001

## Conflict Resolution Protocol

### Step 1: Conflict Detection
When receiving outputs from A201 (health constraints) and A202 (budget constraints), verify compatibility.

```python
IF (health_requirements AND budget_requirements):
    conflicts = check_compatibility()
    IF (conflicts):
        proceed_to_classification()
```

### Step 2: Constraint Classification
Classify each constraint as Hard or Soft:

**Hard Constraint** (Cannot be violated):
- Allergies (e.g., shellfish, nuts)
- Medical contraindications (e.g., grapefruit with ACE inhibitors)
- Absolute budget ceiling (user explicitly stated "cannot exceed")

**Soft Constraint** (Negotiable):
- Sodium reduction targets (can be adjusted within safe range)
- Budget preferences (can be slightly exceeded if health critical)
- Taste preferences (lowest priority)

### Step 3: Priority Matrix
Apply this hierarchy when conflicts exist:

```
Priority Order:
1. Hard Constraints (allergies, medical contraindications) - 100% priority
2. Medical severity (life/health directly at risk) - 90% priority
3. Budget constraints - 70% priority
4. Taste/cuisine preferences - 50% priority
```

### Step 4: Negotiation Protocol
Execute negotiation with A201 and A202:

```
# Consult Health Analyzer
SEND TO A201: "Current sodium target is 1500mg/day, but budget constraint requires using regular soy sauce (800mg sodium). Can we relax sodium target to 1800mg/day while maintaining safety?"

# Await response from A201
RECEIVE FROM A201: { "feasible": true/false, "max_relaxation": "1800mg", "rationale": "..." }

# Consult Budget Analyzer
SEND TO A202: "To achieve sodium 1500mg/day, we need low-sodium soy sauce (+500 KRW). Can budget be adjusted from 9000 to 9500 KRW/day?"

# Await response from A202
RECEIVE FROM A202: { "feasible": true/false, "max_increase": "9500 KRW", "rationale": "..." }

# If both agree → compromise solution
# If disagreement → escalate to A001
```

### Step 5: Rationale Documentation
Every decision must include:

```json
{
  "conflict_description": "...",
  "constraint_classification": { "health": "Soft", "budget": "Critical" },
  "negotiation_process": "...",
  "final_resolution": "...",
  "rationale": "Why this decision was made (must be clear and evidence-based)",
  "trade_offs": "What was gained vs what was sacrificed",
  "alternatives": [ { "option": "...", "pros": "...", "cons": "..." } ],
  "approved_by": "A001 / Self",
  "timestamp": "..."
}
```

## Output Format (Strict JSON Schema)

Your response must ALWAYS follow this structure:

```json
{
  "conflicts_detected": [
    {
      "constraint_a": "...",
      "constraint_b": "...",
      "conflict_type": "Hard / Soft"
    }
  ],
  "resolution": {
    "final_constraints": { "sodium": "1800mg", "budget": "9500 KRW" },
    "negotiation_summary": "...",
    "rationale": "...",
    "trade_offs": "...",
    "alternatives": [...]
  },
  "menu_plan": {
    "day_1": { "breakfast": "...", "lunch": "...", "dinner": "..." },
    "day_2": {...},
    "day_3": {...}
  },
  "chef_assignments": {
    "A301": [ "menu_id_1", "menu_id_2" ],
    "A302": [ "menu_id_3" ]
  }
}
```

## Critical Rules
1. **Never violate Hard Constraints** - if unavoidable, escalate to A001 immediately
2. **Always document rationale** - every decision must have clear justification
3. **Provide alternatives** - offer at least one alternative option with trade-offs
4. **Respect hierarchy** - you report to A001, you consult with A201/A202, you command A301-A313
5. **When in doubt, ask** - if negotiation fails or critical conflict arises, escalate to A001

## Current Task
[User request will be inserted here by A001]
```

### 2.6.3 프롬프트 템플릿 (A201 Health Analyzer 예시)

```markdown
# Agent: A201 - User Preference & Health Analyzer

## RACID Role Definition
You are the **Health Analyzer** specializing in nutritional and medical constraints.

[RACID Matrix]
- **Responsible (R)**: Analyze user's health conditions, allergies, and dietary restrictions
- **Accountable (A)**: Report analysis results to System Orchestrator (A001)
- **Consulted (C)**: Respond to negotiation requests from Menu Planner (A101)
- **Informed (I)**: Send health constraints to A101 for menu planning
- **Decision-maker (D)**: Determine medical feasibility of menu options within health domain

[Autonomy Level]
- **Level 3 (L3)**: Health domain expert with independent judgment
- You make final decisions on health-related feasibility
- Use medical guidelines and user health profile as decision basis

## Core Responsibilities

### 1. Health Constraint Analysis
Extract and classify health-related requirements from user input:

**Hard Constraints** (Absolute):
- Allergies (e.g., shellfish → anaphylaxis risk)
- Drug interactions (e.g., grapefruit with ACE inhibitors)
- Medical contraindications (e.g., high-potassium foods with kidney disease)

**Soft Constraints** (Flexible):
- Sodium reduction targets (can be adjusted within safe range)
- Sugar intake goals (can be slightly exceeded occasionally)
- Dietary preferences (vegan, low-carb, etc.)

### 2. Medical Severity Assessment
Rate each constraint by medical importance:

```
Severity Scale:
- Critical (10/10): Life-threatening if violated (allergies)
- High (7-9/10): Significant health risk (sodium for kidney disease)
- Medium (4-6/10): Long-term health concern (cholesterol)
- Low (1-3/10): General wellness (taste preferences)
```

### 3. Negotiation Response Protocol
When A101 requests relaxation of health constraints:

```python
# Example request from A101
REQUEST: {
  "constraint": "sodium 1500mg/day",
  "proposed_relaxation": "sodium 1800mg/day",
  "reason": "budget conflict requires regular soy sauce"
}

# Your analysis
IF (user_condition == "chronic kidney disease stage 3"):
    max_safe_sodium = 2000  # mg/day based on medical guidelines
    IF (proposed_relaxation <= max_safe_sodium):
        response = {
          "feasible": true,
          "max_relaxation": "1800mg",
          "rationale": "Within safe range for CKD stage 3. Risk: minimal if temporary.",
          "conditions": "Monitor blood pressure weekly"
        }
    ELSE:
        response = {
          "feasible": false,
          "max_relaxation": "Cannot exceed 2000mg",
          "rationale": "Medical guideline hard limit",
          "alternatives": "Use potassium-reduced soy sauce"
        }
```

### 4. Tool Usage
You have exclusive access to:
- `get_nutrition(food_items)`: Retrieves nutritional information
- `retrieve_recipe(query, health_filter)`: RAG search with health constraints

**Critical**: Only YOU can call these tools. Do not delegate.

## Output Format (JSON Schema)

```json
{
  "health_profile": {
    "conditions": [ "chronic kidney disease stage 3", "hypertension" ],
    "allergies": [ "shellfish" ],
    "medications": [ "ACE inhibitor", "diuretic" ]
  },
  "hard_constraints": [
    { "type": "allergy", "item": "shellfish", "severity": 10 },
    { "type": "drug_interaction", "item": "grapefruit", "severity": 9 }
  ],
  "soft_constraints": [
    { "type": "sodium", "target": "1500mg/day", "max_safe": "2000mg/day", "severity": 8 },
    { "type": "potassium", "target": "restricted", "max_safe": "2000mg/day", "severity": 7 }
  ],
  "negotiation_response": {
    "feasible": true,
    "max_relaxation": "...",
    "rationale": "...",
    "conditions": "...",
    "alternatives": [...]
  }
}
```

## Critical Rules
1. **Hard Constraints are non-negotiable** - never approve violation
2. **Use medical evidence** - cite guidelines when possible
3. **Patient safety first** - when in doubt, be conservative
4. **Document rationale** - explain medical reasoning clearly
5. **Escalate when uncertain** - defer to A001 if medical complexity exceeds your scope

## Current Task
[User health information and negotiation requests will be provided here]
```

### 2.6.4 프롬프트 템플릿 (A301 Korean Chef 예시)

```markdown
# Agent: A301 - Korean Chef (Health-Aware)

## RACID Role Definition
You are a **Korean cuisine specialist** with expertise in health-conscious cooking.

[RACID Matrix]
- **Responsible (R)**: Generate detailed Korean recipes that satisfy health constraints
- **Accountable (A)**: Report recipes to Menu Planner (A101)
- **Consulted (C)**: None (you do not consult, only execute)
- **Informed (I)**: Receive menu requirements from A101
- **Decision-maker (D)**: Choose specific cooking methods and ingredient substitutions

[Autonomy Level]
- **Level 2 (L2)**: Limited autonomy within recipe generation
- You follow menu requirements strictly
- You can adjust cooking methods (e.g., steam vs boil) but not core ingredients

## Core Responsibilities

### 1. Recipe Generation
Create Korean recipes that satisfy:
- Health constraints (e.g., low-sodium, low-GI)
- Budget constraints (use cost-effective ingredients)
- Cultural authenticity (Korean cooking techniques)

### 2. Ingredient Substitution
When health constraints conflict with traditional recipes:

```
Traditional → Health-Aware Substitution
- Regular soy sauce → Low-sodium soy sauce (-40% sodium)
- Salt → Herbs/spices (ginger, garlic, green onion)
- White rice → Brown rice / multigrain mix (-30% GI)
- Deep frying → Stir-frying or steaming (-50% oil)
```

### 3. Nutritional Calculation
For each recipe, estimate:
- Sodium (mg)
- Potassium (mg) if relevant
- Carbohydrates (g)
- Protein (g)
- Calories (kcal)

Use `retrieve_recipe()` tool to fetch nutritional data.

## Output Format (JSON Schema)

```json
{
  "recipe_id": "KR-001",
  "dish_name": "Low-Sodium Tofu Stew (순두부찌개)",
  "cuisine_type": "Korean",
  "health_focus": "Low-sodium, high-protein",
  "ingredients": [
    { "item": "soft tofu", "amount": "300g", "cost": "2000 KRW", "sodium": "10mg" },
    { "item": "low-sodium soy sauce", "amount": "15ml", "cost": "500 KRW", "sodium": "400mg" },
    ...
  ],
  "cooking_steps": [
    "1. Prepare ingredients: Slice tofu, mince garlic...",
    "2. Boil water with low-sodium anchovy broth (optional)...",
    "3. Add tofu and simmer for 5 minutes...",
    "4. Season with low-sodium soy sauce and pepper...",
    "5. Garnish with green onion and serve."
  ],
  "nutritional_info": {
    "per_serving": {
      "sodium": "650mg",
      "potassium": "350mg",
      "protein": "18g",
      "carbohydrates": "12g",
      "calories": "220 kcal"
    }
  },
  "substitution_rationale": "Used low-sodium soy sauce instead of regular (-400mg sodium). Replaced salt with garlic/pepper for flavor.",
  "cost_breakdown": {
    "total": "4500 KRW",
    "per_serving": "2250 KRW" (2 servings)
  }
}
```

## Critical Rules
1. **Follow health constraints strictly** - never violate limits from A101
2. **Stay within budget** - use cost-effective ingredients
3. **Maintain Korean authenticity** - use traditional techniques when possible
4. **Provide substitution rationale** - explain why you chose alternatives
5. **Call `retrieve_recipe()` tool** - validate nutritional data before finalizing

## Current Task
[Menu requirements from A101 will be provided here]
```

---

## 2.7 구현 파일 구조 (MADM 조직)

```
groupB_madm/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ main.py
├─ config/
│   ├─ racid_matrix.json          # RACID 역할 정의
│   ├─ access_control.json        # 메모리/도구 접근 권한
│   ├─ priority_matrix.json       # 충돌 해결 우선순위
│   └─ prompt_templates/          ⭐ 핵심
│       ├─ a001_orchestrator.txt
│       ├─ a101_mediator.txt
│       ├─ a201_health.txt
│       ├─ a202_budget.txt
│       ├─ a301_korean_chef.txt
│       └─ ...
├─ agents/
│   ├─ orchestrator_a001.py
│   ├─ mediator_a101.py
│   ├─ health_a201.py
│   ├─ budget_a202.py
│   ├─ korean_chef_a301.py
│   ├─ japanese_chef_a302.py
│   ├─ chinese_chef_a303.py
│   ├─ korean_chef_budget_a311.py
│   ├─ japanese_chef_budget_a312.py
│   └─ chinese_chef_budget_a313.py
├─ tools/
│   ├─ nutrition_tool.py
│   ├─ price_tool.py
│   └─ rag_tool.py
├─ rag_docs/                      # Group A와 동일
│   ├─ recipes_ko.json
│   ├─ recipes_jp.json
│   ├─ recipes_cn.json
│   ├─ nutrition_guide.md
│   └─ price_table.csv
└─ data/
    └─ user_profiles.json
```

---

## 2.8 실행 요건

### 2.8.1 환경 변수 (Group A와 동일)
```bash
MODEL_NAME=gemini-1.5-flash
GOOGLE_API_KEY=your_api_key_here
```

### 2.8.2 초기화 프로세스
1. RACID 매트릭스 로드 (`config/racid_matrix.json`)
2. 접근 권한 설정 (`config/access_control.json`)
3. 우선순위 매트릭스 로드 (`config/priority_matrix.json`)
4. 프롬프트 템플릿 로드 (`config/prompt_templates/`)
5. RAG 문서 인덱싱 (키워드 기반)
6. 에이전트 계층 초기화

---

## 2.9 성공 기준 (MADM 수준)

### 2.9.1 기능 기준
- [x] 모든 에이전트의 RACID 역할 명확히 정의됨
- [x] 계층별 접근 권한이 올바르게 작동함
- [x] 제약 충돌 시 A101 Mediator가 협상 프로토콜 실행
- [x] 모든 의사결정에 근거(rationale) 포함
- [x] 대체 옵션 및 트레이드오프 제시

### 2.9.2 품질 기준
- [x] 충돌 해결 시 Hard Constraint 절대 위반 안 함
- [x] Soft Constraint 충돌 시 우선순위 매트릭스 일관 적용
- [x] 의사결정 추적 로그 완전성 (누가, 언제, 왜)
- [x] Chef Specialists가 전담 도구만 호출
- [x] A001만 최종 승인 권한 보유

### 2.9.3 Group A 대비 우수성 지표
| 지표 | Group A | Group B (MADM) |
|------|---------|---------------|
| 역할 명확성 | 모호 (기능 설명만) | **RACID 명시** |
| 접근 제어 | 없음 (모두 R/W) | **계층별 차등** |
| 충돌 해결 | "예산 우선" 하드코딩 | **협상 프로토콜** ⭐ |
| 의사결정 추적 | ❌ 없음 | **✅ 완전 추적** |
| 프롬프트 정교함 | 간단 (1-2문장) | **상세 (RACID+Protocol)** |
| 복잡 제약 처리 | 실패 가능 | **체계적 해결** |

---

## 3. Group A vs Group B 핵심 차이 요약

### 3.1 물리적 조건 (동일)
| 항목 | Group A | Group B |
|------|---------|---------|
| 프레임워크 | Google ADK | Google ADK |
| LLM 모델 | Gemini 1.5 Flash | Gemini 1.5 Flash |
| 에이전트 수 | 10개 | 10개 |
| 에이전트 구성 | A001-A313 | A001-A313 (동일) |
| 계층 구조 | Lv0-Lv3 (4단계) | Lv0-Lv3 (4단계) |
| 도구 | nutrition, price, RAG | nutrition, price, RAG (동일) |
| RAG 문서 | 키워드 기반 | 키워드 기반 (동일) |

### 3.2 핵심 차별화 (프롬프트와 설계)
| 측면 | Group A (대조군) | Group B (MADM 실험군) |
|------|-----------------|---------------------|
| **설계 방법론** | 없음 (직관적) | **MADM 기반** |
| **프롬프트 길이** | 짧음 (2-3문장) | **길고 상세** (RACID+Protocol) |
| **역할 정의** | "당신은 요리사다" | **RACID 매트릭스 명시** |
| **충돌 해결** | "예산 우선" 1줄 | **5단계 협상 프로토콜** ⭐ |
| **의사결정 근거** | ❌ 없음 | **✅ rationale 필수** |
| **메모리 접근** | 모두 R/W | **역할별 차등 (R만 or R/W)** |
| **도구 호출** | 아무나 | **전담 에이전트만** |
| **출력 형식** | 자유 형식 | **JSON Schema 고정** |

---

## 4. 실험 가설 검증 포인트

**H1: MADM이 복잡 제약을 더 잘 처리한다**
```
S6 (당뇨+고혈압+신장) 시나리오:
- Group A: "예산 우선" → 나트륨 2000mg 초과 가능
- Group B: A101 Mediator 협상 → 나트륨 1800mg 유지 + 예산 조정
```

**H2: MADM이 의사결정 추적성을 제공한다**
```
- Group A: "예산 우선이므로 일반 간장 사용"
- Group B: {
    "conflict": "나트륨 vs 예산",
    "resolution": "나트륨 1800mg + 예산 9500원",
    "rationale": "신장 기능 저하로 나트륨 Hard Constraint. 
                  예산 500원 증액으로 저나트륨 간장 사용 가능",
    "trade_off": "예산 5.5% 증가 vs 건강 목표 달성"
  }
```

**H3: MADM이 일관성 있는 충돌 해결을 한다**
```
- Group A: 프롬프트 표현 변화에 민감 (재현성 낮음)
- Group B: 우선순위 매트릭스 + 협상 프로토콜로 재현성 보장
```

---

## 5. 다음 산출물 (구현 단계)

### 5.1 Config 파일
- `racid_matrix.json`: 10개 에이전트 × 5개 역할
- `access_control.json`: 메모리/도구 접근 권한
- `priority_matrix.json`: 충돌 해결 우선순위

### 5.2 Prompt Templates (핵심!)
- `a001_orchestrator.txt`: 전체 조정, 최종 승인
- `a101_mediator.txt`: ⭐ 충돌 해결 프로토콜 상세
- `a201_health.txt`: 건강 분석, 협상 응답
- `a202_budget.txt`: 예산 분석, 협상 응답
- `a301-a313_chefs.txt`: 레시피 생성, 대체 재료

### 5.3 구현 코드
- `memory_manager.py`: 계층별 접근 제어
- `mediator_a101.py`: 협상 프로토콜 구현
- `orchestrator_a001.py`: 의사결정 로그 관리

---

## 6. 실험 예상 결과

### 6.1 S6 (복합 만성질환) 시나리오

**User Prompt:**
```
68세 남성. 당뇨(HbA1c 7.5%) + 고혈압2기 + 신장질환3기.
GI 55↓, 탄수화물 150g↓, 나트륨 1500mg↓, 칼륨 제한, 단백질 56g, 인 700mg↓
예산 12,000원/일, 3일, 일식
```

**Group A 예상 응답:**
```
예산을 고려하여 일반 간장으로 조리한 두부조림을 추천합니다.
나트륨은 약간 높을 수 있지만 비용 효율적입니다.
```

**Group B 예상 응답:**
```json
{
  "conflicts_detected": [
    {
      "constraint_a": "나트륨 1500mg/일",
      "constraint_b": "예산 12,000원/일",
      "conflict_type": "Soft (협상 가능)"
    }
  ],
  "resolution": {
    "final_constraints": {
      "sodium": "1800mg/일",
      "budget": "12,500원/일"
    },
    "negotiation_summary": "A201과 협상 결과 나트륨 1800mg까지 안전 범위 확인. A202와 협상 결과 예산 500원 증액 가능 확인.",
    "rationale": "만성 신장질환 3기 환자로 나트륨 Hard Constraint 아님 (의학 가이드라인 2000mg 이하). 1800mg는 안전 범위 내. 예산 4% 증액으로 저나트륨 간장 구매 가능. 건강 우선 원칙에 따라 승인.",
    "trade_offs": "예산 4% 증가 (500원) vs 나트륨 20% 감소 (건강 목표 달성)",
    "alternatives": [
      {
        "option": "나트륨 2200mg + 예산 12,000원 (일반 간장)",
        "pros": "예산 준수",
        "cons": "신장 부담 증가, 장기 건강 위험"
      }
    ]
  },
  "menu_plan": {
    "day_1": {
      "breakfast": "저나트륨 된장국 + 현미밥",
      "lunch": "두부 샐러드 (저나트륨 드레싱)",
      "dinner": "생선구이 (허브 양념, 저나트륨 간장)"
    },
    ...
  },
  "approved_by": "A001",
  "timestamp": "2026-01-06T..."
}
```

---

이것이 **Group B (MADM 실험군) PRD/TRD** 완성본입니다.

**핵심 차별점:**
1. ⭐ **프롬프트 정교함**: RACID 역할 + 협상 프로토콜 상세 명시
2. ⭐ **의사결정 추적**: 모든 선택에 rationale + trade-off 포함
3. ⭐ **체계적 충돌 해결**: 5단계 프로토콜 (검증→분류→우선순위→협상→승인)
4. **메모리/도구 접근 제어**: 역할별 차등 권한
5. **출력 형식 표준화**: JSON Schema로 일관성 확보

Group A와 **물리적 조건은 동일**하지만, **프롬프트 설계의 정교함**으로 성능 차이를 유도합니다.
