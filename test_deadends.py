"""
Test script for dead-end element detection.

Acceptance checks:
1. Lamplighter sanity: L₂ = Z/2 wr Z with S = {a,t,T}, offsets {e}
   Build to R=8 (depth_cap=6). Expect ≥1 dead end on layer R=7.
   Canonical example: p=0|-1:1;0:1;1:1 (three consecutive lamps lit, head centered)
   Depth typically ~3.

2. Finite top sanity: Z/2 wr Z/5 with S={a,t,T}.
   Build to R in 3..5. Feature runs; prints counts.

3. For all runs:
   - Every v at distance R has at least one neighbor at R−1 (geodesic parent)
   - For non-dead-ends on S_R, there exists a neighbor at R+1
   - No vertex has dist > R+depth_cap
"""

from cayleylab.groups.lamplighter import Lamplighter, run_dead_end_mode_lamplighter
from cayleylab.groups.wreath import WreathProduct, run_dead_end_mode_wreath
from cayleylab.core.bfs import build_ball
from cayleylab.features.deadends import print_dead_end_results


def test_lamplighter_canonical():
    """Test 1: Canonical lamplighter dead end at R=7"""
    print("=" * 60)
    print("TEST 1: Lamplighter L₂ canonical dead-end")
    print("=" * 60)
    
    lamp = Lamplighter()
    config = lamp.parse_options({'pattern': [2], 'step_mode': 'unit', 'offsets': [0]})
    gens = config.default_generators()
    labels = [g.name for g in gens]
    
    print(f"Group: L₂ = Z/2 wr Z")
    print(f"Generators: {', '.join(labels)}")
    print(f"Parameters: R=7, depth_cap=6")
    print()
    
    results = run_dead_end_mode_lamplighter(config, gens, labels, R=7, depth_cap=6, bfs_build=build_ball)
    print_dead_end_results(results, max_examples=3)
    
    # Verify expectations
    assert results['R'] == 7
    assert results['depth_cap'] == 6
    assert len(results['dead_ends']) >= 1, "Expected at least 1 dead end on layer R=7"
    
    # Check for canonical example
    canonical_found = False
    for de in results['dead_ends']:
        if '-1:1;0:1;1:1' in de['pretty']:  # Three consecutive lamps
            canonical_found = True
            print(f"\n✓ Found canonical dead-end: {de['pretty']}")
            print(f"  Depth: {de['depth']} (expected ~3)")
            assert isinstance(de['depth'], int), "Depth should be an integer"
            assert de['depth'] <= 6, "Depth should be within cap"
    
    assert canonical_found, "Did not find canonical dead-end pattern"
    print("\n✓ TEST 1 PASSED\n")


def test_finite_wreath():
    """Test 2: Finite wreath product Z/2 wr Z/5"""
    print("=" * 60)
    print("TEST 2: Finite wreath product Z/2 wr Z/5")
    print("=" * 60)
    
    wreath = WreathProduct()
    config = wreath.parse_options({'spec': 'Z/2 wr Z/5', 'offsets': ['e']})
    gens = config.default_generators()
    labels = [g.name for g in gens]
    
    print(f"Group: Z/2 wr Z/5")
    print(f"Generators: {', '.join(labels)}")
    
    for R in [3, 4, 5]:
        print(f"\nTesting at radius R={R}, depth_cap=6:")
        results = run_dead_end_mode_wreath(config, gens, labels, R=R, depth_cap=6, bfs_build=build_ball)
        print_dead_end_results(results, max_examples=3)
        
        assert results['R'] == R
        assert results['boundary_count'] > 0, f"Layer S_{R} should have vertices"
    
    print("\n✓ TEST 2 PASSED\n")


def test_correctness_properties():
    """Test 3: Verify correctness properties"""
    print("=" * 60)
    print("TEST 3: Correctness properties verification")
    print("=" * 60)
    
    lamp = Lamplighter()
    config = lamp.parse_options({'pattern': [2], 'step_mode': 'unit', 'offsets': [0]})
    gens = config.default_generators()
    labels = [g.name for g in gens]
    
    R = 5
    depth_cap = 4
    
    print(f"Building ball to R+depth_cap = {R+depth_cap}...")
    V, E, dist, _, _ = build_ball(config, gens, R + depth_cap)
    visited = {V[i]: i for i in range(len(V))}
    
    # Property 1: No vertex has dist > R+depth_cap
    max_dist = max(dist)
    print(f"✓ Property 1: Max distance = {max_dist} ≤ {R+depth_cap}")
    assert max_dist <= R + depth_cap
    
    # Property 2: Every vertex at R has a parent at R-1
    sphere_R = [vid for vid in range(len(V)) if dist[vid] == R]
    print(f"  Sphere S_{R} has {len(sphere_R)} vertices")
    
    for vid in sphere_R:
        state = V[vid]
        has_parent = False
        
        # Check all generator moves
        for g in gens:
            next_state = g.apply(state)
            if next_state in visited:
                next_vid = visited[next_state]
                if dist[next_vid] == R - 1:
                    has_parent = True
                    break
        
        assert has_parent, f"Vertex {vid} at distance {R} has no parent at {R-1}"
    
    print(f"✓ Property 2: All {len(sphere_R)} vertices at R have geodesic parents at R-1")
    
    # Property 3: Non-dead-ends have children at R+1
    from cayleylab.features.deadends import analyze_dead_ends
    results = analyze_dead_ends(config, gens, labels, R, depth_cap, V, dist, visited)
    
    dead_end_vids = {de['vid'] for de in results['dead_ends']}
    non_dead_ends = [vid for vid in sphere_R if vid not in dead_end_vids]
    
    for vid in non_dead_ends:
        state = V[vid]
        has_child = False
        
        for g in gens:
            next_state = g.apply(state)
            if next_state in visited:
                next_vid = visited[next_state]
                if dist[next_vid] == R + 1:
                    has_child = True
                    break
        
        assert has_child, f"Non-dead-end vertex {vid} has no child at R+1"
    
    print(f"✓ Property 3: All {len(non_dead_ends)} non-dead-ends have children at R+1")
    print(f"  ({len(dead_end_vids)} dead-ends correctly identified)")
    
    print("\n✓ TEST 3 PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DEAD-END ELEMENT DETECTION - ACCEPTANCE TESTS")
    print("=" * 60 + "\n")
    
    test_lamplighter_canonical()
    test_finite_wreath()
    test_correctness_properties()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
