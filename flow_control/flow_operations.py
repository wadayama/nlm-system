#!/usr/bin/env python3
"""
Flow Operations for Flow Control System

Functions for managing flow updates, path-based control, and flow conservation
in the s-t network flow control problem.
"""

from typing import Dict, List, Tuple, Optional
from network_model import NetworkState, NetworkPath, NetworkEdge, NetworkNode


class FlowController:
    """Core flow control operations"""
    
    def __init__(self, network: NetworkState):
        """
        Initialize flow controller.
        
        Args:
            network: NetworkState to control
        """
        self.network = network
    
    def update_path_flow(self, path_id: str, delta_flow: float) -> Tuple[bool, str]:
        """
        Update flow on a specific path by changing all constituent edges.
        
        Args:
            path_id: ID of path to modify
            delta_flow: Flow change (positive=increase, negative=decrease)
            
        Returns:
            Tuple of (success, message)
        """
        if path_id not in self.network.paths:
            return False, f"Path {path_id} not found"
        
        path = self.network.paths[path_id]
        
        # Check if path can accommodate this flow change
        can_accommodate, reason = path.can_accommodate_flow(delta_flow, self.network.edges)
        if not can_accommodate:
            return False, f"Cannot update flow: {reason}"
        
        # Apply flow change to all edges in the path
        for edge_id in path.edges:
            if edge_id in self.network.edges:
                edge = self.network.edges[edge_id]
                edge.flow += delta_flow
                # Ensure flow doesn't go negative
                edge.flow = max(0.0, edge.flow)
        
        # Update path flow tracking
        path.current_flow += delta_flow
        path.current_flow = max(0.0, path.current_flow)
        
        return True, f"Updated path {path_id} flow by {delta_flow:.2f}"
    
    def set_path_flow(self, path_id: str, target_flow: float) -> Tuple[bool, str]:
        """
        Set absolute flow on a path.
        
        Args:
            path_id: ID of path to modify
            target_flow: Target flow value
            
        Returns:
            Tuple of (success, message)
        """
        if path_id not in self.network.paths:
            return False, f"Path {path_id} not found"
        
        path = self.network.paths[path_id]
        current_flow = path.current_flow
        delta_flow = target_flow - current_flow
        
        return self.update_path_flow(path_id, delta_flow)
    
    def clear_all_flows(self) -> None:
        """Reset all flows to zero"""
        for edge in self.network.edges.values():
            edge.flow = 0.0
        for path in self.network.paths.values():
            path.current_flow = 0.0
    
    def distribute_flow_equally(self, total_flow: float) -> Tuple[bool, str]:
        """
        Distribute total flow equally among all available paths.
        
        Args:
            total_flow: Total flow to distribute
            
        Returns:
            Tuple of (success, message)
        """
        if not self.network.paths:
            return False, "No paths available"
        
        # Clear existing flows
        self.clear_all_flows()
        
        # Calculate flow per path
        flow_per_path = total_flow / len(self.network.paths)
        
        success_count = 0
        messages = []
        
        for path_id in self.network.paths:
            success, message = self.set_path_flow(path_id, flow_per_path)
            if success:
                success_count += 1
            messages.append(message)
        
        if success_count == len(self.network.paths):
            return True, f"Successfully distributed {total_flow:.2f} flow equally among {len(self.network.paths)} paths"
        else:
            return False, f"Partially successful: {success_count}/{len(self.network.paths)} paths updated"
    
    def get_path_utilizations(self) -> Dict[str, float]:
        """
        Get utilization ratios for all paths.
        
        Returns:
            Dictionary of path_id -> utilization ratio
        """
        utilizations = {}
        
        for path_id, path in self.network.paths.items():
            bottleneck_capacity, _ = path.calculate_bottleneck(self.network.edges)
            if bottleneck_capacity > 0:
                utilizations[path_id] = path.current_flow / bottleneck_capacity
            else:
                utilizations[path_id] = float('inf') if path.current_flow > 0 else 0.0
        
        return utilizations
    
    def handle_failed_edges(self) -> Tuple[int, List[str]]:
        """
        Detect failed edges and automatically zero flows on affected paths.
        
        An edge is considered failed if:
        - is_failed flag is True, OR
        - capacity is 0
        
        Returns:
            Tuple of (number of paths affected, list of affected path IDs)
        """
        affected_paths = set()
        
        # Find all failed edges
        failed_edges = []
        for edge_id, edge in self.network.edges.items():
            if edge.is_failed or edge.capacity == 0:
                failed_edges.append(edge_id)
        
        # Find all paths using failed edges
        for path_id, path in self.network.paths.items():
            for edge_id in path.edges:
                if edge_id in failed_edges:
                    affected_paths.add(path_id)
                    break
        
        # Zero the flow on affected paths
        zeroed_paths = []
        for path_id in affected_paths:
            if self.network.paths[path_id].current_flow > 0:
                success, _ = self.set_path_flow(path_id, 0.0)
                if success:
                    zeroed_paths.append(path_id)
        
        return len(zeroed_paths), zeroed_paths
    
    def calculate_max_safe_flow(self, path_id: str) -> Dict:
        """
        Calculate maximum safe flow for a path and provide alternatives.
        
        Args:
            path_id: ID of path to analyze
            
        Returns:
            Dictionary with flow alternatives and bottleneck information
        """
        if path_id not in self.network.paths:
            return {'error': f'Path {path_id} not found'}
        
        path = self.network.paths[path_id]
        
        # Calculate bottleneck information
        bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(self.network.edges)
        
        # Calculate maximum safe flow (cannot exceed bottleneck)
        max_safe_flow = bottleneck_capacity
        
        # Calculate available capacity (considering current flow)
        available_capacity = max(0, bottleneck_capacity - path.current_flow)
        
        # Suggested flow (current + available, or max safe if starting from zero)
        suggested_flow = min(path.current_flow + available_capacity, max_safe_flow)
        
        return {
            'path_id': path_id,
            'current_flow': path.current_flow,
            'max_safe_flow': max_safe_flow,
            'available_capacity': available_capacity,
            'suggested_flow': suggested_flow,
            'bottleneck_edge': bottleneck_edge,
            'bottleneck_capacity': bottleneck_capacity,
            'edge_sequence': path.edges,
            'is_blocked': bottleneck_capacity <= 0
        }
    
    def set_path_flow_with_alternatives(self, path_id: str, target_flow: float) -> Tuple[bool, str, Dict]:
        """
        Set path flow with detailed alternatives on failure.
        
        Args:
            path_id: ID of path to modify
            target_flow: Target flow value
            
        Returns:
            Tuple of (success, message, alternatives_dict)
        """
        if path_id not in self.network.paths:
            return False, f"Path {path_id} not found", {}
        
        # Try normal flow setting first
        success, message = self.set_path_flow(path_id, target_flow)
        
        # If successful, return with basic info
        if success:
            alternatives = self.calculate_max_safe_flow(path_id)
            return True, message, alternatives
        
        # If failed, provide detailed alternatives
        alternatives = self.calculate_max_safe_flow(path_id)
        
        # Enhance error message with alternatives
        if alternatives and not alternatives.get('error'):
            enhanced_message = message + f"\n💡 Alternatives:"
            enhanced_message += f"\n   • Max safe flow: {alternatives['max_safe_flow']:.1f}"
            enhanced_message += f"\n   • Current available: {alternatives['available_capacity']:.1f}"
            enhanced_message += f"\n   • Bottleneck: {alternatives['bottleneck_edge']} (capacity {alternatives['bottleneck_capacity']:.1f})"
            enhanced_message += f"\n   • Suggested: {alternatives['suggested_flow']:.1f}"
            
            return False, enhanced_message, alternatives
        
        return False, message, alternatives
    
    def saturate_path_flow(self, path_id: str) -> Tuple[bool, str, Dict]:
        """
        Saturate a path by setting its flow to the bottleneck capacity.
        
        Args:
            path_id: ID of path to saturate
            
        Returns:
            Tuple of (success, message, info_dict)
        """
        if path_id not in self.network.paths:
            return False, f"Path {path_id} not found", {}
        
        # Get current path information
        alternatives = self.calculate_max_safe_flow(path_id)
        if 'error' in alternatives:
            return False, alternatives['error'], {}
        
        # Check if path is blocked
        if alternatives['is_blocked']:
            return False, f"Path {path_id} is blocked (bottleneck capacity = 0)", alternatives
        
        current_flow = alternatives['current_flow']
        max_safe_flow = alternatives['max_safe_flow']
        bottleneck_edge = alternatives['bottleneck_edge']
        
        # Check if already saturated
        if abs(current_flow - max_safe_flow) < 0.001:  # Floating point tolerance
            message = f"Path {path_id} already saturated at {current_flow:.1f} (bottleneck: {bottleneck_edge})"
            return True, message, alternatives
        
        # Set flow to saturation level
        success, set_message = self.set_path_flow(path_id, max_safe_flow)
        
        if success:
            message = f"Path {path_id} saturated: {current_flow:.1f} → {max_safe_flow:.1f} (bottleneck: {bottleneck_edge})"
            # Update alternatives with new current flow
            updated_alternatives = self.calculate_max_safe_flow(path_id)
            return True, message, updated_alternatives
        else:
            return False, f"Failed to saturate {path_id}: {set_message}", alternatives
    
    def get_path_info(self, path_id: str) -> Dict:
        """
        Get comprehensive information about a specific path.
        
        Args:
            path_id: ID of path to analyze
            
        Returns:
            Dictionary with detailed path information
        """
        if path_id not in self.network.paths:
            return {'error': f'Path {path_id} not found'}
        
        path = self.network.paths[path_id]
        
        # Calculate bottleneck information
        bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(self.network.edges)
        
        # Calculate utilization
        utilization = (path.current_flow / bottleneck_capacity) if bottleneck_capacity > 0 else float('inf')
        
        # Determine status
        if bottleneck_capacity <= 0:
            status = "BLOCKED"
        elif utilization >= 1.0:
            status = "SATURATED"
        elif utilization >= 0.8:
            status = "HIGH"
        elif utilization >= 0.5:
            status = "NORMAL"
        else:
            status = "LOW"
        
        # Get edge details
        edge_details = []
        for edge_id in path.edges:
            if edge_id in self.network.edges:
                edge = self.network.edges[edge_id]
                edge_flow = sum(p.current_flow for p in self.network.paths.values() if edge_id in p.edges)
                edge_util = (edge_flow / edge.capacity) if edge.capacity > 0 else float('inf')
                edge_details.append({
                    'id': edge_id,
                    'from': edge.from_node,
                    'to': edge.to_node,
                    'capacity': edge.capacity,
                    'flow': edge_flow,
                    'utilization': edge_util,
                    'is_bottleneck': edge_id == bottleneck_edge
                })
        
        # Find other paths sharing edges
        shared_paths = set()
        for other_path_id, other_path in self.network.paths.items():
            if other_path_id != path_id:
                if set(path.edges) & set(other_path.edges):  # Common edges
                    shared_paths.add(other_path_id)
        
        return {
            'path_id': path_id,
            'edges': path.edges,
            'edge_count': len(path.edges),
            'current_flow': path.current_flow,
            'bottleneck_capacity': bottleneck_capacity,
            'bottleneck_edge': bottleneck_edge,
            'utilization': utilization,
            'available_capacity': max(0, bottleneck_capacity - path.current_flow),
            'status': status,
            'is_blocked': bottleneck_capacity <= 0,
            'edge_details': edge_details,
            'shared_paths': list(shared_paths),
            'route_description': ' → '.join([f"{self.network.edges[eid].from_node}" for eid in path.edges[:1]] + 
                                           [f"{self.network.edges[eid].to_node}" for eid in path.edges])
        }
    
    def get_edge_info(self, edge_id: str) -> Dict:
        """
        Get comprehensive information about a specific edge.
        
        Args:
            edge_id: ID of edge to analyze
            
        Returns:
            Dictionary with detailed edge information
        """
        if edge_id not in self.network.edges:
            return {'error': f'Edge {edge_id} not found'}
        
        edge = self.network.edges[edge_id]
        
        # Calculate total flow through this edge
        total_flow = sum(path.current_flow for path in self.network.paths.values() if edge_id in path.edges)
        
        # Calculate utilization
        utilization = (total_flow / edge.capacity) if edge.capacity > 0 else float('inf')
        available_capacity = max(0, edge.capacity - total_flow)
        
        # Determine status
        if edge.capacity <= 0:
            status = "DISABLED"
        elif utilization > 1.0:
            status = "OVERLOAD"
        elif utilization >= 0.8:
            status = "HIGH"
        elif utilization >= 0.5:
            status = "NORMAL"
        else:
            status = "LOW"
        
        # Find paths using this edge
        using_paths = []
        for path_id, path in self.network.paths.items():
            if edge_id in path.edges:
                using_paths.append({
                    'path_id': path_id,
                    'path_flow': path.current_flow,
                    'path_position': path.edges.index(edge_id) + 1,  # 1-indexed position
                    'total_edges': len(path.edges)
                })
        
        # Check if this edge is a bottleneck for any path
        bottleneck_for = []
        for path_id, path in self.network.paths.items():
            if edge_id in path.edges:
                bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(self.network.edges)
                if bottleneck_edge == edge_id:
                    bottleneck_for.append(path_id)
        
        return {
            'edge_id': edge_id,
            'from_node': edge.from_node,
            'to_node': edge.to_node,
            'capacity': edge.capacity,
            'current_flow': total_flow,
            'utilization': utilization,
            'available_capacity': available_capacity,
            'status': status,
            'is_disabled': edge.capacity <= 0,
            'is_overloaded': utilization > 1.0,
            'using_paths': using_paths,
            'path_count': len(using_paths),
            'bottleneck_for': bottleneck_for,
            'is_critical': len(bottleneck_for) > 0
        }
    
    def get_complete_network_state(self) -> Dict:
        """
        Get complete observable network state for control decisions.
        
        Returns all edge capacities, flows, path states, and system metrics
        that a flow controller needs to make informed decisions.
        
        Returns:
            Dictionary with complete network state information
        """
        state = {
            'edges': {},
            'paths': {},
            'system_metrics': {},
        }
        
        # Complete edge information
        for edge_id, edge in self.network.edges.items():
            state['edges'][edge_id] = {
                'from_node': edge.from_node,
                'to_node': edge.to_node,
                'capacity': edge.capacity,
                'current_flow': edge.flow,
                'base_capacity': edge.base_capacity,
                'is_failed': edge.is_failed,
                'utilization': edge.get_utilization(),
                'available_capacity': max(0, edge.capacity - edge.flow)
            }
        
        # Complete path information
        for path_id, path in self.network.paths.items():
            bottleneck_capacity, bottleneck_edge = path.calculate_bottleneck(self.network.edges)
            
            state['paths'][path_id] = {
                'edge_sequence': path.edges,
                'current_flow': path.current_flow,
                'bottleneck_capacity': bottleneck_capacity,
                'bottleneck_edge': bottleneck_edge,
                'utilization': (path.current_flow / bottleneck_capacity) if bottleneck_capacity > 0 else float('inf'),
                'available_capacity': max(0, bottleneck_capacity - path.current_flow),
                'is_blocked': bottleneck_capacity <= 0
            }
        
        # System-wide metrics
        total_throughput = self.network.calculate_total_throughput()
        violations = self.network.validate_flow_conservation()
        
        # Calculate theoretical maximum flow
        try:
            from maxflow_calculator import MaxFlowCalculator
            calc = MaxFlowCalculator(self.network)
            max_flow_value, _ = calc.calculate_max_flow()
        except:
            max_flow_value = 0.0
        
        state['system_metrics'] = {
            'total_throughput': total_throughput,
            'theoretical_max_flow': max_flow_value,
            'network_efficiency': (total_throughput / max_flow_value) if max_flow_value > 0 else 0.0,
            'flow_conservation_violations': len(violations),
            'operational_edges': len([e for e in self.network.edges.values() if not e.is_failed]),
            'failed_edges': len([e for e in self.network.edges.values() if e.is_failed]),
            'blocked_paths': len([p for p_id, p in state['paths'].items() if p['is_blocked']])
        }
        
        
        return state
    
    def find_best_path(self, criteria: str = "capacity") -> Optional[str]:
        """
        Find the best available path based on criteria.
        
        Args:
            criteria: Selection criteria ("capacity", "utilization", "flow")
            
        Returns:
            Path ID of best path, or None if no paths available
        """
        if not self.network.paths:
            return None
        
        best_path = None
        best_value = None
        
        for path_id, path in self.network.paths.items():
            if criteria == "capacity":
                bottleneck_capacity, _ = path.calculate_bottleneck(self.network.edges)
                value = bottleneck_capacity
                if best_value is None or value > best_value:
                    best_value = value
                    best_path = path_id
            
            elif criteria == "utilization":
                utilizations = self.get_path_utilizations()
                value = utilizations.get(path_id, float('inf'))
                if best_value is None or value < best_value:
                    best_value = value
                    best_path = path_id
            
            elif criteria == "flow":
                value = path.current_flow
                if best_value is None or value < best_value:
                    best_value = value
                    best_path = path_id
        
        return best_path
    
    def disable_edge(self, edge_id: str) -> Tuple[bool, str]:
        """
        Disable an edge by setting its capacity to 0 (simulates failure).
        
        Args:
            edge_id: ID of edge to disable
            
        Returns:
            (success, message)
        """
        if edge_id not in self.network.edges:
            available = ", ".join(self.network.edges.keys())
            return False, f"Edge {edge_id} not found. Available: {available}"
        
        edge = self.network.edges[edge_id]
        if edge.is_failed:
            return False, f"Edge {edge_id} is already disabled"
        
        # Store original capacity for recovery
        if not hasattr(edge, 'original_capacity'):
            edge.original_capacity = edge.capacity
        
        # Disable edge
        edge.capacity = 0.0
        edge.is_failed = True
        
        # Clear flows on affected paths
        affected_paths = []
        for path_id, path in self.network.paths.items():
            if edge_id in path.edges:
                if path.current_flow > 0:
                    path.current_flow = 0.0
                    affected_paths.append(path_id)
        
        # Recalculate edge flows based on current path flows
        for edge in self.network.edges.values():
            edge.flow = 0.0
        
        for path in self.network.paths.values():
            for edge_id in path.edges:
                if edge_id in self.network.edges:
                    self.network.edges[edge_id].flow += path.current_flow
        
        affected_str = f" (cleared flows: {', '.join(affected_paths)})" if affected_paths else ""
        return True, f"Edge {edge_id} disabled{affected_str}"
    
    def enable_edge(self, edge_id: str) -> Tuple[bool, str]:
        """
        Enable a disabled edge by restoring its original capacity.
        
        Args:
            edge_id: ID of edge to enable
            
        Returns:
            (success, message)
        """
        if edge_id not in self.network.edges:
            available = ", ".join(self.network.edges.keys())
            return False, f"Edge {edge_id} not found. Available: {available}"
        
        edge = self.network.edges[edge_id]
        if not edge.is_failed:
            return False, f"Edge {edge_id} is already enabled"
        
        # Restore original capacity
        if hasattr(edge, 'original_capacity'):
            edge.capacity = edge.original_capacity
        else:
            edge.capacity = edge.base_capacity
        
        edge.is_failed = False
        
        return True, f"Edge {edge_id} enabled (capacity: {edge.capacity:.1f})"
    
    def list_edge_status(self) -> Dict:
        """
        Get status of all edges.
        
        Returns:
            Dictionary with edge status information
        """
        edge_status = {}
        
        for edge_id, edge in self.network.edges.items():
            edge_status[edge_id] = {
                'from': edge.from_node,
                'to': edge.to_node,
                'capacity': edge.capacity,
                'flow': edge.flow,
                'is_failed': edge.is_failed,
                'utilization': edge.get_utilization() if edge.capacity > 0 else 0.0,
                'status': 'DISABLED' if edge.is_failed else ('OVERLOAD' if edge.flow > edge.capacity else 'OK')
            }
        
        return edge_status
    
    def validate_and_report(self) -> Dict:
        """
        Comprehensive validation of current flow state.
        
        Returns:
            Dictionary with validation results
        """
        # Check flow conservation
        violations = self.network.validate_flow_conservation()
        
        # Check capacity constraints
        overloads = []
        for edge_id, edge in self.network.edges.items():
            if edge.flow > edge.capacity and edge.capacity > 0:
                overloads.append({
                    'edge_id': edge_id,
                    'flow': edge.flow,
                    'capacity': edge.capacity,
                    'violation': edge.flow - edge.capacity
                })
        
        # Calculate total throughput
        total_throughput = self.network.calculate_total_throughput()
        
        # Get path utilizations
        path_utilizations = self.get_path_utilizations()
        
        return {
            'conservation_violations': violations,
            'capacity_overloads': overloads,
            'total_throughput': total_throughput,
            'path_utilizations': path_utilizations,
            'is_valid': len(violations) == 0,
            'has_overloads': len(overloads) > 0
        }



