# CayleyLab - Interactive Cayley Graph Explorer

A terminal-based tool for building and analyzing Cayley graphs of various groups.

## Quick Start

```bash
python -m cayleylab
```

## What It Does

Builds Cayley graphs using breadth-first search (BFS) from the identity element. Given a group and generator set, it explores the ball B_R = {g ∈ G : |g| ≤ R} where |g| is word length.

**Core features:**
- Build balls up to radius R
- Export graphs as PNG/DOT for visualization  
- Analyze growth rates (polynomial vs exponential)
- Evaluate words to find their reduced form
- Find dead-end elements on spheres

## Supported Groups

### 1. Z² (Integer Lattice)
- **State**: (x, y) pairs
- **Generators**: x, X, y, Y (steps ±1 in each direction)
- **Example**: Build the diamond-shaped ball around origin

### 2. D∞ (Infinite Dihedral)
- **State**: (k, ε) where k ∈ Z, ε ∈ {0,1}
- **Generators**: r (rotation), R (inverse), s (reflection)
- **Structure**: Every element is r^k or r^k·s

### 3. Lamplighter (Z/2 ≀ Z)
- **State**: (p, tape) = head position + lamp configuration
- **Generators**: t, T (move head), a (toggle lamp at position 0)
- **Example**: The classic lamplighter group with binary lamps on Z

### 4. General Wreath Products (C ≀ D)
- **Supports**: Z, Z/n, Z², D∞, Dn(n), Free(k) for both C and D
- **Format**: Specify as "C wr D" (e.g., "Z/3 wr Z/5")
- **Generators**: Moves in D, toggles in C at specified offsets

### 5. Lamplighter over Z² (Z/2 ≀ Z²)
- **State**: ((x,y), tape) = position in grid + lamp states
- **Generators**: x, X, y, Y (movement), a (toggle lamp)

### 6. Free Group F_2
- **State**: Reduced words (tuples of letters)
- **Generators**: a, b, A (=a⁻¹), B (=b⁻¹)
- **Automatic reduction**: Cancels adjacent inverses

## System Architecture

### High-Level Design

The code is organized around a simple idea: **write one BFS algorithm that works for any group**.

Instead of writing separate BFS for each group (Z², lamplighter, etc.), we define what operations a "group" needs to provide:
- `identity()` - the identity element
- `default_generators()` - list of generator objects
- `pretty(state)` - human-readable state representation

Each generator object just needs:
- `apply(state)` - returns the new state after applying this generator

Then BFS is completely generic - it doesn't care if states are tuples, integers, or dictionaries. It just calls `gen.apply(state)` and explores.

### Directory Structure

```
cayleylab/
├── core/           # Generic algorithms
│   ├── bfs.py          - Breadth-first search (works for any group)
│   ├── export.py       - PNG/DOT output via Graphviz
│   └── growth.py       - Ball size analysis
├── groups/         # Group implementations  
│   ├── base.py         - Group registry
│   ├── Z2.py           - Z² with Move generators
│   ├── Dinf.py         - D∞ with rotation/reflection
│   ├── lamplighter.py  - Standard lamplighter (Z/2 ≀ Z)
│   ├── lamplighter_z2.py - Lamplighter over grid
│   ├── free.py         - Free group with word reduction
│   ├── wreath.py       - General wreath products
│   ├── wreath_adapters_top.py  - Top group operations
│   └── wreath_adapters_base.py - Base group operations
├── features/       # Additional algorithms
│   └── deadends.py     - Dead-end element detection
└── ui/             # Interactive menu
    ├── main.py         - Main menu system
    └── screens.py      - Input helpers

```

### Key Components

**1. BFS Algorithm (core/bfs.py)**

Single function `build_ball(group, gens, radius)` that:
- Starts from identity
- Uses a queue to track frontier
- For each state, tries all generators
- Stores new states in a hash table (dict)
- Returns V (states), E (edges), dist (distances), words (shortest paths)

The core loop is ~20 lines and works for any group because it only calls the generic interface methods.

**2. Group Implementations**

Each group defines:
- State representation (what is an element?)
- Generator classes (how do they transform states?)
- Pretty printing (how to display states?)

For example, in lamplighter:
- State = `(p, tape)` where tape is tuple of (position, value) pairs
- Toggle generator: modifies tape at current head position
- Step generator: moves head position

**3. Dead-End Detection (features/deadends.py)**

Finds elements g at distance R where every one-step move doesn't increase distance. For each dead-end, runs a local BFS to find the minimum number of steps needed to escape the ball.

Uses the same generic BFS approach - just starts from each trapped element instead of identity.

## Mathematical Background

### Cayley Graphs

For a group G with generating set S, the Cayley graph Γ(G,S) has:
- **Vertices**: Elements of G
- **Edges**: g → g·s for each g ∈ G, s ∈ S

The ball B_R is the set of vertices within distance R from identity using these edges.

### Word Metric

The distance |g| is the length of the shortest word in generators that equals g.

