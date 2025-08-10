#!/usr/bin/env python3
"""Multi-Agent System implementation for coordinated agent execution

This module provides the MultiAgentSystem class that manages multiple agents,
handles their execution, monitors their status, and provides system-level coordination.
"""

import time
import logging
import threading
from datetime import datetime
from typing import List, Dict, Any
from agent_base import BaseAgent
from nlm_interpreter import NLMSession


class MultiAgentSystem:
    """System for managing and executing multiple agents
    
    This class provides a framework for running multiple agents in a coordinated manner,
    whether sequentially or in parallel. It handles system-level state management,
    monitoring, and coordination between agents.
    """
    
    def __init__(self, system_id: str = "default_system", model: str = None):
        """Initialize the multi-agent system
        
        Args:
            system_id: Unique identifier for this system instance
            model: LLM model to use for system session (optional)
        """
        self.system_id = system_id
        self.agents: List[BaseAgent] = []
        self.system_session = NLMSession(namespace=f"system_{system_id}", model=model)
        self.logger = logging.getLogger(f"MultiAgentSystem.{system_id}")
        
        # System state
        self.running = False
        self.start_time = None
        self.agent_threads: Dict[str, threading.Thread] = {}
        
        # Initialize system state
        self._initialize_system_state()
    
    def _initialize_system_state(self):
        """Initialize system-level state variables"""
        # Removed automatic metadata logging (system_id, system_status, system_shutdown)
        # Users can initialize @system_shutdown manually if advanced monitoring is needed
        
        self.logger.info(f"MultiAgentSystem {self.system_id} initialized")
    
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the system
        
        Args:
            agent: Agent instance to add
        """
        self.agents.append(agent)
# Removed automatic agent metadata logging
        
        self.logger.info(f"Added agent {agent.agent_id} (total: {len(self.agents)})")
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the system
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if agent was removed, False if not found
        """
        for i, agent in enumerate(self.agents):
            if agent.agent_id == agent_id:
                del self.agents[i]
# Removed automatic agent metadata logging
                
                self.logger.info(f"Removed agent {agent_id}")
                return True
        
        self.logger.warning(f"Agent {agent_id} not found for removal")
        return False
    
    def get_agent(self, agent_id: str) -> BaseAgent:
        """Get agent by ID
        
        Args:
            agent_id: ID of agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
    
    def run_sequential(self) -> Dict[str, Any]:
        """Run all agents sequentially (one after another)
        
        Returns:
            Dictionary with execution results and statistics
        """
        self.logger.info("Starting sequential agent execution")
        self._set_system_running()
        
        results = {}
        successful = 0
        failed = 0
        
        for agent in self.agents:
            if not self.running:
                self.logger.info("System stop requested, halting sequential execution")
                break
            
            self.logger.info(f"Running agent {agent.agent_id}")
            
            try:
                start_time = time.time()
                agent.run()
                execution_time = time.time() - start_time
                
                results[agent.agent_id] = {
                    "status": "success",
                    "execution_time": execution_time,
                    "final_status": agent.get_status()
                }
                successful += 1
                
                self.logger.info(f"Agent {agent.agent_id} completed successfully in {execution_time:.2f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                results[agent.agent_id] = {
                    "status": "error",
                    "error": str(e),
                    "execution_time": execution_time,
                    "final_status": agent.get_status()
                }
                failed += 1
                
                self.logger.error(f"Agent {agent.agent_id} failed: {e}")
        
        self._set_system_completed()
        
        # Save execution summary
        summary = {
            "execution_mode": "sequential",
            "total_agents": len(self.agents),
            "successful": successful,
            "failed": failed,
            "results": results,
            "system_execution_time": time.time() - self.start_time
        }
        
# Removed automatic execution_summary logging
        return summary
    
    def run_parallel(self, max_concurrent: int = None) -> Dict[str, Any]:
        """Run agents in parallel (simultaneously)
        
        Args:
            max_concurrent: Maximum number of agents to run concurrently (None = no limit)
            
        Returns:
            Dictionary with execution results and statistics
        """
        self.logger.info(f"Starting parallel agent execution (max_concurrent: {max_concurrent})")
        self._set_system_running()
        
        if max_concurrent is None:
            max_concurrent = len(self.agents)
        
        results = {}
        successful = 0
        failed = 0
        
        # Create and start threads for agents
        def run_agent_safe(agent: BaseAgent):
            """Run agent with error handling"""
            try:
                start_time = time.time()
                agent.run()
                execution_time = time.time() - start_time
                
                results[agent.agent_id] = {
                    "status": "success",
                    "execution_time": execution_time,
                    "final_status": agent.get_status()
                }
                
                self.logger.info(f"Agent {agent.agent_id} completed in {execution_time:.2f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                results[agent.agent_id] = {
                    "status": "error",
                    "error": str(e),
                    "execution_time": execution_time,
                    "final_status": agent.get_status()
                }
                
                self.logger.error(f"Agent {agent.agent_id} failed: {e}")
        
        # Start threads for all agents
        threads = []
        for agent in self.agents:
            if not self.running:
                break
            
            thread = threading.Thread(target=run_agent_safe, args=(agent,))
            self.agent_threads[agent.agent_id] = thread
            threads.append(thread)
            thread.start()
            
            self.logger.info(f"Started thread for agent {agent.agent_id}")
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self._set_system_completed()
        
        # Calculate summary
        successful = sum(1 for r in results.values() if r["status"] == "success")
        failed = len(results) - successful
        
        summary = {
            "execution_mode": "parallel",
            "total_agents": len(self.agents),
            "successful": successful,
            "failed": failed,
            "results": results,
            "system_execution_time": time.time() - self.start_time
        }
        
# Removed automatic execution_summary logging
        return summary
    
    # run_monitored() removed - users can implement custom monitoring if needed
    
    def _set_system_running(self):
        """Set system to running state"""
        self.running = True
        self.start_time = time.time()
        # Removed automatic metadata logging (system_status, start_time, system_shutdown)
    
    def _set_system_completed(self):
        """Set system to completed state"""
        self.running = False
# Removed automatic system_status logging
# Removed automatic completion_time logging
        
        total_time = time.time() - self.start_time if self.start_time else 0
# Removed automatic total_execution_time logging
        
        self.logger.info(f"System execution completed in {total_time:.2f}s")
    
    # stop_system() and _stop_all_agents() removed - users can implement if needed
    
    def _get_system_status(self) -> Dict[str, str]:
        """Get status of all agents in the system"""
        status = {}
        for agent in self.agents:
            status[agent.agent_id] = agent.get_status()
        return status
    
    # get_system_info() removed - users can access basic info via len(agents), system_id etc.
    
    # send_broadcast() removed - users can implement custom broadcast if needed
    
    # wait_for_completion() removed - users can implement custom waiting logic if needed
    
    # cleanup(), context manager (__enter__, __exit__), and __repr__() removed for simplicity
    # Users can manage resources manually if needed