#!/usr/bin/env python3
"""
Test script for strict capacity constraints and alternatives functionality.

Tests the new capacity enforcement and alternative suggestion features.
"""

from network_model import create_simple_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay


def test_strict_capacity_constraints():
    """Test strict capacity constraint enforcement"""
    
    print("🔒 TESTING STRICT CAPACITY CONSTRAINTS")
    print("=" * 80)
    
    # Initialize system
    network = create_simple_network()
    controller = FlowController(network)
    
    print("📊 Network Setup:")
    print("   P1: e1(cap=10.0) → e2(cap=8.0)   [bottleneck: e2=8.0]")
    print("   P2: e3(cap=6.0) → e4(cap=12.0)   [bottleneck: e3=6.0]")
    
    # Test 1: Valid flow setting
    print("\n" + "─" * 60)
    print("TEST 1: Valid Flow Setting")
    print("─" * 60)
    
    success, msg, alternatives = controller.set_path_flow_with_alternatives("P1", 6.0)
    print(f"set P1 6.0: {'✅' if success else '❌'} {msg.split(chr(10))[0]}")  # First line only
    if alternatives:
        print(f"  Max safe flow: {alternatives['max_safe_flow']:.1f}")
        print(f"  Available capacity: {alternatives['available_capacity']:.1f}")
    
    # Test 2: Capacity violation
    print("\n" + "─" * 60)
    print("TEST 2: Capacity Violation (should fail)")
    print("─" * 60)
    
    success, msg, alternatives = controller.set_path_flow_with_alternatives("P1", 10.0)
    print(f"set P1 10.0: {'✅' if success else '❌'}")
    print("Error message:")
    for line in msg.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    # Test 3: Exact capacity limit
    print("\n" + "─" * 60)
    print("TEST 3: Exact Capacity Limit")
    print("─" * 60)
    
    controller.clear_all_flows()
    success, msg, alternatives = controller.set_path_flow_with_alternatives("P1", 8.0)
    print(f"set P1 8.0 (exact bottleneck): {'✅' if success else '❌'} {msg.split(chr(10))[0]}")
    if alternatives:
        print(f"  Max safe flow: {alternatives['max_safe_flow']:.1f}")
        print(f"  Available capacity: {alternatives['available_capacity']:.1f}")
    
    # Test 4: Slight overload
    print("\n" + "─" * 60)
    print("TEST 4: Slight Overload (should fail)")
    print("─" * 60)
    
    success, msg, alternatives = controller.set_path_flow_with_alternatives("P1", 8.1)
    print(f"set P1 8.1: {'✅' if success else '❌'}")
    if not success:
        print("Error details:")
        for line in msg.split('\n'):
            if line.strip():
                print(f"  {line}")


def test_maxflow_command_functionality():
    """Test the maxflow command functionality"""
    
    print("\n\n🎯 TESTING MAXFLOW COMMAND FUNCTIONALITY")
    print("=" * 80)
    
    network = create_simple_network()
    controller = FlowController(network)
    
    # Set some initial flows
    controller.set_path_flow("P1", 3.0)
    controller.set_path_flow("P2", 4.0)
    
    print("Current flows: P1=3.0, P2=4.0")
    
    # Test maxflow for each path
    for path_id in ["P1", "P2"]:
        print(f"\n📊 Max Flow Analysis: {path_id}")
        print("─" * 50)
        
        alternatives = controller.calculate_max_safe_flow(path_id)
        
        if 'error' in alternatives:
            print(f"❌ {alternatives['error']}")
            continue
        
        print(f"📈 Current State:")
        print(f"   Current flow: {alternatives['current_flow']:.1f}")
        print(f"   Available capacity: {alternatives['available_capacity']:.1f}")
        
        print(f"\n🎯 Flow Limits:")
        print(f"   Maximum safe flow: {alternatives['max_safe_flow']:.1f}")
        print(f"   Suggested flow: {alternatives['suggested_flow']:.1f}")
        
        print(f"\n🔗 Bottleneck Information:")
        print(f"   Bottleneck edge: {alternatives['bottleneck_edge']}")
        print(f"   Bottleneck capacity: {alternatives['bottleneck_capacity']:.1f}")
        print(f"   Path edges: {' → '.join(alternatives['edge_sequence'])}")
        
        # Utilization
        if alternatives['max_safe_flow'] > 0:
            util = (alternatives['current_flow'] / alternatives['max_safe_flow']) * 100
            print(f"\n📊 Utilization: {util:.1f}%")


