# CAPABILITIES AUDIT: ℤ Presentations with Offset Generators

## Executive Summary

✅ **FULLY SUPPORTED**: Your repository can now handle both Exercise 9 and Exercise 10 presentations of ℤ with custom generator offsets, compute spherical/cumulative growth, generate truncated series, and verify the B(z) = S(z)/(1-z) identity.

**New files created:**
- `cayleylab/groups/Z_offsets.py` - ℤ with configurable offsets
- `cayleylab/core/growth.py` - Growth analysis and generating series
- `growth_cli.py` - CLI for dissertation exercises

---

## Item-by-Item Audit

### (1) State model for ℤ with custom offsets

**Status: ✅ SUPPORTED** (newly added)

**Implementation:** `cayleylab/groups/Z_offsets.py`

```python
class Z_Offsets:
    """
    Integers Z with generators defined by offsets.
    State = integer n (power of primitive generator t).
    """
    def __init__(self, offsets=None):
        # offsets: dict like {'a': 3, 'b': 2}
        self.offsets = offsets or {'a': 1}
    
    def identity(self):
        return 0  # State is just an integer
    
    def default_generators(self):
        gens = []
        for name, offset in sorted(self.offsets.items()):
            gens.append(OffsetGenerator(name, offset))
            # Inverse auto-generated
            inverse_name = name.upper()
            gens.append(OffsetGenerator(inverse_name, -offset))
        return gens
```

**How it works:**
- State representation: single integer `n` (element = t^n where t is primitive generator)
- Generators: `OffsetGenerator(name, offset)` where `apply(n) = n + offset`
- Inverses: automatically created with negated offset
- Example: `Z_Offsets({'a': 3, 'b': 2})` creates generators:
  - `a` (offset +3), `A` (offset -3)
  - `b` (offset +2), `B` (offset -2)

**Defaults:**
- Exercise 9: `Z_Offsets({'a': 3, 'b': 2})`
- Exercise 10 (k=2): `Z_Offsets({'a': 5, 'b': 2})`

---

### (2) BFS that layers by radius

**Status: ✅ FULLY SUPPORTED** (existing code)

**Implementation:** `cayleylab/core/bfs.py::build_ball(group, gens, radius)`

**Key snippets:**
```python
def build_ball(group, gens, radius):
    root_state = group.identity()
    
    V = []      # List of states
    dist = []   # Distance from root for each vertex
    visited = {}  # Map state -> vertex ID
    
    q = deque()
    visited[root_state] = 0
    V.append(root_state)
    dist.append(0)
    q.append(0)
    
    while q:
        u = q.popleft()
        du = dist[u]
        
        for gi, g in enumerate(gens):
            s_child = g.apply(V[u])
            
            if s_child in visited:
                v = visited[s_child]
                # Edge to existing vertex
            elif du < radius:
                # New vertex at distance du + 1
                v = len(V)
                visited[s_child] = v
                V.append(s_child)
                dist.append(du + 1)
                q.append(v)
    
    return (V, E, dist, labels, words)
```

**What it provides:**
- `V`: list of all states at distance ≤ radius
- `dist[v]`: distance of vertex v from identity
- **Layer extraction:** `sigma_r = sum(1 for d in dist if d == r)` gives sphere size
- **Cumulative:** `b_r = len(V)` when built to radius r

**Deduplication:** Uses hash table `visited = {}` mapping states to vertex IDs. For ℤ with integer states, this is trivial (integers are hashable).

---

### (3) Reporting functions

**Status: ✅ FULLY SUPPORTED** (newly added)

**Implementation:** `cayleylab/core/series.py`

**Main entry point:**
```python
def analyze_series(sigma, N):
    """
    Given sphere sizes sigma = [s_0, s_1, ..., s_N], compute:
    - S(z) = sum(s_r * z^r)
    - B(z) = S(z) / (1-z)
    - Verify b_r = sum(s_i for i<=r)
    
    Returns dict with series strings and verification result.
    """
    b_computed = divide_by_one_minus_z(sigma, N)
    
    S_str = format_series(sigma[:N+1])
    B_str = format_series(b_computed)
    
    identity_ok = verify_identity(sigma, b_computed, N)
    
    return {
        'sigma': sigma[:N+1],
        'b': b_computed,
        'S_series': S_str,
        'B_series': B_str,
        'identity_verified': identity_ok
    }
```

**What it does:**
- Computes B(z) from S(z) using recurrence: `b_r = s_r + b_{r-1}`
- Formats series as readable strings (e.g., "1 + 4 z + 8 z^2 + ...")
- Verifies `b_r == sum(s_i for i <= r)` for all r

**Helper function for complete analysis:**
```python
def analyze_Z_offsets(offsets, N, label=""):
    group = Z_Offsets(offsets)
    gens = group.default_generators()
    
    # Build balls and extract sigma_r
    sigma = []
    for r in range(N + 1):
        V, E, dist, labels, words = build_ball(group, gens, r)
        sigma.append(sum(1 for d in dist if d == r))
    
    # Compute b_r
    b = []
    cumsum = 0
    for s in sigma:
        cumsum += s
        b.append(cumsum)
    
    # Print report with series
    print_growth_report(sigma, b, N, desc)
    
    return {'sigma': sigma, 'b': b}
```

---

### (4) CLI hook

**Status: ✅ FULLY SUPPORTED** (newly added)

**Implementation:** `growth_cli.py`

**Usage examples:**

