# MAS Meal Recommendation System - 설치 및 사용 가이드

## 📋 사전 요구사항

- Python 3.8 이상
- Google API Key (Gemini API)

## 🚀 설치 방법

### 1. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Google API 키를 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일을 열어서 다음을 수정:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

Google API 키는 [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급받을 수 있습니다.

### 3. 데이터 디렉토리 생성

```bash
mkdir -p data
```

## 💻 실행 방법

### 기본 실행

```bash
python main.py
```

### 사용 예시

시스템이 시작되면 다음과 같이 대화형으로 사용할 수 있습니다:

```
👤 You: 저녁 추천해줘
👤 You: 당뇨에 좋은 점심 메뉴 추천해줘
👤 You: 3명이 먹을 수 있는 1만원 이하 저녁 메뉴 추천해줘
```

## 🏗️ 프로젝트 구조

```
mad-m(example)/
├── agents/                    # 에이전트 구현
│   ├── orchestrator/         # A001: System Orchestrator
│   ├── menu_planner/         # A101: Menu Planner
│   └── analyzers/
│       ├── preference_health/ # A201: Preference & Health Analyzer
│       │   └── chefs/        # A301-303: Chef Agents
│       └── budget_market/     # A202: Budget Analyzer
├── memory/                    # 메모리 관리 시스템
├── tools/                     # 외부 도구 (API)
├── config/                    # 설정 파일
├── data/                      # 데이터 저장소 (자동 생성)
├── main.py                    # 메인 실행 파일
└── requirements.txt           # 의존성 패키지
```

## 🔧 주요 기능

### 에이전트 계층 구조

- **Lv0 (A001)**: System Orchestrator - 최상위 계획 및 의사결정
- **Lv1 (A101)**: Menu Planner - 메뉴 생성 및 충돌 해결
- **Lv2 (A201, A202)**: Analyzers - 선호도/건강 분석, 예산 분석
- **Lv3 (A301-303)**: Chef Agents - 요리별 레시피 생성

### 메모리 시스템

- **STM (Short-Term Memory)**: 세션 기반 대화 컨텍스트
- **LTM (Long-Term Memory)**: 사용자 프로필, 선호도 이력, 예산 패턴

### 추론 전략

- **A001**: ReAct (Reasoning + Acting)
- **A101**: Chain of Thought (CoT)
- **A201/A202**: CoT + Self-Refine
- **A301-303**: Few-shot Prompting

## 📝 예시 시나리오

### 1. 첫 사용자
```
User: "저녁 추천해줘"
→ A001이 기본 프로필 로드 → A201/A202 분석 → A101 메뉴 생성 → 레시피 제공
```

### 2. 건강 제약 사용자
```
User: "당뇨에 좋은 점심 메뉴 추천해줘"
→ A201이 건강 조건 필터링 → A101/A202 조정 → 혈당 지수 표시
```

### 3. 예산 제약 사용자
```
User: "3명이 먹을 수 있는 1만원 이하 저녁 메뉴 추천해줘"
→ A202가 시장 데이터 조회 → 메뉴 비용 및 재료 표시
```

## ⚙️ 설정

`config/config.yaml` 파일에서 시스템 설정을 변경할 수 있습니다:

- LLM 모델 설정
- 메모리 제한
- 도구 활성화/비활성화

## 🐛 문제 해결

### API 키 오류
- `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
- Google AI Studio에서 API 키가 활성화되어 있는지 확인

### Import 오류
- 프로젝트 루트에서 실행하는지 확인
- `pip install -r requirements.txt`로 모든 패키지가 설치되었는지 확인

### 메모리 오류
- `data/` 디렉토리가 생성되어 있는지 확인
- 파일 권한을 확인

## 📚 추가 정보

자세한 시스템 설계는 `readme.md`를 참조하세요.


