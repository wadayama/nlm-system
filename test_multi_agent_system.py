#!/usr/bin/env python3
"""Test MultiAgentSystem functionality"""

import sys
from pathlib import Path
import logging
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_system import MultiAgentSystem
from agent_examples import DataCollectorAgent, MonitorAgent, ResearchAgent, CoordinatorAgent


class QuickTestAgent(DataCollectorAgent):
    """Test agent that completes quickly without LLM calls"""
    
    def __init__(self, agent_id: str, delay: float = 0.1):
        super().__init__(agent_id, "test_source")
        self.delay = delay
    
    def run(self):
        """Quick test run without LLM execution"""
        self.set_status("running")
        time.sleep(self.delay)  # Simulate work
        self.session.save("test_result", "completed")
        self.set_status("completed")
        return "test completed"


def test_system_creation():
    """Test basic system creation and agent management"""
    print("\n1️⃣ Testing MultiAgentSystem creation...")
    
    # Create system
    system = MultiAgentSystem("test_system")
    
    # Check initial state
    assert system.system_id == "test_system"
    assert len(system.agents) == 0
    assert system.running == False
    
    # Add agents
    agent1 = QuickTestAgent("agent1", 0.1)
    agent2 = QuickTestAgent("agent2", 0.1)
    
    system.add_agent(agent1)
    system.add_agent(agent2)
    
    assert len(system.agents) == 2
    assert system.system_session.get("agent_count") == "2"
    
    # Test agent retrieval
    retrieved = system.get_agent("agent1")
    assert retrieved is not None
    assert retrieved.agent_id == "agent1"
    
    # Test agent removal
    removed = system.remove_agent("agent1")
    assert removed == True
    assert len(system.agents) == 1
    
    print("   ✅ System creation and agent management work")


def test_sequential_execution():
    """Test sequential agent execution"""
    print("\n2️⃣ Testing sequential execution...")
    
    system = MultiAgentSystem("seq_test")
    
    # Add test agents with different delays
    agents = [
        QuickTestAgent("seq1", 0.1),
        QuickTestAgent("seq2", 0.1),
        QuickTestAgent("seq3", 0.1)
    ]
    
    for agent in agents:
        system.add_agent(agent)
    
    # Run sequential
    start_time = time.time()
    results = system.run_sequential()
    execution_time = time.time() - start_time
    
    # Check results
    assert results["execution_mode"] == "sequential"
    assert results["total_agents"] == 3
    assert results["successful"] == 3
    assert results["failed"] == 0
    
    # Should take at least sum of delays (sequential)
    expected_min_time = 0.3  # 3 * 0.1
    assert execution_time >= expected_min_time - 0.1
    
    # Check individual results
    for agent_id in ["seq1", "seq2", "seq3"]:
        assert agent_id in results["results"]
        assert results["results"][agent_id]["status"] == "success"
    
    print(f"   ✅ Sequential execution completed in {execution_time:.2f}s")


def test_parallel_execution():
    """Test parallel agent execution"""
    print("\n3️⃣ Testing parallel execution...")
    
    system = MultiAgentSystem("par_test")
    
    # Add test agents with same delays
    agents = [
        QuickTestAgent("par1", 0.2),
        QuickTestAgent("par2", 0.2),
        QuickTestAgent("par3", 0.2)
    ]
    
    for agent in agents:
        system.add_agent(agent)
    
    # Run parallel
    start_time = time.time()
    results = system.run_parallel()
    execution_time = time.time() - start_time
    
    # Check results
    assert results["execution_mode"] == "parallel"
    assert results["total_agents"] == 3
    assert results["successful"] == 3
    assert results["failed"] == 0
    
    # Should take roughly the time of the longest agent (parallel)
    # Allow some overhead for thread management
    assert execution_time < 0.5  # Much less than sequential would take (0.6s)
    
    print(f"   ✅ Parallel execution completed in {execution_time:.2f}s")


