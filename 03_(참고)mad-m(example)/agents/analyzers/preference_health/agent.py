"""A201: User Preference & Health Analyzer."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent
from tools.nutrition_api import NutritionAPI


class PreferenceHealthAnalyzer(BaseAgent):
    """A201: Analyzes user preferences and health conditions using CoT + Self-Refine."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A201",
            agent_name="User Preference & Health Analyzer",
            level=2,
            memory_manager=memory_manager,
            api_key=api_key
        )
        self.nutrition_api = NutritionAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process preference and health analysis."""
        user_request = input_data.get("user_request", "")
        user_profile = input_data.get("user_profile", {})
        
        self.log("Analyzing user preferences and health conditions")
        
        # CoT Step 1: Extract health information
        health_info = self._extract_health_info(user_request, user_profile)
        
        # CoT Step 2: Analyze preferences
        preferences = self._analyze_preferences(user_request, user_profile)
        
        # CoT Step 3: Check compatibility
        compatibility = self._check_compatibility(health_info, preferences)
        
        # Self-Refine: Refine analysis
        refined_analysis = self._refine_analysis(health_info, preferences, compatibility)
        
        # Update LTM
        if user_profile.get("user_id"):
            self.memory.add_preference(
                user_profile["user_id"],
                refined_analysis
            )
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "health_conditions": health_info.get("conditions", []),
            "preferences": preferences,
            "compatible": compatibility.get("compatible", True),
            "warnings": compatibility.get("warnings", []),
            "recommendations": compatibility.get("recommendations", []),
            "recommended_cuisine": preferences.get("cuisine"),
            "estimated_cost": preferences.get("estimated_cost", 0)
        }
    
    def _extract_health_info(self, user_request: str, user_profile: Dict) -> Dict:
        """Extract health information from request and profile."""
        prompt = f"""Extract health-related information:

User Request: {user_request}
User Profile: {json.dumps(user_profile, ensure_ascii=False)}

Identify:
1. Health conditions mentioned (diabetes, hypertension, obesity, etc.)
2. Dietary restrictions
3. Nutritional requirements
4. Any health-related constraints

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
            # Fallback extraction
            conditions = []
            if "당뇨" in user_request or "diabetes" in user_request.lower():
                conditions.append("diabetes")
            if "고혈압" in user_request or "hypertension" in user_request.lower():
                conditions.append("hypertension")
            if "비만" in user_request or "obesity" in user_request.lower():
                conditions.append("obesity")
            
            return {
                "conditions": conditions or user_profile.get("health_conditions", []),
                "dietary_restrictions": user_profile.get("dietary_restrictions", []),
                "nutritional_requirements": []
            }
    
    def _analyze_preferences(self, user_request: str, user_profile: Dict) -> Dict:
        """Analyze user preferences."""
        prompt = f"""Analyze user preferences from request and profile:

User Request: {user_request}
User Profile: {json.dumps(user_profile, ensure_ascii=False)}

Extract:
1. Cuisine preference
2. Meal type preference
3. Flavor preferences
4. Ingredient preferences
5. Estimated cost range

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
                "cuisine": "korean",
                "meal_type": "dinner",
                "flavor": "balanced",
                "ingredients": [],
                "estimated_cost": 15000
            }
    
    def _check_compatibility(self, health_info: Dict, preferences: Dict) -> Dict:
        """Check compatibility between health and preferences."""
        conditions = health_info.get("conditions", [])
        
        if not conditions:
            return {"compatible": True, "warnings": [], "recommendations": []}
        
        # Use nutrition API to check
        ingredients = preferences.get("ingredients", [])
        nutrition_data = self.nutrition_api.get_nutrition_info(ingredients)
        
        compatibility = {"compatible": True, "warnings": [], "recommendations": []}
        
        for condition in conditions:
            check_result = self.nutrition_api.check_health_compatibility(
                nutrition_data, condition
            )
            if not check_result["compatible"]:
                compatibility["compatible"] = False
            compatibility["warnings"].extend(check_result.get("warnings", []))
            compatibility["recommendations"].extend(check_result.get("recommendations", []))
        
        return compatibility
    
    def _refine_analysis(self, health_info: Dict, preferences: Dict, compatibility: Dict) -> Dict:
        """Self-Refine: Improve analysis based on compatibility."""
        if compatibility["compatible"]:
            return {
                **preferences,
                "health_aware": True,
                "refined": True
            }
        
        # Refine preferences to be more health-compatible
        prompt = f"""Refine preferences to be more health-compatible:

Health Info: {json.dumps(health_info, ensure_ascii=False)}
Original Preferences: {json.dumps(preferences, ensure_ascii=False)}
Compatibility Issues: {json.dumps(compatibility, ensure_ascii=False)}

Suggest refined preferences that address compatibility issues while maintaining user preferences as much as possible.

Return JSON format:"""
        
        response = self.model.generate_content(prompt)
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            refined = json.loads(text.strip())
            return {**preferences, **refined, "refined": True}
        except:
            return preferences


