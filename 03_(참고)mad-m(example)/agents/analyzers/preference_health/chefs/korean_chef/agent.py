"""A301: Korean Chef - Korean recipe generator."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent


class KoreanChef(BaseAgent):
    """A301: Korean Chef using few-shot prompting."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A301",
            agent_name="Korean Chef",
            level=3,
            memory_manager=memory_manager,
            api_key=api_key
        )
        
        # Few-shot examples
        self.examples = [
            {
                "input": {"meal_type": "dinner", "health": "diabetes"},
                "output": {
                    "name": "잡채",
                    "cuisine": "korean",
                    "ingredients": ["당면", "시금치", "당근", "버섯"],
                    "instructions": ["당면을 삶는다", "야채를 볶는다", "양념을 만든다", "모두 섞는다"],
                    "nutrition": {"calories": 350, "carbs": 45, "protein": 12}
                }
            },
            {
                "input": {"meal_type": "lunch", "health": "hypertension"},
                "output": {
                    "name": "된장찌개",
                    "cuisine": "korean",
                    "ingredients": ["된장", "두부", "호박", "양파"],
                    "instructions": ["물을 끓인다", "된장을 풀어 넣는다", "재료를 넣고 끓인다"],
                    "nutrition": {"calories": 280, "sodium": 400, "protein": 15}
                }
            }
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Korean recipe using few-shot prompting."""
        requirements = input_data.get("requirements", {})
        cuisine = input_data.get("cuisine", "korean")
        
        self.log(f"Generating {cuisine} recipe")
        
        # Few-shot prompt
        prompt = self._build_few_shot_prompt(requirements)
        
        response = self.model.generate_content(prompt)
        
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            menu = json.loads(text.strip())
        except:
            # Fallback menu
            menu = {
                "name": "김치찌개",
                "cuisine": "korean",
                "ingredients": ["김치", "돼지고기", "두부", "대파"],
                "instructions": ["김치를 볶는다", "고기를 넣고 볶는다", "물을 넣고 끓인다", "두부를 넣는다"],
                "nutrition": {"calories": 420, "protein": 20, "carbs": 35},
                "servings": requirements.get("servings", 2)
            }
        
        # Store recipe in LTM
        self.memory.add_recipe(menu)
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "menu": menu
        }
    
    def _build_few_shot_prompt(self, requirements: Dict) -> str:
        """Build few-shot prompt with examples."""
        examples_text = "\n\n".join([
            f"Example {i+1}:\nInput: {json.dumps(ex['input'], ensure_ascii=False)}\nOutput: {json.dumps(ex['output'], ensure_ascii=False)}"
            for i, ex in enumerate(self.examples)
        ])
        
        prompt = f"""You are a Korean chef. Generate Korean recipes based on requirements.

{examples_text}

Now generate a Korean recipe for:
Requirements: {json.dumps(requirements, ensure_ascii=False)}

Return a JSON object with:
- name: recipe name
- cuisine: "korean"
- ingredients: list of ingredients
- instructions: list of cooking steps
- nutrition: nutrition information
- servings: number of servings

JSON format only:"""
        
        return prompt


