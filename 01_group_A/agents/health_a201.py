"""A201: User Preference & Health Analyzer Agent"""
from .base_agent import BaseAgent
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import get_nutrition

class HealthAnalyzerAgent(BaseAgent):
    """건강 및 선호도 분석 에이전트"""
    
    def __init__(self):
        system_prompt = """당신은 건강 및 선호도 분석 전문가입니다.
사용자의 건강 상태, 알레르기, 질환, 영양 목표를 분석하여 식단 제약을 생성합니다.

주요 역할:
1. 알레르기 정보 분석
2. 질환 기반 식단 제약 생성 (저염, 당뇨, 저지방 등)
3. 영양 목표 설정
4. 선호도 파악

분석 항목:
- 알레르기 식품 (절대 금지)
- 질환별 제약 (저염, 저당, 저지방 등)
- 영양 목표 (고단백, 저칼로리 등)
- 선호 음식 유형

도구 사용:
- get_nutrition(): 음식의 영양 정보 조회"""
        
        super().__init__("A201", "User Preference & Health Analyzer", system_prompt)
    
    def analyze_health(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """건강 상태 분석"""
        prompt = f"""사용자 정보를 분석하여 건강 제약을 생성하세요.

사용자 정보:
{user_input}

다음 항목을 분석하세요:
1. 알레르기 식품 (절대 금지 목록)
2. 질환별 제약 (저염, 당뇨, 저지방 등)
3. 영양 목표
4. 선호도

JSON 형식으로 응답하세요:
{{
  "allergies": ["알레르기 식품 목록"],
  "disease_constraints": ["저염", "저당"],
  "nutrition_goals": ["고단백", "저칼로리"],
  "preferences": ["한식", "채소"],
  "restricted_foods": ["금지 식품"],
  "recommended_foods": ["권장 식품"]
}}"""
        
        response = self.generate_response(prompt)
        
        # 영양 정보 조회 (예시)
        if "recommended_foods" in str(response):
            # 실제로는 파싱된 결과에서 추출
            sample_foods = ["밥", "된장찌개"]
            nutrition_info = get_nutrition(sample_foods)
        else:
            nutrition_info = {}
        
        return {
            "raw_response": response,
            "nutrition_info": nutrition_info,
            "user_input": user_input
        }

