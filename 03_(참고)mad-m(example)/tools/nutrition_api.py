"""Nutrition API integration for health analysis."""

from typing import Dict, List, Optional
import requests


class NutritionAPI:
    """API for fetching nutrition information."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.edamam.com/api/nutrition-data"  # Example API
    
    def get_nutrition_info(self, ingredients: List[str]) -> Dict:
        """Get nutrition information for ingredients."""
        # Mock implementation - 실제 API로 교체 가능
        nutrition_data = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "sugar": 0,
            "sodium": 0,
            "ingredients": ingredients
        }
        
        # 간단한 모의 데이터 생성
        for ingredient in ingredients:
            if "쌀" in ingredient or "rice" in ingredient.lower():
                nutrition_data["calories"] += 130
                nutrition_data["carbs"] += 28
            elif "고기" in ingredient or "meat" in ingredient.lower():
                nutrition_data["calories"] += 250
                nutrition_data["protein"] += 25
            elif "야채" in ingredient or "vegetable" in ingredient.lower():
                nutrition_data["calories"] += 25
                nutrition_data["fiber"] += 2
        
        return nutrition_data
    
    def check_health_compatibility(self, nutrition_data: Dict, health_condition: str) -> Dict:
        """Check if nutrition data is compatible with health condition."""
        compatibility = {
            "compatible": True,
            "warnings": [],
            "recommendations": []
        }
        
        if health_condition == "diabetes":
            if nutrition_data.get("sugar", 0) > 20:
                compatibility["compatible"] = False
                compatibility["warnings"].append("당 함량이 높습니다")
            if nutrition_data.get("carbs", 0) > 50:
                compatibility["warnings"].append("탄수화물 함량이 높습니다")
                compatibility["recommendations"].append("탄수화물 섭취량을 줄이는 것을 권장합니다")
        
        elif health_condition == "hypertension":
            if nutrition_data.get("sodium", 0) > 500:
                compatibility["compatible"] = False
                compatibility["warnings"].append("나트륨 함량이 높습니다")
        
        elif health_condition == "obesity":
            if nutrition_data.get("calories", 0) > 600:
                compatibility["warnings"].append("칼로리가 높습니다")
                compatibility["recommendations"].append("저칼로리 옵션을 고려하세요")
        
        return compatibility
    
    def calculate_gi_index(self, ingredients: List[str]) -> float:
        """Calculate glycemic index (모의 구현)."""
        # 실제로는 더 복잡한 계산이 필요
        gi_score = 50.0  # 기본값
        
        for ingredient in ingredients:
            if "쌀" in ingredient or "rice" in ingredient.lower():
                gi_score += 20
            elif "면" in ingredient or "noodle" in ingredient.lower():
                gi_score += 15
            elif "야채" in ingredient or "vegetable" in ingredient.lower():
                gi_score -= 10
        
        return max(0, min(100, gi_score))


