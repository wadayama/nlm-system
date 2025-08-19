#!/usr/bin/env python3
"""
Test script for network visualization system - non-interactive testing
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from network_model import create_simple_network
from flow_operations import FlowController
from network_visualizer import NetworkVisualizer


def test_basic_visualization():
    """Test basic visualization functionality"""
    print("Testing network visualization system...")
    
    # Create test network
    network = create_simple_network()
    controller = FlowController(network)
    
    print(f"Created network: {network}")
    
    # Add some flows to make it interesting
    success, msg = controller.set_path_flow("P1", 5.0)
    print(f"Set P1 flow: {success} - {msg}")
    
    success, msg = controller.set_path_flow("P2", 3.0)
    print(f"Set P2 flow: {success} - {msg}")
    
    # Create some alerts by overloading
    success, msg = controller.set_path_flow("P1", 12.0)  
    print(f"Overload P1: {success} - {msg}")
    
    # Generate alerts
    alerts = network.generate_alerts()
    print(f"Generated {len(alerts)} alerts")
    
    # Test validation
    validation = controller.validate_and_report()
    print(f"Validation result: {validation['is_valid']}, {len(validation['capacity_overloads'])} overloads")
    
    # Create visualizer
    visualizer = NetworkVisualizer()
    
    # Set up figure
    fig, axes = visualizer.setup_figure(network)
    print("Figure setup complete")
    
    # Update visualization
    visualizer.update_visualization(network)
    print("Visualization updated")
    
    # Save snapshot
    visualizer.save_snapshot("test_network_visualization.png")
    print("Snapshot saved to test_network_visualization.png")
    
    # Test multiple timesteps
    print("\nTesting multiple timesteps:")
    for i in range(5):
        network.advance_timestep()
        visualizer.update_visualization(network)
        print(f"Timestep {network.timestep}: throughput={network.total_flow:.2f}, alerts={len(network.alerts)}")
    
    # Save final state
    visualizer.save_snapshot("test_network_final.png")
    print("Final snapshot saved to test_network_final.png")
    
    print("\nVisualization test completed successfully!")
    return True


if __name__ == "__main__":
    try:
        test_basic_visualization()
        print("✅ All visualization tests passed!")
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        raise