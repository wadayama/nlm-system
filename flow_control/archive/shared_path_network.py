#!/usr/bin/env python3
"""
Shared Path Network Model

Demonstrates flow control with overlapping paths where multiple paths
share common edges, requiring careful flow aggregation and management.
"""

from typing import Dict, List, Tuple
from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath
from flow_operations import FlowController
from network_display import NetworkCUIDisplay


def create_shared_path_network() -> NetworkState:
    """
    Create a network with overlapping paths.
    
    Network topology:
        e1       e5
    s ─────→ v1 ─────→ t
    │        │ ↘ e6   ↑
    │  e2    │   ↘    │ e7
    └─────→ v2     v3 ─┘
             ↘ e3 ↗
              ↘ ↗
               X (共有エッジ e3)
              ↗ ↘
             ↗   ↘ e4
            
    Paths:
    - P1: s → v1 → t        (e1 → e5)
    - P2: s → v2 → v3 → t   (e2 → e3 → e7)  
    - P3: s → v1 → v3 → t   (e1 → e6 → e7)  ← e1,e7を他パスと共有
    - P4: s → v2 → v1 → t   (e2 → e4 → e5)  ← e2,e5を他パスと共有
    """
    network = NetworkState()
    
    # Create nodes
    nodes = {
        's': NetworkNode('s', 'source'),
        'v1': NetworkNode('v1', 'intermediate'),
        'v2': NetworkNode('v2', 'intermediate'),
        'v3': NetworkNode('v3', 'intermediate'),
        't': NetworkNode('t', 'sink')
    }
    
    for node in nodes.values():
        network.add_node(node)
    
    # Create edges with different capacities
    edges = {
        'e1': NetworkEdge('e1', 's', 'v1', 15.0),   # s → v1
        'e2': NetworkEdge('e2', 's', 'v2', 12.0),   # s → v2
        'e3': NetworkEdge('e3', 'v2', 'v3', 8.0),   # v2 → v3 (ボトルネック候補)
        'e4': NetworkEdge('e4', 'v2', 'v1', 6.0),   # v2 → v1 (クロスリンク)
        'e5': NetworkEdge('e5', 'v1', 't', 10.0),   # v1 → t
        'e6': NetworkEdge('e6', 'v1', 'v3', 7.0),   # v1 → v3
        'e7': NetworkEdge('e7', 'v3', 't', 14.0)    # v3 → t
    }
    
    for edge in edges.values():
        network.add_edge(edge)
    
    # Define paths (some share edges)
    paths = {
        'P1': NetworkPath('P1', ['e1', 'e5']),        # 独立: s→v1→t
        'P2': NetworkPath('P2', ['e2', 'e3', 'e7']),  # e3経由: s→v2→v3→t
        'P3': NetworkPath('P3', ['e1', 'e6', 'e7']),  # e1,e7共有: s→v1→v3→t
        'P4': NetworkPath('P4', ['e2', 'e4', 'e5'])   # e2,e5共有: s→v2→v1→t
    }
    
    for path in paths.values():
        network.add_path(path)
    
    return network


