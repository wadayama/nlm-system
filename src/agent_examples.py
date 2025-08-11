#!/usr/bin/env python3
"""Concrete agent implementations for various use cases

This module provides ready-to-use agent implementations that demonstrate
different patterns of agent behavior.
"""

from agent_base import BaseAgent
import time
import logging


class DataCollectorAgent(BaseAgent):
    """Agent that collects data once and completes
    
    This is an example of a one-shot agent that performs a single task
    and then completes. Useful for data gathering, initialization, or
    any task that doesn't require continuous execution.
    """
    
    def __init__(self, agent_id: str, data_source: str = None, model: str = None, reasoning_effort: str = "low", verbosity: str = "low"):
        """Initialize data collector agent
        
        Args:
            agent_id: Unique identifier for this agent
            data_source: Description of data source to collect from
            model: LLM model to use (optional)
            reasoning_effort: Reasoning level - "low", "medium", "high" (default: "low")
            verbosity: Response verbosity - "low", "medium", "high" (default: "low")
        """
        super().__init__(agent_id, model, reasoning_effort, verbosity)
        self.data_source = data_source or "default source"
        self.session.save("data_source", self.data_source)
    
    def run(self):
        """Collect data once and complete"""
        self.set_status("collecting")
        self.logger.info(f"Starting data collection from {self.data_source}")
        
        # Simulate data collection with a macro
        result = self.execute_macro(
            f"Collect data from {self.data_source} and summarize key findings. "
            f"Save the summary to {{collected_data}}"
        )
        
        # Store metadata about the collection
        self.session.save("collection_time", str(time.time()))
        self.session.save("collection_result", "success")
        
        self.set_status("completed")
        self.logger.info("Data collection completed")
        
        return result


class MonitorAgent(BaseAgent):
    """Agent that continuously monitors and reports
    
    This is an example of a continuous agent that runs in a loop,
    checking conditions and reporting status. Useful for system monitoring,
    alert detection, or any task requiring ongoing observation.
    """
    
    def __init__(self, agent_id: str, check_interval: float = 5.0, model: str = None, reasoning_effort: str = "low", verbosity: str = "low"):
        """Initialize monitor agent
        
        Args:
            agent_id: Unique identifier for this agent
            check_interval: Seconds between monitoring checks
            model: LLM model to use (optional)
            reasoning_effort: Reasoning level - "low", "medium", "high" (default: "low")
            verbosity: Response verbosity - "low", "medium", "high" (default: "low")
        """
        super().__init__(agent_id, model, reasoning_effort, verbosity)
        self.check_interval = check_interval
        self.session.save("check_interval", str(check_interval))
        self.check_count = 0
    
    def run(self):
        """Run continuous monitoring loop"""
        self.running = True
        self.set_status("monitoring")
        self.logger.info("Starting monitoring")
        
        while self.running:
            self.check_count += 1
            
            # Perform monitoring check
            self.perform_check()
            
            # Check for stop conditions
            if self.should_stop():
                break
            
            # Wait before next check
            time.sleep(self.check_interval)
        
        self.set_status("stopped")
        self.logger.info(f"Monitoring stopped after {self.check_count} checks")
    
    def perform_check(self):
        """Perform a single monitoring check"""
        self.session.save("last_check_time", str(time.time()))
        self.session.save("check_count", str(self.check_count))
        
        # Check system status
        result = self.execute_macro(
            "Check current system status and identify any issues. "
            "Save status to {{monitor_status}} and any alerts to {{monitor_alerts}}"
        )
        
        # Check if there are critical alerts
        alerts = self.session.get("monitor_alerts")
        if alerts and "critical" in str(alerts).lower():
            self.send_alert(alerts)
        
        self.logger.info(f"Check #{self.check_count} completed")
    
    def should_stop(self):
        """Check if monitoring should stop"""
        # Check for global stop signal
        if self.session.get("@stop_all_monitoring") == "true":
            return True
        
        # Check for agent-specific stop signal
        if self.session.get("stop_monitoring") == "true":
            return True
        
        # Check for max iterations (safety limit)
        if self.check_count >= 100:
            self.logger.warning("Reached maximum check count limit")
            return True
        
        return False
    
    def send_alert(self, alert_message: str):
        """Send alert to coordinator or other agents"""
        self.logger.warning(f"Alert detected: {alert_message}")
        
        # Send to coordinator if exists
        coordinator_status = self.session.variable_db.get_variable("coordinator:agent_status") or "unknown"
        if coordinator_status != "unknown":
            # Send alert via global variable
            self.session.save("@msg_for_coordinator", f"ALERT: {alert_message}")
            self.session.save("@msg_for_coordinator_from", self.agent_id)
        
        # Set global alert flag
        self.session.save("@system_alert", alert_message)
        self.session.save("@system_alert_time", str(time.time()))


