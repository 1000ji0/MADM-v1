"""A001: System Orchestrator Agent"""
from typing import Dict
from .base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    """전체 흐름을 제어하는 오케스트레이터 에이전트"""
    
    def __init__(self):
        system_prompt = """당신은 식단 추천 시스템의 오케스트레이터입니다.
    전체 작업 흐름을 제어하고 다른 에이전트들에게 작업을 분배합니다. 단, 모든 요청은 '한 끼' 기준으로 처리합니다.

    작업 흐름(한 끼 기준):
    1. 사용자 입력 파싱 (한 끼 요청인지 확인)
    2. 건강 분석 에이전트(A201) 호출
    3. 예산 분석 에이전트(A202) 호출
    4. 메뉴 플래너(A101)에게 결과 전달
    5. 셰프 에이전트들에게 간결한 1인분 레시피 요청
    6. 최종 결과 통합 및 출력

    항상 간결하고 실행 가능한 형식으로 응답하세요 (한 끼 기준)."""
        
        super().__init__("A001", "System Orchestrator", system_prompt)
    
    def parse_user_request(self, user_input: str) -> Dict:
        """사용자 요청 파싱"""
        prompt = f"""사용자 요청을 분석하여 다음 정보를 추출하세요:
- 목표 (식단 목적)
- 건강 제약 (알레르기, 질환, 영양 목표)
- 예산 제약
- 선호도 (음식 유형, 맛 등)
- 기간 (몇 일치 식단인지)

JSON 형식으로 응답하세요:
{{
  "goal": "...",
  "health_constraints": [...],
  "budget": "...",
  "preferences": [...],
  "duration": "..."
}}"""
        
        response = self.generate_response(prompt)
        # 간단한 파싱 (실제로는 JSON 파싱 필요)
        return {
            "raw_response": response,
            "user_input": user_input
        }
    
    def create_final_response(self, menu_plan: Dict, recipes: Dict) -> str:
        """최종 응답 생성"""
        prompt = f"""다음 정보를 바탕으로 사용자에게 '한 끼' 최종 응답을 생성하세요:

    메뉴 계획:
    {menu_plan}

    레시피 정보:
    {recipes}

    요구사항:
    1. 한 끼(아침/점심/저녁) 기준으로 추천 메뉴를 한 줄로 요약하세요.
    2. 레시피는 1인분 기준, 재료 목록과 3단계 이내의 조리 순서로 간결히 제시하세요.
    3. 재료 리스트와 대략 비용 추정(한 끼 기준)을 포함하세요.
    4. 영양 요약은 핵심 지표만 포함하세요.

    간결하고 실용적으로 작성하세요."""
        
        return self.generate_response(prompt)

