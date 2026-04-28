"""A311: Korean Chef (Budget-Aware)

RACID: Responsible (R), Consulted (C)
Autonomy: L2 (Rule-based execution)
Memory access: STM 읽기, LTM 읽기

책임:
- 예산 제약을 준수하는 한식 레시피 생성 및 비용 최적화

출력 형식:
- JSON 구조: {raw, rag, prices, cost_breakdown}
"""
from typing import Dict, Any
import json
from .base_agent import BaseAgent
from tools import retrieve_recipe, get_market_prices
import os

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a301_a313_chefs.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class KoreanChefBudgetAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A311", "Korean Chef (Budget)", system_prompt)

    def create_recipe(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        query = requirement.get("menu_name", "저가 한식")
        rag = retrieve_recipe(query, "korean")
        prices = get_market_prices(["쌀", "된장", "두부"])
        prompt = (
            "다음 요구사항으로 예산 제약을 준수하는 한식 레시피를 반드시 JSON으로 출력하세요."
            " 출력 JSON은 최소한 'ingredients', 'instructions', 'cost_breakdown' 필드를 포함해야 합니다."
            " 'cost_breakdown'이 없다면 도구에서 제공한 가격으로 계산할 것입니다."
        )
        raw = self.generate_response(prompt, context={"requirement": requirement, "rag": rag, "prices": prices})

        # 모델이 JSON을 반환했는지 시도해서 파싱합니다.
        parsed = None
        cost_breakdown = None
        try:
            parsed = json.loads(raw)
            cost_breakdown = parsed.get("cost_breakdown")
        except Exception:
            parsed = None

        # 모델 출력에 cost_breakdown이 없으면 tools.get_market_prices 결과로 기본 집계 생성
        if not cost_breakdown:
            # prices 형식: {"ingredients": [{"name":..., "price":...}, ...], "total_price": N}
            by_item = []
            total = 0
            for item in prices.get("ingredients", []):
                by_item.append({"name": item.get("name"), "unit": item.get("unit"), "price": item.get("price")})
                try:
                    total += int(item.get("price", 0))
                except Exception:
                    pass
            cost_breakdown = {"estimated_total": prices.get("total_price", total), "by_item": by_item}

        return {"raw": raw, "parsed": parsed, "rag": rag, "prices": prices, "cost_breakdown": cost_breakdown}

