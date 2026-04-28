# Group B - MADM 기반 멀티 에이전트 식단 추천 시스템

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [폴더 구조](#폴더-구조)
3. [에이전트 아키텍처](#에이전트-아키텍처)
4. [각 에이전트 상세 설명](#각-에이전트-상세-설명)
5. [프롬프트 템플릿](#프롬프트-템플릿)
6. [실행 방법](#실행-방법)

---

## 프로젝트 개요

**Group B**는 MADM(Multi-Agent Decision Making) 방법론을 적용한 실험군입니다. PRD/TRD(`prd_trd.md`) 기반으로 RACID 역할 모델, 계층적 자율성, 메모리 접근 제어, 충돌 해결 프로토콜을 체계화하여 Group A 대조군과 비교합니다.

### 핵심 특징
- **RACID 역할 모델**: 각 에이전트의 책임과 권한을 명확히 정의
- **계층적 자율성**: L2(규칙 기반) ~ L4(자체 평가·개선) 단계별 의사결정 권한
- **메모리 접근 제어**: STM/LTM 읽기·쓰기 권한을 에이전트별로 차등 부여
- **충돌 해결 프로토콜**: 우선순위 계층(생명 안전 > 의료 > 영양 > 예산 > 선호)에 따른 협상 전략
- **응답 길이 제한**: 기본 500자, 최대 550자로 제한하여 간결하고 일관된 출력 보장

### 구성
- **10개 에이전트**: Orchestrator(A001), Mediator(A101), Health Analyzer(A201), Budget Analyzer(A202), Chef 에이전트 6개(A301-A313)
- **RAG 문서**: 한식/일식/중식 레시피, 영양 가이드, 가격 정보
- **도구(Tools)**: 영양 API, 가격 API, RAG 검색

---

## 폴더 구조

```
group_B/
├── README.md                    # 프로젝트 개요 및 실행 가이드
├── groupb.md                    # 이 문서 (종합 설명)
├── requirements.txt             # Python 패키지 의존성
├── .env                         # 환경 변수 (API Key, MODEL_NAME)
├── prd_trd.md                   # 제품/기술 요구사항 문서
├── agent_prompt.md              # MADM 기반 에이전트 프롬프트 마스터 문서
│
├── main.py                      # 메인 실행 파일
│
├── config/                      # 설정 파일
│   ├── racid_matrix.json        # RACID 역할 매트릭스
│   ├── access_control.json      # 메모리 접근 제어
│   ├── priority_matrix.json     # 충돌 해결 우선순위
│   └── prompt_templates/        # 에이전트별 프롬프트 템플릿
│       ├── a001_orchestrator.txt
│       ├── a101_mediator.txt
│       ├── a201_health.txt
│       ├── a202_budget.txt
│       └── a301_a313_chefs.txt
│
├── agents/                      # 에이전트 구현
│   ├── __init__.py
│   ├── base_agent.py           # BaseAgent 클래스 (공통 기능)
│   ├── orchestrator_a001.py    # A001: System Orchestrator
│   ├── mediator_a101.py        # A101: Menu Planner & Mediator
│   ├── health_a201.py          # A201: Health Analyzer
│   ├── budget_a202.py          # A202: Budget Analyzer
│   ├── chef_a301.py            # A301: Korean Chef (Health-Aware)
│   ├── chef_a302.py            # A302: Japanese Chef (Health-Aware)
│   ├── chef_a303.py            # A303: Chinese Chef (Health-Aware)
│   ├── chef_a311.py            # A311: Korean Chef (Budget-Aware)
│   ├── chef_a312.py            # A312: Japanese Chef (Budget-Aware)
│   └── chef_a313.py            # A313: Chinese Chef (Budget-Aware)
│
├── tools/                       # 도구 모듈
│   ├── __init__.py
│   ├── nutrition_tool.py       # 영양 정보 조회
│   ├── price_tool.py           # 가격 정보 조회
│   └── rag_tool.py             # RAG 레시피 검색
│
├── rag_docs/                    # RAG 문서
│   ├── recipes_ko.json         # 한식 레시피
│   ├── recipes_jp.json         # 일식 레시피
│   ├── recipes_cn.json         # 중식 레시피
│   ├── nutrition_guide.md      # 영양 가이드
│   └── price_table.csv         # 가격 정보
│
└── data/                        # 데이터
    ├── user_profiles.json      # 사용자 프로필
    └── result.json             # 실행 결과 (자동 저장)
```

---

## 에이전트 아키텍처

### 계층 구조

```
┌─────────────────────────────────────────────┐
│   A001: System Orchestrator (L4)           │  ← 최종 책임자
│   [Accountable, Dynamic Coordinator]       │
└──────────────┬──────────────────────────────┘
               │
               ├─── A101: Menu Planner & Mediator (L3)
               │    [Responsible, Informed, Coordinator]
               │    │
               │    ├─── A201: Health Analyzer (L3)
               │    │    [Responsible, Consulted]
               │    │
               │    └─── A202: Budget Analyzer (L3)
               │         [Responsible, Consulted]
               │
               └─── Chef Agents (L2)
                    ├─── A301: Korean Chef (Health)
                    ├─── A302: Japanese Chef (Health)
                    ├─── A303: Chinese Chef (Health)
                    ├─── A311: Korean Chef (Budget)
                    ├─── A312: Japanese Chef (Budget)
                    └─── A313: Chinese Chef (Budget)
```

### RACID 역할 모델

| 에이전트 | Responsible | Accountable | Consulted | Informed | Dynamic Coordinator |
|---------|------------|-------------|-----------|----------|---------------------|
| A001    | -          | ✅          | -         | ✅       | ✅                  |
| A101    | ✅         | -           | -         | ✅       | ✅                  |
| A201    | ✅         | -           | ✅        | -        | -                   |
| A202    | ✅         | -           | ✅        | -        | -                   |
| A3xx    | ✅         | -           | ✅        | -        | -                   |

### 자율성 레벨

| 레벨 | 설명 | 적용 에이전트 |
|-----|------|-------------|
| L4  | 자체 평가 및 개선, 전략적 의사결정 | A001 |
| L3  | 적응적 추론, 협상 프로토콜 실행 | A101, A201, A202 |
| L2  | 규칙 기반 실행, 템플릿 기반 생성 | A301-A313 |

### 메모리 접근 권한

| 에이전트 | STM 읽기 | STM 쓰기 | LTM 읽기 | LTM 쓰기 | 타 에이전트 메모리 |
|---------|---------|---------|---------|---------|-------------------|
| A001    | ✅      | ✅      | ✅      | ✅      | ✅ 조회 가능      |
| A101    | ✅      | ✅      | ✅      | -       | -                |
| A201    | ✅      | ✅      | ✅      | -       | -                |
| A202    | ✅      | ✅      | ✅      | -       | -                |
| A3xx    | ✅      | -       | ✅      | -       | -                |

---

## 각 에이전트 상세 설명

### A001: System Orchestrator

**역할**: 전체 시스템의 최종 책임자 및 조정자

**RACID**: Accountable (A), Dynamic Coordinator (D), Informed (I)  
**자율성**: L4 (Self-evaluation and improvement)  
**메모리 접근**: STM/LTM 전체 읽기·쓰기, 다른 에이전트 메모리 조회 가능

**책임**:
- 사용자 요청을 구조화하고 워크플로우 전체를 감독
- Health(A201)·Budget(A202) 분석을 병렬로 위임
- Mediator(A101)에게 통합 및 충돌 중재 지시
- Chef 에이전트 선택 및 레시피 생성 요청
- 최종 결과 검증 및 사용자에게 응답

**충돌 해결 원칙**:
1. 생명 안전 (알레르기, 약물 상호작용) - 최우선
2. 의학적 제약 (저염, GI 제한 등)
3. 영양 목표 (단백질, 칼슘 등)
4. 예산 제약
5. 사용자 선호

**출력 형식**:
- 추천 메뉴 (끼니별)
- 간결한 레시피 요약
- 재료 목록 및 예측 비용
- 영양 요약 (단백질, 나트륨 등)
- 충돌 해결 근거 및 대체안

**구현 파일**: `agents/orchestrator_a001.py`

---

### A101: Menu Planner & Mediator

**역할**: 제약 통합 및 충돌 중재자

**RACID**: Responsible (R), Informed (I), Dynamic Coordinator (D)  
**자율성**: L3 (Adaptive with negotiation)  
**메모리 접근**: STM 전체 읽기/쓰기, LTM 읽기 전용

**책임**:
- Health와 Budget 분석 결과를 통합
- 제약 충돌 발생 시 협상 및 중재 수행
- 우선순위 기반 타협안 생성
- 통합 결과를 Orchestrator에게 보고

**충돌 해결 프로토콜**:
- 우선순위 계층에 따라 상위 제약 유지, 하위 항목에서 대체안 탐색
- 타협 불가능 시 Orchestrator에 에스컬레이션
- 예: "저염(의학) + 최저가(예산)" 충돌 → 저염 유지, 예산 내 저가 식재료 재선택

**협상 전략**:
- Hard constraint: 절대 위반 불가
- Soft constraint: 협상 가능, max_relaxation 범위 내
- Trade-off: 우선순위 기반 균형점 탐색

**출력 형식** (JSON):
```json
{
  "meal": "breakfast|lunch|dinner",
  "dish": "요리명",
  "brief_description": "한 줄 설명",
  "estimated_cost": "원",
  "protein_g": 숫자,
  "conflicts_detected": [...],
  "resolution_rationale": "...",
  "alternatives": [...]
}
```

**구현 파일**: `agents/mediator_a101.py`

---

### A201: User Preference & Health Analyzer

**역할**: 건강 제약 분석 전문가

**RACID**: Responsible (R), Consulted (C)  
**자율성**: L3 (Adaptive reasoning)  
**메모리 접근**: STM 읽기/쓰기, LTM 읽기

**책임**:
- 사용자 건강 상태, 알레르기, 약물 복용 정보 분석
- 의학적 제약 조건 생성 (Hard/Soft 구분)
- 위험 수준 평가 (Critical/Important/Recommended)
- 약물-식품 상호작용 감지

**분석 프로세스**:
1. 건강 상태 파악 (진단명, 약물, 알레르기)
2. 제약 조건 생성 (금지 식품, 영양소 제한/목표)
3. 위험 수준 분류:
   - 🔴 Critical: 생명 위협 (알레르기, 약물 상호작용)
   - 🟡 Important: 질환 악화 (당뇨+고GI, 고혈압+고염)
   - 🟢 Recommended: 최적화 (영양 균형)

**출력 형식** (JSON):
```json
{
  "critical_constraints": [
    {"type": "allergy", "food": "갑각류", "severity": "anaphylaxis"}
  ],
  "medical_constraints": [
    {"type": "GI", "limit": "≤55", "reason": "제2형 당뇨"},
    {"type": "sodium", "limit": "≤2000mg/day", "reason": "고혈압"}
  ],
  "nutritional_goals": [
    {"nutrient": "단백질", "target": "≥60g/day", "reason": "근성장"}
  ],
  "drug_interactions": [
    {"drug": "ACE억제제", "avoid": "고칼륨 식품 (바나나, 시금치)"}
  ]
}
```

**의학적 판단 원칙**:
- 보수적 접근: 불확실하면 제한
- 대체안 제시: 금지보다 안전한 대안 제공
- 의료 상담 권고: "의료진과 상담하세요" 문구 포함

**구현 파일**: `agents/health_a201.py`

---

### A202: Budget & Market Analyzer

**역할**: 예산 최적화 전문가

**RACID**: Responsible (R), Consulted (C)  
**자율성**: L3 (Adaptive optimization)  
**메모리 접근**: STM 읽기/쓰기, LTM 읽기

**책임**:
- 예산 분석 및 가격 정보 조회
- 가성비 최적화 전략 제시
- 대량 구매/계절성/재고 고려한 구매 계획
- 협상 시 예산 완화안 제공

**분석 프로세스**:
1. 예산 제약 파악 (일일/주간 예산, 초기 투자 가능 여부)
2. 가성비 전략:
   - 저가 고단백: 계란, 두부, 닭가슴살, 통조림 참치
   - 대량 구매: 쌀, 냉동 채소, 냉동 닭가슴살
   - 계절 식재료 활용
3. 비용 최적화:
   - 식재료 공유 (여러 끼니 활용)
   - 재고 관리 (유통기한 고려)
   - 외식 대체 전략

**출력 형식** (JSON):
```json
{
  "budget_summary": {
    "total_budget": "35,000원/주",
    "daily_budget": "5,000원/일",
    "flexibility": "초기 투자 가능"
  },
  "cost_effective_items": [
    {"item": "계란", "price": "200원/개", "protein": "6g/개"},
    {"item": "두부", "price": "1,500원/300g", "protein": "10g/100g"}
  ],
  "bulk_purchase_strategy": [
    {"item": "냉동 닭가슴살", "quantity": "2kg", "price": "12,000원", "servings": "20끼"}
  ],
  "daily_allocation": {
    "Day1": "4,800원",
    "Day2": "5,200원"
  }
}
```

**가성비 원칙**:
- 영양 밀도 우선: 가격 대비 영양소 함량
- 가공식품 최소화: 나트륨↑, 가격↑
- 조리 간편성: 시간 = 비용

**구현 파일**: `agents/budget_a202.py`

---

### A301-A303: Chef Agents (Health-Aware)

**역할**: 건강 제약 기반 레시피 생성 전문가

**에이전트**:
- **A301**: Korean Chef (Health-Aware) - 한식 전문
- **A302**: Japanese Chef (Health-Aware) - 일식 전문
- **A303**: Chinese Chef (Health-Aware) - 중식 전문

**RACID**: Responsible (R), Consulted (C)  
**자율성**: L2 (Rule-based execution)  
**메모리 접근**: STM 읽기, LTM 읽기

**책임**:
- 건강 제약을 준수하는 요리 레시피 생성
- 요리 스타일별 전문 지식 제공
- 대체재 및 조리 팁 제공

**레시피 생성 원칙**:
1. 제약 우선 필터링:
   - 금지 식품 절대 사용 금지
   - 영양소 제한 준수
   - 의학적 제약 반영
2. 요리 특성 유지:
   - **한식(A301)**: 전통 조리법, 발효식품, 계절 식재료
   - **일식(A302)**: 저염 조리법, 생선/해조류, 간장/미소 최소화
   - **중식(A303)**: 향신료 활용, 볶음/찜, MSG 무첨가
3. 건강 최적화:
   - 저염: 다시마/무 육수, 레몬/식초 활용
   - 저GI: 잡곡밥, 통곡물, 채소↑
   - 고단백: 두부, 생선, 계란

**출력 형식** (요약형, 상세 레시피 단계 제외):
```json
{
  "dish_name": "추천 메뉴명",
  "reason": "선택 이유 (건강 고려사항)",
  "cooking_method": "조리 개요 (예: 삶기 + 혼합)",
  "ingredients": [
    {"item": "두부", "amount": "150g", "price": "1500원"}
  ],
  "total_cost": "총 예상 비용",
  "nutrition": {
    "calories": "kcal",
    "protein_g": 18,
    "gi_index": 55,
    "sodium_mg": 420
  },
  "health_notes": "건강 고려사항"
}
```

**구현 파일**: `agents/chef_a301.py`, `agents/chef_a302.py`, `agents/chef_a303.py`

---

### A311-A313: Chef Agents (Budget-Aware)

**역할**: 예산 제약 기반 레시피 생성 전문가

**에이전트**:
- **A311**: Korean Chef (Budget-Aware) - 한식 전문
- **A312**: Japanese Chef (Budget-Aware) - 일식 전문
- **A313**: Chinese Chef (Budget-Aware) - 중식 전문

**RACID**: Responsible (R), Consulted (C)  
**자율성**: L2 (Rule-based execution)  
**메모리 접근**: STM 읽기, LTM 읽기

**책임**:
- 예산 제약을 준수하는 레시피 생성
- 가성비 조리법 제공
- 비용 최적화 전략 제시

**레시피 생성 원칙**:
1. 저가 식재료 우선:
   - 계란, 두부, 냉동 닭가슴살
   - 제철 채소
   - 통조림 활용
2. 비용 최적화:
   - 식재료 공유 (여러 끼 활용)
   - 간단한 조리법 (시간 절약)
   - 대량 조리 가능
3. 영양 유지:
   - 예산 내 영양 밀도 최대화
   - 단백질 목표 달성

**출력 형식** (Health-Aware Chef와 동일, cost_breakdown 추가):
```json
{
  "dish_name": "추천 메뉴명",
  "reason": "선택 이유 (예산 고려사항)",
  "cooking_method": "조리 개요",
  "ingredients": [...],
  "cost_breakdown": {
    "estimated_total": "총 비용",
    "by_item": [
      {"name": "두부", "unit": "300g", "price": 1500}
    ]
  },
  "nutrition": {...},
  "health_notes": "건강 고려사항"
}
```

**구현 파일**: `agents/chef_a311.py`, `agents/chef_a312.py`, `agents/chef_a313.py`

---

## 프롬프트 템플릿

각 에이전트의 시스템 프롬프트는 `config/prompt_templates/` 디렉토리에 텍스트 파일로 저장되어 있으며, `BaseAgent` 초기화 시 로드됩니다. 또한 `agent_prompt.md`의 에이전트별 섹션이 자동으로 시스템 프롬프트 앞에 추가됩니다.

### 프롬프트 파일 목록

| 파일명 | 설명 |
|-------|------|
| `a001_orchestrator.txt` | A001 System Orchestrator 프롬프트 |
| `a101_mediator.txt` | A101 Menu Planner & Mediator 프롬프트 |
| `a201_health.txt` | A201 Health Analyzer 프롬프트 |
| `a202_budget.txt` | A202 Budget Analyzer 프롬프트 |
| `a301_a313_chefs.txt` | A301-A313 Chef 에이전트 공통 프롬프트 |

### 프롬프트 구성 요소

각 프롬프트 템플릿은 다음 구성 요소를 포함합니다:

1. **RACID 역할**: 에이전트의 책임과 권한
2. **자율성 레벨**: 의사결정 권한 범위
3. **메모리 접근**: STM/LTM 읽기/쓰기 권한
4. **핵심 책임**: 주요 작업 및 의무
5. **작업 프로세스**: 단계별 실행 절차
6. **출력 형식**: JSON 스키마 및 예시
7. **제약 조건**: 우선순위 및 규칙
8. **응답 지시**: 언어, 길이, 스타일 가이드

### 응답 길이 제한

모든 에이전트는 다음 길이 제한을 준수합니다:

- **기본 권장 길이**: 500자 이내 (환경변수 `RESPONSE_MAX_CHARS`로 조정 가능)
- **최대 출력 길이**: 550자 (환경변수 `RESPONSE_TOTAL_MAX_CHARS`로 조정 가능)
- **절단 방식**: JSON 구조 보존 우선, 문장 단위 안전 절단

설정 방법:
```bash
export RESPONSE_MAX_CHARS=500
export RESPONSE_TOTAL_MAX_CHARS=550
```

---

## 실행 방법

### 1. 환경 설정

**Python 가상환경 생성 및 활성화**:
```bash
cd /Users/cheonjiyeong/00.Research/2025_MADM_에이전트개발방법론/실험/group_B
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**패키지 설치**:
```bash
pip install -r requirements.txt
```

**환경 변수 설정** (`.env` 파일):
```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-lite
MODEL_TEMPERATURE=0.7
MODEL_MAX_OUTPUT_TOKENS=1024
RESPONSE_MAX_CHARS=500
RESPONSE_TOTAL_MAX_CHARS=550
AUTO_SAVE_RESULTS=true
```

### 2. 프로그램 실행

```bash
python main.py
```

### 3. 실행 흐름

1. 사용자 입력 받기
2. Orchestrator(A001)가 요청 파싱
3. Health(A201), Budget(A202) 병렬 분석
4. Mediator(A101)가 결과 통합 및 충돌 중재
5. 적절한 Chef 에이전트 선택 (건강 우선 vs 예산 우선)
6. Chef가 레시피 생성
7. Orchestrator가 최종 응답 생성
8. 결과를 `data/result.json`에 자동 저장 (AUTO_SAVE_RESULTS=true 시)

### 4. 결과 확인

실행 결과는 다음 정보를 포함합니다:

- **추천 메뉴**: 끼니별 요리명
- **선택 이유**: 건강/예산/선호 고려사항
- **조리 개요**: 간단한 조리 방법
- **준비 재료**: 재료명, 수량, 가격
- **총 비용**: 예상 비용
- **영양 정보**: 칼로리, 단백질, GI, 나트륨 등
- **건강 고려사항**: 제약 충족 여부 및 근거
- **에이전트 응답 시간**: 각 에이전트별 처리 시간

### 5. 트러블슈팅

**429 할당량 초과 오류**:
- 원인: API 분당 요청 한도(RPM) 또는 토큰 한도(TPM) 초과
- 해결:
  - 잠시 대기 후 재시도 (1-2분)
  - Google Cloud Console에서 할당량 확인
  - 에이전트 호출 간격 조정
  - 더 가벼운 모델 사용 (gemini-2.0-flash-lite)

**API Key 오류**:
- `.env` 파일에 올바른 `GOOGLE_API_KEY` 설정 확인
- API Key 만료 여부 확인

**응답 길이 문제**:
- `RESPONSE_MAX_CHARS`, `RESPONSE_TOTAL_MAX_CHARS` 환경변수 조정
- 프롬프트 템플릿에서 "간결하게" 지시 강화

---

## 부록: BaseAgent 클래스

모든 에이전트는 `BaseAgent` 클래스를 상속받아 공통 기능을 사용합니다.

### 주요 기능

1. **모델 초기화**: Gemini API 연결 및 모델 선택
2. **프롬프트 구성**: 시스템 프롬프트 + 컨텍스트 + STM/LTM
3. **응답 생성**: `generate_response()` 메서드
4. **응답 길이 제한**: 자동 절단 및 JSON 구조 보존
5. **응답 시간 측정**: `last_response_time` 속성
6. **메모리 관리**: STM(Short-Term Memory), LTM(Long-Term Memory)

### agent_prompt.md 통합

`BaseAgent`는 초기화 시 `agent_prompt.md` 파일에서 해당 에이전트 ID의 섹션을 추출하여 시스템 프롬프트 앞에 자동으로 추가합니다. 이를 통해 MADM 가이드라인이 모든 에이전트에 일관되게 적용됩니다.

### 구현 위치

`agents/base_agent.py`

---

## 참고 문서

- `README.md`: 프로젝트 개요 및 빠른 시작 가이드
- `prd_trd.md`: 제품/기술 요구사항 문서
- `agent_prompt.md`: MADM 기반 에이전트 프롬프트 마스터 문서
- `config/racid_matrix.json`: RACID 역할 매트릭스
- `config/access_control.json`: 메모리 접근 제어
- `config/priority_matrix.json`: 충돌 해결 우선순위

---

## 라이선스 및 연락처

이 프로젝트는 연구 목적으로 개발되었습니다.

**연구 주제**: MADM 방법론 기반 멀티 에이전트 시스템의 의사결정 품질 비교 연구  
**실험군**: Group B (MADM 적용)  
**대조군**: Group A (기본 프롬프트)

---

**문서 작성일**: 2026년 1월 6일  
**버전**: 1.0