class ResearchAgent(BaseAgent):
    """Agent that performs multi-phase research tasks
    
    This agent demonstrates a phased approach where the agent progresses
    through different stages of work. Each phase can have different logic
    and the agent maintains state between phases.
    """
    
    def __init__(self, agent_id: str, research_topic: str = None, model: str = None, reasoning_effort: str = "low", verbosity: str = "low"):
        """Initialize research agent
        
        Args:
            agent_id: Unique identifier for this agent
            research_topic: Topic to research
            model: LLM model to use (optional)
            reasoning_effort: Reasoning level - "low", "medium", "high" (default: "low")
            verbosity: Response verbosity - "low", "medium", "high" (default: "low")
        """
        super().__init__(agent_id, model, reasoning_effort, verbosity)
        self.research_topic = research_topic or self.session.get("@research_topic") or "general topic"
        self.session.save("research_topic", self.research_topic)
        self.session.save("research_phase", "initialized")
    
    def run(self):
        """Execute research through multiple phases"""
        self.running = True
        self.set_status("researching")
        self.logger.info(f"Starting research on: {self.research_topic}")
        
        phases = [
            ("literature_review", self.phase_literature_review),
            ("data_collection", self.phase_data_collection),
            ("analysis", self.phase_analysis),
            ("synthesis", self.phase_synthesis),
            ("reporting", self.phase_reporting)
        ]
        
        for phase_name, phase_method in phases:
            if not self.running:
                break
            
            self.session.save("research_phase", phase_name)
            self.logger.info(f"Entering phase: {phase_name}")
            
            # Execute phase
            phase_result = phase_method()
            
            # Check if phase requests stop
            if phase_result == "stop":
                break
            
            # Small delay between phases
            time.sleep(1)
        
        self.set_status("completed")
        self.logger.info("Research completed")
    
    def phase_literature_review(self):
        """Phase 1: Review existing literature"""
        result = self.execute_macro(
            f"Review existing literature on '{self.research_topic}'. "
            f"Identify key concepts, theories, and gaps in knowledge. "
            f"Save findings to {{literature_findings}}"
        )
        
        findings = self.session.get("literature_findings")
        if not findings:
            self.logger.warning("No literature findings generated")
            return "stop"
        
        self.session.save("phase_1_complete", "true")
        return "continue"
    
    def phase_data_collection(self):
        """Phase 2: Collect relevant data"""
        result = self.execute_macro(
            f"Based on literature findings {{literature_findings}}, "
            f"identify what data needs to be collected for '{self.research_topic}'. "
            f"Create a data collection plan and save to {{data_plan}}"
        )
        
        # Simulate data collection
        result = self.execute_macro(
            f"Following the data plan {{data_plan}}, "
            f"collect relevant data and statistics. "
            f"Save collected data to {{research_data}}"
        )
        
        self.session.save("phase_2_complete", "true")
        return "continue"
    
    def phase_analysis(self):
        """Phase 3: Analyze collected data"""
        result = self.execute_macro(
            f"Analyze the research data {{research_data}} for '{self.research_topic}'. "
            f"Identify patterns, trends, and significant findings. "
            f"Save analysis results to {{analysis_results}}"
        )
        
        self.session.save("phase_3_complete", "true")
        return "continue"
    
    def phase_synthesis(self):
        """Phase 4: Synthesize findings"""
        result = self.execute_macro(
            f"Synthesize all findings from literature {{literature_findings}}, "
            f"data {{research_data}}, and analysis {{analysis_results}}. "
            f"Create comprehensive conclusions about '{self.research_topic}'. "
            f"Save synthesis to {{research_synthesis}}"
        )
        
        self.session.save("phase_4_complete", "true")
        return "continue"
    
    def phase_reporting(self):
        """Phase 5: Generate final report"""
        result = self.execute_macro(
            f"Create a final research report on '{self.research_topic}' that includes: "
            f"1. Executive summary "
            f"2. Literature review from {{literature_findings}} "
            f"3. Methodology and data from {{data_plan}} "
            f"4. Analysis from {{analysis_results}} "
            f"5. Conclusions from {{research_synthesis}} "
            f"Save the complete report to {{final_report}}"
        )
        
        # Notify completion
        self.session.save("@research_complete", "true")
        self.session.save("phase_5_complete", "true")
        
        # Send report notification
        self.broadcast_completion()
        
        return "continue"
    
    def broadcast_completion(self):
        """Notify other agents that research is complete"""
        report = self.session.get("final_report")
        if report:
            # Broadcast completion via global variables (broadcast method not available)
            completion_message = (
                f"🔬 Research completed: '{self.research_topic}' by {self.agent_id}. "
                f"Report available with {len(report)} characters."
            )
            self.session.save("@broadcast_message", completion_message)
            self.session.save("@broadcast_message_from", self.agent_id)
            self.session.save("@broadcast_message_time", str(time.time()))
            
            # Set specific global variables for easy access
            self.session.save("@latest_research_report", report[:500])  # First 500 chars
            self.session.save("@latest_research_topic", self.research_topic)
            self.session.save("@latest_research_agent", self.agent_id)


