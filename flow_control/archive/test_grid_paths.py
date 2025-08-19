#!/usr/bin/env python3
"""Test actual number of paths in grid networks"""

from network_generators import NetworkGenerator
from path_enumerator import CompletePathEnumerator

def test_grid_path_count():
    generator = NetworkGenerator(seed=42)
    
    # Create 3x3 grid
    print("🔍 Testing 3x3 Grid Network Path Enumeration")
    print("=" * 60)
    
    network = generator.create_grid_network(3, 3)
    
    print(f"📊 Network Structure:")
    print(f"   Nodes: {len(network.nodes)}")
    print(f"   Edges: {len(network.edges)}")
    print(f"   Predefined paths: {len(network.paths)}")
    
    # Show predefined paths
    print(f"\n🛤️  Predefined Paths:")
    for path_id, path in network.paths.items():
        print(f"   {path_id}: {' → '.join(path.edges)}")
    
    # Now enumerate ALL possible s-t paths
    print(f"\n🔍 Complete Path Enumeration:")
    enumerator = CompletePathEnumerator(network)
    result = enumerator.enumerate_all_paths()
    
    print(f"   Time: {result.enumeration_time:.3f}s")
    print(f"   Total paths found: {result.total_paths_found}")
    print(f"   Complete: {result.is_complete}")
    
    print(f"\n📋 All Possible s-t Paths:")
    for i, path_edges in enumerate(result.paths):
        print(f"   P{i+1:02d}: {' → '.join(path_edges)}")
    
    # Compare with theory
    # For 3x3 grid, theoretical paths = C(4,2) = 6 (Catalan number related)
    # But actual depends on grid structure
    print(f"\n📊 Analysis:")
    print(f"   Predefined vs Complete: {len(network.paths)} vs {result.total_paths_found}")
    print(f"   Ratio: {result.total_paths_found / max(1, len(network.paths)):.1f}x more paths available")

if __name__ == "__main__":
    test_grid_path_count()
