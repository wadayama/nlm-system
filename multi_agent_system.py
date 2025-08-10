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
    
    def __init__(self, system_id: str = "default_system"):
        """Initialize the multi-agent system
        
        Args:
            system_id: Unique identifier for this system instance
        """
        self.system_id = system_id
        self.agents: List[BaseAgent] = []
        self.system_session = NLMSession(namespace=f"system_{system_id}")
        self.logger = logging.getLogger(f"MultiAgentSystem.{system_id}")
        
        # System state
        self.running = False
        self.start_time = None
        self.agent_threads: Dict[str, threading.Thread] = {}
        
        # Initialize system state
        self._initialize_system_state()
    
    def _initialize_system_state(self):
        """Initialize system-level state variables"""
        self.system_session.save("system_id", self.system_id)
        self.system_session.save("system_status", "initialized")
        self.system_session.save("creation_time", str(datetime.now()))
        self.system_session.save("agent_count", "0")
        self.system_session.save("@system_shutdown", "false")
        
        self.logger.info(f"MultiAgentSystem {self.system_id} initialized")
    
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the system
        
        Args:
            agent: Agent instance to add
        """
        self.agents.append(agent)
        self.system_session.save("agent_count", str(len(self.agents)))
        
        # Log agent addition
        agent_list = [a.agent_id for a in self.agents]
        self.system_session.save("agent_list", ",".join(agent_list))
        
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
                self.system_session.save("agent_count", str(len(self.agents)))
                
                agent_list = [a.agent_id for a in self.agents]
                self.system_session.save("agent_list", ",".join(agent_list))
                
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
        
        self.system_session.save("execution_summary", str(summary))
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
        
        self.system_session.save("execution_summary", str(summary))
        return summary
    
    def run_monitored(self, check_interval: float = 5.0, max_runtime: float = 300.0) -> Dict[str, Any]:
        """Run agents with monitoring and automatic management
        
        Args:
            check_interval: Seconds between monitoring checks
            max_runtime: Maximum total runtime in seconds
            
        Returns:
            Dictionary with execution results and statistics
        """
        self.logger.info(f"Starting monitored execution (check_interval: {check_interval}s, max_runtime: {max_runtime}s)")
        self._set_system_running()
        
        # Start all agents in parallel
        def run_agent_monitored(agent: BaseAgent):
            try:
                agent.run()
            except Exception as e:
                self.logger.error(f"Agent {agent.agent_id} error: {e}")
                agent.set_status("error")
        
        # Start threads
        threads = []
        for agent in self.agents:
            thread = threading.Thread(target=run_agent_monitored, args=(agent,))
            self.agent_threads[agent.agent_id] = thread
            threads.append(thread)
            thread.start()
        
        # Monitoring loop
        monitoring_start = time.time()
        while self.running and (time.time() - monitoring_start) < max_runtime:
            
            # Check agent statuses
            status_report = self._get_system_status()
            self.logger.debug(f"System status: {status_report}")
            
            # Check if all agents are done
            all_done = all(not thread.is_alive() for thread in threads)
            if all_done:
                self.logger.info("All agents completed")
                break
            
            # Check for system stop signals
            if self.system_session.get("@system_shutdown") == "true":
                self.logger.info("System shutdown requested")
                self._stop_all_agents()
                break
            
            # Wait before next check
            time.sleep(check_interval)
        
        # Ensure all threads are finished
        for thread in threads:
            if thread.is_alive():
                self.logger.warning(f"Waiting for thread to complete...")
                thread.join(timeout=10)
        
        self._set_system_completed()
        
        # Generate final report
        final_status = self._get_system_status()
        summary = {
            "execution_mode": "monitored",
            "total_agents": len(self.agents),
            "monitoring_duration": time.time() - monitoring_start,
            "final_status": final_status,
            "system_execution_time": time.time() - self.start_time
        }
        
        return summary
    
    def _set_system_running(self):
        """Set system to running state"""
        self.running = True
        self.start_time = time.time()
        self.system_session.save("system_status", "running")
        self.system_session.save("start_time", str(datetime.now()))
        self.system_session.save("@system_shutdown", "false")
    
    def _set_system_completed(self):
        """Set system to completed state"""
        self.running = False
        self.system_session.save("system_status", "completed")
        self.system_session.save("completion_time", str(datetime.now()))
        
        total_time = time.time() - self.start_time if self.start_time else 0
        self.system_session.save("total_execution_time", str(total_time))
        
        self.logger.info(f"System execution completed in {total_time:.2f}s")
    
    def stop_system(self):
        """Stop the entire system gracefully"""
        self.logger.info("Stopping multi-agent system")
        self.running = False
        self.system_session.save("@system_shutdown", "true")
        self._stop_all_agents()
        self.system_session.save("system_status", "stopped")
    
    def _stop_all_agents(self):
        """Stop all agents"""
        for agent in self.agents:
            agent.stop()
    
    def _get_system_status(self) -> Dict[str, str]:
        """Get status of all agents in the system"""
        status = {}
        for agent in self.agents:
            status[agent.agent_id] = agent.get_status()
        return status
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        agent_info = []
        for agent in self.agents:
            agent_info.append({
                "agent_id": agent.agent_id,
                "agent_class": agent.__class__.__name__,
                "status": agent.get_status(),
                "runtime_info": agent.get_runtime_info()
            })
        
        return {
            "system_id": self.system_id,
            "system_status": self.system_session.get("system_status"),
            "agent_count": len(self.agents),
            "agents": agent_info,
            "creation_time": self.system_session.get("creation_time"),
            "start_time": self.system_session.get("start_time"),
            "running": self.running
        }
    
    def send_broadcast(self, message: str):
        """Send a message to all agents in the system
        
        Args:
            message: Message to broadcast
        """
        self.logger.info(f"Broadcasting message to {len(self.agents)} agents")
        
        for agent in self.agents:
            agent.send_message(agent.agent_id, f"BROADCAST: {message}")
        
        # Also set as global message
        self.system_session.save("@system_broadcast", message)
        self.system_session.save("@system_broadcast_time", str(datetime.now()))
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """Wait for all agents to complete
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait indefinitely)
            
        Returns:
            True if all completed, False if timeout
        """
        start_wait = time.time()
        
        while self.running:
            # Check if all agents are in completed/stopped state
            statuses = self._get_system_status()
            all_done = all(status in ["completed", "stopped", "error"] for status in statuses.values())
            
            if all_done:
                self.logger.info("All agents have completed")
                return True
            
            # Check timeout
            if timeout and (time.time() - start_wait) > timeout:
                self.logger.warning("Timeout waiting for agent completion")
                return False
            
            time.sleep(1)
        
        return True
    
    def cleanup(self):
        """Clean up system resources"""
        self.logger.info("Cleaning up multi-agent system")
        
        # Stop any running agents
        self._stop_all_agents()
        
        # Clear system state
        self.system_session.save("system_status", "cleaned_up")
        self.system_session.save("cleanup_time", str(datetime.now()))
        
        # Clear thread references
        self.agent_threads.clear()
        
        self.logger.info("System cleanup completed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.cleanup()
    
    def __repr__(self):
        """String representation"""
        return f"MultiAgentSystem(id='{self.system_id}', agents={len(self.agents)}, status='{self.system_session.get('system_status')}')"