def create_flow_test_scenario(network: NetworkState) -> None:
    """
    Create a test scenario with some initial flows for testing.
    
    Args:
        network: Network to set up
    """
    controller = FlowController(network)
    
    # Add some test flows
    if "P1" in network.paths:
        controller.set_path_flow("P1", 3.0)
    if "P2" in network.paths:
        controller.set_path_flow("P2", 2.0)


if __name__ == "__main__":
    # Test with the simple network
    from network_model import create_simple_network
    
    print("Testing Flow Operations...")
    network = create_simple_network()
    controller = FlowController(network)
    
    # Test basic flow updates
    print("\n1. Testing basic flow operations:")
    success, msg = controller.set_path_flow("P1", 5.0)
    print(f"Set P1 flow to 5.0: {success} - {msg}")
    
    success, msg = controller.set_path_flow("P2", 3.0)
    print(f"Set P2 flow to 3.0: {success} - {msg}")
    
    # Check current state
    print(f"\nCurrent throughput: {network.calculate_total_throughput():.2f}")
    
    # Test validation
    print("\n2. Testing validation:")
    validation_result = controller.validate_and_report()
    print(f"Validation: {validation_result}")
    
    # Test path utilizations
    print("\n3. Path utilizations:")
    utilizations = controller.get_path_utilizations()
    for path_id, util in utilizations.items():
        print(f"  Path {path_id}: {util:.2f}")
    
    # Test edge failure handling
    print("\n4. Testing edge failure handling:")
    network.edges["e1"].is_failed = True
    network.edges["e1"].capacity = 0.0
    num_affected, affected_paths = controller.handle_failed_edges()
    print(f"  Affected paths: {affected_paths} (zeroed {num_affected} paths)")
    
    print(f"\nFinal network state:")
    print(network.get_network_summary())
    
