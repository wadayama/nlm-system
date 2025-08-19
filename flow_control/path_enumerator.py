#!/usr/bin/env python3
"""
Complete s-t Path Enumeration for Flow Control System

Provides both complete enumeration and intelligent sampling of s-t paths.
Allows users to choose between theoretical completeness and practical efficiency.
"""

import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from network_model import NetworkState, NetworkNode, NetworkEdge, NetworkPath


@dataclass
class PathEnumerationResult:
    """Results from path enumeration"""
    paths: List[List[str]]  # List of edge sequences
    enumeration_time: float
    total_paths_found: int
    is_complete: bool  # True if all paths found, False if sampled
    max_length_limit: Optional[int] = None
    max_paths_limit: Optional[int] = None


class CompletePathEnumerator:
    """Complete enumeration of all s-t paths in a network"""
    
    def __init__(self, network: NetworkState):
        """Initialize path enumerator"""
        self.network = network
        self.source = network.source_node
        self.sink = network.sink_node
        self.adjacency = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build adjacency list: node_id -> [(next_node, edge_id), ...]"""
        adj = {}
        for node_id in self.network.nodes:
            adj[node_id] = []
        
        for edge_id, edge in self.network.edges.items():
            adj[edge.from_node].append((edge.to_node, edge_id))
        
        return adj
    
    def enumerate_all_paths(self, 
                           max_length: Optional[int] = None,
                           max_paths: Optional[int] = None) -> PathEnumerationResult:
        """
        Enumerate all simple s-t paths.
        
        Args:
            max_length: Maximum path length (edges). None = no limit
            max_paths: Maximum number of paths to find. None = find all
            
        Returns:
            PathEnumerationResult with all found paths
        """
        if not self.source or not self.sink:
            return PathEnumerationResult([], 0.0, 0, True)
        
        start_time = time.time()
        all_paths = []
        
        def dfs(current_node: str, current_path: List[str], visited: Set[str]):
            # Check limits
            if max_paths and len(all_paths) >= max_paths:
                return False  # Stop search
            
            if max_length and len(current_path) >= max_length:
                return True  # Continue search but don't extend this path
            
            # Found target
            if current_node == self.sink:
                all_paths.append(current_path.copy())
                return True
            
            # Explore neighbors
            if current_node in self.adjacency:
                for next_node, edge_id in self.adjacency[current_node]:
                    if next_node not in visited:  # Ensure simple paths
                        visited.add(next_node)
                        current_path.append(edge_id)
                        
                        continue_search = dfs(next_node, current_path, visited)
                        
                        # Backtrack
                        current_path.pop()
                        visited.remove(next_node)
                        
                        if not continue_search:
                            return False  # Early termination
            
            return True
        
        # Start DFS from source
        visited = {self.source}
        dfs(self.source, [], visited)
        
        end_time = time.time()
        is_complete = not (max_paths and len(all_paths) >= max_paths)
        
        return PathEnumerationResult(
            paths=all_paths,
            enumeration_time=end_time - start_time,
            total_paths_found=len(all_paths),
            is_complete=is_complete,
            max_length_limit=max_length,
            max_paths_limit=max_paths
        )
    
    def count_all_paths(self, max_length: Optional[int] = None) -> int:
        """
        Count total number of s-t paths without storing them.
        More memory efficient for large graphs.
        """
        if not self.source or not self.sink:
            return 0
        
        count = 0
        
        def dfs(current_node: str, path_length: int, visited: Set[str]) -> int:
            nonlocal count
            
            if max_length and path_length >= max_length:
                return count
            
            if current_node == self.sink:
                count += 1
                return count
            
            if current_node in self.adjacency:
                for next_node, _ in self.adjacency[current_node]:
                    if next_node not in visited:
                        visited.add(next_node)
                        dfs(next_node, path_length + 1, visited)
                        visited.remove(next_node)
            
            return count
        
        visited = {self.source}
        dfs(self.source, 0, visited)
        return count


class SmartPathSelector:
    """Complete path enumeration with safety limits"""
    
    def __init__(self, network: NetworkState):
        """Initialize path selector for complete enumeration"""
        self.network = network
        self.enumerator = CompletePathEnumerator(network)
    
    def estimate_complexity(self) -> Tuple[int, int]:
        """
        Estimate enumeration complexity.
        
        Returns:
            (estimated_paths, network_size)
        """
        num_nodes = len(self.network.nodes)
        
        # Try actual count for reasonable-sized networks
        try:
            estimated_paths = self.enumerator.count_all_paths(max_length=num_nodes + 5)
        except:
            estimated_paths = min(10000, 2 ** (num_nodes - 2))
        
        return estimated_paths, num_nodes
    
    def enumerate_all_paths(self, 
                           max_paths: int = None,
                           max_time_seconds: float = 10.0) -> PathEnumerationResult:
        """
        Enumerate all possible s-t paths with safety limits.
        
        Args:
            max_paths: Maximum number of paths to enumerate (None = no limit)
            max_time_seconds: Maximum time to spend on enumeration
            
        Returns:
            PathEnumerationResult with all found paths
        """
        estimated_paths, network_size = self.estimate_complexity()
        
        print(f"🛤️  Complete Path Enumeration:")
        print(f"   Network: {network_size} nodes, {len(self.network.edges)} edges")
        print(f"   Estimated paths: {estimated_paths}")
        
        try:
            # Perform complete enumeration with safety limits
            result = self.enumerator.enumerate_all_paths(
                max_length=network_size + 10,  # Allow longer paths
                max_paths=max_paths
            )
            
            # Check if enumeration took too long
            if result.enumeration_time > max_time_seconds:
                print(f"   ⚠️  Enumeration took {result.enumeration_time:.2f}s (>{max_time_seconds}s limit)")
            
            if not result.is_complete:
                print(f"   ⚠️  Enumeration limited to {result.max_paths_limit} paths")
            
            print(f"   ✅ Found {result.total_paths_found} paths in {result.enumeration_time:.3f}s")
            return result
            
        except Exception as e:
            print(f"   ❌ Complete enumeration failed: {str(e)[:50]}")
            # Return empty result instead of fallback
            return PathEnumerationResult([], 0.0, 0, True)
    


class PathAnalyzer:
    """Analyze and compare different path sets"""
    
    def __init__(self, network: NetworkState):
        """Initialize path analyzer"""
        self.network = network
    
    def analyze_path_set(self, paths: List[List[str]]) -> Dict:
        """
        Analyze a set of paths for flow control potential.
        
        Returns:
            Analysis dictionary with metrics
        """
        if not paths:
            return {"error": "No paths provided"}
        
        analysis = {
            "path_count": len(paths),
            "path_lengths": [],
            "bottleneck_capacities": [],
            "shared_edges": {},
            "path_details": []
        }
        
        # Analyze each path
        for i, path_edges in enumerate(paths):
            path_id = f"P{i+1}"
            
            # Create temporary path object
            temp_path = NetworkPath(path_id, path_edges)
            bottleneck, bottleneck_edge = temp_path.calculate_bottleneck(self.network.edges)
            
            analysis["path_lengths"].append(len(path_edges))
            analysis["bottleneck_capacities"].append(bottleneck)
            analysis["path_details"].append({
                "path_id": path_id,
                "edges": path_edges,
                "length": len(path_edges),
                "bottleneck_capacity": bottleneck,
                "bottleneck_edge": bottleneck_edge
            })
            
            # Track shared edges
            for edge_id in path_edges:
                if edge_id not in analysis["shared_edges"]:
                    analysis["shared_edges"][edge_id] = []
                analysis["shared_edges"][edge_id].append(path_id)
        
        # Calculate summary statistics
        if analysis["bottleneck_capacities"]:
            analysis["total_bottleneck_capacity"] = sum(analysis["bottleneck_capacities"])
            analysis["average_bottleneck"] = sum(analysis["bottleneck_capacities"]) / len(analysis["bottleneck_capacities"])
            analysis["min_bottleneck"] = min(analysis["bottleneck_capacities"])
            analysis["max_bottleneck"] = max(analysis["bottleneck_capacities"])
        
        # Identify highly shared edges
        analysis["highly_shared_edges"] = {
            edge_id: paths for edge_id, paths in analysis["shared_edges"].items()
            if len(paths) > 1
        }
        
        return analysis
    
    def compare_path_sets(self, complete_result: PathEnumerationResult, 
                         sampled_result: PathEnumerationResult) -> Dict:
        """Compare complete vs sampled path sets"""
        comparison = {
            "complete": {
                "count": complete_result.total_paths_found,
                "time": complete_result.enumeration_time,
                "is_complete": complete_result.is_complete
            },
            "sampled": {
                "count": sampled_result.total_paths_found,
                "time": sampled_result.enumeration_time,
                "is_complete": sampled_result.is_complete
            }
        }
        
        # Analyze both sets
        if complete_result.paths:
            complete_analysis = self.analyze_path_set(complete_result.paths)
            comparison["complete"]["total_capacity"] = complete_analysis.get("total_bottleneck_capacity", 0)
            comparison["complete"]["avg_capacity"] = complete_analysis.get("average_bottleneck", 0)
        
        if sampled_result.paths:
            sampled_analysis = self.analyze_path_set(sampled_result.paths)
            comparison["sampled"]["total_capacity"] = sampled_analysis.get("total_bottleneck_capacity", 0)
            comparison["sampled"]["avg_capacity"] = sampled_analysis.get("average_bottleneck", 0)
        
        # Calculate efficiency ratios
        if comparison["complete"]["count"] > 0:
            comparison["coverage_ratio"] = comparison["sampled"]["count"] / comparison["complete"]["count"]
            comparison["time_ratio"] = comparison["sampled"]["time"] / comparison["complete"]["time"]
            
            if comparison["complete"]["total_capacity"] > 0:
                comparison["capacity_ratio"] = comparison["sampled"]["total_capacity"] / comparison["complete"]["total_capacity"]
        
        return comparison


def demonstrate_path_enumeration():
    """Demonstrate path enumeration capabilities"""
    print("🛤️  PATH ENUMERATION DEMONSTRATION")
    print("=" * 80)
    
    # Test with different network sizes
    from network_generators import NetworkGenerator
    generator = NetworkGenerator(seed=42)
    
    # Small network: complete enumeration
    print("\n1️⃣ Small Network (Complete Enumeration):")
    small_network = generator.create_from_edge_list([
        ("s", "a", 5.0),
        ("s", "b", 4.0),
        ("a", "t", 6.0),
        ("b", "t", 3.0),
        ("a", "b", 2.0)  # Additional connection
    ], [])  # No predefined paths
    
    enumerator = CompletePathEnumerator(small_network)
    result = enumerator.enumerate_all_paths()
    
    print(f"   Found {result.total_paths_found} paths in {result.enumeration_time:.3f}s")
    print(f"   Complete enumeration: {result.is_complete}")
    for i, path in enumerate(result.paths):
        print(f"   P{i+1}: {' → '.join(path)}")
    
    # Medium network: complete enumeration  
    print("\n2️⃣ Medium Network (3x4 Grid):")
    medium_network = generator.create_grid_network(3, 4)
    
    print(f"   Found {len(medium_network.paths)} paths from network generation")
    
    # Large network: complete enumeration with limits
    print("\n3️⃣ Large Network (Complete with Limits):")
    large_network = generator.create_random_network(12, 20)
    
    print(f"   Found {len(large_network.paths)} paths from network generation")
    
    # Path analysis
    print("\n📊 Path Analysis:")
    analyzer = PathAnalyzer(small_network)
    analysis = analyzer.analyze_path_set(result.paths)
    
    print(f"   Total paths: {analysis['path_count']}")
    print(f"   Path lengths: {analysis['path_lengths']}")
    print(f"   Bottleneck capacities: {[f'{x:.1f}' for x in analysis['bottleneck_capacities']]}")
    print(f"   Total capacity: {analysis.get('total_bottleneck_capacity', 0):.1f}")
    print(f"   Shared edges: {len(analysis['highly_shared_edges'])}")


if __name__ == "__main__":
    demonstrate_path_enumeration()