"""RAG 기반 레시피 검색 도구"""
import json
import os
from typing import Dict, Any, List

def retrieve_recipe(query: str, cuisine_type: str = None) -> Dict[str, Any]:
    """
    RAG 문서에서 레시피를 검색합니다.
    
    Args:
        query: 검색 쿼리 (예: "저염 된장찌개", "예산 한식")
        cuisine_type: 요리 유형 ('korean', 'japanese', 'chinese')
    
    Returns:
        레시피 정보 딕셔너리
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rag_dir = os.path.join(base_dir, 'rag_docs')
    
    # 요리 유형에 따라 파일 선택
    if cuisine_type == 'korean' or '한식' in query or '한국' in query:
        recipe_file = os.path.join(rag_dir, 'recipes_ko.json')
    elif cuisine_type == 'japanese' or '일식' in query or '일본' in query:
        recipe_file = os.path.join(rag_dir, 'recipes_jp.json')
    elif cuisine_type == 'chinese' or '중식' in query or '중국' in query:
        recipe_file = os.path.join(rag_dir, 'recipes_cn.json')
    else:
        # 기본값: 한식
        recipe_file = os.path.join(rag_dir, 'recipes_ko.json')
    
    # 파일 읽기
    try:
        with open(recipe_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
    except FileNotFoundError:
        return {'error': f'레시피 파일을 찾을 수 없습니다: {recipe_file}'}
    
    # 키워드 기반 검색 (간단한 매칭)
    query_lower = query.lower()
    matched_recipes = []
    
    for recipe in recipes:
        score = 0
        # 제목 매칭
        if 'title' in recipe:
            title_lower = recipe['title'].lower()
            if any(keyword in title_lower for keyword in query_lower.split()):
                score += 10
        # 설명 매칭
        if 'description' in recipe:
            desc_lower = recipe['description'].lower()
            if any(keyword in desc_lower for keyword in query_lower.split()):
                score += 5
        # 태그 매칭
        if 'tags' in recipe:
            for tag in recipe['tags']:
                if tag.lower() in query_lower:
                    score += 3
        
        if score > 0:
            recipe['match_score'] = score
            matched_recipes.append(recipe)
    
    # 점수 순으로 정렬
    matched_recipes.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    # 상위 3개 반환
    return {
        'query': query,
        'count': len(matched_recipes),
        'recipes': matched_recipes[:3]
    }

