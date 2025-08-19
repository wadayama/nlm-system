#!/usr/bin/env python3
"""Test larger grid networks"""

from network_generators import NetworkGenerator

def test_large_grids():
    generator = NetworkGenerator(seed=42)
    
    print("🔍 Testing Larger Grid Networks with Complete Enumeration")
    print("=" * 70)
    
    # Test 4x4 grid
    print("\n📊 4x4 Grid Network:")
    network = generator.create_grid_network(4, 4)
    print(f"   Nodes: {len(network.nodes)}, Edges: {len(network.edges)}, Paths: {len(network.paths)}")
    
    # Test with sampling option
    print("\n📊 4x4 Grid Network (Sampling mode):")
    network_sampled = generator.create_grid_network(4, 4, use_complete_enumeration=False)
    print(f"   Nodes: {len(network_sampled.nodes)}, Edges: {len(network_sampled.edges)}, Paths: {len(network_sampled.paths)}")
    
    print(f"\n📈 Comparison:")
    print(f"   Complete enumeration: {len(network.paths)} paths")
    print(f"   Legacy sampling: {len(network_sampled.paths)} paths")
    print(f"   Improvement: {len(network.paths) / max(1, len(network_sampled.paths)):.1f}x more paths")

if __name__ == "__main__":
    test_large_grids()
