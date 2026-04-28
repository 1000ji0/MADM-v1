"""A201: User Preference & Health Analyzer

RACID: Responsible (R), Consulted (C)
Autonomy: L3 (Adaptive reasoning)
Memory access: STM 읽기/쓰기, LTM 읽기

책임:
- 사용자의 건강 상태, 알레르기, 약물 복용 등을 분석하고 의학적 제약을 생성
- 제약을 Hard/Soft로 구분하고 위험 수준(critical/important/recommended)을 판단

출력 형식:
- JSON 구조: {critical_constraints, medical_constraints, nutritional_goals, drug_interactions}
"""
import os
from typing import Dict, Any
from .base_agent import BaseAgent
from tools import get_nutrition

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a201_health.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class HealthAnalyzerAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A201", "Health Analyzer", system_prompt)

    def analyze(self, user_input: str) -> Dict[str, Any]:
        prompt = "사용자 정보를 기반으로 건강 제약을 추출하고 JSON으로 응답하세요. Hard/Soft 구분과 의료 중요도를 포함하세요."
        raw = self.generate_response(prompt, context={"user_input": user_input})
        # 샘플 영양 조회
        nutrition = get_nutrition(["밥", "된장찌개"])
        return {"raw": raw, "sample_nutrition": nutrition}

