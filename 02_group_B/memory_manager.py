"""계층별 메모리 및 접근 제어"""
import json
from typing import Dict, Any
import os

ACCESS_PATH = os.path.join(os.path.dirname(__file__), "config", "access_control.json")


class MemoryManager:
    def __init__(self):
        with open(ACCESS_PATH, "r", encoding="utf-8") as f:
            self.access = json.load(f)
        self.store: Dict[str, Dict[str, Any]] = {
            "DecisionLog": {},
            "HealthContext": {},
            "BudgetContext": {},
            "ConflictLog": {},
            "MenuPlan": {},
            "RecipeCache": {}
        }

    def _can(self, memory: str, agent_id: str, mode: str) -> bool:
        perm = self.access.get(memory, {}).get(agent_id) or self.access.get(memory, {}).get("A301-A313")
        if not perm:
            return False
        if mode == "r":
            return perm in ("r", "rw")
        if mode == "w":
            return perm == "rw"
        return False

    def read(self, memory: str, agent_id: str):
        if not self._can(memory, agent_id, "r"):
            return None
        return self.store.get(memory)

    def write(self, memory: str, agent_id: str, data: Any):
        if not self._can(memory, agent_id, "w"):
            return False
        self.store[memory] = data
        return True

    def append_log(self, memory: str, agent_id: str, key: str, value: Any):
        if not self._can(memory, agent_id, "w"):
            return False
        if memory not in self.store:
            self.store[memory] = {}
        self.store[memory][key] = value
        return True

