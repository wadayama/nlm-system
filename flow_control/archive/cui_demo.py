#!/usr/bin/env python3
"""
CUI Demo - Command Line Interface Demonstration

Shows various CUI capabilities for the flow control system.
"""

import time
from network_model import create_simple_network
from flow_operations import FlowController, FlowOptimizer
from network_display import NetworkCUIDisplay


def demo_cui_features():
    """Demonstrate all CUI features"""
    
    # Initialize system
    network = create_simple_network()
    controller = FlowController(network)
    optimizer = FlowOptimizer(network)
    display = NetworkCUIDisplay()
    
    print("🎬 FLOW CONTROL CUI DEMONSTRATION")
    print("=" * 80)
    print("This demo shows various command-line interface features.")
    input("Press Enter to continue...")
    
    # Demo 1: Basic status display
    print("\n" + "🔹" * 30 + " DEMO 1: BASIC STATUS " + "🔹" * 30)
    controller.set_path_flow("P1", 8.0)
    controller.set_path_flow("P2", 4.0)
    network.generate_alerts()
    
    display.display_network_status(network)
    input("\nPress Enter for next demo...")
    
    # Demo 2: Overload scenario
    print("\n" + "🔸" * 30 + " DEMO 2: OVERLOAD SCENARIO " + "🔸" * 30)
    controller.set_path_flow("P1", 15.0)  # Create overload
    controller.set_path_flow("P2", 2.0)
    network.generate_alerts()
    
    display.display_network_status(network)
    input("\nPress Enter for next demo...")
    
    # Demo 3: Compact monitoring
    print("\n" + "🔷" * 30 + " DEMO 3: COMPACT MONITORING " + "🔷" * 30)
    print("Watching network evolution over 8 timesteps:")
    print()
    
    for i in range(8):
        network.advance_timestep()
        display.display_compact_status(network)
        time.sleep(0.8)
    
    input("\nPress Enter for next demo...")
    
    # Demo 4: Flow optimization
    print("\n" + "🔶" * 30 + " DEMO 4: FLOW OPTIMIZATION " + "🔶" * 30)
    print("Before optimization:")
    display.display_compact_status(network)
    
    print("\nRunning greedy optimization...")
    throughput, msg = optimizer.maximize_throughput_greedy()
    network.generate_alerts()
    
    print(f"✅ {msg}")
    print("\nAfter optimization:")
    display.display_compact_status(network)
    
    input("\nPress Enter for final demo...")
    
    # Demo 5: Manual control simulation
    print("\n" + "🔺" * 30 + " DEMO 5: MANUAL CONTROL " + "🔺" * 30)
    print("Simulating manual flow adjustments:")
    
    adjustments = [
        ("P1", -10.0, "Reduce P1 to relieve overload"),
        ("P2", +5.0, "Increase P2 to use available capacity"), 
        ("P1", +2.0, "Fine-tune P1"),
        ("P2", -1.0, "Fine-tune P2")
    ]
    
    for path, delta, description in adjustments:
        print(f"\n📝 Action: {description}")
        success, msg = controller.update_path_flow(path, delta)
        network.generate_alerts()
        print(f"   {msg}")
        display.display_compact_status(network)
        time.sleep(1.0)
    
    print(f"\n🏁 Final optimized state:")
    display.display_network_status(network)
    
    print("\n" + "=" * 80)
    print("🎉 CUI Demonstration Complete!")
    print("💡 Try 'uv run python interactive_monitor.py' for interactive control")
    print("=" * 80)


def quick_status_check():
    """Quick network status check utility"""
    network = create_simple_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    # Random scenario
    import random
    controller.set_path_flow("P1", random.uniform(5, 15))
    controller.set_path_flow("P2", random.uniform(2, 8))
    
    # Advance a few steps
    for _ in range(random.randint(3, 8)):
        network.advance_timestep()
    
    network.generate_alerts()
    display.display_network_status(network)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_status_check()
    else:
        demo_cui_features()