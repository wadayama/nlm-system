#!/usr/bin/env python3
"""Base Agent class for multi-agent system

Provides the foundation for all agent implementations in the NLM system.
Each agent has its own NLM session (namespace) for state management.
"""

from nlm_interpreter import NLMSession
from datetime import datetime
import logging


class BaseAgent:
    """Base class for all agents in the multi-agent system
    
    This class provides the foundation for creating various types of agents.
    Subclasses must implement the run() method to define agent behavior.
    
    Attributes:
        agent_id: Unique identifier for the agent
        session: NLM session for state management and macro execution
        running: Flag to control agent execution
        logger: Logger instance for this agent
    """
    
    def __init__(self, agent_id: str, model: str = None, reasoning_effort: str = "low", verbosity: str = "low"):
        """Initialize the agent
        
        Args:
            agent_id: Unique identifier for the agent (becomes NLM namespace)
            model: LLM model to use (optional, uses default if not specified)
            reasoning_effort: Reasoning level - "low", "medium", "high" (default: "low")
            verbosity: Response verbosity - "low", "medium", "high" (default: "low")
        """
        self.agent_id = agent_id
        self.session = NLMSession(namespace=agent_id, model=model, 
                                 reasoning_effort=reasoning_effort, verbosity=verbosity)
        self.running = False
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
        # Initialize agent state in SQLite
        # Removed automatic metadata logging (agent_id, agent_status, creation_time) to reduce noise
        
        # Initialization logging removed for cleaner output
    
    def run(self):
        """Main execution method for the agent
        
        This method must be implemented by all subclasses.
        It defines the agent's behavior and can be:
        - One-shot: Execute once and return
        - Continuous: Run in a loop until stopped
        
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run() method"
        )
    
    def execute_macro(self, macro_content: str, model: str = None, 
                      reasoning_effort: str = None, verbosity: str = None) -> str:
        """Execute a natural language macro with optional parameter overrides
        
        Args:
            macro_content: The macro content to execute
            model: Optional model override for this execution only
            reasoning_effort: Optional reasoning effort override ("low", "medium", "high")
            verbosity: Optional verbosity override ("low", "medium", "high")
            
        Returns:
            The result of macro execution
        """
        override_info = []
        if model: override_info.append(f"model={model}")
        if reasoning_effort: override_info.append(f"reasoning={reasoning_effort}")
        if verbosity: override_info.append(f"verbosity={verbosity}")
        
        debug_msg = f"Executing macro: {macro_content[:50]}..."
        if override_info:
            debug_msg += f" [overrides: {', '.join(override_info)}]"
        self.logger.debug(debug_msg)
        
        result = self.session.execute(macro_content, model=model, 
                                    reasoning_effort=reasoning_effort, 
                                    verbosity=verbosity)
        # Removed automatic last_macro_time logging to reduce noise
        return result
    
    
    def get_status(self) -> str:
        """Get the current status of this agent
        
        Returns:
            Current agent status
        """
        return self.session.get("agent_status") or "unknown"
    
    def set_status(self, status: str):
        """Set the agent status
        
        Args:
            status: New status to set
        """
        self.session.save("agent_status", status)
        self.session.save("status_update_time", str(datetime.now()))
    