class CoordinatorAgent(BaseAgent):
    """Agent that coordinates other agents
    
    This agent monitors and coordinates the activities of other agents,
    assigning tasks, checking progress, and ensuring overall system goals
    are met.
    """
    
    def __init__(self, agent_id: str, team_agents: list = None, model: str = None, reasoning_effort: str = "low", verbosity: str = "low"):
        """Initialize coordinator agent
        
        Args:
            agent_id: Unique identifier for this agent
            team_agents: List of agent IDs to coordinate
            model: LLM model to use (optional)
            reasoning_effort: Reasoning level - "low", "medium", "high" (default: "low")
            verbosity: Response verbosity - "low", "medium", "high" (default: "low")
        """
        super().__init__(agent_id, model, reasoning_effort, verbosity)
        self.team_agents = team_agents or []
        self.session.save("team_size", str(len(self.team_agents)))
        self.session.save("team_agents", ",".join(self.team_agents))
        self.coordination_cycles = 0
    
    def run(self):
        """Run coordination loop"""
        self.running = True
        self.set_status("coordinating")
        self.logger.info(f"Starting coordination of {len(self.team_agents)} agents")
        
        while self.running:
            self.coordination_cycles += 1
            
            # Check team status
            team_status = self.check_team_status()
            
            # Make coordination decisions
            self.coordinate_team(team_status)
            
            # Check messages from team
            self.process_team_messages()
            
            # Check completion conditions
            if self.check_completion():
                break
            
            # Wait before next cycle
            time.sleep(3)
        
        self.set_status("completed")
        self.logger.info(f"Coordination completed after {self.coordination_cycles} cycles")
    
    def check_team_status(self) -> dict:
        """Check the status of all team members"""
        status_report = {}
        
        for agent_id in self.team_agents:
            status = self.session.variable_db.get_variable(f"{agent_id}:agent_status") or "unknown"
            status_report[agent_id] = status
            
            # Log any status changes
            last_known = self.session.get(f"last_status_{agent_id}")
            if last_known != status:
                self.logger.info(f"Agent {agent_id} status changed: {last_known} -> {status}")
                self.session.save(f"last_status_{agent_id}", status)
        
        self.session.save("team_status", str(status_report))
        return status_report
    
    def coordinate_team(self, team_status: dict):
        """Make coordination decisions based on team status"""
        # Count agents in different states
        idle_agents = [aid for aid, status in team_status.items() if status in ["initialized", "completed"]]
        working_agents = [aid for aid, status in team_status.items() if status in ["running", "collecting", "monitoring", "researching"]]
        
        self.session.save("idle_agents", str(len(idle_agents)))
        self.session.save("working_agents", str(len(working_agents)))
        
        # Assign tasks to idle agents
        if idle_agents and self.session.get("@pending_tasks"):
            self.assign_tasks(idle_agents)
        
        # Check for stuck agents
        for agent_id in working_agents:
            last_activity = self.session.variable_db.get_variable(f"{agent_id}:last_activity_time")
            if last_activity:
                # Check if agent hasn't been active for too long
                try:
                    import datetime
                    last_time = datetime.datetime.fromisoformat(last_activity)
                    now = datetime.datetime.now()
                    if (now - last_time).seconds > 300:  # 5 minutes
                        self.logger.warning(f"Agent {agent_id} may be stuck")
                        # Send status check via global variable
                        self.session.save(f"@msg_for_{agent_id}", "STATUS_CHECK: Please report status")
                        self.session.save(f"@msg_for_{agent_id}_from", self.agent_id)
                except:
                    pass
    
    def assign_tasks(self, idle_agents: list):
        """Assign pending tasks to idle agents"""
        tasks = self.session.get("@pending_tasks")
        if tasks:
            for agent_id in idle_agents:
                # Send task assignment via global variable
                self.session.save(f"@msg_for_{agent_id}", f"NEW_TASK: {tasks}")
                self.session.save(f"@msg_for_{agent_id}_from", self.agent_id)
                self.logger.info(f"Assigned task to {agent_id}")
                break  # Assign one task at a time
    
    def process_team_messages(self):
        """Process messages from team members"""
        # Check for messages via global variables (simplified)
        messages = []
        msg = self.session.get(f"@msg_for_{self.agent_id}")
        if msg:
            sender = self.session.get(f"@msg_for_{self.agent_id}_from") or "unknown"
            messages.append({"from": sender, "message": msg})
        
        for msg in messages:
            sender = msg["from"]
            content = msg["message"]
            
            if "ALERT" in content:
                self.handle_alert(sender, content)
            elif "complete" in content.lower():
                self.handle_completion(sender, content)
            elif "help" in content.lower() or "error" in content.lower():
                self.handle_help_request(sender, content)
        
        # Clear processed messages
        if messages:
            # Clear messages
            self.session.delete(f"@msg_for_{self.agent_id}")
            self.session.delete(f"@msg_for_{self.agent_id}_from")
    
    def handle_alert(self, sender: str, alert: str):
        """Handle alert from team member"""
        self.logger.warning(f"Alert from {sender}: {alert}")
        self.session.save("@system_alert", alert)
        
        # Notify all agents
        for agent_id in self.team_agents:
            if agent_id != sender:
                # Broadcast alert via global variable
                self.session.save(f"@msg_for_{agent_id}", f"ALERT from {sender}: {alert}")
                self.session.save(f"@msg_for_{agent_id}_from", self.agent_id)
    
    def handle_completion(self, sender: str, message: str):
        """Handle completion notification from team member"""
        self.logger.info(f"Agent {sender} reported completion")
        self.session.save(f"completed_{sender}", "true")
    
    def handle_help_request(self, sender: str, message: str):
        """Handle help request from team member"""
        self.logger.info(f"Help request from {sender}")
        
        # Try to provide assistance or reassign task
        result = self.execute_macro(
            f"Agent {sender} needs help with: {message}. "
            f"Provide guidance or solution. Save response to {{help_response}}"
        )
        
        help_response = self.session.get("help_response")
        if help_response:
            # Send help response via global variable
            self.session.save(f"@msg_for_{sender}", f"HELP: {help_response}")
            self.session.save(f"@msg_for_{sender}_from", self.agent_id)
    
    def check_completion(self) -> bool:
        """Check if coordination should complete"""
        # Check for global completion signal
        if self.session.get("@project_complete") == "true":
            return True
        
        # Check if all agents are done
        team_status = self.check_team_status()
        all_complete = all(status in ["completed", "stopped"] for status in team_status.values())
        
        if all_complete:
            self.logger.info("All team agents have completed")
            self.session.save("@project_complete", "true")
            return True
        
        # Safety limit
        if self.coordination_cycles >= 100:
            self.logger.warning("Reached maximum coordination cycles")
            return True
        
        return False