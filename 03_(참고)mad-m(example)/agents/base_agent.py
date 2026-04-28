"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import google.generativeai as genai
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from memory.memory_manager import MemoryManager


class BaseAgent(ABC):
    """Base class for all agents in the MAS."""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        level: int,
        memory_manager: MemoryManager,
        api_key: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.level = level
        self.memory = memory_manager
        
        # Initialize Gemini model
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output."""
        pass
    
    def log(self, message: str, metadata: Optional[Dict] = None):
        """Log message to memory."""
        self.memory.add_dialogue(self.agent_id, message, metadata)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        return f"""You are {self.agent_name} (Agent ID: {self.agent_id}).
Your role is to assist in meal recommendation tasks.
Be concise and focused on your specific responsibilities."""

