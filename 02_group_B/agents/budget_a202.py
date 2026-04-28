"""A202: Budget & Market Analyzer

RACID: Responsible (R), Consulted (C)
Autonomy: L3 (Adaptive optimization)
Memory access: STM 읽기/쓰기, LTM 읽기

책임:
- 예산 제약 분석, 가격 정보 조회 및 가성비 최적화 전략 제시
- 대량 구매/계절성/재고 고려한 구매 계획 수립

출력 형식:
- JSON 구조: {budget_summary, cost_effective_items, bulk_purchase_strategy, daily_allocation}
"""
import os
from typing import Dict, Any
from .base_agent import BaseAgent
from tools import get_market_prices

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a202_budget.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class BudgetAnalyzerAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A202", "Budget Analyzer", system_prompt)

    def analyze(self, user_input: str) -> Dict[str, Any]:
        prompt = "예산, 기간, 인원, 식사 횟수를 추정하고 장보기 계획을 JSON으로 작성하세요."
        raw = self.generate_response(prompt, context={"user_input": user_input})
        prices = get_market_prices(["쌀", "된장", "두부"])
        return {"raw": raw, "price_info": prices}

