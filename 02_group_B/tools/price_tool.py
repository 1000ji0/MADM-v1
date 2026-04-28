"""가격 정보 조회 도구"""
import csv
import os
from typing import List, Dict, Any

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag_docs", "price_table.csv")

def _load_price_db() -> Dict[str, Dict[str, Any]]:
    db: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("재료")
                if not name:
                    continue
                db[name] = {
                    "price": int(row.get("가격(원)", "0")),
                    "unit": row.get("단위", ""),
                    "category": row.get("카테고리", "")
                }
    return db

def get_market_prices(ingredients: List[str]) -> Dict[str, Any]:
    """
    재료들의 시장 가격 정보를 반환합니다.
    """
    db = _load_price_db()
    result = {"ingredients": [], "total_price": 0}
    for ing in ingredients:
        matched = next((k for k in db if k in ing or ing in k), None)
        info = db.get(matched) or {"price": 5000, "unit": "1개", "category": ""}
        row = dict(info)
        row["name"] = ing
        result["ingredients"].append(row)
        result["total_price"] += row["price"]
    return result

