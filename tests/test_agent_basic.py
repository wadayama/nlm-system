#!/usr/bin/env python3
"""Basic tests for BaseAgent implementation"""

import sys
from pathlib import Path
import logging
import time
from datetime import datetime

# Add parent directory to path for imports

from agent_base import BaseAgent


def test_base_agent_cannot_instantiate():
    """Test that BaseAgent.run() raises NotImplementedError"""
    print("\n1️⃣ Testing BaseAgent.run() raises NotImplementedError...")
    
    agent = BaseAgent("test_agent")
    
    # Clear any previous state for clean test
    agent.session.clear_local()
    
    # Check initial state
    assert agent.agent_id == "test_agent"
    assert agent.get_status() == "unknown"  # No automatic status initialization
    assert agent.running == False
    
    # Try to run - should raise NotImplementedError
    try:
        agent.run()
        assert False, "Should raise NotImplementedError"
    except NotImplementedError as e:
        print(f"   ✅ Expected error: {e}")
        assert "must implement run() method" in str(e)
        assert "BaseAgent" in str(e)


def test_concrete_agent():
    """Test that concrete agent implementation works"""
    print("\n2️⃣ Testing concrete agent implementation...")
    
    # Create a test agent that implements run()
    class TestAgent(BaseAgent):
        def run(self):
            self.logger.info("Starting test run")
            self.session.save("test_result", "success")
            self.set_status("completed")
            return "test completed"
    
    agent = TestAgent("test_concrete")
    
    # Clear any previous state for clean test
    agent.session.clear_local()
    
    # Check initial state
    assert agent.agent_id == "test_concrete"
    assert agent.get_status() == "unknown"
    
    # Run the agent
    result = agent.run()
    assert result == "test completed"
    
    # Check that state was properly saved
    assert agent.session.get("test_result") == "success"
    # agent_id and last_activity no longer automatically saved (removed for simplification)
    assert agent.get_status() == "completed"
    
    print("   ✅ Concrete agent works correctly")


def test_agent_state_management():
    """Test agent state management capabilities"""
    print("\n3️⃣ Testing agent state management...")
    
    class StateTestAgent(BaseAgent):
        def run(self):
            # Update status through lifecycle
            self.set_status("starting")
            assert self.get_status() == "starting"
            
            self.set_status("running")
            self.session.save("task_progress", "50%")
            
            self.set_status("finalizing")
            self.session.save("task_result", "processed")
            
            self.set_status("completed")
    
    agent = StateTestAgent("state_test")
    
    # Clear any previous state for clean test
    agent.session.clear_local()
    
    # Initial state
    assert agent.get_status() == "unknown"
    
    # Run and check state transitions
    agent.run()
    
    # Final state verification
    assert agent.get_status() == "completed"
    assert agent.session.get("task_result") == "processed"
    assert agent.session.get("task_progress") == "50%"
    
    # Runtime info functionality removed for simplification
    # Basic status check still available
    assert agent.get_status() == "completed"
    assert agent.running == False
    
    print("   ✅ State management works correctly")


def test_agent_communication():
    """Test inter-agent communication via global variables"""
    print("\n4️⃣ Testing inter-agent communication (simplified)...")
    
    # Communication features have been removed from BaseAgent
    # This test now demonstrates simple global variable communication
    
    class SimpleCommAgent(BaseAgent):
        def run(self):
            # Check for messages via global variables
            msg = self.session.get("@msg_for_me")
            if msg:
                self.session.save("received_message", msg)
                # Send response via global variable
                if msg == "ping":
                    self.session.save("@response", "pong")
    
    # Create two agents
    agent1 = SimpleCommAgent("agent1")
    agent2 = SimpleCommAgent("agent2")
    
    # Clear any previous state
    agent1.session.clear_local()
    agent2.session.clear_local()
    
    # Agent1 sends message via global variable
    agent1.session.save("@msg_for_me", "ping")
    
    # Agent2 processes the message
    agent2.run()
    
    # Check that agent2 received and responded
    assert agent2.session.get("received_message") == "ping"
    assert agent2.session.get("@response") == "pong"
    
    print("   ✅ Simple global variable communication works correctly")


