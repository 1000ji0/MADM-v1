"""영양 정보 조회 도구"""
import json
import os
from typing import List, Dict, Any

def get_nutrition(food_items: List[str]) -> Dict[str, Any]:
    """
    음식 항목들의 영양 정보를 반환합니다.
    
    Args:
        food_items: 음식 항목 리스트 (예: ['밥', '된장찌개', '김치'])
    
    Returns:
        영양 정보 딕셔너리 (칼로리, 탄수화물, 단백질, 지방, 나트륨 등)
    """
    # 가상 데이터 - 실제로는 API나 DB에서 조회
    nutrition_db = {
        '밥': {'calories': 300, 'carbs': 65, 'protein': 6, 'fat': 0.5, 'sodium': 5},
        '된장찌개': {'calories': 150, 'carbs': 8, 'protein': 10, 'fat': 5, 'sodium': 800},
        '김치': {'calories': 25, 'carbs': 4, 'protein': 1, 'fat': 0.2, 'sodium': 500},
        '불고기': {'calories': 250, 'carbs': 5, 'protein': 25, 'fat': 12, 'sodium': 600},
        '비빔밥': {'calories': 400, 'carbs': 70, 'protein': 15, 'fat': 8, 'sodium': 1000},
        '초밥': {'calories': 200, 'carbs': 30, 'protein': 15, 'fat': 3, 'sodium': 400},
        '라멘': {'calories': 450, 'carbs': 60, 'protein': 20, 'fat': 12, 'sodium': 2000},
        '돈까스': {'calories': 350, 'carbs': 25, 'protein': 20, 'fat': 18, 'sodium': 500},
        '짜장면': {'calories': 500, 'carbs': 80, 'protein': 15, 'fat': 15, 'sodium': 1500},
        '탕수육': {'calories': 400, 'carbs': 40, 'protein': 25, 'fat': 20, 'sodium': 800},
        '마파두부': {'calories': 200, 'carbs': 10, 'protein': 12, 'fat': 10, 'sodium': 1200},
    }
    
    result = {
        'items': [],
        'total': {'calories': 0, 'carbs': 0, 'protein': 0, 'fat': 0, 'sodium': 0}
    }
    
    for item in food_items:
        # 키워드 매칭 (부분 일치)
        matched = None
        for key in nutrition_db.keys():
            if key in item or item in key:
                matched = key
                break
        
        if matched:
            nutrition = nutrition_db[matched].copy()
            nutrition['name'] = item
            result['items'].append(nutrition)
            # 총합 계산
            for key in ['calories', 'carbs', 'protein', 'fat', 'sodium']:
                result['total'][key] += nutrition[key]
        else:
            # 기본값 (알 수 없는 음식)
            default_nutrition = {
                'name': item,
                'calories': 200,
                'carbs': 30,
                'protein': 10,
                'fat': 5,
                'sodium': 500
            }
            result['items'].append(default_nutrition)
            for key in ['calories', 'carbs', 'protein', 'fat', 'sodium']:
                result['total'][key] += default_nutrition[key]
    
    return result

