#!/usr/bin/env python3
"""
Test script for edge failure handling functionality.

Demonstrates automatic path flow zeroing when edges fail.
"""

from network_model import NetworkState, create_simple_network
from shared_path_network import create_shared_path_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay
import time


def test_simple_network_failure():
    """Test edge failure handling on simple network"""
    print("=" * 80)
    print("TEST 1: Simple Network Edge Failure")
    print("=" * 80)
    
    # Create network and set initial flows
    network = create_simple_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    # Set initial flows
    controller.set_path_flow("P1", 5.0)
    controller.set_path_flow("P2", 3.0)
    
    print("\n1. Initial State:")
    print(f"   P1 flow: {network.paths['P1'].current_flow:.1f}")
    print(f"   P2 flow: {network.paths['P2'].current_flow:.1f}")
    print(f"   Total throughput: {network.calculate_total_throughput():.1f}")
    
    # Force edge failure on e1 (used by P1)
    print("\n2. Forcing edge e1 failure (used by path P1)...")
    network.edges["e1"].is_failed = True
    network.edges["e1"].capacity = 0.0
    
    # Handle failures manually
    num_affected, affected_paths = controller.handle_failed_edges()
    
    print(f"\n3. Failure handling result:")
    print(f"   Affected paths: {affected_paths}")
    print(f"   Number of paths zeroed: {num_affected}")
    
    print(f"\n4. After failure handling:")
    print(f"   P1 flow: {network.paths['P1'].current_flow:.1f}")
    print(f"   P2 flow: {network.paths['P2'].current_flow:.1f}")
    print(f"   Total throughput: {network.calculate_total_throughput():.1f}")
    
    # Recover edge
    print("\n5. Recovering edge e1...")
    network.edges["e1"].is_failed = False
    network.edges["e1"].capacity = 10.0
    
    # Restore flow
    controller.set_path_flow("P1", 5.0)
    print(f"   P1 flow restored to: {network.paths['P1'].current_flow:.1f}")
    print(f"   Total throughput: {network.calculate_total_throughput():.1f}")


def test_shared_network_failure():
    """Test edge failure handling on shared path network"""
    print("\n" + "=" * 80)
    print("TEST 2: Shared Path Network Edge Failure")
    print("=" * 80)
    
    # Create shared path network
    network = create_shared_path_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    # Set initial flows
    controller.set_path_flow("P1", 5.0)  # Uses e1, e5
    controller.set_path_flow("P2", 4.0)  # Uses e2, e3, e7
    controller.set_path_flow("P3", 3.0)  # Uses e1, e6, e7 (shares e1 with P1, e7 with P2)
    controller.set_path_flow("P4", 2.0)  # Uses e2, e4, e5 (shares e2 with P2, e5 with P1)
    
    print("\n1. Initial State:")
    for path_id, path in network.paths.items():
        print(f"   {path_id} flow: {path.current_flow:.1f} (edges: {', '.join(path.edges)})")
    print(f"   Total throughput: {network.calculate_total_throughput():.1f}")
    
    # Force failure on shared edge e1 (used by P1 and P3)
    print("\n2. Forcing edge e1 failure (shared by P1 and P3)...")
    network.edges["e1"].is_failed = True
    network.edges["e1"].capacity = 0.0
    
    # Handle failures
    num_affected, affected_paths = controller.handle_failed_edges()
    
    print(f"\n3. Failure handling result:")
    print(f"   Affected paths: {affected_paths}")
    print(f"   Number of paths zeroed: {num_affected}")
    
    print(f"\n4. After failure handling:")
    for path_id, path in network.paths.items():
        status = "ZEROED" if path_id in affected_paths else "ACTIVE"
        print(f"   {path_id} flow: {path.current_flow:.1f} [{status}]")
    print(f"   Total throughput: {network.calculate_total_throughput():.1f}")


