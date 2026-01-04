from collections import deque


def build_ball(group, gens, radius):
    # Build the radius-n ball for 'group' with generators 'gens'.
    # Include every edge whose endpoints both lie at distance <= radius.
    # Returns (V, E, dist, labels, words).
    
    # Initialize with identity
    root_state = group.identity()
    
    V = []  # List of states
    E = []  # List of edges (u, v, gen_index)
    dist = []  # Distance from root for each vertex
    words = []  # Word (generator sequence) for each vertex
    
    visited = {}  # Map state -> vertex ID
    
    q = deque()
    vid = 0
    visited[root_state] = vid
    V.append(root_state)
    dist.append(0)
    words.append('e')  # identity = empty word
    q.append(vid)
    
    while q:
        u = q.popleft()
        du = dist[u]
        
        # Apply each generator
        for gi, g in enumerate(gens):
            s_child = g.apply(V[u])
            
            if s_child in visited:
                # State already exists - add edge to it
                v = visited[s_child]
                E.append((u, v, gi))
            elif du < radius:
                # New state within radius - create vertex and edge
                v = len(V)
                visited[s_child] = v
                V.append(s_child)
                dist.append(du + 1)
                # Build word: parent_word + generator_name
                parent_word = words[u]
                new_word = parent_word + g.name if parent_word != 'e' else g.name
                words.append(new_word)
                q.append(v)
                E.append((u, v, gi))
            # else: du == radius, child would be at radius+1, skip creating vertex but no edge either
    
    labels = [g.name for g in gens]
    return (V, E, dist, labels, words)


def transitions_from(gens, state):
    # Yield (gen_idx, next_state) for each generator applied to state
    for i, g in enumerate(gens):
        yield i, g.apply(state)

