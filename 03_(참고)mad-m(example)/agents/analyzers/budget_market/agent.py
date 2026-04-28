"""A202: Budget & Market Analyzer."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent
from tools.price_api import PriceAPI


class BudgetMarketAnalyzer(BaseAgent):
    """A202: Analyzes budget and market prices using CoT + Self-Refine."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A202",
            agent_name="Budget & Market Analyzer",
            level=2,
            memory_manager=memory_manager,
            api_key=api_key
        )
        self.price_api = PriceAPI()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process budget and market analysis."""
        user_request = input_data.get("user_request", "")
        user_profile = input_data.get("user_profile", {})
        
        self.log("Analyzing budget and market conditions")
        
        # CoT Step 1: Extract budget information
        budget_info = self._extract_budget_info(user_request, user_profile)
        
        # CoT Step 2: Analyze market prices
        market_analysis = self._analyze_market(budget_info)
        
        # CoT Step 3: Calculate cost estimates
        cost_estimate = self._estimate_costs(budget_info, market_analysis)
        
        # Self-Refine: Optimize within budget
        optimized = self._optimize_budget(cost_estimate, budget_info)
        
        # Update LTM
        if user_profile.get("user_id"):
            self.memory.update_budget_pattern(
                user_profile["user_id"],
                optimized
            )
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "budget_limit": budget_info.get("budget_limit"),
            "budget_range": budget_info.get("budget_range"),
            "market_analysis": market_analysis,
            "estimated_cost": cost_estimate.get("total_cost", 0),
            "within_budget": optimized.get("within_budget", True),
            "suggestions": optimized.get("suggestions", [])
        }
    
    def _extract_budget_info(self, user_request: str, user_profile: Dict) -> Dict:
        """Extract budget information from request."""
        prompt = f"""Extract budget-related information:

User Request: {user_request}
User Profile: {json.dumps(user_profile, ensure_ascii=False)}

Identify:
1. Budget limit mentioned
2. Number of servings
3. Meal type
4. Any cost constraints

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
            budget_limit = None
            if "원" in user_request or "won" in user_request.lower():
                # Extract number before 원
                import re
                numbers = re.findall(r'\d+', user_request)
                if numbers:
                    budget_limit = int(numbers[0])
            
            return {
                "budget_limit": budget_limit or user_profile.get("budget_range", {}).get("max", 20000),
                "budget_range": user_profile.get("budget_range", {"min": 5000, "max": 20000}),
                "servings": 2,
                "meal_type": "dinner"
            }
    
    def _analyze_market(self, budget_info: Dict) -> Dict:
        """Analyze market prices."""
        # Use price API to get market trends
        common_ingredients = ["쌀", "고기", "야채", "양파"]
        trends = {}
        
        for ingredient in common_ingredients:
            trends[ingredient] = self.price_api.get_market_trends(ingredient)
        
        return {
            "trends": trends,
            "market_status": "stable",
            "seasonal_factors": {}
        }
    
    def _estimate_costs(self, budget_info: Dict, market_analysis: Dict) -> Dict:
        """Estimate costs for typical meal."""
        # Sample ingredients for cost estimation
        sample_ingredients = [
            {"name": "쌀", "quantity": 0.2, "unit": "kg"},
            {"name": "고기", "quantity": 0.3, "unit": "kg"},
            {"name": "야채", "quantity": 0.2, "unit": "kg"},
            {"name": "양파", "quantity": 0.1, "unit": "kg"}
        ]
        
        cost_result = self.price_api.calculate_recipe_cost(sample_ingredients)
        servings = budget_info.get("servings", 2)
        cost_per_serving = self.price_api.estimate_serving_cost(
            cost_result["total_cost"], servings
        )
        
        return {
            "total_cost": cost_result["total_cost"],
            "cost_per_serving": cost_per_serving,
            "ingredient_costs": cost_result["ingredient_costs"],
            "servings": servings
        }
    
    def _optimize_budget(self, cost_estimate: Dict, budget_info: Dict) -> Dict:
        """Self-Refine: Optimize to fit budget."""
        budget_limit = budget_info.get("budget_limit", float('inf'))
        total_cost = cost_estimate.get("total_cost", 0)
        
        within_budget = total_cost <= budget_limit
        
        suggestions = []
        if not within_budget:
            suggestions = self.price_api.suggest_budget_alternatives(
                budget_limit, total_cost
            )
        
        return {
            "within_budget": within_budget,
            "current_cost": total_cost,
            "budget_limit": budget_limit,
            "suggestions": suggestions,
            "optimization_needed": not within_budget
        }


