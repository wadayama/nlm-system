#!/usr/bin/env python3
"""
Max Flow Calculator for Flow Control System

Calculates theoretical maximum flow using min-cut max-flow theorem.
Uses NetworkX's max flow algorithms for accurate computation.
"""

import networkx as nx
from typing import Dict, Tuple, Optional
from network_model import NetworkState, create_simple_network
from flow_operations import FlowController
from network_display import NetworkCUIDisplay


class MaxFlowCalculator:
    """Calculate theoretical maximum flow for network"""
    
    def __init__(self, network: NetworkState):
        """Initialize max flow calculator"""
        self.network = network
        self.nx_graph = None
        self.max_flow_value = None
        self.min_cut = None
    
    def build_nx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from our network model"""
        G = nx.DiGraph()
        
        # Add nodes
        for node_id in self.network.nodes:
            G.add_node(node_id)
        
        # Add edges with capacity
        for edge_id, edge in self.network.edges.items():
            G.add_edge(edge.from_node, edge.to_node, 
                      capacity=edge.capacity, 
                      edge_id=edge_id)
        
        self.nx_graph = G
        return G
    
    def calculate_max_flow(self) -> Tuple[float, Dict]:
        """
        Calculate maximum flow using NetworkX's algorithms.
        
        Returns:
            Tuple of (max_flow_value, flow_dict)
        """
        if self.nx_graph is None:
            self.build_nx_graph()
        
        if not self.network.source_node or not self.network.sink_node:
            return 0.0, {}
        
        # Calculate max flow
        flow_value, flow_dict = nx.maximum_flow(
            self.nx_graph, 
            self.network.source_node, 
            self.network.sink_node
        )
        
        self.max_flow_value = flow_value
        return flow_value, flow_dict
    
    def find_min_cut(self) -> Tuple[float, Tuple[set, set]]:
        """
        Find minimum cut in the network.
        
        Returns:
            Tuple of (cut_value, (source_partition, sink_partition))
        """
        if self.nx_graph is None:
            self.build_nx_graph()
        
        if not self.network.source_node or not self.network.sink_node:
            return 0.0, (set(), set())
        
        # Find min cut
        cut_value, partition = nx.minimum_cut(
            self.nx_graph,
            self.network.source_node,
            self.network.sink_node
        )
        
        self.min_cut = (cut_value, partition)
        return cut_value, partition
    
    def get_cut_edges(self) -> list:
        """Get edges that form the minimum cut"""
        if self.min_cut is None:
            self.find_min_cut()
        
        _, (source_partition, sink_partition) = self.min_cut
        cut_edges = []
        
        for edge_id, edge in self.network.edges.items():
            if (edge.from_node in source_partition and 
                edge.to_node in sink_partition):
                cut_edges.append((edge_id, edge))
        
        return cut_edges
    
    def calculate_path_based_max_flow(self) -> float:
        """
        Calculate max flow considering only defined paths.
        This might be less than theoretical max flow.
        """
        total_max = 0.0
        
        for path_id, path in self.network.paths.items():
            bottleneck, _ = path.calculate_bottleneck(self.network.edges)
            total_max += bottleneck
        
        # This is an upper bound, actual might be less due to shared edges
        return total_max
    
    def display_max_flow_analysis(self):
        """Display comprehensive max flow analysis"""
        print("\n" + "="*70)
        print("🌊 MAX FLOW ANALYSIS (Min-Cut Max-Flow Theorem)")
        print("="*70)
        
        # Calculate max flow
        max_flow, flow_dict = self.calculate_max_flow()
        
        print(f"\n📈 Theoretical Maximum Flow: {max_flow:.2f}")
        print(f"   (Maximum s→t flow possible with current capacities)")
        
        # Calculate min cut
        cut_value, (source_part, sink_part) = self.find_min_cut()
        
        print(f"\n✂️  Minimum Cut Value: {cut_value:.2f}")
        print(f"   (Should equal max flow by min-cut max-flow theorem)")
        
        # Show cut edges
        cut_edges = self.get_cut_edges()
        if cut_edges:
            print(f"\n🔗 Cut Edges (bottleneck):")
            total_cut_capacity = 0
            for edge_id, edge in cut_edges:
                print(f"   {edge_id}: {edge.from_node}→{edge.to_node}, capacity={edge.capacity:.1f}")
                total_cut_capacity += edge.capacity
            print(f"   Total cut capacity: {total_cut_capacity:.1f}")
        
        # Compare with current flow
        current_throughput = self.network.calculate_total_throughput()
        utilization = (current_throughput / max_flow * 100) if max_flow > 0 else 0
        
        print(f"\n📊 Current vs Maximum:")
        print(f"   Current throughput: {current_throughput:.2f}")
        print(f"   Maximum possible:   {max_flow:.2f}")
        print(f"   Utilization:        {utilization:.1f}%")
        print(f"   Unused capacity:    {max_flow - current_throughput:.2f}")
        
        # Path-based analysis
        path_max = self.calculate_path_based_max_flow()
        print(f"\n🛤️  Path-Based Analysis:")
        print(f"   Sum of path capacities: {path_max:.2f}")
        if path_max > max_flow:
            print(f"   ⚠️  Paths share edges, actual max is {max_flow:.2f}")
        
        # Visual bar
        bar_length = 40
        current_fill = int((current_throughput / max_flow * bar_length)) if max_flow > 0 else 0
        bar = "█" * current_fill + "░" * (bar_length - current_fill)
        print(f"\n📉 Utilization Bar:")
        print(f"   [{bar}] {current_throughput:.1f}/{max_flow:.1f}")


def demonstrate_max_flow():
    """Demonstrate max flow calculations"""
    
    print("🌊 MAX FLOW CALCULATION DEMONSTRATION")
    print("="*70)
    
    # Test with simple network
    print("\n1️⃣ Simple 2-Path Network:")
    network1 = create_simple_network()
    controller1 = FlowController(network1)
    
    # Set some flows
    controller1.set_path_flow("P1", 5.0)
    controller1.set_path_flow("P2", 3.0)
    
    calc1 = MaxFlowCalculator(network1)
    calc1.display_max_flow_analysis()
    
    # Test with complex network from samples
    print("\n\n2️⃣ Complex Multi-Path Network:")
    from network_samples import NetworkSampleGallery
    gallery = NetworkSampleGallery()
    network2 = gallery.get_sample("complex")
    controller2 = FlowController(network2)
    
    # Set some flows
    controller2.set_path_flow("P1", 4.0)
    controller2.set_path_flow("P2", 3.0)
    controller2.set_path_flow("P3", 2.0)
    controller2.set_path_flow("P4", 1.0)
    
    calc2 = MaxFlowCalculator(network2)
    calc2.display_max_flow_analysis()


if __name__ == "__main__":
    demonstrate_max_flow()