BFS finds this exactly because it explores in layers:
- Layer 0: {e} (identity)
- Layer 1: S (generators)  
- Layer 2: {s₁s₂ : s₁,s₂ ∈ S} (words of length 2)
- etc.

The first time BFS reaches g, that's the shortest path.

### Growth Rates

Ball sizes |B_R| grow at different rates:
- **Polynomial**: Z², Dinf have |B_R| ~ R² and |B_R| ~ R
- **Exponential**: Lamplighter, free groups have |B_R| ~ c^R for some c > 1

The code computes ratios |B_{R+1}|/|B_R| to classify growth type.

### Dead-End Elements

An element g ∈ S_R (sphere at radius R) is a dead-end if:
- ∀s ∈ S: |gs| ≤ R (no one-step move increases distance)

Dead-ends exist in groups like lamplighter but not in Z² or free groups. The "depth" of a dead-end is the minimum k such that some k-step word escapes the ball.

## Usage Examples

### Build and Export a Ball

```python
from cayleylab.core.bfs import build_ball
from cayleylab.core.export import write_png, write_dot
from cayleylab.groups.lamplighter import Lamplighter

# Create lamplighter with pattern [2]
lamp = Lamplighter()
configured = lamp.parse_options({
    "pattern": [2],
    "step_mode": "unit",
    "offsets": [0]
})

# Get default generators
gens = configured.default_generators()

# Build radius-5 ball
V, E, dist, words, labels = build_ball(configured, gens, 5)

print(f"Ball has {len(V)} elements and {len(E)} edges")

# Export for visualization
write_dot(V, E, dist, labels, words, configured, "lamp_r5.dot")
write_png(V, E, dist, labels, words, configured, "lamp_r5.png")
```

### Analyze Growth

```python
from cayleylab.core.growth import compute_growth, classify_growth

# Compute ball sizes for radii 0..10
results = compute_growth(configured, gens, max_radius=10)

# Results is list of (radius, size, ratio) tuples
for r, size, ratio in results:
    print(f"R={r}: |V|={size}, ratio={ratio:.2f}")

# Classify growth type
growth_type, param = classify_growth(results)
print(f"Growth: {growth_type} with parameter {param}")
```

### Find Dead-Ends

```python
from cayleylab.features.deadends import analyze_dead_ends
from cayleylab.core.bfs import build_ball

# Build to R + depth_cap to ensure we can compute depths
R = 7
depth_cap = 6
V, E, dist, words, labels = build_ball(configured, gens, R + depth_cap)

# Create state -> vertex_id mapping
visited = {V[i]: i for i in range(len(V))}

# Find dead-ends on sphere at radius R
results = analyze_dead_ends(
    configured, gens, labels, R, depth_cap, V, dist, visited
)

print(f"Layer {R} has {results['boundary_count']} elements")
print(f"Found {len(results['dead_ends'])} dead-ends")

for de in results['dead_ends']:
    print(f"  State: {de['pretty']}, Depth: {de['depth']}")
```

## Implementation Notes

### Why This Design?

**Goal**: Understand Cayley graphs for different groups without copy-pasting the BFS algorithm.

**Solution**: Define a minimal interface that any group must implement, then write BFS once using only that interface.

This is called "duck typing" in Python - we don't formally declare an interface, we just expect groups to have certain methods. If they do, BFS works.

### State Representation Choices

**Z²**: Tuples `(x, y)` - simple and immutable, works as dict keys

**Lamplighter**: `(p, sorted_tape)` where tape is tuple of `(position, value)` pairs. Must be canonical (sorted, no zeros) so different paths to same state produce identical representations.

**Wreath Products**: Similar to lamplighter but with more general top/base groups. Uses adapter pattern to handle different group operations.

**Free Group**: Tuples of letters with automatic reduction - whenever we append a letter, immediately cancel if it's inverse of last letter.

### Performance

BFS complexity is O(|V| + |E|) where V is vertices in ball and E is edges.

For radius R:
- Z²: |V| ~ R², |E| ~ R² (polynomial)
- Lamplighter: |V| ~ c^R where c ≈ 2.5 (exponential)

The slowest part is usually creating and hashing states. Python dicts are fast, and tuples hash quickly, so this works well up to ~10,000 vertices.

Beyond that, you'd want to optimize state representation or use different data structures. But for exploring small balls (R ≤ 10), this simple approach is fine.

## File Formats

### DOT (Graphviz)

Text format for graph visualization:
```dot
digraph G {
  v0 [label="e"];
  v1 [label="t"];
  v0 -> v1 [label="t"];
  ...
}
```

Convert to image: `dot -Tpng graph.dot -o graph.png`

### PNG

The code generates PNG directly using Graphviz's `dot` command if available, otherwise falls back to matplotlib/networkx.

## References

This implements algorithms from geometric group theory for computing Cayley graphs. Key concepts:

- **Cayley graphs**: Standard construction relating groups and graphs
- **Word metric**: Distance = shortest word length
- **Growth rates**: Polynomial vs exponential classification
- **Dead-end elements**: Trap elements in spheres (see Cleary-Taback papers)
