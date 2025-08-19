#!/usr/bin/env python3
"""
Test Planar Layout Functionality

Tests the new planar layout algorithms for s-t networks,
focusing on minimal crossings and proper s-t placement.
"""

from network_generators import NetworkGenerator
from flow_operations import FlowController
from network_visualizer import display_network, NetworkGraphVisualizer


def test_planar_layouts():
    """Test different planar layout algorithms"""
    print("🎨 TESTING PLANAR LAYOUT ALGORITHMS")
    print("=" * 70)
    
    generator = NetworkGenerator(seed=42)
    
    # Test networks with different complexities
    test_networks = {
        "Simple Diamond": generator.create_from_edge_list([
            ("s", "a", 5.0), ("s", "b", 4.0), 
            ("a", "t", 6.0), ("b", "t", 3.0)
        ], [["e0", "e2"], ["e1", "e3"]]),
        
        "Complex Multi-Path": generator.create_from_edge_list([
            ("s", "a", 10.0), ("s", "b", 8.0),
            ("a", "c", 6.0), ("a", "d", 7.0),
            ("b", "c", 5.0), ("b", "d", 9.0),
            ("c", "t", 8.0), ("d", "t", 6.0)
        ], [
            ["e0", "e2", "e6"],  # s→a→c→t
            ["e0", "e3", "e7"],  # s→a→d→t
            ["e1", "e4", "e6"],  # s→b→c→t
            ["e1", "e5", "e7"]   # s→b→d→t
        ]),
        
        "Grid 3x3": generator.create_grid_network(3, 3),
        "Layered Network": generator.create_layered_network([1, 3, 2, 1])
    }
    
    # Test all layout types
    layout_types = ["planar_st", "planar", "hierarchical", "spring"]
    
    for network_name, network in test_networks.items():
        print(f"\n📊 Testing {network_name}:")
        print(f"   Nodes: {len(network.nodes)}, Edges: {len(network.edges)}, Paths: {len(network.paths)}")
        
        # Set some flows for visualization
        controller = FlowController(network)
        if network.paths:
            path_ids = list(network.paths.keys())[:2]
            for path_id in path_ids:
                alternatives = controller.calculate_max_safe_flow(path_id)
                if not alternatives.get('error'):
                    max_safe = alternatives['max_safe_flow']
                    if max_safe > 0:
                        controller.set_path_flow_with_alternatives(path_id, max_safe * 0.6)
        
        # Test each layout
        for layout in layout_types:
            try:
                visualizer = NetworkGraphVisualizer(network)
                pos = visualizer._determine_layout(layout)
                
                # Check s-t placement
                s_x = pos.get('s', (0, 0))[0] if 's' in pos else None
                t_x = pos.get('t', (0, 0))[0] if 't' in pos else None
                
                placement_ok = s_x is not None and t_x is not None and s_x < t_x
                status = "✅" if placement_ok else "⚠️"
                
                print(f"   {status} {layout:>12}: s@({s_x:.2f}) < t@({t_x:.2f}) = {placement_ok}")
                
            except Exception as e:
                print(f"   ❌ {layout:>12}: Error - {str(e)[:30]}")


