"""A101: Menu Planner & Mediator - Conflict resolver and menu generator."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent
from agents.analyzers.preference_health.chefs.korean_chef.agent import KoreanChef
from agents.analyzers.preference_health.chefs.japanese_chef.agent import JapaneseChef
from agents.analyzers.preference_health.chefs.chinese_chef.agent import ChineseChef


class MenuPlanner(BaseAgent):
    """A101: Menu Planner using Chain of Thought reasoning."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A101",
            agent_name="Menu Planner & Mediator",
            level=1,
            memory_manager=memory_manager,
            api_key=api_key
        )
        
        # Initialize chef agents
        self.chefs = {
            "korean": KoreanChef(memory_manager, api_key),
            "japanese": JapaneseChef(memory_manager, api_key),
            "chinese": ChineseChef(memory_manager, api_key)
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process menu planning request using CoT."""
        user_request = input_data.get("user_request", "")
        preference_analysis = input_data.get("preference_analysis", {})
        budget_analysis = input_data.get("budget_analysis", {})
        user_profile = input_data.get("user_profile", {})
        
        self.log("Starting menu planning process")
        
        # Chain of Thought: Step 1 - Understand requirements
        requirements = self._analyze_requirements(
            user_request, preference_analysis, budget_analysis
        )
        
        # Chain of Thought: Step 2 - Select cuisine
        cuisine = self._select_cuisine(requirements, user_profile)
        
        # Chain of Thought: Step 3 - Generate menu
        menu = self._generate_menu(cuisine, requirements)
        
        # Chain of Thought: Step 4 - Validate and refine
        validated_menu = self._validate_menu(menu, requirements)
        
        # Store in STM
        self.memory.add_temporary_menu(validated_menu)
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "menu": validated_menu,
            "rationale": f"Selected {cuisine} cuisine based on preferences and budget",
            "requirements": requirements
        }
    
    def _analyze_requirements(self, user_request: str, preference_analysis: Dict, budget_analysis: Dict) -> Dict:
        """CoT Step 1: Analyze requirements."""
        prompt = f"""Analyze the requirements for menu planning:

User Request: {user_request}
Preference Analysis: {json.dumps(preference_analysis, ensure_ascii=False)}
Budget Analysis: {json.dumps(budget_analysis, ensure_ascii=False)}

Extract key requirements:
1. Meal type (breakfast, lunch, dinner)
2. Cuisine preference
3. Health constraints
4. Budget constraints
5. Number of servings

Return JSON format:"""
        
        response = self.model.generate_content(prompt)
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            return {
                "meal_type": "dinner",
                "cuisine": "korean",
                "health_constraints": preference_analysis.get("health_conditions", []),
                "budget_limit": budget_analysis.get("budget_limit", 20000),
                "servings": 2
            }
    
    def _select_cuisine(self, requirements: Dict, user_profile: Dict) -> str:
        """CoT Step 2: Select appropriate cuisine."""
        cuisine_pref = requirements.get("cuisine") or user_profile.get("cuisine_preferences", ["korean"])[0]
        
        # Normalize cuisine name
        cuisine_map = {
            "korean": "korean",
            "한국": "korean",
            "japanese": "japanese",
            "일본": "japanese",
            "chinese": "chinese",
            "중국": "chinese"
        }
        
        for key, value in cuisine_map.items():
            if key.lower() in str(cuisine_pref).lower():
                return value
        
        return "korean"  # default
    
    def _generate_menu(self, cuisine: str, requirements: Dict) -> Dict:
        """CoT Step 3: Generate menu using chef agent."""
        chef = self.chefs.get(cuisine, self.chefs["korean"])
        
        menu_result = chef.process({
            "requirements": requirements,
            "cuisine": cuisine
        })
        
        return menu_result.get("menu", {})
    
    def _validate_menu(self, menu: Dict, requirements: Dict) -> Dict:
        """CoT Step 4: Validate menu against requirements."""
        prompt = f"""Validate the generated menu against requirements:

Menu: {json.dumps(menu, ensure_ascii=False)}
Requirements: {json.dumps(requirements, ensure_ascii=False)}

Check:
1. Does it meet health constraints?
2. Does it fit budget?
3. Does it match cuisine preference?
4. Are all ingredients available?

Return validated menu with adjustments if needed (JSON format):"""
        
        response = self.model.generate_content(prompt)
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            validated = json.loads(text.strip())
            return validated.get("menu", menu)
        except:
            return menu


