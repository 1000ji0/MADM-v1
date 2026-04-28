"""A101: Menu Planner & Mediator (Mediator / Menu Planner)

RACID: Responsible (R), Informed (I), Dynamic Coordinator (D)
Autonomy: L3 (Adaptive with negotiation)
Memory access: STM 전체 읽기/쓰기, LTM 읽기 전용

책임:
- HealthAnalyzer와 BudgetAnalyzer 결과 통합 및 충돌 중재
- 우선순위 기반 협상 전략으로 타협안 생성
- 통합된 메뉴 계획(단위: 한 끼 기준 권장)과 충돌 해결 근거를 반환

출력 형식:
- JSON 스키마: {meal, dish, brief_description, estimated_cost, protein_g}
"""
import os
import json
from typing import Dict, Any
from .base_agent import BaseAgent

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a101_mediator.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class MediatorAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A101", "Menu Planner & Mediator", system_prompt)

    def plan(self, health_result: Dict[str, Any], budget_result: Dict[str, Any], user_req: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "건강 분석과 예산 분석 결과를 통합해 충돌을 검증하고 메뉴 계획을 작성하세요. "
            "우선순위: Hard>의료>예산>선호. JSON으로 응답."
        )
        context = {
            "health_result": health_result,
            "budget_result": budget_result,
            "user_request": user_req
        }
        raw = self.generate_response(prompt, context=context)
        return {"raw": raw}

