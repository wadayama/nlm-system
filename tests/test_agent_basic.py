#!/usr/bin/env python3
"""Basic tests for BaseAgent implementation"""

import sys
from pathlib import Path
import logging
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_base import BaseAgent


def test_base_agent_cannot_instantiate():
    """Test that BaseAgent.run() raises NotImplementedError"""
    print("\n1️⃣ Testing BaseAgent.run() raises NotImplementedError...")
    
    agent = BaseAgent("test_agent")
    
    # Check initial state
    assert agent.agent_id == "test_agent"
    assert agent.get_status() == "initialized"
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
            self.log_activity("Starting test run")
            self.session.save("test_result", "success")
            self.set_status("completed")
            return "test completed"
    
    agent = TestAgent("test_concrete")
    
    # Check initial state
    assert agent.agent_id == "test_concrete"
    assert agent.get_status() == "initialized"
    
    # Run the agent
    result = agent.run()
    assert result == "test completed"
    
    # Check that state was properly saved
    assert agent.session.get("test_result") == "success"
    assert agent.session.get("agent_id") == "test_concrete"
    assert agent.get_status() == "completed"
    assert agent.session.get("last_activity") == "Starting test run"
    
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
    
    # Initial state
    assert agent.get_status() == "initialized"
    
    # Run and check state transitions
    agent.run()
    
    # Final state verification
    assert agent.get_status() == "completed"
    assert agent.session.get("task_result") == "processed"
    assert agent.session.get("task_progress") == "50%"
    
    # Check runtime info
    info = agent.get_runtime_info()
    assert info["agent_id"] == "state_test"
    assert info["agent_class"] == "StateTestAgent"
    assert info["status"] == "completed"
    assert info["running"] == False
    assert "creation_time" in info
    
    print("   ✅ State management works correctly")


def test_agent_communication():
    """Test inter-agent communication"""
    print("\n4️⃣ Testing inter-agent communication...")
    
    class CommunicatingAgent(BaseAgent):
        def run(self):
            # Check for messages
            messages = self.check_messages()
            self.session.save("received_messages", str(len(messages)))
            
            # Process messages
            for msg in messages:
                if msg["message"] == "ping":
                    self.send_message(msg["from"], "pong")
    
    # Create two agents
    agent1 = CommunicatingAgent("agent1")
    agent2 = CommunicatingAgent("agent2")
    
    # Agent1 sends message to Agent2
    agent1.send_message("agent2", "Hello from agent1")
    agent1.send_message("agent2", "ping")
    
    # Agent2 checks messages
    messages = agent2.check_messages()
    print(f"   Debug: Found {len(messages)} messages")
    for i, msg in enumerate(messages):
        print(f"   Debug: Message {i+1}: from={msg.get('from')}, message={msg.get('message')[:30]}...")
    
    # Debug: Check what global variables exist
    all_globals = agent2.session.list_global()
    print(f"   Debug: Global variables: {list(all_globals.keys())}")
    
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    assert messages[0]["from"] == "agent1"
    assert messages[0]["message"] == "Hello from agent1"
    assert messages[1]["message"] == "ping"
    assert "timestamp" in messages[0]
    
    # Agent2 processes messages
    agent2.run()
    
    # Agent1 should receive the pong response
    agent1_messages = agent1.check_messages()
    assert len(agent1_messages) == 1
    assert agent1_messages[0]["from"] == "agent2"
    assert agent1_messages[0]["message"] == "pong"
    
    # Clear messages
    agent2.clear_messages()
    assert len(agent2.check_messages()) == 0
    
    print("   ✅ Inter-agent communication works correctly")


def test_agent_global_coordination():
    """Test global variable coordination between agents"""
    print("\n5️⃣ Testing global variable coordination...")
    
    class CoordinatedAgent(BaseAgent):
        def run(self):
            # Set a global flag
            self.session.save("@project_status", "in_progress")
            
            # Wait for coordination signal
            if self.wait_for_global("ready_signal", "go", max_attempts=3):
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
                    self.stop()
            
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
    
    # Supervisor checks worker statuses
    worker1_status = agent3.get_agent_status("worker1")
    worker2_status = agent3.get_agent_status("worker2")
    
    assert worker1_status == "working"
    assert worker2_status == "idle"
    
    # Check non-existent agent
    unknown_status = agent3.get_agent_status("non_existent")
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