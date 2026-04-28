# MADM: Multi-Agent Design Methodology
## 설계 중심의 Multi AI Agent Design Methodology 제안: RACID 역할 모델 중심으로

> **이 저장소는 아래 논문의 PoC(Proof-of-Concept) 실험 구현체입니다.**  
> 논문의 재현 가능성을 위해 공개하며, 일반 배포용 프로덕션 코드가 아닙니다.

📄 **논문:** 설계 중심의 Multi AI Agent Design Methodology(MADM) 제안: RACID 역할 모델 중심으로  
📰 **게재:** Journal of Digital Contents Society (한국디지털콘텐츠학회), Vol. 27, No. 2, pp. 519–531, Feb. 2026  
🔗 **DOI:** [10.9728/dcs.2026.27.2.519](https://dx.doi.org/10.9728/dcs.2026.27.2.519)


![논문게재](https://img.shields.io/badge/JDCS-2026.02-blue)
![방법론](https://img.shields.io/badge/AI%20에이전트-개발방법론-green)
![상태](https://img.shields.io/badge/상태-PoC-orange)

---

## 📌 연구 개요

다중 에이전트 시스템(MAS)은 복잡한 문제 해결에 유용하지만, UC Berkeley MAST 연구에 따르면 초기 설계 단계 결함이 전체 실패의 44.2%를 차지한다. 기존 구현 중심 프레임워크(AutoGen, LangGraph, CrewAI 등)는 "무엇을, 왜, 어떻게 설계해야 하는가"에 대한 체계적 가이드라인을 제공하지 않는다.

본 연구는 이를 보완하기 위해 **설계 중심 방법론 MADM**을 제안한다. MADM은 RACI 매트릭스를 AI 에이전트 환경에 맞게 확장한 **RACID 역할 모델**을 중심으로, MAS 개발 전 단계에서 역할·책임·조정 구조를 명시적으로 정의하는 프레임워크다.

---

## 🔄 MADM 3단계 방법론

```
[Phase 1] 환경 분석 (Environmental Analysis)
  - As-Is 현재 상태 분석
  - 문제 도메인 정의 (실행형/탐색형/정의형/상호작용형)
  - 핵심 기능 영역 식별 및 우선순위화
  - 요구사항 도출 (기능적/비기능적/메모리 요구사항)
           ↓
[Phase 2] AI 에이전트 설계 (AI Agent Design)
  - 기능 분석 및 에이전트 배정 (L0~L3 계층 구조)
  - RACID 모델 기반 역할 체계 설계
  - 에이전트 상세 명세 (Persona + Capability)
  - 메모리 아키텍처 설계 (STM/LTM)
  - 관계 모델 설계 (수직적/수평적 관계)
  - 시스템 아키텍처 다이어그램 작성
           ↓
[Phase 3] MAS 구현 (MAS Implementation)
  - 에이전트 프레임워크 선정
  - LLM / Memory / Tool / Autonomy 구현
  - 에이전트 간 통신 및 오케스트레이션
  - 단위 테스트 → 통합 테스트 → 배포
```

---

## 🧩 RACID 역할 모델

RACI 매트릭스를 AI 에이전트 환경에 맞게 확장한 모델이다.

| Role | 정의 |
|------|------|
| **R** Responsible | 작업을 실제 수행하는 실행 책임자. 다수 지정 가능 |
| **A** Accountable | 최종 의사결정권자. 각 작업에 반드시 한 명만 지정 |
| **C** Consulted | 전문 지식 제공 자문 역할. 직접 실행하지 않음 |
| **I** Informed | 진행 상황 및 결과를 통보받는 이해관계자 |
| **D** Dynamic Coordinator | 예외 상황 발생 시 작업 재배정 및 워크플로 조정. 주로 L0 오케스트레이터 |

---

## 🧪 PoC 실험: 복합 제약 식사 메뉴 추천 시스템

### 실험 목적

MADM 방법론의 일반적 성능 우수성 입증이 아닌, 체계적 설계 접근이 **결과물 품질에 미치는 영향을 탐색적으로 확인**하기 위한 개념증명(PoC).

### 비교 그룹

| 구분 | Group A (대조군) | Group B (실험군) |
|------|----------------|----------------|
| 설계 방식 | 구현 중심 (직관·경험 기반) | MADM 방법론 적용 |
| RACID 매트릭스 | 미적용 | 적용 |
| 역할·책임 명세 | 없음 | 명시적 문서화 |
| 우선순위 계층 | 단순 규칙 | 생명 안전 → 의학 → 영양 → 예산 → 선호도 |

### 시스템 구성 (두 그룹 동일)

| 항목 | 설정 |
|------|------|
| 에이전트 수 | 10개 |
| LLM | Gemini 2.0 Flash |
| 프레임워크 | Google ADK |
| 도구 | RAG, Function Calling, MCP |
| 오케스트레이션 | CPDE |

### 에이전트 목록

| Agent ID | 이름 | 레벨 |
|---------|------|------|
| A001 | System Orchestrator | L0 |
| A101 | Menu Planner & Mediator | L1 |
| A201 | User Preference & Health Analyzer | L2 |
| A202 | Budget & Market Analyzer | L2 |
| A301~A303 | Korean/Japanese/Chinese Chef (Health-Aware) | L3 |
| A311~A313 | Korean/Japanese/Chinese Chef (Budget-Aware) | L3 |

### 실험 결과

| Metric | Group A (Baseline) | Group B (MADM) | 개선 |
|--------|-------------------|----------------|------|
| 평균 점수 | 56.24 | 66.48 | **+10.24 (+18.2%)** |
| Success Rate (≥71점) | 18.0% (9/50) | 56.0% (28/50) | **+38.0%p** |
| Major Failure (≤40점) | 20.0% (10/50) | 14.0% (7/50) | **−6.0%p** |
| 평균 응답 시간 | 24.65초 | 28.07초 | +3.42초 |

안전·의학 제약이 중첩되는 시나리오(S3 다중 알레르기, S6 당뇨+고혈압+약물, S10 와파린 복용)에서 Group B의 점수 개선폭이 상대적으로 크게 관찰되었다.

---

## 📁 프로젝트 구조

```
MADM_v1/
├── 01_group_A/           # 대조군 (구현 중심 설계)
│   └── main.py
├── 02_group_B/           # 실험군 (MADM 방법론 적용)
│   └── main.py
├── 03_(참고)mad-m(example)/  # 참고 예제 구현
│   └── main.py
├── data/                 # 공통 데이터 및 실험 결과
├── rag_docs/             # RAG용 도메인 문서
│   ├── 영양 가이드
│   ├── 레시피
│   └── 식재료 가격표
├── pyproject.toml
└── README.md
```

---

## 🚀 빠른 시작

**환경 요구사항:** Python 3.10+, uv 또는 pip

### uv 사용 (권장)

```bash
uv venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows
uv sync
```

### pip 사용

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 실행

```bash
# Group A (대조군)
python 01_group_A/main.py

# Group B (실험군, MADM 적용)
python 02_group_B/main.py

# 참고 예제
python "03_(참고)mad-m(example)/main.py"
```

---

## 🛠️ 기술 스택

- **LLM:** Gemini 2.0 Flash (Google)
- **프레임워크:** Google ADK
- **도구:** RAG, Function Calling, MCP
- **메모리:** STM (세션 기반) / LTM (사용자 프로필, 레시피 DB)

---

## ⚠️ 연구의 한계

- 설계 결함 자체를 직접 계량화하지 못함 (출력물 품질로 간접 평가)
- 단일 도메인(식사 메뉴 추천), 10개 에이전트, 50개 테스트 케이스로 일반화 가능성 제한
- 평가자 간 신뢰도 검증 및 통계적 유의성 검정 미포함
- 우선순위 체계의 도메인 적응 원칙 미제시

---

## 🚀 향후 연구 방향

- 설계 단계 결함을 직접 측정할 수 있는 정량 지표 개발
- 도메인별 우선순위 조정 원칙 수립
- 다양한 도메인·규모에서의 재현 실험 및 통계적 검증
- 평가자 간 신뢰도 검증을 포함한 엄밀한 실험 설계

---

## 📚 주요 참고문헌

- Cemri et al. (2025). Why Do Multi-Agent LLM Systems Fail? arXiv:2503.13657
- Feng et al. (2025). Levels of Autonomy for AI Agents. arXiv:2506.12469
- Suhanda & Pratami (2021). RACI Matrix Design for Managing Stakeholders. *IJIES*, Vol. 5, No. 2.

---

## 📄 라이선스

MIT License © 2026 [Ji-Yeong Cheon](https://github.com/1000ji0)

이 프로젝트는 MIT 라이선스 하에 공개됩니다.
사용·수정·배포 시 출처를 표시해주세요.
