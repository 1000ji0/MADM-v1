"""A001: System Orchestrator

RACID: Accountable (A), Dynamic Coordinator (D), Informed (I)
Autonomy: L4 (Self-evaluation and improvement)
Memory access: STM/LTM 전체 읽기/쓰기, 다른 에이전트 메모리 조회 가능

책임:
- 전체 워크플로우 감독, 작업 분배 및 동적 조정
- Health/Budget 분석을 병렬로 위임하고 Menu Planner에 통합 지시
- 충돌 발생 시 우선순위에 따라 최종 중재 및 검증

출력 형식:
- 사용자에게 전달하는 최종 요약(추천 메뉴, 레시피 요약, 재료/비용, 영양 요약, 충돌 근거)
"""
import os
import json
from typing import Dict, Any
from .base_agent import BaseAgent

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a001_orchestrator.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A001", "System Orchestrator", system_prompt)

    def parse_user_request(self, user_input: str) -> Dict[str, Any]:
        prompt = (
            "사용자 요청을 분석하여 목표, 건강 제약, 예산, 선호, 기간을 JSON으로 정리하세요.\n"
            "JSON keys: goal, health_constraints, budget, preferences, duration"
        )
        result = self.generate_response(f"{prompt}\n\n[사용자 입력]\n{user_input}")
        return {"raw": result}

    def final_response(self, menu_plan: Dict[str, Any], recipes: Dict[str, Any], conflicts: Dict[str, Any]) -> str:
        prompt = (
            "다음 정보를 통합하여 최종 응답을 작성하세요.\n"
            "- 추천 메뉴명만 (조리 단계나 상세 레시피는 절대 포함하지 마세요)\n"
            "- 메뉴 선택 이유 (건강/예산/선호 고려사항)\n"
            "- 조리 개요 (간단한 설명만)\n"
            "- 준비 재료 (재료명, 수량, 가격)\n"
            "- 총 예상 비용\n"
            "- 영양 정보 (칼로리, 단백질, GI, 나트륨 등)\n"
            "- 건강 고려사항 (제약 충족 여부 및 근거)\n"
            "- 충돌 해결 내역 (있을 경우만)\n"
            "상세한 조리 단계나 레시피는 절대 포함하지 말고, 한국어로 간결히 정리하세요."
        )
        context = {"menu_plan": menu_plan, "recipes": recipes, "conflicts": conflicts}
        return self.generate_response(prompt, context=context)

