#!/usr/bin/env python3
"""Test broadcast functionality in BaseAgent"""

import sys
from pathlib import Path
import logging
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_base import BaseAgent


def test_broadcast_basic():
    """Test basic broadcast functionality"""
    print("\n1️⃣ Testing basic broadcast...")
    
    # Create agents with unique namespaces
    agent1 = BaseAgent("test1_broadcaster")
    agent2 = BaseAgent("test1_receiver1") 
    agent3 = BaseAgent("test1_receiver2")
    
    # Get baseline timestamp to filter out old broadcasts
    start_time = time.time()
    time.sleep(0.1)
    
    # Send broadcast
    agent1.broadcast("System maintenance starting in 5 minutes")
    
    # Check broadcasts from other agents (only recent ones)
    from datetime import datetime
    since_time = datetime.fromtimestamp(start_time).isoformat()
    broadcasts_2 = agent2.check_broadcasts(since_timestamp=since_time)
    broadcasts_3 = agent3.check_broadcasts(since_timestamp=since_time)
    
    # Verify broadcast received
    assert len(broadcasts_2) == 1
    assert len(broadcasts_3) == 1
    assert broadcasts_2[0]["sender"] == "test1_broadcaster"
    assert broadcasts_2[0]["message"] == "System maintenance starting in 5 minutes"
    assert broadcasts_3[0]["sender"] == "test1_broadcaster"
    
    print("   ✅ Basic broadcast works")


def test_multiple_broadcasts():
    """Test multiple broadcasts from different agents"""
    print("\n2️⃣ Testing multiple broadcasts...")
    
    # Create agents with unique namespaces
    monitor = BaseAgent("test2_monitor")
    collector = BaseAgent("test2_collector") 
    coordinator = BaseAgent("test2_coordinator")
    
    # Get timestamp before sending to filter old broadcasts
    start_time = time.time()
    time.sleep(0.1)
    
    # Send broadcasts
    monitor.broadcast("⚠️ High CPU usage detected")
    time.sleep(0.1)  # Small delay to ensure different timestamps
    collector.broadcast("📊 Data collection completed: 1000 records")
    time.sleep(0.1)
    coordinator.broadcast("✅ All systems operational")
    
    # Check only recent broadcasts
    from datetime import datetime
    since_time = datetime.fromtimestamp(start_time).isoformat()
    broadcasts = monitor.check_broadcasts(since_timestamp=since_time)
    
    # Should see all 3 broadcasts (including own)
    assert len(broadcasts) == 3
    
    # Verify senders (use test2_ prefixed names)
    senders = [b["sender"] for b in broadcasts]
    assert "test2_monitor" in senders
    assert "test2_collector" in senders
    assert "test2_coordinator" in senders
    
    # Verify messages
    messages = [b["message"] for b in broadcasts]
    assert any("High CPU" in msg for msg in messages)
    assert any("Data collection" in msg for msg in messages)
    assert any("operational" in msg for msg in messages)
    
    print("   ✅ Multiple broadcasts work")


def test_broadcast_timestamp_filtering():
    """Test timestamp filtering for broadcasts"""
    print("\n3️⃣ Testing broadcast timestamp filtering...")
    
    agent1 = BaseAgent("test3_early_sender")
    agent2 = BaseAgent("test3_late_sender")
    receiver = BaseAgent("test3_receiver")
    
    # Get initial timestamp to filter old broadcasts
    start_time = time.time()
    time.sleep(0.1)
    
    # Send early broadcast
    agent1.broadcast("Early message")
    early_time = time.time()
    
    # Wait a bit
    time.sleep(0.5)
    
    # Send late broadcast  
    agent2.broadcast("Late message")
    
    # Check broadcasts since start (should be 2)
    from datetime import datetime
    since_start = datetime.fromtimestamp(start_time).isoformat()
    all_broadcasts = receiver.check_broadcasts(since_timestamp=since_start)
    assert len(all_broadcasts) == 2
    
    # Check only recent broadcasts (after early_time)
    from datetime import datetime
    since_time = datetime.fromtimestamp(early_time + 0.1).isoformat()
    recent_broadcasts = receiver.check_broadcasts(since_timestamp=since_time)
    
    # Should only see the late message
    assert len(recent_broadcasts) == 1
    assert recent_broadcasts[0]["sender"] == "test3_late_sender"
    assert recent_broadcasts[0]["message"] == "Late message"
    
    print("   ✅ Timestamp filtering works")


def test_broadcast_latest_access():
    """Test latest broadcast access"""
    print("\n4️⃣ Testing latest broadcast access...")
    
    agent1 = BaseAgent("test4_sender1")
    agent2 = BaseAgent("test4_sender2")
    receiver = BaseAgent("test4_receiver")
    
    # Send broadcasts
    agent1.broadcast("First message")
    time.sleep(0.1)
    agent2.broadcast("Latest message")
    
    # Check latest broadcast via global variables
    latest_message = receiver.session.get("@latest_broadcast_message")
    latest_sender = receiver.session.get("@latest_broadcast_sender")
    
    assert latest_message == "Latest message"
    assert latest_sender == "test4_sender2"
    
    print("   ✅ Latest broadcast access works")


def test_broadcast_collision_resistance():
    """Test that concurrent broadcasts don't overwrite each other"""
    print("\n5️⃣ Testing broadcast collision resistance...")
    
    # Create multiple senders
    senders = [BaseAgent(f"test5_sender_{i}") for i in range(5)]
    receiver = BaseAgent("test5_receiver")
    
    # Get timestamp before sending
    start_time = time.time()
    time.sleep(0.1)
    
    # Send broadcasts rapidly
    for i, sender in enumerate(senders):
        sender.broadcast(f"Message from sender {i}")
        time.sleep(0.01)  # Very small delay
    
    # Check broadcasts since start time
    from datetime import datetime
    since_time = datetime.fromtimestamp(start_time).isoformat()
    broadcasts = receiver.check_broadcasts(since_timestamp=since_time)
    
    # Should receive all 5 broadcasts
    assert len(broadcasts) == 5
    
    # Verify unique senders
    senders_received = [b["sender"] for b in broadcasts]
    assert len(set(senders_received)) == 5  # All unique
    
    # Verify unique messages
    messages = [b["message"] for b in broadcasts] 
    assert len(set(messages)) == 5  # All unique
    
    print("   ✅ Broadcast collision resistance works")


def run_all_tests():
    """Run all broadcast tests"""
    print("🧪 Running Broadcast Tests")
    print("=" * 50)
    
    # Reduce logging noise
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        test_broadcast_basic()
        test_multiple_broadcasts()
        test_broadcast_timestamp_filtering()
        test_broadcast_latest_access()
        test_broadcast_collision_resistance()
        
        print("\n" + "=" * 50)
        print("✅ All broadcast tests passed!")
        print("\n📊 Test Summary:")
        print("  • Basic broadcast functionality ✓")
        print("  • Multiple agent broadcasts ✓")
        print("  • Timestamp filtering ✓")
        print("  • Latest broadcast access ✓")
        print("  • Collision resistance ✓")
        
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