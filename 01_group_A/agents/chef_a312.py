"""A312: Japanese Chef (Budget-Aware)"""
from .base_agent import BaseAgent
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import retrieve_recipe, get_market_prices

class JapaneseChefBudgetAgent(BaseAgent):
    """예산 조건 기반 일식 레시피 생성 셰프"""
    
    def __init__(self):
        system_prompt = """당신은 일식 레시피를 매우 잘 아는 요리사입니다.
예산 조건을 고려하여 경제적인 일식 레시피를 작성합니다.

주요 역할:
1. 예산 제약을 고려한 일식 레시피 생성
2. 가격 효율적인 재료 선택
3. 예산 내 최적 메뉴 추천
4. 비용 절감 조리법 제안

도구 사용:
- retrieve_recipe(): RAG에서 레시피 검색
- get_market_prices(): 재료 가격 확인"""
        
        super().__init__("A312", "Japanese Chef (Budget-Aware)", system_prompt)
    
    def create_recipe(self, menu_item: str, budget_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """예산 조건 기반 레시피 생성"""
        # RAG에서 레시피 검색
        rag_result = retrieve_recipe(f"예산 {menu_item}", cuisine_type='japanese')
        
        prompt = f"""다음 메뉴에 대한 예산 조건을 고려한 일식 레시피를 작성하세요.

메뉴: {menu_item}

예산 제약:
{budget_constraints}

참고 레시피 (RAG 검색 결과):
{rag_result}

레시피 작성 시:
1. 예산 제약을 반드시 반영
2. 가격 효율적인 재료 선택
3. 대체 재료 제안 (비슷한 맛, 낮은 가격)
4. 조리 순서를 명확히 설명
5. 비용 절감 팁 포함

다음 형식으로 작성하세요:
{{
  "menu_name": "{menu_item}",
  "cuisine_type": "일식",
  "budget_focus": true,
  "ingredients": ["재료 목록"],
  "steps": ["조리 순서"],
  "estimated_cost": "예상 비용",
  "cost_saving_tips": "비용 절감 팁"
}}"""
        
        response = self.generate_response(prompt)
        
        # 가격 정보 조회
        sample_ingredients = ["면", "계란", "대파"]
        price_info = get_market_prices(sample_ingredients)
        
        return {
            "raw_response": response,
            "rag_result": rag_result,
            "price_info": price_info
        }