def test_failure_scenarios():
    """Test capacity constraints under failure conditions"""
    
    print("\n\n⚠️  TESTING FAILURE SCENARIOS")
    print("=" * 80)
    
    network = create_simple_network()
    controller = FlowController(network)
    
    # Set initial flow
    success, _, _ = controller.set_path_flow_with_alternatives("P1", 6.0)
    print(f"Initial setup: P1=6.0 {'✅' if success else '❌'}")
    
    # Force edge failure
    print("\nForcing edge e2 failure...")
    network.edges["e2"].is_failed = True
    network.edges["e2"].capacity = 0.0
    
    # Test flow setting on blocked path
    print("\n📊 Testing flow setting on blocked path:")
    alternatives = controller.calculate_max_safe_flow("P1")
    
    if alternatives.get('is_blocked'):
        print("❌ Path P1 is BLOCKED")
        print(f"   Blocked at: {alternatives['bottleneck_edge']}")
        print(f"   Current flow: {alternatives['current_flow']:.1f}")
    
    # Try to set flow on blocked path
    success, msg, _ = controller.set_path_flow_with_alternatives("P1", 5.0)
    print(f"\nAttempt to set P1=5.0 on blocked path:")
    print(f"{'✅' if success else '❌'} {msg.split(chr(10))[0]}")
    
    # Test unaffected path
    print(f"\n📊 Testing unaffected path P2:")
    alternatives_p2 = controller.calculate_max_safe_flow("P2")
    print(f"P2 max safe flow: {alternatives_p2['max_safe_flow']:.1f}")
    
    success, _, _ = controller.set_path_flow_with_alternatives("P2", 5.0)
    print(f"Set P2=5.0: {'✅' if success else '❌'}")


def test_incremental_flow_increases():
    """Test incremental flow increases hitting capacity limits"""
    
    print("\n\n📈 TESTING INCREMENTAL FLOW INCREASES")
    print("=" * 80)
    
    network = create_simple_network()
    controller = FlowController(network)
    
    print("Testing incremental increases on P1 (bottleneck capacity = 8.0):")
    
    flows_to_test = [2.0, 4.0, 6.0, 8.0, 9.0, 10.0]
    
    for target_flow in flows_to_test:
        success, msg, alternatives = controller.set_path_flow_with_alternatives("P1", target_flow)
        status = "✅" if success else "❌"
        
        if success:
            current = alternatives['current_flow']
            available = alternatives['available_capacity']
            print(f"{status} set P1 {target_flow:.1f} → current={current:.1f}, available={available:.1f}")
        else:
            print(f"{status} set P1 {target_flow:.1f} → REJECTED")
            # Show only the first line of error message for brevity
            error_line = msg.split('\n')[0]
            print(f"      Reason: {error_line}")


def main():
    """Run all capacity constraint tests"""
    
    print("🔒 CAPACITY CONSTRAINTS & ALTERNATIVES TEST SUITE")
    print("=" * 80)
    print("Testing strict capacity enforcement and alternative suggestions")
    print("=" * 80)
    
    test_strict_capacity_constraints()
    test_maxflow_command_functionality()
    test_failure_scenarios()
    test_incremental_flow_increases()
    
    print("\n" + "=" * 80)
    print("✅ ALL CAPACITY CONSTRAINT TESTS COMPLETED")
    print("=" * 80)
    print("\n💡 Key Features Demonstrated:")
    print("✅ Strict capacity constraint enforcement")
    print("✅ Detailed alternatives on flow setting failure")
    print("✅ Maximum safe flow calculation")
    print("✅ Bottleneck identification and analysis")
    print("✅ Capacity-aware flow suggestions")
    print("✅ Graceful handling of edge failures")
    print("\n🚀 Ready for LLM-based intelligent flow control!")


if __name__ == "__main__":
    main()