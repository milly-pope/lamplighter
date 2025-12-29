from typing import List


def layer_sizes(dist):
    """Return [|S0|, |S1|, ..., |Sn|] where Si is the sphere at distance i."""
    if not dist:
        return []
    max_d = max(dist)
    counts = [0] * (max_d + 1)
    for d in dist:
        counts[d] += 1
    return counts


def check_generic(V, E, dist):
    """
    Return a list of error strings (empty => PASS).
    Checks:
    - Root at dist 0
    - Every edge has |dist[v] - dist[u]| == 1
    - No vertex has distance > max detected
    - Every non-root vertex has at least one incoming edge from dist-1
    """
    errors = []
    
    if not V:
        errors.append("Empty vertex set")
        return errors
    
    # Check root at dist 0
    if dist[0] != 0:
        errors.append(f"Root vertex 0 has distance {dist[0]}, expected 0")
    
    # Check edge distances
    for u, v, gi in E:
        du = dist[u]
        dv = dist[v]
        if abs(dv - du) != 1:
            errors.append(f"Edge ({u}, {v}, {gi}): |dist[{v}]-dist[{u}]| = |{dv}-{du}| != 1")
    
    # Check that every non-root vertex has an incoming edge from distance d-1
    max_d = max(dist)
    incoming = {i: [] for i in range(len(V))}
    for u, v, gi in E:
        incoming[v].append(u)
    
    for v in range(1, len(V)):  # Skip root at 0
        dv = dist[v]
        has_predecessor = any(dist[u] == dv - 1 for u in incoming[v])
        if not has_predecessor:
            errors.append(f"Vertex {v} at distance {dv} has no incoming edge from distance {dv-1}")
    
    return errors


def check_Z2_counts(n, Vcount):
    """
    Expected |B(n)| in L1 metric: 2n(n+1) + 1.
    Returns error string or None.
    """
    expected = 2 * n * (n + 1) + 1
    if Vcount != expected:
        return f"Z^2 ball size: got {Vcount}, expected {expected}"
    return None


def check_Dinf_counts(n, Vcount):
    """
    Expected |B(0)| = 1; for n >= 1, |B(n)| = 4*n.
    Returns error string or None.
    """
    if n == 0:
        expected = 1
    else:
        expected = 4 * n
    
    if Vcount != expected:
        return f"D∞ ball size: got {Vcount}, expected {expected}"
    return None


def check_L2_counts_small(n, Vcount):
    """
    For lamplighter L2 with generators {a,t,T} and unit step:
    n: 0, 1, 2,  3,  4,  5
    |V|: 1, 4, 10, 22, 44, 84
    Only valid for pattern=[2], step_mode="unit", offsets=[0].
    Returns error string or None.
    """
    known = {0: 1, 1: 4, 2: 10, 3: 22, 4: 44, 5: 84}
    if n not in known:
        return None  # No known value
    
    expected = known[n]
    if Vcount != expected:
        return f"Lamplighter L2 ball size: got {Vcount}, expected {expected}"
    return None
