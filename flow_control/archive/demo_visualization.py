#!/usr/bin/env python3
"""
Flow Control Visualization Demo

Interactive demonstration of the network visualization system
showing real-time network state changes, flow dynamics, and alert generation.
"""

import matplotlib
# Use non-interactive backend for demo screenshots
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import time
import random
from network_model import create_simple_network
from flow_operations import FlowController, FlowOptimizer
from network_visualizer import NetworkVisualizer


def demo_basic_visualization():
    """Demonstrate basic visualization functionality"""
    print("🎨 Flow Control Network Visualization Demo")
    print("=" * 50)
    
    # Create and set up network
    network = create_simple_network()
    controller = FlowController(network)
    visualizer = NetworkVisualizer()
    
    print("📊 Setting up network with initial flows...")
    
    # Create interesting initial state
    controller.set_path_flow("P1", 4.0)
    controller.set_path_flow("P2", 2.0)
    
    # Set up visualization
    fig, axes = visualizer.setup_figure(network)
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_00_initial.png")
    
    print(f"Initial state: Throughput={network.calculate_total_throughput():.1f}")
    print(f"P1 flow: {network.paths['P1'].current_flow:.1f}")
    print(f"P2 flow: {network.paths['P2'].current_flow:.1f}")
    print("📸 Saved: demo_step_00_initial.png")
    
    return network, controller, visualizer


