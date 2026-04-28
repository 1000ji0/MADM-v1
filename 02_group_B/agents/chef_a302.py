"""A302: Japanese Chef (Health-Aware)

RACID: Responsible (R), Consulted (C)
Autonomy: L2 (Rule-based execution)
Memory access: STM 읽기, LTM 읽기

책임:
- 건강 제약을 준수하는 일식 레시피 생성

출력 형식:
- JSON 구조: {menu_name, constraints_met, ingredients, recipe, nutrition, health_note}
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from tools import retrieve_recipe, get_nutrition
import os

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompt_templates", "a301_a313_chefs.txt")


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class JapaneseChefHealthAgent(BaseAgent):
    def __init__(self):
        system_prompt = _load_prompt(TEMPLATE)
        super().__init__("A302", "Japanese Chef (Health)", system_prompt)

    def create_recipe(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        query = requirement.get("menu_name", "저염 일식")
        rag = retrieve_recipe(query, "japanese")
        prompt = "요구사항을 만족하는 일식 레시피를 JSON으로 작성하세요. 건강 제약을 준수하고 대체재 근거를 포함하세요."
        raw = self.generate_response(prompt, context={"requirement": requirement, "rag": rag})
        nutrition = get_nutrition([query])
        return {"raw": raw, "rag": rag, "nutrition": nutrition}

