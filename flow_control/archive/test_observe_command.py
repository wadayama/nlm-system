#!/usr/bin/env python3
"""
Test script for the new 'observe' command functionality.

Demonstrates complete network state observation capabilities.
"""

from network_model import create_simple_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay


def test_observe_command():
    """Test the complete network state observation"""
    
    print("🔍 TESTING COMPLETE NETWORK STATE OBSERVATION")
    print("=" * 80)
    
    # Initialize system
    network = create_simple_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    # Set up scenario
    print("Setting up test scenario...")
    controller.set_path_flow("P1", 6.0)
    controller.set_path_flow("P2", 4.0)
    network.generate_alerts()
    
    # Get complete state
    print("\n📊 Getting complete observable network state:")
    state = controller.get_complete_network_state()
    
    # Display structured data
    print("\n🔍 COMPLETE OBSERVABLE NETWORK STATE")
    print("=" * 80)
    
    # System overview
    metrics = state['system_metrics']
    print(f"📊 System Overview (t={state['timestamp']}):")
    print(f"   Throughput: {metrics['total_throughput']:.2f} / {metrics['theoretical_max_flow']:.2f} (efficiency: {metrics['network_efficiency']:.1%})")
    print(f"   Edges: {metrics['operational_edges']} operational, {metrics['failed_edges']} failed")
    print(f"   Paths: {len(state['paths'])} total, {metrics['blocked_paths']} blocked")
    print(f"   Alerts: {metrics['active_alerts_count']} active")
    
    # Edge details
    print(f"\n🔗 Edge States:")
    print(f"{'ID':<4} {'From':<4} {'To':<4} {'Capacity':<8} {'Flow':<8} {'Available':<9} {'Util%':<6} {'Status'}")
    print("-" * 60)
    for edge_id, edge_data in state['edges'].items():
        status = "FAIL" if edge_data['is_failed'] else "OK"
        util_pct = edge_data['utilization'] * 100 if edge_data['utilization'] != float('inf') else 999
        print(f"{edge_id:<4} {edge_data['from_node']:<4} {edge_data['to_node']:<4} "
              f"{edge_data['capacity']:<8.1f} {edge_data['current_flow']:<8.1f} "
              f"{edge_data['available_capacity']:<9.1f} {util_pct:<6.0f} {status}")
    
    # Path details
    print(f"\n🛤️  Path States:")
    print(f"{'ID':<4} {'Edges':<12} {'Flow':<8} {'Capacity':<8} {'Available':<9} {'Util%':<6} {'Status'}")
    print("-" * 65)
    for path_id, path_data in state['paths'].items():
        status = "BLOCKED" if path_data['is_blocked'] else "OK"
        edges_str = "→".join(path_data['edge_sequence'])
        util_pct = path_data['utilization'] * 100 if path_data['utilization'] != float('inf') else 999
        print(f"{path_id:<4} {edges_str:<12} {path_data['current_flow']:<8.1f} "
              f"{path_data['bottleneck_capacity']:<8.1f} {path_data['available_capacity']:<9.1f} "
              f"{util_pct:<6.0f} {status}")
        if path_data['bottleneck_edge']:
            print(f"     └─ Bottleneck: {path_data['bottleneck_edge']}")
    
    # Test failure scenario
    print("\n" + "=" * 80)
    print("🚨 TESTING FAILURE SCENARIO")
    print("=" * 80)
    
    # Force edge failure
    print("Forcing edge e1 failure...")
    network.edges["e1"].is_failed = True
    network.edges["e1"].capacity = 0.0
    
    # Handle failures automatically
    num_affected, affected_paths = controller.handle_failed_edges()
    print(f"Auto-handled {num_affected} paths: {affected_paths}")
    
    # Regenerate alerts
    network.generate_alerts()
    
    # Get updated state
    print("\n📊 Updated state after failure:")
    state_after = controller.get_complete_network_state()
    
    # Show key differences
    print(f"\nKey changes:")
    print(f"  Throughput: {metrics['total_throughput']:.2f} → {state_after['system_metrics']['total_throughput']:.2f}")
    print(f"  Failed edges: {metrics['failed_edges']} → {state_after['system_metrics']['failed_edges']}")
    print(f"  Blocked paths: {metrics['blocked_paths']} → {state_after['system_metrics']['blocked_paths']}")
    print(f"  Network efficiency: {metrics['network_efficiency']:.1%} → {state_after['system_metrics']['network_efficiency']:.1%}")
    
    # Show failed edge details
    print(f"\nFailed edges:")
    for edge_id, edge_data in state_after['edges'].items():
        if edge_data['is_failed']:
            print(f"  {edge_id}: {edge_data['from_node']}→{edge_data['to_node']} (capacity=0, was={edge_data['base_capacity']})")
    
    # Show affected paths
    print(f"\nBlocked paths:")
    for path_id, path_data in state_after['paths'].items():
        if path_data['is_blocked']:
            print(f"  {path_id}: {path_data['edge_sequence']} (flow={path_data['current_flow']:.1f})")
    
    print("\n" + "=" * 80)
    print("✅ OBSERVATION TEST COMPLETE")
    print("=" * 80)
    print("\n💡 This complete state information enables:")
    print("   • Full situational awareness")
    print("   • Informed control decisions")
    print("   • Failure impact assessment")
    print("   • Capacity planning")
    print("   • Performance optimization")


if __name__ == "__main__":
    test_observe_command()