"""A101: Menu Planner & Mediator Agent"""
from .base_agent import BaseAgent
from typing import Dict, Any

class MenuPlannerAgent(BaseAgent):
    """메뉴 계획 및 충돌 처리 에이전트"""
    
    def __init__(self):
      system_prompt = """당신은 메뉴 플래너이자 중재자입니다.
    건강 분석과 예산 분석 결과를 취합하여 '한 끼' 기준의 메뉴를 설계합니다.

    지시사항:
    1. 항상 '한 끼(예: 아침/점심/저녁) 기준'으로 계획하세요.
    2. 건강(예: 저염) 및 예산 제약을 우선 고려하세요.
    3. 출력은 매우 간결하게(각 항목 1문장 이내) 작성하세요.

    충돌 처리 규칙: 건강 제약 vs 예산 제약 충돌 시 예산 우선
    """

      super().__init__("A101", "Menu Planner & Mediator", system_prompt)
    
    def plan_menu(self, health_result: Dict[str, Any], budget_result: Dict[str, Any], 
                  user_request: Dict[str, Any]) -> Dict[str, Any]:
        """메뉴 계획 생성"""
        prompt = f"""건강 분석 결과와 예산 분석 결과를 바탕으로 '한 끼' 메뉴를 계획하세요.

건강 분석 결과:
{health_result}

예산 분석 결과:
{budget_result}

사용자 요청:
{user_request}

지침:
1. 한 끼(아침/점심/저녁) 중 하나만 제안하세요.
2. 알레르기/금지 식품은 포함하지 마세요.
3. 응답은 간결하게(핵심만, 1~2문장) 작성하세요.

JSON 형식으로 응답하세요:
{{
  "meal_plan": {{
    "meal": "(예: lunch)",
    "dish": "요리명",
    "brief_description": "한 줄 설명"
  }},
  "conflict_resolution": "충돌 처리 근거",
  "recommended_cuisines": ["한식", "일식"],
  "estimated_cost": "..."
}}"""
        
        response = self.generate_response(prompt)
        return {
            "raw_response": response,
            "health_result": health_result,
            "budget_result": budget_result
        }
    
    def resolve_conflicts(self, conflicts: list) -> str:
        """충돌 해결"""
        prompt = f"""다음 충돌 상황을 해결하세요. 예산 우선 규칙을 적용하세요.

충돌 목록:
{conflicts}

각 충돌에 대해:
1. 충돌 내용 설명
2. 예산 우선 규칙 적용 근거
3. 대체안 제시

명확하게 설명하세요."""
        
        return self.generate_response(prompt)

