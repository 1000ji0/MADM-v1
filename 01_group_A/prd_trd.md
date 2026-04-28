# Group A (대조군) – 기능 중심 직관적 MAS 구현 (Google ADK)
본 문서는 Group A를 Google ADK 기반 MAS로 구현하기 위한 PRD/TRD 통합 문서이다.  
설계 방법론(역할 모델링, 문서화, 접근권한 설계 등)은 최소화하고, 기능 요구사항 중심으로 구현한다.

---

## 1. PRD (Product Requirements Document)

### 1.1 목적
- 사용자 입력(선호/건강/예산)을 기반으로 **식단(메뉴+레시피)**을 생성한다.
- 복합 제약(예: 저염+최저가)이 충돌할 경우 **예산 우선 규칙**으로 처리한다.
- 시스템은 **10개 에이전트 MAS**로 구성한다.

### 1.2 사용자 시나리오
1) 사용자가 식단 추천 요청을 입력  
2) 시스템이 사용자 프로필/제약/예산 정보를 확인  
3) 건강/예산 분석 결과를 바탕으로 메뉴 계획  
4) 셰프 에이전트가 요리 유형별 레시피 생성  
5) 최종 결과(메뉴 + 선택 이유 + 대체안) 출력

### 1.3 범위
**포함**
- 멀티에이전트 기반 식단 생성
- 가격/영양 정보 조회(도구 호출)
- RAG 기반 레시피 검색(가상 문서)

**제외**
- 방법론 기반 산출물(역할 모델/계층적 권한 등)
- 모델 해석 가능성(XAI) 고도화
- 임상/현장 평가 로직

### 1.4 기능 요구사항(FR)
| ID | 기능 | 설명 | 우선순위 |
|---|---|---|---|
| FR-A1 | 요청 해석 | 사용자 요구(목표, 제약, 선호)를 구조화 | High |
| FR-A2 | 건강 분석 | 알레르기/질환/영양 목표 기반 제약 생성 | High |
| FR-A3 | 예산 분석 | 예산 한도 기반 장보기 계획/가격 판단 | High |
| FR-A4 | 메뉴 계획 | (건강+예산) 결과 취합 후 1~n일 식단 계획 | High |
| FR-A5 | 레시피 생성 | 한/일/중 레시피 생성(건강/예산 버전) | High |
| FR-A6 | 충돌 처리 | 복합 제약 충돌 시 **예산 우선** 규칙 | High |
| FR-A7 | 결과 통합 | 최종 메뉴, 레시피, 재료, 근거 출력 | High |

### 1.5 출력물 형식(최종 응답)
- 추천 메뉴(아침/점심/저녁 또는 1끼 기준)
- 레시피(조리 순서)
- 재료 리스트 + 대략 비용 추정
- 영양 요약(핵심 지표만)
- 복합 제약 충돌 시 처리 근거(“예산 우선”)

---

## 2. TRD (Technical Requirements Document)

### 2.1 기술 스택 / 환경
- Framework: **Google ADK**
- LLM: **Gemini 2.5 Flash** (API 키는 사용자가 별도 지정)
- Language: Python 3.x
- Runtime: 가상환경(venv) 기반
- Storage(로컬 가정): JSON/CSV/간단 DB(선택)
- RAG: “가상 문서” 기반(로컬 텍스트 파일/JSON) + 간단 검색

> 주의: Group A에서는 “권한 분리/정교한 메모리 구조” 없이 단순 구현.

---

## 2.2 에이전트 구성(10개) 및 자율성
| Agent ID | Agent Name | Autonomy | 기능 |
|---|---|---|---|
| A001 | System Orchestrator | L3 | 전체 흐름 제어, 작업 분배, 최종 응답 생성 |
| A101 | Menu Planner & Mediator | L3 | 분석 결과 취합, 충돌 처리(예산 우선), 식단 설계 |
| A201 | User Preference & Health Analyzer | L3 | 건강 제약/선호 분석 |
| A202 | Budget & Market Analyzer | L3 | 예산/가격 분석 |
| A301 | Korean Chef (Health-Aware) | L2 | 건강 조건 기반 한식 레시피 |
| A302 | Japanese Chef (Health-Aware) | L2 | 건강 조건 기반 일식 레시피 |
| A303 | Chinese Chef (Health-Aware) | L2 | 건강 조건 기반 중식 레시피 |
| A311 | Korean Chef (Budget-Aware) | L2 | 예산 조건 기반 한식 레시피 |
| A312 | Japanese Chef (Budget-Aware) | L2 | 예산 조건 기반 일식 레시피 |
| A313 | Chinese Chef (Budget-Aware) | L2 | 예산 조건 기반 중식 레시피 |

