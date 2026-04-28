"""Group B - MADM 기반 멀티 에이전트 시스템"""
import json
import os
from agents import (
    OrchestratorAgent,
    MediatorAgent,
    HealthAnalyzerAgent,
    BudgetAnalyzerAgent,
    KoreanChefHealthAgent,
    JapaneseChefHealthAgent,
    ChineseChefHealthAgent,
    KoreanChefBudgetAgent,
    JapaneseChefBudgetAgent,
    ChineseChefBudgetAgent,
)
from memory_manager import MemoryManager


def load_user_profiles():
    path = os.path.join(os.path.dirname(__file__), "data", "user_profiles.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": []}


class MADMSystem:
    def __init__(self):
        self.mem = MemoryManager()
        self.a001 = OrchestratorAgent()
        self.a101 = MediatorAgent()
        self.a201 = HealthAnalyzerAgent()
        self.a202 = BudgetAnalyzerAgent()
        self.chefs_health = {
            "korean": KoreanChefHealthAgent(),
            "japanese": JapaneseChefHealthAgent(),
            "chinese": ChineseChefHealthAgent()
        }
        self.chefs_budget = {
            "korean": KoreanChefBudgetAgent(),
            "japanese": JapaneseChefBudgetAgent(),
            "chinese": ChineseChefBudgetAgent()
        }
        profiles = load_user_profiles()
        if profiles.get("users"):
            for agent in [self.a001, self.a101, self.a201, self.a202, *self.chefs_health.values(), *self.chefs_budget.values()]:
                agent.load_ltm(profiles["users"][0])

    def run(self, user_input: str):
        print("[1단계] 요청 파싱...")
        parsed = self.a001.parse_user_request(user_input)

        print("[2단계] 건강 분석...")
        health = self.a201.analyze(user_input)

        print("[3단계] 예산 분석...")
        budget = self.a202.analyze(user_input)

        print("[4단계] 중재/메뉴 계획...")
        plan = self.a101.plan(health, budget, parsed)

        print("[5단계] 레시피 생성...")
        recipes = {}
        for cuisine, chef in list(self.chefs_budget.items())[:2]:
            req = {"menu_name": f"{cuisine} 메뉴", "constraints": {"budget": budget, "health": health}}
            recipes[cuisine] = chef.create_recipe(req)

        print("[6단계] 최종 응답...")
        final = self.a001.final_response(plan, recipes, conflicts={"raw": plan.get("raw")})
        # 응답 시간 합산
        agents = [self.a001, self.a101, self.a201, self.a202]
        agents += list(self.chefs_health.values()) + list(self.chefs_budget.values())
        total_time = 0.0
        for ag in agents:
            t = getattr(ag, 'get_last_response_time', lambda: None)()
            if t is not None:
                try:
                    total_time += float(t)
                except Exception:
                    pass

        return {
            "parse": parsed,
            "health": health,
            "budget": budget,
            "plan": plan,
            "recipes": recipes,
            "final": final,
            "total_response_time_seconds": round(total_time, 2)
        }


def main():
    print("Group B - MADM 멀티 에이전트 시스템")
    example = (
        "안녕하세요. 고혈압이 있어 저염 식단이 필요하고 1일 예산은 1만원입니다. "
        "3일치 한식/일식 식단을 추천해주세요."
    )
    user_input = input("요청을 입력하세요 (엔터 시 예시 사용): ").strip() or example
    system = MADMSystem()
    result = system.run(user_input)
    print("\n=== 최종 결과 ===")
    print(result["final"])
    # 총 응답 시간 출력
    total_time = result.get('total_response_time_seconds')
    if total_time is not None:
        print(f"\n총 응답 시간(초): {total_time}")
    out = os.path.join(os.path.dirname(__file__), "data", "result.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"자동 저장 완료: {out}")


if __name__ == "__main__":
    main()

