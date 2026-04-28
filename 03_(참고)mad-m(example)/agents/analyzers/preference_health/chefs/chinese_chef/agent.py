"""A303: Chinese Chef - Chinese recipe generator."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent


class ChineseChef(BaseAgent):
    """A303: Chinese Chef using few-shot prompting."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A303",
            agent_name="Chinese Chef",
            level=3,
            memory_manager=memory_manager,
            api_key=api_key
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Chinese recipe."""
        requirements = input_data.get("requirements", {})
        
        prompt = f"""You are a Chinese chef. Generate Chinese recipes.

Requirements: {json.dumps(requirements, ensure_ascii=False)}

Return JSON with: name, cuisine: "chinese", ingredients, instructions, nutrition, servings."""
        
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
                "name": "짜장면",
                "cuisine": "chinese",
                "ingredients": ["면", "춘장", "돼지고기", "양파"],
                "instructions": ["면을 삶는다", "춘장을 볶는다", "고기를 볶는다", "면과 함께 볶는다"],
                "nutrition": {"calories": 520, "protein": 22, "carbs": 65},
                "servings": requirements.get("servings", 2)
            }
        
        self.memory.add_recipe(menu)
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "menu": menu
        }