def demo_overload_scenario():
    """Demonstrate overload detection and visualization"""
    print("\n🔥 Demonstrating Overload Scenario...")
    
    network, controller, visualizer = demo_basic_visualization()
    
    # Create overload situation
    print("Creating overload on P1...")
    controller.set_path_flow("P1", 12.0)  # Should exceed capacity
    
    # Generate alerts
    alerts = network.generate_alerts()
    print(f"Generated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"  - {alert.description}")
    
    # Update visualization
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_01_overload.png")
    print("📸 Saved: demo_step_01_overload.png")
    
    # Show validation results
    validation = controller.validate_and_report()
    print(f"Validation: {len(validation['capacity_overloads'])} overloads detected")
    
    return network, controller, visualizer


def demo_failure_recovery():
    """Demonstrate failure and recovery scenarios"""
    print("\n⚡ Demonstrating Failure and Recovery...")
    
    network, controller, visualizer = demo_overload_scenario()
    
    # Force edge failure
    print("Forcing edge e2 failure...")
    network.edges["e2"].is_failed = True
    network.edges["e2"].capacity = 0.0
    
    # Generate alerts for failure
    alerts = network.generate_alerts()
    print(f"After failure: {len(alerts)} alerts")
    
    # Update visualization
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_02_failure.png")
    print("📸 Saved: demo_step_02_failure.png")
    
    # Show recovery
    print("Simulating recovery...")
    network.edges["e2"].is_failed = False
    network.edges["e2"].capacity = 6.0  # Partial recovery
    
    # Rebalance flows
    optimizer = FlowOptimizer(network)
    optimizer.balance_path_utilization()
    
    alerts = network.generate_alerts()
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_03_recovery.png")
    print("📸 Saved: demo_step_03_recovery.png")
    print(f"After recovery: {len(alerts)} alerts")
    
    return network, controller, visualizer


def demo_optimization():
    """Demonstrate optimization algorithms"""
    print("\n🎯 Demonstrating Optimization Algorithms...")
    
    network, controller, visualizer = demo_failure_recovery()
    
    # Clear flows and optimize
    print("Clearing flows and running greedy optimization...")
    controller.clear_all_flows()
    
    optimizer = FlowOptimizer(network)
    throughput, description = optimizer.maximize_throughput_greedy()
    
    print(f"Optimization result: {description}")
    print(f"Achieved throughput: {throughput:.2f}")
    
    # Update visualization
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_04_optimized.png")
    print("📸 Saved: demo_step_04_optimized.png")
    
    return network, controller, visualizer


def demo_time_progression():
    """Demonstrate time progression with capacity changes"""
    print("\n⏰ Demonstrating Time Progression...")
    
    network, controller, visualizer = demo_optimization()
    
    print("Simulating 10 timesteps with random capacity changes...")
    
    for timestep in range(1, 11):
        network.advance_timestep()
        
        # Occasionally adjust flows randomly
        if timestep % 3 == 0:
            path_id = random.choice(["P1", "P2"])
            delta = random.uniform(-0.5, 0.5)
            success, msg = controller.update_path_flow(path_id, delta)
            if success:
                print(f"  t={timestep}: Adjusted {path_id} by {delta:.2f}")
        
        # Generate alerts
        alerts = network.generate_alerts()
        throughput = network.calculate_total_throughput()
        
        print(f"  t={timestep}: Throughput={throughput:.2f}, Alerts={len(alerts)}")
        
        # Save key timesteps
        if timestep in [3, 6, 10]:
            visualizer.update_visualization(network)
            visualizer.save_snapshot(f"demo_step_05_t{timestep:02d}.png")
            print(f"    📸 Saved: demo_step_05_t{timestep:02d}.png")
    
    return network, controller, visualizer


def demo_performance_analysis():
    """Demonstrate performance analysis visualization"""
    print("\n📈 Performance Analysis Summary...")
    
    network, controller, visualizer = demo_time_progression()
    
    # Final state analysis
    print(f"Final network state (t={network.timestep}):")
    print(f"  Total throughput: {network.total_flow:.2f}")
    print(f"  Violation count: {network.violation_count}")
    print(f"  History length: {len(network.total_throughput_history)}")
    
    # Path utilizations
    utilizations = controller.get_path_utilizations()
    print("  Path utilizations:")
    for path_id, util in utilizations.items():
        print(f"    {path_id}: {util:.2f}")
    
    # System summary
    print(f"\nNetwork summary:")
    print(network.get_network_summary())
    
    # Final visualization
    visualizer.update_visualization(network)
    visualizer.save_snapshot("demo_step_06_final.png")
    print("📸 Saved: demo_step_06_final.png")
    
    return network, controller, visualizer


def create_comparison_visualization():
    """Create a comparison of different network states"""
    print("\n🔄 Creating State Comparison Visualization...")
    
    # Create multiple network states for comparison
    states = []
    
    # State 1: Balanced flows
    net1 = create_simple_network()
    ctrl1 = FlowController(net1)
    ctrl1.distribute_flow_equally(8.0)
    net1.generate_alerts()
    states.append(("Balanced Flows", net1))
    
    # State 2: Overloaded
    net2 = create_simple_network()
    ctrl2 = FlowController(net2)
    ctrl2.set_path_flow("P1", 15.0)
    ctrl2.set_path_flow("P2", 1.0)
    net2.generate_alerts()
    states.append(("Overloaded P1", net2))
    
    # State 3: Failed edge
    net3 = create_simple_network()
    ctrl3 = FlowController(net3)
    ctrl3.set_path_flow("P1", 3.0)
    ctrl3.set_path_flow("P2", 5.0)
    net3.edges["e1"].is_failed = True
    net3.edges["e1"].capacity = 0.0
    net3.generate_alerts()
    states.append(("Edge e1 Failed", net3))
    
    # Create comparison visualization
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Network State Comparison', fontsize=16, fontweight='bold')
    
    for i, (title, network) in enumerate(states):
        visualizer = NetworkVisualizer()
        # Set up single subplot
        temp_fig, temp_axes = plt.subplots(2, 2, figsize=(10, 8))
        visualizer.axes = temp_axes
        visualizer.fig = temp_fig
        visualizer._build_networkx_graph(network)
        
        # Draw only topology on comparison plot
        ax = axes[i]
        ax.set_title(f'{title}\nThroughput: {network.calculate_total_throughput():.1f}, Alerts: {len(network.alerts)}')
        
        # Simple network drawing for comparison
        if visualizer.graph and visualizer.pos:
            import networkx as nx
            
            # Node colors
            node_colors = []
            for node_id in visualizer.graph.nodes():
                node = network.nodes.get(node_id)
                if node:
                    if node.type == 'source':
                        node_colors.append('#2E8B57')
                    elif node.type == 'sink':
                        node_colors.append('#DC143C')
                    else:
                        node_colors.append('#4682B4')
                else:
                    node_colors.append('#4682B4')
            
            # Draw nodes
            nx.draw_networkx_nodes(visualizer.graph, visualizer.pos, ax=ax,
                                  node_color=node_colors, node_size=600, alpha=0.8)
            
            # Edge colors based on state
            normal_edges = []
            overload_edges = []
            failed_edges = []
            
            for (u, v, data) in visualizer.graph.edges(data=True):
                edge_obj = data.get('edge_obj')
                if edge_obj:
                    if edge_obj.is_failed or edge_obj.capacity == 0:
                        failed_edges.append((u, v))
                    elif edge_obj.overload_alert or edge_obj.flow > edge_obj.capacity:
                        overload_edges.append((u, v))
                    else:
                        normal_edges.append((u, v))
            
            # Draw edges
            if normal_edges:
                nx.draw_networkx_edges(visualizer.graph, visualizer.pos, ax=ax,
                                      edgelist=normal_edges, edge_color='#708090', width=2)
            if overload_edges:
                nx.draw_networkx_edges(visualizer.graph, visualizer.pos, ax=ax,
                                      edgelist=overload_edges, edge_color='#FF4500', width=3)
            if failed_edges:
                nx.draw_networkx_edges(visualizer.graph, visualizer.pos, ax=ax,
                                      edgelist=failed_edges, edge_color='#8B0000', 
                                      width=3, style='dashed')
            
            # Labels
            nx.draw_networkx_labels(visualizer.graph, visualizer.pos, ax=ax, 
                                   font_size=10, font_weight='bold')
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.close(temp_fig)  # Clean up temporary figure
    
    plt.tight_layout()
    plt.savefig("demo_comparison.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("📸 Saved: demo_comparison.png")


def main():
    """Run complete visualization demonstration"""
    print("🚀 Starting Complete Flow Control Visualization Demo")
    print("=" * 60)
    
    try:
        # Set random seed for reproducible demo
        random.seed(42)
        
        # Run demonstration sequence
        network, controller, visualizer = demo_basic_visualization()
        demo_overload_scenario()
        demo_failure_recovery()
        demo_optimization()
        demo_time_progression()
        demo_performance_analysis()
        create_comparison_visualization()
        
        print("\n" + "=" * 60)
        print("✅ Visualization Demo Complete!")
        print("=" * 60)
        
        print("Generated visualization files:")
        import os
        demo_files = [f for f in os.listdir('.') if f.startswith('demo_')]
        for file in sorted(demo_files):
            print(f"  📸 {file}")
        
        print(f"\nTotal files generated: {len(demo_files)}")
        print("\n🎨 The visualization system demonstrates:")
        print("  • Real-time network topology display")
        print("  • Flow state monitoring with color coding") 
        print("  • Performance history tracking")
        print("  • Alert dashboard with system status")
        print("  • Multi-state comparison capabilities")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()