"""A202: Budget & Market Analyzer Agent"""
from .base_agent import BaseAgent
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import get_market_prices

class BudgetAnalyzerAgent(BaseAgent):
    """예산 및 시장 분석 에이전트"""
    
    def __init__(self):
        system_prompt = """당신은 예산 및 시장 분석 전문가입니다.
사용자의 예산 한도를 분석하고 가격대비 효율적인 재료를 추천하며 예산 내 식단 계획을 짜고 장보기 계획을 수립합니다.

분석 항목:
- 총 예산
- 식사 횟수
- 인당 예산 계산
- 재료별 가격 정보
- 예산 대비 최적 메뉴 추천

도구 사용:
- get_market_prices(): 재료 가격 정보 조회"""
        
        super().__init__("A202", "Budget & Market Analyzer", system_prompt)
    
    def analyze_budget(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """예산 분석"""
        prompt = f"""사용자 예산 정보를 분석하세요.

사용자 정보:
{user_input}

다음 항목을 분석하세요:
1. 총 예산
2. 식사 기간 및 횟수
3. 인당 예산
4. 예산 대비 추천 메뉴
5. 가격 효율적인 재료 추천

JSON 형식으로 응답하세요:
{{
  "total_budget": "...",
  "meals_count": "...",
  "budget_per_meal": "...",
  "recommended_ingredients": ["재료 목록"],
  "budget_category": "저예산/중예산/고예산",
  "shopping_plan": {{
    "ingredients": ["재료", "가격"],
    "total_cost": "..."
  }}
}}"""
        
        response = self.generate_response(prompt)
        
        # 가격 정보 조회 (예시)
        sample_ingredients = ["쌀", "된장", "두부"]
        price_info = get_market_prices(sample_ingredients)
        
        return {
            "raw_response": response,
            "price_info": price_info,
            "user_input": user_input
        }

