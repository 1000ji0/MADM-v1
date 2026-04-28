"""가격 정보 조회 도구"""
import json
import os
from typing import List, Dict, Any

def get_market_prices(ingredients: List[str]) -> Dict[str, Any]:
    """
    재료들의 시장 가격 정보를 반환합니다.
    
    Args:
        ingredients: 재료 리스트 (예: ['쌀', '된장', '두부', '돼지고기'])
    
    Returns:
        가격 정보 딕셔너리 (재료별 가격 및 총액)
    """
    # 가상 가격 데이터 (단위: 원)
    price_db = {
        '쌀': {'price': 15000, 'unit': '1kg'},
        '된장': {'price': 5000, 'unit': '500g'},
        '두부': {'price': 2000, 'unit': '1팩'},
        '돼지고기': {'price': 12000, 'unit': '100g'},
        '소고기': {'price': 20000, 'unit': '100g'},
        '닭고기': {'price': 8000, 'unit': '100g'},
        '김치': {'price': 8000, 'unit': '1kg'},
        '배추': {'price': 3000, 'unit': '1포기'},
        '고추장': {'price': 4000, 'unit': '500g'},
        '간장': {'price': 3000, 'unit': '500ml'},
        '마늘': {'price': 5000, 'unit': '100g'},
        '생강': {'price': 4000, 'unit': '100g'},
        '대파': {'price': 2000, 'unit': '1단'},
        '양파': {'price': 2000, 'unit': '1kg'},
        '당근': {'price': 3000, 'unit': '1kg'},
        '계란': {'price': 6000, 'unit': '10개'},
        '생선': {'price': 15000, 'unit': '1마리'},
        '새우': {'price': 18000, 'unit': '200g'},
        '면': {'price': 3000, 'unit': '1인분'},
        '라면': {'price': 1500, 'unit': '1봉'},
    }
    
    result = {
        'ingredients': [],
        'total_price': 0
    }
    
    for ingredient in ingredients:
        # 키워드 매칭
        matched = None
        for key in price_db.keys():
            if key in ingredient or ingredient in key:
                matched = key
                break
        
        if matched:
            price_info = price_db[matched].copy()
            price_info['name'] = ingredient
            result['ingredients'].append(price_info)
            result['total_price'] += price_info['price']
        else:
            # 기본값 (알 수 없는 재료)
            default_price = {
                'name': ingredient,
                'price': 5000,
                'unit': '1개'
            }
            result['ingredients'].append(default_price)
            result['total_price'] += default_price['price']
    
    return result

