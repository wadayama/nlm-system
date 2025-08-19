#!/usr/bin/env python3
"""
CLI Demo Script for Flow Control System

Demonstrates key CLI functionality with automated commands.
"""

import time
import sys
from network_model import create_simple_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay


def demo_cli_functionality():
    """Demonstrate CLI functionality with automated commands"""
    
    print("🖥️  FLOW CONTROL CLI DEMONSTRATION")
    print("=" * 80)
    print("Simulating interactive CLI commands...\n")
    
    # Initialize system
    network = create_simple_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    def execute_command(cmd_name, cmd_func):
        """Execute a command with visual feedback"""
        print(f"💻 Command: {cmd_name}")
        print("─" * 50)
        cmd_func()
        print()
        time.sleep(1.5)
    
    # Demo 1: Show initial status
    def cmd_initial_status():
        print("📊 Initial Network Status:")
        display.display_compact_status(network)
    
    execute_command("status (initial)", cmd_initial_status)
    
    # Demo 2: Set path flows
    def cmd_set_flows():
        print("🎛️  Setting path flows:")
        success1, msg1 = controller.set_path_flow("P1", 8.0)
        success2, msg2 = controller.set_path_flow("P2", 4.0)
        print(f"  set P1 8.0  → {'✅' if success1 else '❌'} {msg1}")
        print(f"  set P2 4.0  → {'✅' if success2 else '❌'} {msg2}")
        network.generate_alerts()
        print(f"  Total throughput: {network.calculate_total_throughput():.1f}")
    
    execute_command("set P1 8.0; set P2 4.0", cmd_set_flows)
    
    # Demo 3: Show full status
    def cmd_full_status():
        print("📋 Full Network Status After Setting Flows:")
        display.display_network_status(network)
    
    execute_command("status (full)", cmd_full_status)
    
    # Demo 4: Adjust flows
    def cmd_adjust_flows():
        print("🔧 Adjusting path flows:")
        success1, msg1 = controller.update_path_flow("P1", -2.0)
        success2, msg2 = controller.update_path_flow("P2", +1.5)
        print(f"  adjust P1 -2.0  → {'✅' if success1 else '❌'} {msg1}")
        print(f"  adjust P2 +1.5  → {'✅' if success2 else '❌'} {msg2}")
        network.generate_alerts()
        print(f"  New throughput: {network.calculate_total_throughput():.1f}")
    
    execute_command("adjust P1 -2.0; adjust P2 +1.5", cmd_adjust_flows)
    
    # Demo 5: Simulate timesteps
    def cmd_advance_time():
        print("⏰ Advancing time (5 timesteps):")
        for i in range(5):
            network.advance_timestep()
            print(f"  t={network.timestep}: ", end="")
            display.display_compact_status(network)
            time.sleep(0.5)
    
    execute_command("step 5", cmd_advance_time)
    
    # Demo 6: Force edge failure
    def cmd_force_failure():
        print("⚠️  Forcing edge failure to demonstrate auto-handling:")
        print(f"  Before failure: P1={network.paths['P1'].current_flow:.1f}, P2={network.paths['P2'].current_flow:.1f}")
        
        # Force edge failure
        network.edges["e1"].is_failed = True
        network.edges["e1"].capacity = 0.0
        print("  → Forced edge e1 failure (used by path P1)")
        
        # Handle failures
        num_affected, affected_paths = controller.handle_failed_edges()
        print(f"  → Auto-handled {num_affected} paths: {affected_paths}")
        print(f"  After handling: P1={network.paths['P1'].current_flow:.1f}, P2={network.paths['P2'].current_flow:.1f}")
    
    execute_command("force failure + auto-handle", cmd_force_failure)
    
    # Demo 7: Clear and redistribute
    def cmd_redistribute():
        print("🔄 Redistributing flows:")
        controller.clear_all_flows()
        print("  → Cleared all flows")
        
        success, msg = controller.distribute_flow_equally(10.0)
        print(f"  distribute 10.0  → {'✅' if success else '❌'} {msg}")
        network.generate_alerts()
        
        # Show final state
        print("  Final state:")
        display.display_compact_status(network)
    
    execute_command("clear; distribute 10.0", cmd_redistribute)
    
    # Demo 8: Validation check
    def cmd_validation():
        print("🔍 System validation:")
        validation = controller.validate_and_report()
        print(f"  Flow conservation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
        print(f"  Capacity overloads: {'❌ Found' if validation['has_overloads'] else '✅ None'}")
        print(f"  Total throughput: {validation['total_throughput']:.1f}")
        
        utilizations = validation['path_utilizations']
        print("  Path utilizations:")
        for path_id, util in utilizations.items():
            print(f"    {path_id}: {util:.1%}")
    
    execute_command("validate", cmd_validation)
    
    print("=" * 80)
    print("🎉 CLI DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("\n💡 Key CLI Features Demonstrated:")
    print("✅ Path flow control (set, adjust, clear, distribute)")
    print("✅ Real-time status monitoring (status, compact)")
    print("✅ Time progression (step, automatic timestep)")
    print("✅ Automatic edge failure handling")
    print("✅ System validation and health checks")
    print("\n🚀 To try interactive mode: uv run python interactive_monitor.py")


if __name__ == "__main__":
    demo_cli_functionality()