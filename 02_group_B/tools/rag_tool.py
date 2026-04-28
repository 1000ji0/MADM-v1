"""RAG 기반 레시피 검색 도구"""
import json
import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAG_DIR = os.path.join(BASE_DIR, "rag_docs")

FILE_MAP = {
    "korean": "recipes_ko.json",
    "japanese": "recipes_jp.json",
    "chinese": "recipes_cn.json"
}

def _load_recipes(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def retrieve_recipe(query: str, cuisine_type: str = "korean") -> Dict[str, Any]:
    """단순 키워드 기반 레시피 검색"""
    recipe_file = FILE_MAP.get(cuisine_type, "recipes_ko.json")
    recipe_path = os.path.join(RAG_DIR, recipe_file)
    if not os.path.exists(recipe_path):
        return {"error": f"레시피 파일을 찾을 수 없습니다: {recipe_path}"}

    recipes = _load_recipes(recipe_path)
    query_lower = query.lower()
    matched = []
    for r in recipes:
        score = 0
        title = r.get("title", "").lower()
        desc = r.get("description", "").lower()
        tags = " ".join(r.get("tags", [])).lower()
        for token in query_lower.split():
            if token in title:
                score += 5
            if token in desc:
                score += 2
            if token in tags:
                score += 2
        if score > 0:
            r_copy = dict(r)
            r_copy["match_score"] = score
            matched.append(r_copy)
    matched.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {"query": query, "count": len(matched), "recipes": matched[:3]}

