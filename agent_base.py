#!/usr/bin/env python3
"""Base Agent class for multi-agent system

Provides the foundation for all agent implementations in the NLM system.
Each agent has its own NLM session (namespace) for state management and conversation history.
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
    
    def __init__(self, agent_id: str, model: str = None):
        """Initialize the agent
        
        Args:
            agent_id: Unique identifier for the agent (becomes NLM namespace)
            model: LLM model to use (optional, uses default if not specified)
        """
        self.agent_id = agent_id
        self.session = NLMSession(namespace=agent_id, model=model)
        self.running = False
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
        # Initialize agent state in SQLite
        self.session.save("agent_id", agent_id)
        self.session.save("agent_status", "initialized")
        self.session.save("creation_time", str(datetime.now()))
        
        self.logger.info(f"Agent {agent_id} initialized")
    
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
    
    def execute_macro(self, macro_content: str) -> str:
        """Execute a natural language macro
        
        Args:
            macro_content: The macro content to execute
            
        Returns:
            The result of macro execution
        """
        self.logger.debug(f"Executing macro: {macro_content[:50]}...")
        result = self.session.execute(macro_content)
        self.session.save("last_macro_time", str(datetime.now()))
        return result
    
    def stop(self):
        """Stop the agent gracefully"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self.running = False
        self.session.save("agent_status", "stopping")
        self.session.save("stop_time", str(datetime.now()))
    
    # === Communication Methods ===
    
    def send_message(self, target_agent: str, message: str):
        """Send a message to another agent
        
        Messages are stored as global variables that can be accessed by the target agent.
        Each message gets a unique timestamp-based ID to prevent overwrites.
        
        Args:
            target_agent: ID of the target agent
            message: Message content to send
        """
        import time
        # Use timestamp with microseconds to ensure uniqueness
        timestamp = datetime.now()
        msg_id = str(int(time.time() * 1000000))  # Microsecond precision
        msg_key = f"msg_{self.agent_id}_to_{target_agent}_{msg_id}"
        
        self.session.save(f"@{msg_key}", message)
        self.session.save(f"@{msg_key}_timestamp", str(timestamp))
        self.logger.info(f"Sent message to {target_agent}: {message[:50]}...")
    
    def check_messages(self) -> list:
        """Check for messages sent to this agent
        
        Returns:
            List of message dictionaries with 'from', 'message', and 'timestamp' keys
        """
        messages = []
        all_globals = self.session.list_global()
        
        # Look for messages addressed to this agent
        # Pattern: msg_sender_to_receiver_msgid
        target_pattern = f"_to_{self.agent_id}_"
        for key, value in all_globals.items():
            if target_pattern in key and key.startswith("msg_") and not key.endswith("_timestamp"):
                # Parse the key: msg_sender_to_receiver_msgid
                parts = key.split("_")
                if len(parts) >= 5:  # msg, sender, to, receiver, msgid
                    sender = parts[1]
                    
                    # Get timestamp if available
                    timestamp_key = f"{key}_timestamp"
                    timestamp = all_globals.get(timestamp_key, "unknown")
                    
                    messages.append({
                        "from": sender,
                        "message": value,
                        "timestamp": timestamp
                    })
        
        # Sort messages by timestamp if possible
        try:
            messages.sort(key=lambda x: x["timestamp"])
        except:
            pass  # If timestamps can't be sorted, keep original order
        
        if messages:
            self.logger.info(f"Found {len(messages)} messages")
        
        return messages
    
    def clear_messages(self):
        """Clear all messages sent to this agent"""
        all_globals = self.session.list_global()
        target_pattern = f"_to_{self.agent_id}_"
        
        for key in list(all_globals.keys()):
            if target_pattern in key and key.startswith("msg_"):
                self.session.delete(f"@{key}")
        
        self.logger.info("Cleared all messages")
    
    # === State Management Methods ===
    
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
    
    def get_agent_status(self, agent_id: str) -> str:
        """Get the status of another agent
        
        Args:
            agent_id: ID of the agent to check
            
        Returns:
            Status of the specified agent or "unknown" if not found
        """
        # Access another agent's namespace directly
        status = self.session.variable_db.get_variable(f"{agent_id}:agent_status")
        return status if status else "unknown"
    
    def wait_for_global(self, key: str, expected_value: str, max_attempts: int = 30) -> bool:
        """Wait for a global variable to reach an expected value
        
        Args:
            key: Global variable name (without @ prefix)
            expected_value: The value to wait for
            max_attempts: Maximum number of attempts (default 30)
            
        Returns:
            True if the expected value was reached, False if timeout
        """
        import time
        
        for attempt in range(max_attempts):
            current_value = self.session.get(f"@{key}")
            if current_value == expected_value:
                self.logger.debug(f"Global variable @{key} reached expected value: {expected_value}")
                return True
            
            self.logger.debug(f"Waiting for @{key} to become {expected_value} (attempt {attempt + 1}/{max_attempts})")
            time.sleep(1.0)
        
        self.logger.warning(f"Timeout waiting for @{key} to become {expected_value}")
        return False
    
    # === Utility Methods ===
    
    def log_activity(self, activity: str):
        """Log an activity with timestamp
        
        Args:
            activity: Description of the activity
        """
        self.session.save("last_activity", activity)
        self.session.save("last_activity_time", str(datetime.now()))
        self.logger.info(f"Activity: {activity}")
    
    def get_runtime_info(self) -> dict:
        """Get runtime information about this agent
        
        Returns:
            Dictionary containing runtime information
        """
        info = {
            "agent_id": self.agent_id,
            "agent_class": self.__class__.__name__,
            "status": self.get_status(),
            "running": self.running,
            "creation_time": self.session.get("creation_time"),
            "last_activity": self.session.get("last_activity"),
            "last_activity_time": self.session.get("last_activity_time")
        }
        
        # Add stop time if agent was stopped
        stop_time = self.session.get("stop_time")
        if stop_time:
            info["stop_time"] = stop_time
        
        return info
    
    def __repr__(self):
        """String representation of the agent"""
        return f"{self.__class__.__name__}(agent_id='{self.agent_id}', status='{self.get_status()}')"