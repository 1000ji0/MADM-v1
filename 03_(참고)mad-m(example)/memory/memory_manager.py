"""Memory Manager for STM and LTM management."""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class MemoryManager:
    """Manages Short-Term Memory (STM) and Long-Term Memory (LTM)."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # STM: Session-based temporary memory
        self.stm: Dict[str, Any] = {
            "dialogue_context": [],
            "temporary_menu_list": []
        }
        
        # LTM: Persistent memory
        self.ltm_path = self.data_dir / "ltm.json"
        self.ltm: Dict[str, Any] = self._load_ltm()
        
    def _load_ltm(self) -> Dict[str, Any]:
        """Load Long-Term Memory from disk."""
        if self.ltm_path.exists():
            with open(self.ltm_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "user_profiles": {},
            "preference_history": [],
            "budget_patterns": {},
            "recipe_database": []
        }
    
    def _save_ltm(self):
        """Save Long-Term Memory to disk."""
        with open(self.ltm_path, 'w', encoding='utf-8') as f:
            json.dump(self.ltm, f, ensure_ascii=False, indent=2)
    
    # STM Operations
    def add_dialogue(self, agent_id: str, message: str, metadata: Optional[Dict] = None):
        """Add dialogue context to STM."""
        self.stm["dialogue_context"].append({
            "agent_id": agent_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
    
    def get_dialogue_context(self, limit: int = 10) -> List[Dict]:
        """Get recent dialogue context."""
        return self.stm["dialogue_context"][-limit:]
    
    def add_temporary_menu(self, menu: Dict):
        """Add temporary menu to STM."""
        self.stm["temporary_menu_list"].append({
            **menu,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_temporary_menus(self) -> List[Dict]:
        """Get temporary menu list."""
        return self.stm["temporary_menu_list"]
    
    def clear_stm(self):
        """Clear Short-Term Memory (called at session end)."""
        self.stm = {
            "dialogue_context": [],
            "temporary_menu_list": []
        }
    
    # LTM Operations
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from LTM."""
        return self.ltm["user_profiles"].get(user_id)
    
    def update_user_profile(self, user_id: str, profile: Dict):
        """Update user profile in LTM."""
        if user_id not in self.ltm["user_profiles"]:
            self.ltm["user_profiles"][user_id] = {}
        self.ltm["user_profiles"][user_id].update(profile)
        self.ltm["user_profiles"][user_id]["last_updated"] = datetime.now().isoformat()
        self._save_ltm()
    
    def add_preference(self, user_id: str, preference: Dict):
        """Add preference to history."""
        self.ltm["preference_history"].append({
            "user_id": user_id,
            **preference,
            "timestamp": datetime.now().isoformat()
        })
        self._save_ltm()
    
    def get_preference_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get preference history for user."""
        history = [p for p in self.ltm["preference_history"] if p.get("user_id") == user_id]
        return history[-limit:]
    
    def update_budget_pattern(self, user_id: str, pattern: Dict):
        """Update budget pattern for user."""
        if user_id not in self.ltm["budget_patterns"]:
            self.ltm["budget_patterns"][user_id] = []
        self.ltm["budget_patterns"][user_id].append({
            **pattern,
            "timestamp": datetime.now().isoformat()
        })
        self._save_ltm()
    
    def get_budget_pattern(self, user_id: str) -> Optional[Dict]:
        """Get latest budget pattern for user."""
        patterns = self.ltm["budget_patterns"].get(user_id, [])
        return patterns[-1] if patterns else None
    
    def add_recipe(self, recipe: Dict):
        """Add recipe to database."""
        self.ltm["recipe_database"].append({
            **recipe,
            "added_at": datetime.now().isoformat()
        })
        self._save_ltm()
    
    def get_recipes(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get recipes from database with optional filters."""
        recipes = self.ltm["recipe_database"]
        if filters:
            for key, value in filters.items():
                recipes = [r for r in recipes if r.get(key) == value]
        return recipes
    
    # Access Control Simulation
    def can_access(self, agent_id: str, memory_type: str, operation: str = "read") -> bool:
        """Check if agent can access specific memory."""
        access_rules = {
            "A001": {
                "stm": ["read", "write"],
                "ltm": ["read", "write"]
            },
            "A101": {
                "stm": ["read", "write"],
                "ltm": ["read"]
            },
            "A201": {
                "stm": ["read"],
                "ltm": {"user_profiles": ["read", "write"], "preference_history": ["read", "write"]}
            },
            "A202": {
                "stm": ["read"],
                "ltm": {"budget_patterns": ["read", "write"]}
            },
            "A301": {"ltm": {"recipe_database": ["read"]}},
            "A302": {"ltm": {"recipe_database": ["read"]}},
            "A303": {"ltm": {"recipe_database": ["read"]}}
        }
        
        agent_rules = access_rules.get(agent_id, {})
        if memory_type == "stm":
            return operation in agent_rules.get("stm", [])
        elif memory_type == "ltm":
            ltm_rules = agent_rules.get("ltm", [])
            if isinstance(ltm_rules, list):
                return operation in ltm_rules
            # For specific LTM sections
            return True  # Simplified for now
        return False


