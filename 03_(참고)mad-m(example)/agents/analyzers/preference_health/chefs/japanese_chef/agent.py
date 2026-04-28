"""A302: Japanese Chef - Japanese recipe generator."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent


class JapaneseChef(BaseAgent):
    """A302: Japanese Chef using few-shot prompting."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A302",
            agent_name="Japanese Chef",
            level=3,
            memory_manager=memory_manager,
            api_key=api_key
        )
        
        self.examples = [
            {
                "input": {"meal_type": "dinner"},
                "output": {
                    "name": "돈부리",
                    "cuisine": "japanese",
                    "ingredients": ["밥", "돼지고기", "양파", "계란"],
                    "instructions": ["밥을 준비한다", "고기를 볶는다", "양파를 볶는다", "계란을 올린다"],
                    "nutrition": {"calories": 550, "protein": 25, "carbs": 60}
                }
            }
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Japanese recipe."""
        requirements = input_data.get("requirements", {})
        
        prompt = f"""You are a Japanese chef. Generate Japanese recipes.

Requirements: {json.dumps(requirements, ensure_ascii=False)}

Return JSON with: name, cuisine: "japanese", ingredients, instructions, nutrition, servings."""
        
        response = self.model.generate_content(prompt)
        
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            menu = json.loads(text.strip())
        except:
            menu = {
                "name": "라멘",
                "cuisine": "japanese",
                "ingredients": ["라면", "계란", "파", "돼지고기"],
                "instructions": ["라면을 끓인다", "토핑을 올린다"],
                "nutrition": {"calories": 480, "protein": 18, "carbs": 55},
                "servings": requirements.get("servings", 2)
            }
        
        self.memory.add_recipe(menu)
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "menu": menu
        }


