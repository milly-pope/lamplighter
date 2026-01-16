# Dead-end element detection for Cayley graphs
# Mathematical definition:
# - Dead-end element: g at distance R where ∀ s∈S, |g·s| ≤ |g|
#   (no one-step edge from g leaves the ball B_R)
# - Dead-end depth: smallest k ≥ 1 such that ∃ word w of length k with |g·w| ≥ R+1

from collections import deque


def analyze_dead_ends(group, gens, labels, R, depth_cap, V, dist, visited):
    # Scan S_R (sphere at radius R) for dead ends and compute their depth
    # Returns dict with results and examples
    # Find all vertices on sphere S_R
    boundary = [vid for vid in range(len(V)) if dist[vid] == R]
    
    # Detect dead ends: vertices with no neighbor at R+1
    dead_end_vids = []
    for vid in boundary:
        state = V[vid]
        has_outward = False
        
        for gi, g in enumerate(gens):
            next_state = g.apply(state)
            if next_state in visited:
                next_vid = visited[next_state]
                if dist[next_vid] == R + 1:
                    has_outward = True
                    break
        
        if not has_outward:
            dead_end_vids.append(vid)
    
    # For each dead end, compute depth and witness word
    dead_ends = []
    for vid in dead_end_vids:
        depth, witness = _compute_depth(vid, V, dist, visited, gens, labels, R, depth_cap)
        dead_ends.append({
            'vid': vid,
            'pretty': group.pretty(V[vid]),
            'depth': depth,
            'witness': witness
        })
    
    return {
        'R': R,
        'depth_cap': depth_cap,
        'boundary_count': len(boundary),
        'dead_ends': dead_ends
    }


def _compute_depth(start_vid, V, dist, visited, gens, labels, R, depth_cap):
    # Local BFS from dead-end vertex to find minimal depth to escape ball B_R
    # Returns: (depth, witness_word) where depth is int if found within cap, else ">=cap+1"
    start_state = V[start_vid]
    
    # BFS queue: (state, path_length, path_labels)
    queue = deque([(start_state, 0, [])])
    local_visited = {start_state}
    
    while queue:
        state, depth, path = queue.popleft()
        
        # Check if we've escaped the ball
        if state in visited:
            vid = visited[state]
            if dist[vid] >= R + 1:
                return depth, path if path else None
        
        # Stop if we've hit the depth cap
        if depth >= depth_cap:
            continue
        
        # Explore neighbors
        for gi, g in enumerate(gens):
            next_state = g.apply(state)
            if next_state not in local_visited:
                local_visited.add(next_state)
                new_path = path + [labels[gen_idx]]
                queue.append((next_state, depth + 1, new_path))
    
    # Did not find escape within depth_cap
    return f">={depth_cap + 1}", None


def print_dead_end_results(results, max_examples=10):
    # Print dead-end analysis results to terminal
    # max_examples: Maximum number of examples to show (0 = all)
    R = results['R']
    depth_cap = results['depth_cap']
    boundary_count = results['boundary_count']
    dead_ends = results['dead_ends']
    
    print(f"\nLayer size |S_{R}| = {boundary_count}")
    print(f"Dead ends found: {len(dead_ends)}")
    
    if dead_ends:
        # Calculate depth range (only for finite depths)
        finite_depths = [de['depth'] for de in dead_ends if isinstance(de['depth'], int)]
        if finite_depths:
            min_depth = min(finite_depths)
            max_depth = max(finite_depths)
            print(f"Depth range among dead ends: {min_depth} .. {max_depth}")
        
        # Show examples
        num_to_show = len(dead_ends) if max_examples == 0 else min(max_examples, len(dead_ends))
        print(f"\nShowing {num_to_show} of {len(dead_ends)} dead end(s):")
        
        for de in dead_ends[:num_to_show]:
            vid = de['vid']
            depth = de['depth']
            state = de['pretty']
            witness = " ".join(de['witness']) if de['witness'] else "—"
            
            print(f"[vid={vid}] d={R}  depth={depth}  state={state}  witness={witness}")
    else:
        print(f"No dead ends found on layer {R}.")