---

## 2.3 오케스트레이션(단순 파이프라인)
### 2.3.1 흐름
1) A001: 사용자 입력 파싱 → 작업 계획 수립  
2) A201: 건강/선호 분석 결과 생성  
3) A202: 예산/가격 분석 결과 생성  
4) A101: (A201+A202) 취합 → 충돌 처리 → 메뉴 후보 생성  
5) A001: 메뉴 유형 선택 → 적절한 셰프 호출  
6) 셰프(A30x/A31x): 레시피 생성  
7) A101: 결과 포맷 정리  
8) A001: 최종 응답 출력

### 2.3.2 충돌 처리 규칙
- 건강 제약 vs 예산 제약 충돌 시: **예산 우선**
- 예: “저염”과 “최저가” 충돌 → 저염을 완화한 대체안 제시 가능  
  (단, 알레르기/금지 식품은 항상 최우선으로 유지)

---

## 2.4 메모리 설계(단순)
- STM: 세션 내 대화 전체
- LTM: 사용자 프로필/선호/건강/예산/레시피 저장(로컬 JSON/DB)
- 접근: **모든 에이전트가 전부 접근 가능**(Group A 특징)

---

## 2.5 Tool / RAG 설계 (가상 문서)
### 2.5.1 도구(Functions)
- get_nutrition(food_items[]) → 영양 요약 반환(가상/샘플 데이터 가능)
- get_market_prices(ingredients[]) → 가격 정보 반환(가상/샘플 데이터 가능)
- retrieve_recipe(query) → RAG 문서에서 레시피 후보 검색

### 2.5.2 RAG 문서(가상)
`/rag_docs/`
- recipes_ko.json
- recipes_jp.json
- recipes_cn.json
- nutrition_guide.md (저염/당뇨 등 간단 규칙)
- price_table.csv (식재료 예시 가격)

> Group A에서는 임베딩 기반 벡터DB 없이도 “키워드/룰 기반 검색”으로 시작 가능.

---

## 2.6 프롬프트 정책(Group A 스타일)
- “역할 설명 위주”의 직관적 페르소나
- 예산 충돌 규칙을 1~2문장으로 추가

### 예시(Health-Aware Korean Chef)
- “당신은 한식 레시피를 매우 잘 아는 요리사다. 사용자의 건강 제약을 고려해 레시피를 작성하라.”

### 예시(복합 제약 규칙)
- “저염이면서 최저가 등 충돌이 발생하면 예산 조건을 우선하라.”

---

## 2.7 구현 파일 구조(권장)
groupA_adk/
README.md
requirements.txt
.env.example
main.py

agents/
orchestrator_a001.py
planner_a101.py
health_a201.py
budget_a202.py
chef_a301.py
chef_a302.py
chef_a303.py
chef_a311.py
chef_a312.py
chef_a313.py

tools/
nutrition_tool.py
price_tool.py
rag_tool.py

rag_docs/
recipes_ko.json
recipes_jp.json
recipes_cn.json
nutrition_guide.md
price_table.csv

data/
user_profiles.json

---

## 2.8 실행 요건
- venv 활성화 후 실행
- API 키는 사용자가 환경 변수로 주입
- RAG 문서는 가상 데이터로 제공

---

## 2.9 성공 기준(기능 수준)
- 사용자 입력만으로 식단 결과 생성 가능
- 건강/예산 분석이 각각 수행되고 결과가 통합됨
- 복합 제약 충돌 시 예산 우선이 일관되게 적용됨
- 도구 호출(가격/영양/RAG)이 최소 1회 이상 발생

---

# 3. 다음 산출물(구현 단계에서 필요)
- (1) ADK용 main.py 오케스트레이션 스켈레톤
- (2) 각 agent별 prompt + output schema
- (3) tool 함수 입력/출력 schema 정의(JSON)
- (4) mock rag_docs 생성(레시피/가격/영양)