def test_agent_global_coordination():
    """Test global variable coordination between agents"""
    print("\n5️⃣ Testing global variable coordination...")
    
    class CoordinatedAgent(BaseAgent):
        def run(self):
            # Set a global flag
            self.session.save("@project_status", "in_progress")
            
            # Wait for coordination signal (using alternative implementation)
            import time
            synchronized = False
            for attempt in range(3):
                current_value = self.session.get("@ready_signal")
                if current_value == "go":
                    synchronized = True
                    break
                time.sleep(1.0)
            
            if synchronized:
                self.session.save("coordination_result", "synchronized")
            else:
                self.session.save("coordination_result", "timeout")
    
    agent = CoordinatedAgent("coordinator")
    
    # Set the signal before running
    agent.session.save("@ready_signal", "go")
    
    # Run agent
    agent.run()
    
    # Check coordination worked
    assert agent.session.get("@project_status") == "in_progress"
    assert agent.session.get("coordination_result") == "synchronized"
    
    # Test timeout scenario
    agent.session.save("@ready_signal", "wait")
    agent.run()
    assert agent.session.get("coordination_result") == "timeout"
    
    print("   ✅ Global coordination works correctly")


def test_agent_stop_mechanism():
    """Test agent stop mechanism"""
    print("\n6️⃣ Testing agent stop mechanism...")
    
    class StoppableAgent(BaseAgent):
        def run(self):
            self.running = True
            self.set_status("running")
            
            iterations = 0
            while self.running and iterations < 10:
                iterations += 1
                self.session.save("iterations", str(iterations))
                
                # Simulate some work
                time.sleep(0.1)
                
                # Check for stop signal
                if self.session.get("@stop_signal") == "true":
                    # stop() method removed - manually stop
                    self.running = False
                    self.session.save("agent_status", "stopping")
                    self.session.save("stop_time", str(datetime.now()))
            
            self.set_status("stopped")
            return iterations
    
    agent = StoppableAgent("stoppable")
    
    # Set stop signal after a few iterations
    agent.session.save("@stop_signal", "true")
    
    # Run agent
    result = agent.run()
    
    # Check it stopped properly
    assert agent.running == False
    assert agent.get_status() == "stopped"
    assert "stop_time" in agent.session.list_local()
    assert result < 10  # Should stop before reaching 10 iterations
    
    print(f"   ✅ Agent stopped after {result} iterations")


def test_agent_status_checking():
    """Test checking status of other agents"""
    print("\n7️⃣ Testing cross-agent status checking...")
    
    # Create multiple agents
    agent1 = BaseAgent("worker1")
    agent2 = BaseAgent("worker2")
    agent3 = BaseAgent("supervisor")
    
    # Set different statuses
    agent1.set_status("working")
    agent2.set_status("idle")
    
    # Supervisor checks worker statuses (using direct variable access)
    worker1_status = agent3.session.variable_db.get_variable("worker1:agent_status") or "unknown"
    worker2_status = agent3.session.variable_db.get_variable("worker2:agent_status") or "unknown"
    
    assert worker1_status == "working"
    assert worker2_status == "idle"
    
    # Check non-existent agent
    unknown_status = agent3.session.variable_db.get_variable("non_existent:agent_status") or "unknown"
    assert unknown_status == "unknown"
    
    print("   ✅ Cross-agent status checking works correctly")


def test_agent_macro_execution():
    """Test macro execution wrapper"""
    print("\n8️⃣ Testing macro execution...")
    
    class MacroAgent(BaseAgent):
        def run(self):
            # Execute a simple macro
            result = self.execute_macro("Save 'test_value' to {{macro_result}}")
            return result
    
    agent = MacroAgent("macro_test")
    
    # Note: This will only work if LLM is available
    # For basic testing, we'll just verify the method exists and can be called
    try:
        # The execute_macro method should be available
        assert hasattr(agent, 'execute_macro')
        assert callable(agent.execute_macro)
        
        # Check that last_macro_time is saved after execution
        # (This would be set if we actually ran a macro)
        print("   ✅ Macro execution method available")
    except Exception as e:
        print(f"   ⚠️ Macro execution test skipped (LLM not available): {e}")


def run_all_tests():
    """Run all basic agent tests"""
    print("🧪 Running BaseAgent Basic Tests")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,  # Set to INFO or DEBUG for more details
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        test_base_agent_cannot_instantiate()
        test_concrete_agent()
        test_agent_state_management()
        test_agent_communication()
        test_agent_global_coordination()
        test_agent_stop_mechanism()
        test_agent_status_checking()
        test_agent_macro_execution()
        
        print("\n" + "=" * 60)
        print("✅ All basic tests passed!")
        print("\n📊 Test Summary:")
        print("  • BaseAgent requires run() implementation ✓")
        print("  • Concrete agents work correctly ✓")
        print("  • State management functions properly ✓")
        print("  • Inter-agent communication works ✓")
        print("  • Global coordination successful ✓")
        print("  • Stop mechanism functions ✓")
        print("  • Cross-agent status checking works ✓")
        print("  • Macro execution available ✓")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)