"""A001: System Orchestrator - Top-level planner and decision maker."""

from typing import Dict, Any, Optional
import json
from agents.base_agent import BaseAgent
from agents.menu_planner.agent import MenuPlanner
from agents.analyzers.preference_health.agent import PreferenceHealthAnalyzer
from agents.analyzers.budget_market.agent import BudgetMarketAnalyzer


class SystemOrchestrator(BaseAgent):
    """A001: System Orchestrator with ReAct-based reasoning."""
    
    def __init__(self, memory_manager, api_key: Optional[str] = None):
        super().__init__(
            agent_id="A001",
            agent_name="System Orchestrator",
            level=0,
            memory_manager=memory_manager,
            api_key=api_key
        )
        
        # Initialize sub-agents
        self.menu_planner = MenuPlanner(memory_manager, api_key)
        self.preference_analyzer = PreferenceHealthAnalyzer(memory_manager, api_key)
        self.budget_analyzer = BudgetMarketAnalyzer(memory_manager, api_key)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user request using ReAct pattern."""
        user_request = input_data.get("user_request", "")
        user_id = input_data.get("user_id", "default_user")
        
        self.log(f"Received user request: {user_request}")
        
        # Step 1: Load user profile from LTM
        user_profile = self.memory.get_user_profile(user_id)
        if not user_profile:
            user_profile = self._create_default_profile(user_id)
        
        # Step 2: ReAct reasoning cycle
        thought = self._think(user_request, user_profile)
        self.log(f"Thought: {thought}")
        
        # Step 3: Plan task decomposition
        plan = self._plan(user_request, user_profile)
        self.log(f"Plan: {json.dumps(plan, ensure_ascii=False)}")
        
        # Step 4: Execute parallel analysis
        preference_result = self.preference_analyzer.process({
            "user_request": user_request,
            "user_profile": user_profile
        })
        
        budget_result = self.budget_analyzer.process({
            "user_request": user_request,
            "user_profile": user_profile
        })
        
        # Step 5: Check for conflicts and arbitrate
        conflicts = self._detect_conflicts(preference_result, budget_result)
        if conflicts:
            resolution = self._arbitrate(conflicts, preference_result, budget_result)
            self.log(f"Conflict resolved: {resolution}")
        
        # Step 6: Delegate to menu planner
        menu_result = self.menu_planner.process({
            "user_request": user_request,
            "preference_analysis": preference_result,
            "budget_analysis": budget_result,
            "user_profile": user_profile
        })
        
        # Step 7: Make final decision
        final_decision = self._make_decision(menu_result, preference_result, budget_result)
        
        return {
            "agent_id": self.agent_id,
            "status": "success",
            "final_menu": final_decision,
            "preference_analysis": preference_result,
            "budget_analysis": budget_result,
            "reasoning": thought
        }
    
    def _think(self, user_request: str, user_profile: Dict) -> str:
        """ReAct: Think step."""
        prompt = f"""Analyze the user request and determine what needs to be done.

User Request: {user_request}
User Profile: {json.dumps(user_profile, ensure_ascii=False)}

Think step by step:
1. What is the user asking for?
2. What information do we need?
3. What agents should be involved?
4. What are the potential constraints?

Provide your reasoning:"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _plan(self, user_request: str, user_profile: Dict) -> Dict:
        """Create execution plan."""
        prompt = f"""Create a structured plan for handling this meal recommendation request.

User Request: {user_request}
User Profile: {json.dumps(user_profile, ensure_ascii=False)}

Return a JSON plan with:
- tasks: list of tasks to execute
- agents: list of agents to involve
- constraints: list of constraints to consider
- expected_output: what we expect to produce

Format as JSON only:"""
        
        response = self.model.generate_content(prompt)
        try:
            # Extract JSON from response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            return {
                "tasks": ["analyze_preferences", "analyze_budget", "generate_menu"],
                "agents": ["A201", "A202", "A101"],
                "constraints": [],
                "expected_output": "personalized_menu"
            }
    
    def _create_default_profile(self, user_id: str) -> Dict:
        """Create default user profile."""
        profile = {
            "user_id": user_id,
            "preferences": [],
            "health_conditions": [],
            "budget_range": {"min": 5000, "max": 20000},
            "dietary_restrictions": [],
            "cuisine_preferences": ["korean", "japanese", "chinese"]
        }
        self.memory.update_user_profile(user_id, profile)
        return profile
    
    def _detect_conflicts(self, preference_result: Dict, budget_result: Dict) -> list:
        """Detect conflicts between preference and budget analysis."""
        conflicts = []
        
        if preference_result.get("recommended_cuisine") and budget_result.get("budget_constraint"):
            pref_cost = preference_result.get("estimated_cost", 0)
            budget_limit = budget_result.get("budget_limit", float('inf'))
            if pref_cost > budget_limit:
                conflicts.append({
                    "type": "cost_conflict",
                    "message": "선호 요리의 예상 비용이 예산을 초과합니다"
                })
        
        return conflicts
    
    def _arbitrate(self, conflicts: list, preference_result: Dict, budget_result: Dict) -> Dict:
        """Arbitrate conflicts."""
        prompt = f"""Resolve conflicts in meal recommendation:

Conflicts: {json.dumps(conflicts, ensure_ascii=False)}
Preference Analysis: {json.dumps(preference_result, ensure_ascii=False)}
Budget Analysis: {json.dumps(budget_result, ensure_ascii=False)}

Provide a resolution that balances preferences and budget constraints.
Return JSON with:
- resolution: description of how to resolve
- adjustments: what needs to be adjusted
- final_recommendation: the balanced recommendation"""
        
        response = self.model.generate_content(prompt)
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            return {
                "resolution": "Adjust menu to fit budget while maintaining preferences",
                "adjustments": ["reduce_portion", "substitute_ingredients"],
                "final_recommendation": "balanced_menu"
            }
    
    def _make_decision(self, menu_result: Dict, preference_result: Dict, budget_result: Dict) -> Dict:
        """Make final decision on menu."""
        return {
            "menu": menu_result.get("menu", {}),
            "rationale": menu_result.get("rationale", ""),
            "meets_preferences": preference_result.get("compatible", True),
            "meets_budget": budget_result.get("within_budget", True),
            "total_cost": budget_result.get("estimated_cost", 0)
        }


