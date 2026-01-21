# Dead-end element detection for Cayley graphs
# Definition: v at distance r is a dead-end if all generators keep it at distance ≤ r
# (no one-step edge from v increases distance)


def analyze_dead_ends(group, gens, labels, R, depth_cap, V, dist, visited):
    # Find dead-end elements in ball B_R
    # A vertex at distance r is a dead-end if all neighbors have distance ≤ r
    # Returns dict with results
    
    # Check ALL vertices in the ball, not just the frontier
    dead_end_vids = []
    for vid in range(len(V)):
        state = V[vid]
        r = dist[vid]
        has_escape = False
        
        # Check if any generator increases distance
        for g in gens:
            next_state = g.apply(state)
            if next_state in visited:
                next_vid = visited[next_state]
                if dist[next_vid] > r:
                    has_escape = True
                    break
        
        if not has_escape:
            dead_end_vids.append(vid)
    
    # Collect dead-end info
    dead_ends = []
    for vid in dead_end_vids:
        dead_ends.append({
            'vid': vid,
            'distance': dist[vid],
            'pretty': group.pretty(V[vid])
        })
    
    return {
        'R': R,
        'ball_size': len(V),
        'dead_ends': dead_ends
    }


def print_dead_end_results(results, max_examples=10):
    # Print dead-end analysis results
    R = results['R']
    ball_size = results['ball_size']
    dead_ends = results['dead_ends']
    
    print(f"\nBall size |B_{R}| = {ball_size}")
    print(f"Dead ends found: {len(dead_ends)}")
    
    if dead_ends:
        # Show examples
        num_to_show = len(dead_ends) if max_examples == 0 else min(max_examples, len(dead_ends))
        print(f"\nShowing {num_to_show} of {len(dead_ends)} dead end(s):")
        
        for de in dead_ends[:num_to_show]:
            vid = de['vid']
            r = de['distance']
            state = de['pretty']
            print(f"[vid={vid}] distance={r}  state={state}")
    else:
        print(f"No dead ends found in ball B_{R}.")
