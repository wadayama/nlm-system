#!/usr/bin/env python3
"""
CUI Display Module for Flow Control System

Provides clean command-line interface displays for network status,
throughput, alerts, and path information.
"""

from typing import Dict, List, Optional
from network_model import NetworkState, NetworkPath, NetworkEdge
from flow_operations import FlowController


class NetworkCUIDisplay:
    """Command Line User Interface display for network status"""
    
    def __init__(self):
        """Initialize CUI display"""
        self.display_width = 80
        self.compact_mode = False
    
    def print_separator(self, char='=', width=None):
        """Print a separator line"""
        width = width or self.display_width
        print(char * width)
    
    def print_header(self, title: str):
        """Print a formatted header"""
        self.print_separator('=')
        print(f" {title} ".center(self.display_width))
        self.print_separator('=')
    
    def print_section(self, title: str):
        """Print a section header"""
        print(f"\n📊 {title}")
        self.print_separator('-', 50)
    
    def display_network_status(self, network: NetworkState):
        """Display complete network status"""
        self.print_header("FLOW CONTROL NETWORK STATUS")
        
        # System overview
        self._display_system_overview(network)
        
        # Throughput summary
        self._display_throughput_summary(network)
        
        # Path information
        self._display_path_details(network)
        
        # Edge status
        self._display_edge_status(network)
        
        
        print()
    
    def _display_system_overview(self, network: NetworkState):
        """Display basic system information"""
        self.print_section("System Overview")
        
        throughput = network.calculate_total_throughput()
        violations = network.validate_flow_conservation()
        
        print(f"🌐 Network Topology:")
        print(f"   Nodes: {len(network.nodes)} | Edges: {len(network.edges)} | Paths: {len(network.paths)}")
        print(f"   Source: {network.source_node} | Sink: {network.sink_node}")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Total Throughput: {throughput:.2f}")
        print(f"   Flow Violations: {len(violations)}")
    
    def _display_throughput_summary(self, network: NetworkState):
        """Display throughput summary"""
        self.print_section("Throughput Summary")
        
        throughput = network.calculate_total_throughput()
        
        # Calculate actual max flow using min-cut max-flow theorem
        try:
            from maxflow_calculator import MaxFlowCalculator
            calc = MaxFlowCalculator(network)
            max_flow_value, _ = calc.calculate_max_flow()
            max_display_throughput = max_flow_value if max_flow_value > 0 else 50.0
        except:
            max_display_throughput = 50.0  # Fallback if calculation fails
        
        # Throughput display with bar
        bar_length = 30
        bar_fill = min(int((throughput / max_display_throughput) * bar_length), bar_length) if max_display_throughput > 0 else 0
        throughput_bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
        
        print(f"📈 Total Throughput: {throughput:.2f}")
        print(f"   [{throughput_bar}] {throughput:.1f}/{max_display_throughput:.1f} (max-flow)")
        
    
    def _display_path_details(self, network: NetworkState):
        """Display detailed path information"""
        self.print_section("s-t Path Details")
        
        if not network.paths:
            print("   ❌ No paths available")
            return
        
        print(f"{'Path ID':<8} {'Route':<15} {'Flow':<8} {'Capacity':<10} {'Utilization':<12} {'Status'}")
        self.print_separator('-', 70)
        
        for path_id, path in network.paths.items():
            route = " → ".join(path.edges)
            flow = path.current_flow
            bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(network.edges)
            
            if bottleneck_capacity > 0:
                utilization = (flow / bottleneck_capacity) * 100
                util_str = f"{utilization:.1f}%"
            else:
                util_str = "∞" if flow > 0 else "0.0%"
            
            # Status indicators
            if bottleneck_capacity == 0:
                status = "🚫 BLOCKED"
            elif flow > bottleneck_capacity:
                status = "🔴 OVERLOAD"
            elif utilization > 80:
                status = "🟡 HIGH"
            elif utilization > 50:
                status = "🟢 NORMAL"
            else:
                status = "🔵 LOW"
            
            print(f"{path_id:<8} {route:<15} {flow:<8.1f} {bottleneck_capacity:<10.1f} {util_str:<12} {status}")
        
        # Path utilization bars
        print(f"\n📊 Path Utilization Visualization:")
        for path_id, path in network.paths.items():
            bottleneck_capacity, _ = path.calculate_bottleneck(network.edges)
            if bottleneck_capacity > 0:
                util_ratio = path.current_flow / bottleneck_capacity
                bar_length = 25
                
                if util_ratio <= 1.0:
                    # Normal case: 0-100% utilization
                    filled = int(util_ratio * bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                else:
                    # Overload case: >100% utilization (show as full bar + red indicators)
                    filled = bar_length
                    over_ratio = min(util_ratio - 1.0, 1.0)  # Cap overload at 100% extra
                    over_filled = int(over_ratio * bar_length)
                    bar = "█" * filled + "🔴" * over_filled
                
                print(f"   {path_id}: [{bar}] {path.current_flow:.1f}/{bottleneck_capacity:.1f}")
    
    def _display_edge_status(self, network: NetworkState):
        """Display edge status information"""
        self.print_section("Edge Status")
        
        print(f"{'Edge ID':<8} {'From':<6} {'To':<6} {'Capacity':<10} {'Flow':<8} {'Util%':<8} {'Status'}")
        self.print_separator('-', 55)
        
        for edge_id, edge in network.edges.items():
            utilization = edge.get_utilization() * 100  # Convert to percentage
            util_str = f"{utilization:.0f}%" if utilization != float('inf') else "∞"
            
            # Status
            if edge.is_failed:
                status = "⚫ FAILED"
            elif edge.flow > edge.capacity and edge.capacity > 0:
                status = "🔴 OVER"
            elif utilization > 90:
                status = "🟡 HIGH"
            else:
                status = "🟢 OK"
            
            print(f"{edge_id:<8} {edge.from_node:<6} {edge.to_node:<6} {edge.capacity:<10.1f} {edge.flow:<8.1f} {util_str:<8} {status}")
    
    
    def display_compact_status(self, network: NetworkState):
        """Display compact one-line status"""
        throughput = network.calculate_total_throughput()
        
        # Path utilizations
        path_utils = []
        for path_id, path in network.paths.items():
            bottleneck_capacity, _ = path.calculate_bottleneck(network.edges)
            if bottleneck_capacity > 0:
                util = (path.current_flow / bottleneck_capacity) * 100
                path_utils.append(f"{path_id}:{util:.0f}%")
            else:
                path_utils.append(f"{path_id}:∞")
        
        path_str = " ".join(path_utils)
        
        print(f"Throughput:{throughput:6.1f} | {path_str}")
    


def demo_cui_display():
    """Demonstrate CUI display functionality"""
    from network_model import create_simple_network
    
    print("🖥️  Flow Control Network - CUI Display Demo")
    print("=" * 80)
    
    # Create network with some flows
    network = create_simple_network()
    controller = FlowController(network)
    display = NetworkCUIDisplay()
    
    # Set up interesting scenario
    controller.set_path_flow("P1", 12.0)
    controller.set_path_flow("P2", 3.0)
    
    # Display full status
    display.display_network_status(network)
    
    # Demonstrate compact status
    print("\n" + "=" * 80)
    print("📺 COMPACT STATUS DEMONSTRATION")
    print("=" * 80)
    
    display.display_compact_status(network)


if __name__ == "__main__":
    demo_cui_display()