"""영양 정보 조회 도구"""
import json
import os
from typing import List, Dict, Any

RAG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag_docs", "nutrition_guide.md")

def _load_basic_db() -> Dict[str, Dict[str, Any]]:
    """간단한 영양 DB (확장 시 교체 가능)"""
    return {
        "밥": {"calories": 300, "carbs": 65, "protein": 6, "fat": 0.5, "sodium": 5},
        "된장찌개": {"calories": 150, "carbs": 8, "protein": 10, "fat": 5, "sodium": 800},
        "김치": {"calories": 25, "carbs": 4, "protein": 1, "fat": 0.2, "sodium": 500},
        "라멘": {"calories": 450, "carbs": 60, "protein": 20, "fat": 12, "sodium": 2000},
        "초밥": {"calories": 200, "carbs": 30, "protein": 15, "fat": 3, "sodium": 400}
    }

def get_nutrition(food_items: List[str]) -> Dict[str, Any]:
    """
    음식 항목들의 영양 정보를 반환합니다.
    """
    db = _load_basic_db()
    result = {"items": [], "total": {"calories": 0, "carbs": 0, "protein": 0, "fat": 0, "sodium": 0}}

    for item in food_items:
        matched = next((k for k in db if k in item or item in k), None)
        info = db.get(matched) or {"calories": 200, "carbs": 30, "protein": 10, "fat": 5, "sodium": 500}
        row = dict(info)
        row["name"] = item
        result["items"].append(row)
        for key in ["calories", "carbs", "protein", "fat", "sodium"]:
            result["total"][key] += row[key]
    return result