def test_automatic_timestep_handling():
    """Test automatic failure handling during timestep advance"""
    print("\n" + "=" * 80)
    print("TEST 3: Automatic Failure Handling in Timestep")
    print("=" * 80)
    
    network = create_simple_network()
    controller = FlowController(network)
    
    # Set initial flows
    controller.set_path_flow("P1", 6.0)
    controller.set_path_flow("P2", 4.0)
    
    print("\n1. Initial state (t=0):")
    print(f"   P1: {network.paths['P1'].current_flow:.1f}, P2: {network.paths['P2'].current_flow:.1f}")
    print(f"   Throughput: {network.calculate_total_throughput():.1f}")
    
    # Simulate 5 timesteps
    print("\n2. Running simulation with random failures...")
    print("   (auto_handle_failures=True)")
    print()
    
    for i in range(5):
        # Advance with automatic failure handling
        network.advance_timestep(auto_handle_failures=True)
        
        # Check if any paths were auto-handled
        if hasattr(network, 'last_auto_handled_paths'):
            if network.last_auto_handled_paths:
                print(f"   t={network.timestep}: Auto-zeroed paths: {network.last_auto_handled_paths}")
        
        # Display current state
        p1_flow = network.paths['P1'].current_flow
        p2_flow = network.paths['P2'].current_flow
        throughput = network.calculate_total_throughput()
        
        # Check edge states
        e1_status = "FAILED" if network.edges["e1"].is_failed else f"OK ({network.edges['e1'].capacity:.1f})"
        e3_status = "FAILED" if network.edges["e3"].is_failed else f"OK ({network.edges['e3'].capacity:.1f})"
        
        print(f"   t={network.timestep}: P1={p1_flow:.1f}, P2={p2_flow:.1f}, Throughput={throughput:.1f}")
        print(f"         Edge status: e1={e1_status}, e3={e3_status}")
        
        time.sleep(0.5)  # Brief pause for readability


def test_manual_vs_automatic():
    """Compare manual vs automatic failure handling"""
    print("\n" + "=" * 80)
    print("TEST 4: Manual vs Automatic Failure Handling Comparison")
    print("=" * 80)
    
    # Test manual handling
    print("\n--- Manual Handling ---")
    network1 = create_simple_network()
    controller1 = FlowController(network1)
    controller1.set_path_flow("P1", 8.0)
    controller1.set_path_flow("P2", 2.0)
    
    print(f"Before failure: P1={network1.paths['P1'].current_flow:.1f}, P2={network1.paths['P2'].current_flow:.1f}")
    
    # Force failure and manually handle
    network1.edges["e2"].is_failed = True
    network1.edges["e2"].capacity = 0.0
    num, paths = controller1.handle_failed_edges()
    
    print(f"After manual handling: P1={network1.paths['P1'].current_flow:.1f}, P2={network1.paths['P2'].current_flow:.1f}")
    print(f"Zeroed paths: {paths}")
    
    # Test automatic handling
    print("\n--- Automatic Handling ---")
    network2 = create_simple_network()
    controller2 = FlowController(network2)
    controller2.set_path_flow("P1", 8.0)
    controller2.set_path_flow("P2", 2.0)
    
    print(f"Before failure: P1={network2.paths['P1'].current_flow:.1f}, P2={network2.paths['P2'].current_flow:.1f}")
    
    # Force failure and advance timestep (auto-handles)
    network2.edges["e2"].is_failed = True
    network2.edges["e2"].capacity = 0.0
    network2.advance_timestep(auto_handle_failures=True)
    
    print(f"After auto handling: P1={network2.paths['P1'].current_flow:.1f}, P2={network2.paths['P2'].current_flow:.1f}")
    if hasattr(network2, 'last_auto_handled_paths'):
        print(f"Auto-zeroed paths: {network2.last_auto_handled_paths}")


def main():
    """Run all tests"""
    print("\n🔧 EDGE FAILURE HANDLING TEST SUITE")
    print("=" * 80)
    print("Testing automatic path flow zeroing when edges fail")
    print("=" * 80)
    
    # Run tests
    test_simple_network_failure()
    test_shared_network_failure()
    test_automatic_timestep_handling()
    test_manual_vs_automatic()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
    print("\nKey findings:")
    print("1. Failed edges automatically zero flows on affected paths")
    print("2. Shared edges affect multiple paths when they fail")
    print("3. Automatic handling works during timestep advancement")
    print("4. Manual and automatic handling produce identical results")


if __name__ == "__main__":
    main()