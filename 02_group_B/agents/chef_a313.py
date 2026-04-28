"""A313: Chinese Chef (Budget-Aware)

RACID: Responsible (R), Consulted (C)
Autonomy: L2 (Rule-based execution)
Memory access: STM 읽기, LTM 읽기

책임:
- 예산 제약을 준수하는 중식 레시피 생성 및 비용 최적화

출력 형식:
- JSON 구조: {raw, rag, prices, cost_breakdown}
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from tools import retrieve_recipe, get_market_prices
import os

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a301_a313_chefs.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class ChineseChefBudgetAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A313", "Chinese Chef (Budget)", system_prompt)

    def create_recipe(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        query = requirement.get("menu_name", "저가 중식")
        rag = retrieve_recipe(query, "chinese")
        prices = get_market_prices(["면", "돼지고기", "양파"])
        prompt = "예산 제약을 준수하는 중식 레시피를 JSON으로 작성하세요. 비용 내역과 절감 팁을 포함하세요."
        raw = self.generate_response(prompt, context={"requirement": requirement, "rag": rag, "prices": prices})
        return {"raw": raw, "rag": rag, "prices": prices}

