"""Group A - 멀티 에이전트 식단 추천 시스템 메인"""
import json
import os
from typing import Dict
from agents import (
    OrchestratorAgent,
    MenuPlannerAgent,
    HealthAnalyzerAgent,
    BudgetAnalyzerAgent,
    KoreanChefHealthAgent,
    JapaneseChefHealthAgent,
    ChineseChefHealthAgent,
    KoreanChefBudgetAgent,
    JapaneseChefBudgetAgent,
    ChineseChefBudgetAgent,
)

class MultiAgentSystem:
    """멀티 에이전트 시스템 오케스트레이터"""
    
    def __init__(self):
        # 모든 에이전트 초기화
        self.orchestrator = OrchestratorAgent()
        self.menu_planner = MenuPlannerAgent()
        self.health_analyzer = HealthAnalyzerAgent()
        self.budget_analyzer = BudgetAnalyzerAgent()
        
        # 셰프 에이전트들
        self.chefs_health = {
            'korean': KoreanChefHealthAgent(),
            'japanese': JapaneseChefHealthAgent(),
            'chinese': ChineseChefHealthAgent(),
        }
        
        self.chefs_budget = {
            'korean': KoreanChefBudgetAgent(),
            'japanese': JapaneseChefBudgetAgent(),
            'chinese': ChineseChefBudgetAgent(),
        }
        
        # 사용자 프로필 로드
        self.load_user_profiles()
    
    def load_user_profiles(self):
        """사용자 프로필 로드"""
        profile_path = os.path.join(os.path.dirname(__file__), 'data', 'user_profiles.json')
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                # 모든 에이전트에 프로필 공유 (Group A 특징: 모든 에이전트가 접근 가능)
                for agent in [self.orchestrator, self.menu_planner, self.health_analyzer, 
                             self.budget_analyzer] + list(self.chefs_health.values()) + list(self.chefs_budget.values()):
                    if profiles.get('users'):
                        agent.load_ltm(profiles['users'][0] if profiles['users'] else {})
        except FileNotFoundError:
            pass
    
    def process_request(self, user_input: str) -> Dict:
        """
        사용자 요청 처리
        
        Args:
            user_input: 사용자 입력 문자열
        
        Returns:
            최종 결과 딕셔너리
        """
        print("=" * 60)
        print("멀티 에이전트 식단 추천 시스템 시작")
        print("=" * 60)
        
        # 1. 오케스트레이터: 사용자 요청 파싱
        print("\n[1단계] 사용자 요청 파싱 중...")
        parsed_request = self.orchestrator.parse_user_request(user_input)
        print(f"파싱 결과: {parsed_request.get('raw_response', '')[:100]}...")
        
        # 2. 건강 분석 에이전트
        print("\n[2단계] 건강 분석 중...")
        health_result = self.health_analyzer.analyze_health(parsed_request)
        print(f"건강 분석 완료")
        
        # 3. 예산 분석 에이전트
        print("\n[3단계] 예산 분석 중...")
        budget_result = self.budget_analyzer.analyze_budget(parsed_request)
        print(f"예산 분석 완료")
        
        # 4. 메뉴 플래너: 결과 취합 및 메뉴 계획
        print("\n[4단계] 메뉴 계획 수립 중...")
        menu_plan = self.menu_planner.plan_menu(
            health_result, 
            budget_result, 
            parsed_request
        )
        print(f"메뉴 계획 완료")
        
        # 5. 셰프 에이전트: 레시피 생성
        print("\n[5단계] 레시피 생성 중...")
        recipes = {}
        
        # 메뉴 계획에서 추천 요리 유형 확인 (간단한 추론)
        recommended_cuisines = ['korean', 'japanese', 'chinese']  # 기본값
        
        # 예산 우선 규칙에 따라 예산 셰프 또는 건강 셰프 선택
        # 여기서는 간단히 예산이 낮으면 예산 셰프, 높으면 건강 셰프 사용
        use_budget_chefs = True  # 기본값: 예산 우선
        
        for cuisine in recommended_cuisines[:2]:  # 상위 2개만
            if use_budget_chefs:
                chef = self.chefs_budget[cuisine]
                menu_item = f"{cuisine} 메뉴"
                recipe = chef.create_recipe(menu_item, budget_result)
            else:
                chef = self.chefs_health[cuisine]
                menu_item = f"{cuisine} 메뉴"
                recipe = chef.create_recipe(menu_item, health_result)
            
            recipes[cuisine] = recipe
            print(f"  - {cuisine} 레시피 생성 완료")
        
        # 6. 오케스트레이터: 최종 응답 생성
        print("\n[6단계] 최종 응답 생성 중...")
        final_response = self.orchestrator.create_final_response(menu_plan, recipes)
        
        print("\n" + "=" * 60)
        print("처리 완료!")
        print("=" * 60)
        # 응답 시간 합산
        agents = [self.orchestrator, self.menu_planner, self.health_analyzer, self.budget_analyzer]
        agents += list(self.chefs_health.values()) + list(self.chefs_budget.values())
        total_time = 0.0
        for ag in agents:
            t = getattr(ag, 'get_last_response_time', lambda: None)()
            if t:
                total_time += float(t)

        return {
            'final_response': final_response,
            'menu_plan': menu_plan,
            'recipes': recipes,
            'health_analysis': health_result,
            'budget_analysis': budget_result,
            'total_response_time_seconds': round(total_time, 2)
        }

def main():
    """메인 함수"""
    print("Group A - Google ADK 기반 멀티 에이전트 식단 추천 시스템")
    print("=" * 60)
    
    # 시스템 초기화
    mas = MultiAgentSystem()
    
    # 예시 사용자 입력
    example_input = """
    안녕하세요. 저는 고혈압이 있어서 저염 식단이 필요하고, 
    예산은 1인당 하루 1만원 정도입니다. 
    3일치 식단을 추천해주세요. 한식과 일식을 선호합니다.
    """
    
    print("\n예시 사용자 입력:")
    print(example_input)
    print("\n")
    
    # 사용자 입력 받기
    user_input = input("사용자 요청을 입력하세요 (엔터 시 예시 사용): ").strip()
    if not user_input:
        user_input = example_input
    
    # 요청 처리
    result = mas.process_request(user_input)
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("최종 결과")
    print("=" * 60)
    print(result['final_response'])
    # 총 응답 시간 출력
    total_time = result.get('total_response_time_seconds')
    if total_time is not None:
        print(f"\n총 응답 시간(초): {total_time}")
    
    # 결과 저장 (환경변수로 자동 저장 제어)
    auto_save_env = os.getenv('AUTO_SAVE_RESULTS', '').strip().lower()
    auto_save = False
    if auto_save_env in ('1', 'true', 'yes', 'y'):
        auto_save = True

    if auto_save:
        output_path = os.path.join(os.path.dirname(__file__), 'data', 'result.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"자동 저장: 결과가 {output_path}에 저장되었습니다.")
    else:
        save_result = input("\n결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save_result == 'y':
            output_path = os.path.join(os.path.dirname(__file__), 'data', 'result.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"결과가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()

