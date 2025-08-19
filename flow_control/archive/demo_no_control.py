#!/usr/bin/env python3
"""
Flow Control Demo with NO flow adjustments - only capacity changes
"""

import matplotlib
matplotlib.use('Agg')

from network_model import create_simple_network
from flow_operations import FlowController
from network_visualizer import NetworkVisualizer


def demo_no_flow_control():
    """Demonstrate network with capacity changes but NO flow control"""
    print("🚫 Flow Control Demo - NO Flow Adjustments")
    print("Only capacity changes, flows remain fixed")
    print("=" * 50)
    
    # Create network
    network = create_simple_network()
    controller = FlowController(network)
    visualizer = NetworkVisualizer()
    
    # Set initial flows (will remain fixed)
    controller.set_path_flow("P1", 12.0)
    controller.set_path_flow("P2", 3.0)
    print(f"Initial flows: P1=12.0, P2=3.0")
    print(f"Initial throughput: {network.calculate_total_throughput():.2f}")
    
    # Set up visualization
    fig, axes = visualizer.setup_figure(network)
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_no_control_t00.png")
    
    print(f"\nSimulating 10 timesteps with ONLY capacity changes...")
    
    for timestep in range(1, 11):
        network.advance_timestep()
        
        # NO FLOW CONTROL - only capacity changes
        # (capacity changes happen in advance_timestep)
        
        alerts = network.generate_alerts()
        throughput = network.calculate_total_throughput()
        
        print(f"  t={timestep}: Throughput={throughput:.2f}, Alerts={len(alerts)}")
        
        # Show capacity changes
        for edge_id, edge in network.edges.items():
            if edge.capacity != 10.0 and edge.capacity != 8.0 and edge.capacity != 6.0 and edge.capacity != 12.0:
                print(f"    {edge_id}: capacity={edge.capacity:.2f}")
        
        if timestep in [5, 10]:
            visualizer.update_visualization(network)
            visualizer.save_snapshot(f"demo_no_control_t{timestep:02d}.png")
    
    print(f"\nFinal flows: P1={network.paths['P1'].current_flow:.2f}, P2={network.paths['P2'].current_flow:.2f}")
    print(f"Final throughput: {network.calculate_total_throughput():.2f}")
    
    print("\n📸 Generated files:")
    print("  - demo_no_control_t00.png (initial)")
    print("  - demo_no_control_t05.png (mid)")
    print("  - demo_no_control_t10.png (final)")


if __name__ == "__main__":
    demo_no_flow_control()