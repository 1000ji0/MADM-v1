"""Price API integration for market and budget analysis."""

from typing import Dict, List, Optional
from datetime import datetime


class PriceAPI:
    """API for fetching market prices and cost evaluation."""
    
    def __init__(self):
        # 모의 가격 데이터베이스
        self.price_db = {
            "쌀": 5000,  # per kg
            "rice": 5000,
            "고기": 15000,  # per kg
            "meat": 15000,
            "닭고기": 8000,
            "chicken": 8000,
            "돼지고기": 12000,
            "pork": 12000,
            "소고기": 30000,
            "beef": 30000,
            "생선": 10000,
            "fish": 10000,
            "야채": 3000,  # per kg
            "vegetable": 3000,
            "양파": 2000,
            "onion": 2000,
            "마늘": 5000,
            "garlic": 5000,
            "고추장": 3000,
            "gochujang": 3000,
            "된장": 4000,
            "doenjang": 4000,
            "간장": 2000,
            "soy_sauce": 2000,
        }
    
    def get_ingredient_price(self, ingredient: str, quantity: float = 1.0) -> float:
        """Get price for an ingredient."""
        # 간단한 매칭 로직
        ingredient_lower = ingredient.lower()
        for key, price in self.price_db.items():
            if key.lower() in ingredient_lower:
                return price * quantity
        return 2000  # 기본 가격
    
    def calculate_recipe_cost(self, ingredients: List[Dict[str, any]]) -> Dict:
        """Calculate total cost for a recipe."""
        total_cost = 0
        ingredient_costs = []
        
        for ingredient in ingredients:
            name = ingredient.get("name", "")
            quantity = ingredient.get("quantity", 1.0)
            unit = ingredient.get("unit", "kg")
            
            # 단위 변환 (간단한 예시)
            if unit == "g":
                quantity = quantity / 1000
            elif unit == "ml":
                quantity = quantity / 1000
            
            price = self.get_ingredient_price(name, quantity)
            total_cost += price
            ingredient_costs.append({
                "ingredient": name,
                "quantity": quantity,
                "unit": unit,
                "price": price
            })
        
        return {
            "total_cost": round(total_cost, 2),
            "ingredient_costs": ingredient_costs,
            "currency": "KRW",
            "calculated_at": datetime.now().isoformat()
        }
    
    def get_market_trends(self, ingredient: str) -> Dict:
        """Get market price trends (모의 구현)."""
        base_price = self.get_ingredient_price(ingredient)
        return {
            "ingredient": ingredient,
            "current_price": base_price,
            "trend": "stable",  # stable, increasing, decreasing
            "price_change_percent": 0.0,
            "seasonal_factor": 1.0
        }
    
    def suggest_budget_alternatives(self, target_budget: float, current_cost: float) -> List[Dict]:
        """Suggest alternatives to meet budget constraints."""
        suggestions = []
        
        if current_cost > target_budget:
            savings_needed = current_cost - target_budget
            suggestions.append({
                "type": "substitute",
                "message": f"예산을 {savings_needed:.0f}원 절감하기 위해 일부 재료를 대체할 수 있습니다",
                "options": [
                    "고급 재료를 일반 재료로 대체",
                    "계절 재료 활용",
                    "대량 구매 할인 활용"
                ]
            })
        
        return suggestions
    
    def estimate_serving_cost(self, total_cost: float, servings: int) -> float:
        """Estimate cost per serving."""
        return round(total_cost / max(servings, 1), 2)