def test_monitored_execution():
    """Test monitored execution with system management"""
    print("\n4️⃣ Testing monitored execution...")
    
    system = MultiAgentSystem("mon_test")
    
    # Add agents with different behaviors
    agents = [
        QuickTestAgent("mon1", 0.5),
        QuickTestAgent("mon2", 0.3),
        QuickTestAgent("mon3", 0.4)
    ]
    
    for agent in agents:
        system.add_agent(agent)
    
    # Run with monitoring
    start_time = time.time()
    results = system.run_monitored(check_interval=0.1, max_runtime=5.0)
    execution_time = time.time() - start_time
    
    # Check results
    assert results["execution_mode"] == "monitored"
    assert results["total_agents"] == 3
    assert execution_time < 2.0  # Should complete well before max_runtime
    
    # Check system status
    system_info = system.get_system_info()
    assert system_info["system_id"] == "mon_test"
    assert system_info["agent_count"] == 3
    
    print(f"   ✅ Monitored execution completed in {execution_time:.2f}s")


def test_system_coordination():
    """Test system-level coordination features"""
    print("\n5️⃣ Testing system coordination...")
    
    system = MultiAgentSystem("coord_test")
    
    # Create agents that can communicate
    agent1 = QuickTestAgent("coord1", 0.1)
    agent2 = QuickTestAgent("coord2", 0.1)
    
    system.add_agent(agent1)
    system.add_agent(agent2)
    
    # Test broadcast
    system.send_broadcast("Test message to all agents")
    
    # Check broadcast was set
    broadcast = system.system_session.get("@system_broadcast")
    assert broadcast == "Test message to all agents"
    
    # Test system stop
    system.stop_system()
    assert system.running == False
    assert system.system_session.get("@system_shutdown") == "true"
    
    print("   ✅ System coordination features work")


def test_error_handling():
    """Test error handling in multi-agent execution"""
    print("\n6️⃣ Testing error handling...")
    
    class ErrorAgent(QuickTestAgent):
        """Agent that throws an error"""
        def run(self):
            self.set_status("running")
            raise ValueError("Test error")
    
    system = MultiAgentSystem("error_test")
    
    # Mix of successful and failing agents
    system.add_agent(QuickTestAgent("good1", 0.1))
    system.add_agent(ErrorAgent("bad1", 0.1))
    system.add_agent(QuickTestAgent("good2", 0.1))
    
    # Run and check error handling
    results = system.run_sequential()
    
    assert results["successful"] == 2
    assert results["failed"] == 1
    assert "bad1" in results["results"]
    assert results["results"]["bad1"]["status"] == "error"
    assert "error" in results["results"]["bad1"]
    
    print("   ✅ Error handling works correctly")


def test_context_manager():
    """Test context manager functionality"""
    print("\n7️⃣ Testing context manager...")
    
    # Use system as context manager
    with MultiAgentSystem("context_test") as system:
        system.add_agent(QuickTestAgent("ctx1", 0.1))
        system.add_agent(QuickTestAgent("ctx2", 0.1))
        
        # System should be properly initialized
        assert len(system.agents) == 2
        
        # Run agents
        results = system.run_sequential()
        assert results["successful"] == 2
    
    # After context exit, system should be cleaned up
    assert system.system_session.get("system_status") == "cleaned_up"
    
    print("   ✅ Context manager works correctly")


def test_real_agent_integration():
    """Test with real agent implementations"""
    print("\n8️⃣ Testing real agent integration...")
    
    system = MultiAgentSystem("real_test")
    
    # Create different types of real agents
    collector = DataCollectorAgent("collector", "test_db")
    researcher = ResearchAgent("researcher", "test topic")
    
    # Add to system
    system.add_agent(collector)
    system.add_agent(researcher)
    
    # Check system recognizes different agent types
    system_info = system.get_system_info()
    agent_classes = [agent["agent_class"] for agent in system_info["agents"]]
    
    assert "DataCollectorAgent" in agent_classes
    assert "ResearchAgent" in agent_classes
    
    print("   ✅ Real agent integration works")


def run_all_tests():
    """Run all multi-agent system tests"""
    print("🧪 Running MultiAgentSystem Tests")
    print("=" * 60)
    
    # Reduce logging noise
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        test_system_creation()
        test_sequential_execution()
        test_parallel_execution()
        test_monitored_execution()
        test_system_coordination()
        test_error_handling()
        test_context_manager()
        test_real_agent_integration()
        
        print("\n" + "=" * 60)
        print("✅ All MultiAgentSystem tests passed!")
        print("\n📊 Test Summary:")
        print("  • System creation and management ✓")
        print("  • Sequential execution ✓")
        print("  • Parallel execution ✓")
        print("  • Monitored execution ✓")
        print("  • System coordination ✓")
        print("  • Error handling ✓")
        print("  • Context manager ✓")
        print("  • Real agent integration ✓")
        
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