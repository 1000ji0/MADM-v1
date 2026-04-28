# Group B - MADM 기반 멀티 에이전트 식단 추천 (Google ADK)

## 개요
PRD/TRD(`prd_trd.md`) 기반으로 RACID 역할 모델과 협상 프로토콜을 적용한 멀티 에이전트 시스템입니다. Group A와 물리적 구성(10개 에이전트, RAG 문서)은 동일하지만, 프롬프트 정교화와 접근 제어로 차별화합니다.

## 설치 및 실행
```bash
cd /Users/cheonjiyeong/00.Research/2025_MADM_에이전트개발방법론/실험/group_B
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 변수 (.env)
`.env` 파일(사용자 제공)에 다음 값이 있어야 합니다:
```
GOOGLE_API_KEY=...
MODEL_NAME=gemini-pro   # 미설정 시 코드에서 gemini-pro 기본 사용
```

## 실행
```bash
python main.py
```

## 구조
```
group_B/
├─ README.md
├─ requirements.txt
├─ .env              # 사용자 제공 (API Key, MODEL_NAME)
├─ prd_trd.md        # 요구사항 (PRD/TRD)
├─ config/
│   ├─ racid_matrix.json
│   ├─ access_control.json
│   ├─ priority_matrix.json
│   └─ prompt_templates/
├─ agents/           # A001, A101, A201, A202, A301-A313
├─ tools/            # nutrition, price, rag
├─ rag_docs/         # 제공된 RAG 문서 (recipes_ko/jp/cn, nutrition, price)
└─ data/
    └─ user_profiles.json
```

