# Group A - Google ADK 기반 멀티 에이전트 식단 추천 시스템

## 개요
사용자의 선호도, 건강 상태, 예산을 고려하여 식단과 레시피를 생성하는 멀티 에이전트 시스템입니다.

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일에 Google API 키와 모델 이름을 설정하세요:
```
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-pro
```

**사용 가능한 모델:**
- `gemini-pro` (기본값, 가장 안정적)
- `gemini-1.5-pro`
- `gemini-1.5-flash-latest`
- `gemini-1.5-pro-latest`

`MODEL_NAME`을 설정하지 않으면 기본값으로 `gemini-pro`가 사용됩니다.
시스템이 자동으로 사용 가능한 모델을 확인하고 적절한 모델을 선택합니다.

### 4. 실행
```bash
python main.py
```

## 에이전트 구성
- **A001**: System Orchestrator - 전체 흐름 제어
- **A101**: Menu Planner & Mediator - 메뉴 계획 및 충돌 처리
- **A201**: User Preference & Health Analyzer - 건강 분석
- **A202**: Budget & Market Analyzer - 예산 분석
- **A301-A303**: Health-Aware Chefs (한/일/중식)
- **A311-A313**: Budget-Aware Chefs (한/일/중식)

## 주요 기능
- 사용자 선호도/건강 상태 기반 식단 생성
- 예산 제약 조건 고려
- 복합 제약 충돌 시 예산 우선 규칙 적용
- RAG 기반 레시피 검색
- 영양 정보 및 가격 정보 조회