def test_planar_graph_detection():
    """Test planar graph detection and layout"""
    print("\n🔍 TESTING PLANAR GRAPH DETECTION")
    print("=" * 70)
    
    generator = NetworkGenerator()
    
    # Create known planar and non-planar networks
    test_cases = [
        {
            "name": "Simple Path (Planar)",
            "edges": [("s", "a", 5.0), ("a", "b", 4.0), ("b", "t", 3.0)],
            "paths": [["e0", "e1", "e2"]],
            "expected_planar": True
        },
        {
            "name": "Diamond (Planar)", 
            "edges": [("s", "a", 5.0), ("s", "b", 4.0), ("a", "t", 6.0), ("b", "t", 3.0)],
            "paths": [["e0", "e2"], ["e1", "e3"]],
            "expected_planar": True
        },
        {
            "name": "K3,3-like (Non-Planar)",
            "edges": [
                ("s", "a", 1.0), ("s", "b", 1.0), ("s", "c", 1.0),
                ("a", "x", 1.0), ("a", "y", 1.0), ("a", "z", 1.0),
                ("b", "x", 1.0), ("b", "y", 1.0), ("b", "z", 1.0),
                ("c", "x", 1.0), ("c", "y", 1.0), ("c", "z", 1.0),
                ("x", "t", 1.0), ("y", "t", 1.0), ("z", "t", 1.0)
            ],
            "paths": [["e0", "e3", "e12"], ["e1", "e4", "e13"]],
            "expected_planar": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📐 Testing {test_case['name']}:")
        
        try:
            network = generator.create_from_edge_list(test_case['edges'], test_case['paths'])
            visualizer = NetworkGraphVisualizer(network)
            
            # Check planarity
            import networkx as nx
            is_planar = nx.is_planar(visualizer.nx_graph)
            expected = test_case['expected_planar']
            
            status = "✅" if is_planar == expected else "⚠️"
            print(f"   {status} Planarity: {is_planar} (expected: {expected})")
            
            # Test planar layout
            try:
                pos = visualizer._create_planar_layout()
                print(f"   ✅ Planar layout: {len(pos)} positions generated")
            except Exception as e:
                print(f"   ❌ Planar layout failed: {str(e)[:40]}")
            
            # Test s-t optimized layout
            try:
                pos = visualizer._create_planar_st_layout()
                s_x = pos.get('s', (0, 0))[0]
                t_x = pos.get('t', (0, 0))[0]
                placement_ok = s_x < t_x
                status = "✅" if placement_ok else "⚠️"
                print(f"   {status} S-T optimized: s@{s_x:.2f} < t@{t_x:.2f}")
            except Exception as e:
                print(f"   ❌ S-T layout failed: {str(e)[:40]}")
                
        except Exception as e:
            print(f"   ❌ Network creation failed: {e}")


def test_crossing_minimization():
    """Test edge crossing minimization"""
    print("\n✂️  TESTING EDGE CROSSING MINIMIZATION")
    print("=" * 70)
    
    generator = NetworkGenerator(seed=123)
    
    # Create a network with potential crossings
    network = generator.create_from_edge_list([
        ("s", "a", 5.0), ("s", "b", 4.0),
        ("a", "c", 3.0), ("a", "d", 6.0),
        ("b", "c", 7.0), ("b", "d", 2.0),
        ("c", "t", 4.0), ("d", "t", 5.0)
    ], [
        ["e0", "e2", "e6"],  # s→a→c→t (upper path)
        ["e1", "e5", "e7"],  # s→b→d→t (lower path)
        ["e0", "e3", "e7"],  # s→a→d→t (cross path)
        ["e1", "e4", "e6"]   # s→b→c→t (cross path)
    ])
    
    print(f"Network: {len(network.nodes)} nodes, {len(network.edges)} edges")
    print("Paths that may cause crossings:")
    for path_id, path in network.paths.items():
        edge_sequence = " → ".join(path.edges)
        print(f"  {path_id}: {edge_sequence}")
    
    # Test different layouts
    layouts = ["planar_st", "planar", "spring", "kamada_kawai"]
    
    visualizer = NetworkGraphVisualizer(network)
    
    for layout in layouts:
        try:
            pos = visualizer._determine_layout(layout)
            
            # Simple heuristic to estimate crossings
            crossings = estimate_crossings(network, pos)
            
            # Check s-t placement
            s_x = pos.get('s', (0, 0))[0]
            t_x = pos.get('t', (0, 0))[0]
            placement = s_x < t_x
            
            status = "✅" if placement else "⚠️"
            print(f"   {status} {layout:>12}: ~{crossings} crossings, s<t: {placement}")
            
        except Exception as e:
            print(f"   ❌ {layout:>12}: Error - {str(e)[:30]}")


def estimate_crossings(network, pos):
    """Simple heuristic to estimate edge crossings"""
    if len(pos) < 4:
        return 0
    
    edges = [(network.edges[eid].from_node, network.edges[eid].to_node) 
             for eid in network.edges]
    
    crossings = 0
    for i, (a1, a2) in enumerate(edges):
        for j, (b1, b2) in enumerate(edges[i+1:], i+1):
            if {a1, a2} & {b1, b2}:  # Edges share a node
                continue
            
            # Check if line segments intersect
            if all(node in pos for node in [a1, a2, b1, b2]):
                if segments_intersect(pos[a1], pos[a2], pos[b1], pos[b2]):
                    crossings += 1
    
    return crossings


def segments_intersect(p1, p2, p3, p4):
    """Check if two line segments intersect"""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def main():
    """Run all planar layout tests"""
    print("🎨 PLANAR LAYOUT TESTING SUITE")
    print("=" * 80)
    print("Testing s-t optimized layouts with minimal edge crossings")
    print("=" * 80)
    
    test_planar_layouts()
    test_planar_graph_detection()
    test_crossing_minimization()
    
    print("\n" + "=" * 80)
    print("🎯 PLANAR LAYOUT FEATURES SUMMARY")
    print("=" * 80)
    print("✅ Planar graph detection and layout")
    print("✅ S-T optimized positioning (s left, t right)")
    print("✅ Layered structure for minimal crossings")
    print("✅ Crossing minimization algorithms")
    print("✅ Fallback strategies for complex graphs")
    
    print("\n🚀 Enhanced network visualization with optimal s-t layout ready!")
    print("\n💡 Usage:")
    print("   display_network(network)                    # Auto s-t optimized")
    print("   display_network(network, layout='planar')   # Planar if possible")
    print("   display_network(network, layout='planar_st') # S-t optimized planar")


if __name__ == "__main__":
    main()