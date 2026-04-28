"""A301: Korean Chef (Health-Aware)"""
from .base_agent import BaseAgent
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import retrieve_recipe, get_nutrition

class KoreanChefHealthAgent(BaseAgent):
    """건강 조건 기반 한식 레시피 생성 셰프"""
    
    def __init__(self):
        system_prompt = """당신은 한식 레시피를 매우 잘 아는 요리사입니다.
사용자의 건강 제약을 고려하여 한식 레시피를 작성합니다.

주요 역할:
1. 건강 제약을 고려한 한식 레시피 생성
2. 저염, 저당, 저지방 등 건강 조건 반영
3. 알레르기 식품 제외
4. 영양 균형 고려

도구 사용:
- retrieve_recipe(): RAG에서 레시피 검색
- get_nutrition(): 영양 정보 확인"""
        
        super().__init__("A301", "Korean Chef (Health-Aware)", system_prompt)
    
    def create_recipe(self, menu_item: str, health_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """건강 조건 기반 레시피 생성"""
        # RAG에서 레시피 검색
        rag_result = retrieve_recipe(f"저염 {menu_item}", cuisine_type='korean')
        
        prompt = f"""다음 메뉴에 대한 건강 조건을 고려한 한식 레시피를 작성하세요.

메뉴: {menu_item}

건강 제약:
{health_constraints}

참고 레시피 (RAG 검색 결과):
{rag_result}

레시피 작성 시:
1. 건강 제약을 반드시 반영
2. 저염, 저당, 저지방 조리법 사용
3. 알레르기 식품 절대 사용 금지
4. 조리 순서를 명확히 설명
5. 영양 정보 고려

다음 형식으로 작성하세요:
{{
  "menu_name": "{menu_item}",
  "cuisine_type": "한식",
  "health_focus": true,
  "ingredients": ["재료 목록"],
  "steps": ["조리 순서"],
  "nutrition_notes": "영양 정보",
  "health_modifications": "건강 조정 사항"
}}"""
        
        response = self.generate_response(prompt)
        
        # 영양 정보 조회
        nutrition_info = get_nutrition([menu_item])
        
        return {
            "raw_response": response,
            "rag_result": rag_result,
            "nutrition_info": nutrition_info
        }