class SharedPathFlowManager:
    """Manager for handling flows on overlapping paths"""
    
    def __init__(self, network: NetworkState):
        """Initialize shared path flow manager"""
        self.network = network
        self.controller = FlowController(network)
        self.display = NetworkCUIDisplay()
        
        # Build edge-to-paths mapping
        self.edge_to_paths = self._build_edge_path_mapping()
    
    def _build_edge_path_mapping(self) -> Dict[str, List[str]]:
        """Build mapping of which paths use each edge"""
        edge_to_paths = {}
        
        for path_id, path in self.network.paths.items():
            for edge_id in path.edges:
                if edge_id not in edge_to_paths:
                    edge_to_paths[edge_id] = []
                edge_to_paths[edge_id].append(path_id)
        
        return edge_to_paths
    
    def calculate_edge_flows(self) -> Dict[str, float]:
        """
        Calculate actual edge flows by summing path flows.
        
        For shared edges, the flow is the sum of all paths using that edge.
        """
        edge_flows = {}
        
        for edge_id in self.network.edges:
            edge_flows[edge_id] = 0.0
            
            # Sum flows from all paths using this edge
            if edge_id in self.edge_to_paths:
                for path_id in self.edge_to_paths[edge_id]:
                    path = self.network.paths[path_id]
                    edge_flows[edge_id] += path.current_flow
        
        return edge_flows
    
    def update_edge_flows_from_paths(self):
        """Update all edge flows based on current path flows"""
        edge_flows = self.calculate_edge_flows()
        
        for edge_id, flow in edge_flows.items():
            self.network.edges[edge_id].flow = flow
    
    def display_shared_edge_analysis(self):
        """Display analysis of shared edges"""
        print("\n📊 Shared Edge Analysis")
        print("=" * 70)
        
        # Find shared edges
        shared_edges = {edge_id: paths for edge_id, paths in self.edge_to_paths.items() 
                       if len(paths) > 1}
        
        if not shared_edges:
            print("No shared edges in this network.")
            return
        
        print(f"{'Edge':<6} {'Capacity':<10} {'Total Flow':<12} {'Paths Using Edge':<30} {'Status'}")
        print("-" * 70)
        
        for edge_id, path_list in sorted(shared_edges.items()):
            edge = self.network.edges[edge_id]
            path_str = ", ".join(path_list)
            
            # Calculate total flow from paths
            total_flow = sum(self.network.paths[pid].current_flow for pid in path_list)
            
            # Status
            if total_flow > edge.capacity:
                status = "🔴 OVER"
            elif total_flow > edge.capacity * 0.8:
                status = "🟡 HIGH"
            else:
                status = "🟢 OK"
            
            print(f"{edge_id:<6} {edge.capacity:<10.1f} {total_flow:<12.1f} {path_str:<30} {status}")
        
        # Show flow breakdown
        print("\n📈 Flow Breakdown by Path:")
        for edge_id, path_list in sorted(shared_edges.items()):
            print(f"\n{edge_id} (capacity={self.network.edges[edge_id].capacity:.1f}):")
            for path_id in path_list:
                flow = self.network.paths[path_id].current_flow
                print(f"  └─ {path_id}: {flow:.1f}")
            total = sum(self.network.paths[pid].current_flow for pid in path_list)
            print(f"  Total: {total:.1f}")
    
    def check_shared_edge_constraints(self) -> List[Tuple[str, float, float]]:
        """
        Check capacity constraints on shared edges.
        
        Returns:
            List of (edge_id, total_flow, capacity) for violated edges
        """
        violations = []
        
        edge_flows = self.calculate_edge_flows()
        
        for edge_id, total_flow in edge_flows.items():
            edge = self.network.edges[edge_id]
            if total_flow > edge.capacity:
                violations.append((edge_id, total_flow, edge.capacity))
        
        return violations
    
    def optimize_with_sharing(self) -> Tuple[bool, str]:
        """
        Optimize flows considering shared edge constraints.
        
        This is a more complex optimization that accounts for edge sharing.
        """
        # Simple heuristic: reduce flows on paths that share overloaded edges
        violations = self.check_shared_edge_constraints()
        
        if not violations:
            return True, "No shared edge violations found"
        
        adjustments = []
        
        for edge_id, total_flow, capacity in violations:
            overload = total_flow - capacity
            paths_using = self.edge_to_paths.get(edge_id, [])
            
            if len(paths_using) > 1:
                # Distribute reduction among paths using this edge
                reduction_per_path = overload / len(paths_using)
                
                for path_id in paths_using:
                    current_flow = self.network.paths[path_id].current_flow
                    new_flow = max(0, current_flow - reduction_per_path)
                    self.controller.set_path_flow(path_id, new_flow)
                    adjustments.append(f"{path_id}→{new_flow:.1f}")
        
        return True, f"Adjusted flows: {', '.join(adjustments)}"


def demonstrate_shared_paths():
    """Demonstrate flow control with shared paths"""
    print("🔀 SHARED PATH NETWORK DEMONSTRATION")
    print("=" * 80)
    
    # Create network
    network = create_shared_path_network()
    manager = SharedPathFlowManager(network)
    display = NetworkCUIDisplay()
    
    print("\n📐 Network Topology:")
    print("  Nodes: s, v1, v2, v3, t")
    print("  Paths:")
    print("    P1: s → v1 → t       (e1 → e5)")
    print("    P2: s → v2 → v3 → t  (e2 → e3 → e7)")
    print("    P3: s → v1 → v3 → t  (e1 → e6 → e7) ← shares e1 with P1, e7 with P2")
    print("    P4: s → v2 → v1 → t  (e2 → e4 → e5) ← shares e2 with P2, e5 with P1")
    
    # Set initial flows
    print("\n🎛️  Setting initial path flows:")
    manager.controller.set_path_flow('P1', 5.0)
    manager.controller.set_path_flow('P2', 4.0)
    manager.controller.set_path_flow('P3', 3.0)
    manager.controller.set_path_flow('P4', 2.0)
    
    # Update edge flows based on path flows
    manager.update_edge_flows_from_paths()
    network.generate_alerts()
    
    print("  P1: 5.0, P2: 4.0, P3: 3.0, P4: 2.0")
    
    # Show edge analysis
    manager.display_shared_edge_analysis()
    
    # Check constraints
    print("\n⚠️  Constraint Check:")
    violations = manager.check_shared_edge_constraints()
    if violations:
        print("  Capacity violations detected:")
        for edge_id, total_flow, capacity in violations:
            print(f"    {edge_id}: flow={total_flow:.1f} > capacity={capacity:.1f}")
    else:
        print("  ✅ All shared edges within capacity")
    
    # Display full status
    print()
    display.display_network_status(network)
    
    # Optimize
    print("\n🔧 Optimizing with shared edge constraints...")
    success, msg = manager.optimize_with_sharing()
    print(f"  {msg}")
    
    # Update and show results
    manager.update_edge_flows_from_paths()
    network.generate_alerts()
    
    print("\n📊 After Optimization:")
    manager.display_shared_edge_analysis()
    
    # Final status
    print("\n" + "=" * 80)
    print("🏁 Final Network State:")
    display.display_compact_status(network)


if __name__ == "__main__":
    demonstrate_shared_paths()