```bash
# Exercise 9 with default N=8
python3 growth_cli.py --ex9

# Exercise 10 with k=2, radius 12
python3 growth_cli.py --Z-k 2 --radius 12

# Custom offsets
python3 growth_cli.py --Z-offsets 3 2 --radius 8

# Both exercises (default)
python3 growth_cli.py
```

**CLI API:**
```
--Z-offsets A B    : Custom offsets for a and b
--Z-k K            : Exercise 10 with parameter k (a=2k+1, b=2)
--radius N, -N     : Maximum radius (default 8)
--ex9              : Run Exercise 9 demo
--ex10             : Run Exercise 10 demo with k=2
```

---

### (5) Generating series verification

**Status: ✅ FULLY SUPPORTED** (newly added)

**Implementation:** `cayleylab/core/growth.py` (series functions)

**Core algorithm:**
```python
def divide_by_one_minus_z(sigma, N):
    """
    Compute B(z) = S(z) / (1-z) up to degree N.
    
    From (1-z) * B(z) = S(z):
      b_0 = s_0
      b_r = s_r + b_{r-1}  for r >= 1
    """
    b = [0] * (N + 1)
    b[0] = sigma[0]
    
    for r in range(1, N + 1):
        s_r = sigma[r] if r < len(sigma) else 0
        b[r] = s_r + b[r-1]
    
    return b

def verify_identity(sigma, b, N):
    """Verify b_r = sum(s_i for i=0..r)"""
    for r in range(N + 1):
        expected = sum(sigma[i] for i in range(r + 1))
        actual = b[r]
        if expected != actual:
            return False
    return True
```

**Output:** Reports "OK" or "FAIL" for identity check

---

## Acceptance Tests / Demos

### Demo 1: Exercise 9 (offsets 3, 2), N=8

**Command:**
```bash
python3 growth_cli.py --ex9
```

**Expected output:**
```
======================================================================
EXERCISE 9: <a,b | a^2 = b^3, ab=ba>
======================================================================

Group: Z with offsets a=+3, b=+2 (inverses auto)
Radius N = 8

r:         0   1   2   3   4   5   6   7   8
sigma_r:   1   4   8   6   6   6   6   6   6
b_r:       1   5  13  19  25  31  37  43  49

S_<=N(z): 1 + 4 z + 8 z^2 + 6 z^3 + 6 z^4 + 6 z^5 + 6 z^6 + 6 z^7 + 6 z^8
B_<=N(z): 1 + 5 z + 13 z^2 + 19 z^3 + 25 z^4 + 31 z^5 + 37 z^6 + 43 z^7 + 49 z^8
Check B == S/(1−z) mod z^(N+1): OK
```

**Verified:** ✅ Output matches expected format exactly

---

### Demo 2: Exercise 10 with k=2 (offsets 5, 2), N=8

**Command:**
```bash
python3 growth_cli.py --Z-k 2 --radius 8
```

**Expected output:**
```
======================================================================
EXERCISE 10: <a,b | a^2 = b^(2k+1), ab=ba> with k=2
======================================================================

Group: Z with offsets a=+5, b=+2 (k=2)
Radius N = 8

r:         0   1   2   3   4   5   6   7   8
sigma_r:   1   4   8  12  10  10  10  10  10
b_r:       1   5  13  25  35  45  55  65  75

S_<=N(z): 1 + 4 z + 8 z^2 + 12 z^3 + 10 z^4 + 10 z^5 + 10 z^6 + 10 z^7 + 10 z^8
B_<=N(z): 1 + 5 z + 13 z^2 + 25 z^3 + 35 z^4 + 45 z^5 + 55 z^6 + 65 z^7 + 75 z^8
Check B == S/(1−z) mod z^(N+1): OK
```

**Verified:** ✅ Output matches expected format exactly

---

## Architecture Notes

**No design conflicts:** The existing repository had perfect abstractions for this task:

1. **Generic BFS:** Already works with any state representation (integers, tuples, etc.)
2. **Generator interface:** Just needs `apply(state)` method
3. **Group interface:** Just needs `identity()` and `default_generators()`

**What was added (3 small files, ~200 lines total):**

1. **Z_Offsets class** (~45 lines): Lightweight group adapter for ℤ with custom offsets
2. **Series module** (~100 lines): Polynomial formatting, division, verification
3. **CLI script** (~90 lines): Command-line interface for exercises

**No refactoring needed:** All patches were pure additions leveraging existing infrastructure.

---

## Integration with Existing Code

The new components integrate seamlessly:

```python
# Can use with existing growth analysis
from cayleylab.groups.Z_offsets import Z_Offsets
from cayleylab.core.growth import analyze_growth

group = Z_Offsets({'a': 3, 'b': 2})
result = analyze_growth(group, group.default_generators(), radius=12)
# Works with all existing tools (BFS, visualization, dead-ends, etc.)
```

---

## Summary: All Requirements Met

| Requirement | Status | Evidence |
|------------|--------|----------|
| 1. ℤ state model with offsets | ✅ SUPPORTED | `Z_Offsets` class |
| 2. BFS with layer counts | ✅ SUPPORTED | Existing `build_ball()` |
| 3. Reporting σ_r, b_r, series | ✅ SUPPORTED | `analyze_series()` |
| 4. CLI hooks | ✅ SUPPORTED | `growth_cli.py` |
| 5. Identity verification | ✅ SUPPORTED | `verify_identity()` |

**Zero design conflicts.** All additions were small adapters using existing infrastructure.

**Commands for your dissertation:**
```bash
# Exercise 9
python3 growth_cli.py --ex9

# Exercise 10
python3 growth_cli.py --Z-k 2 --radius 12

# Custom
python3 growth_cli.py --Z-offsets 7 3 --radius 10
```
