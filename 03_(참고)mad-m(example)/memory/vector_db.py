"""Vector database for preference recall using embeddings."""

from typing import List, Dict, Optional
import json
import numpy as np
from pathlib import Path


class VectorDB:
    """Simple vector database for preference similarity search."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.vectors_path = self.data_dir / "vectors.json"
        self.vectors: List[Dict] = []
        self._load_vectors()
    
    def _load_vectors(self):
        """Load vectors from disk."""
        if self.vectors_path.exists():
            with open(self.vectors_path, 'r', encoding='utf-8') as f:
                self.vectors = json.load(f)
    
    def _save_vectors(self):
        """Save vectors to disk."""
        with open(self.vectors_path, 'w', encoding='utf-8') as f:
            json.dump(self.vectors, f, ensure_ascii=False, indent=2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    
    def add_preference(self, user_id: str, preference_text: str, embedding: List[float], metadata: Optional[Dict] = None):
        """Add preference with embedding."""
        self.vectors.append({
            "user_id": user_id,
            "preference_text": preference_text,
            "embedding": embedding,
            "metadata": metadata or {}
        })
        self._save_vectors()
    
    def search_similar(self, query_embedding: List[float], user_id: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """Search for similar preferences."""
        results = []
        for vec_data in self.vectors:
            if user_id and vec_data["user_id"] != user_id:
                continue
            similarity = self._cosine_similarity(query_embedding, vec_data["embedding"])
            results.append({
                **vec_data,
                "similarity": similarity
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get_user_preferences(self, user_id: str) -> List[Dict]:
        """Get all preferences for a user."""
        return [v for v in self.vectors if v["user_id"] == user_id]


