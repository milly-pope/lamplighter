# CayleyLab

An interactive terminal application for exploring Cayley graphs of groups.

## Features

- **Three group families**: Z², D∞, and Lamplighter/Wreath products
- **Generic BFS**: Single algorithm works for any group via Protocol interface
- **Interactive CLI**: Numbered menus for all operations
- **Exports**: JSON and DOT (Graphviz) formats
- **Verification**: Built-in checks for ball sizes and structural properties
- **Standard library only**: No external dependencies

## Installation

No installation needed! Just run from the lamplighter directory:

```bash
python -m cayleylab
```

## Usage

### Interactive Mode

Launch the interactive menu:

```bash
python -m cayleylab
```

You'll see:

1. **Group selection**: Choose Z², D∞, or Lamplighter
2. **Mode selection**: Build ball, Evaluate word, or Verify
3. **Configuration**: Each group has specific options
4. **Export**: Save as JSON and DOT files

### Group-Specific Options

**Z²**
- State: (x, y) pairs
- Generators: x, X, y, Y (standard basis ±e₁, ±e₂)
- Distance: L1 metric

**D∞**
- State: (k, eps) where k ∈ Z, eps ∈ {0,1}
- Generators: r (rotation), R (inverse rotation), s (reflection)
- Every element is r^m or r^m s

**Lamplighter / Wreath**
- State: (p, tape) where p = head position, tape = lamp states
- Options:
  - `pattern`: List of moduli [m₀, m₁, ...] (default [2])
  - `step_mode`: "unit" (±1) or "block" (±B where B = len(pattern))
  - `offsets`: Which toggles to expose (0→a, 1→b, 2→c, ...)
- Generators:
  - t, T: move head
  - a, b, c: toggle lamps at offsets 0, 1, 2
  - A, B, C: inverse toggles (only for mod > 2)

### Programmatic Usage

```python
from cayleylab.core.bfs import build_ball
from cayleylab.core.export import write_json, write_dot
from cayleylab.groups.Z2 import Z2

# Create group and generators
z2 = Z2()
gens = z2.default_generators()

# Build radius-3 ball
V, E, dist, labels = build_ball(z2, gens, radius=3)

# Export
write_json(V, E, dist, labels, z2, "z2_ball.json")
write_dot(V, E, dist, labels, z2, "z2_ball.dot")

print(f"|V| = {len(V)}, |E| = {len(E)}")
```

## Verification

Each group has known formulas for ball sizes:

- **Z²**: |B(n)| = 2n(n+1) + 1
- **D∞**: |B(0)| = 1, |B(n)| = 4n for n ≥ 1
- **Lamplighter L₂** (pattern=[2], unit step, gens={a,t,T}):
  - n=0,1,2,3,4,5 → |V|=1,4,10,22,44,84

Run verification from the interactive menu or programmatically:

```python
from cayleylab.verify.checks import check_generic, check_Z2_counts

V, E, dist, labels = build_ball(z2, gens, 3)

# Generic checks (edges, distances, connectivity)
errors = check_generic(V, E, dist)
if errors:
    for err in errors:
        print(f"FAIL: {err}")
else:
    print("PASS: All generic checks passed")

# Family-specific check
err = check_Z2_counts(3, len(V))
if err:
    print(f"FAIL: {err}")
else:
    print(f"PASS: Ball size correct")
```

## File Structure

```
cayleylab/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for python -m cayleylab
├── core/
│   ├── types.py          # Protocol definitions
│   ├── bfs.py            # Generic BFS algorithm
│   └── export.py         # JSON and DOT export
├── groups/
│   ├── base.py           # Group registry
│   ├── Z2.py             # Z² implementation
│   ├── Dinf.py           # D∞ implementation
│   └── lamplighter.py    # Lamplighter/Wreath implementation
├── ui/
│   ├── screens.py        # UI helpers (menus, prompts)
│   └── main.py           # Interactive menu system
└── verify/
    └── checks.py         # Verification functions
```

## Examples

### Build Z² ball radius 3

```bash
python -m cayleylab
# Select: 1) Z^2
# Select: 1) Build a radius-n ball
# Radius: 3
# Files: z2_r3.json, z2_r3.dot
```

### Evaluate word in Lamplighter

```bash
python -m cayleylab
# Select: 3) Lamplighter / Wreath
# Select: 2) Evaluate a word
# Pattern: 2
# Step mode: unit
# Offsets: 0
# Word: t a T
# Result: p=0|1:1
```

### Verify D∞ ball

```bash
python -m cayleylab
# Select: 2) D∞
# Select: 3) Verify
# Radius: 3
# Output: PASS for generic checks and |B(3)|=12
```

## Export Formats

### JSON Schema

```json
{
  "meta": {
    "group": "Group Name",
    "generators": ["g1", "g2", ...],
    "radius": n
  },
  "vertices": [
    {"id": 0, "dist": 0, "label": "...", "raw": "..."}
  ],
  "edges": [
    {"u": 0, "v": 1, "gen": "g1"}
  ]
}
```

### DOT Format

```dot
digraph G {
  graph [splines=true];
  node [shape=record];
  v0 [label="0|p=(0,0)|d=0"];
  v0 -> v1 [label="x"];
  ...
}
```

Render with Graphviz:
```bash
dot -Tpng z2_r3.dot -o z2_r3.png
```

## Adding New Groups

1. Create a new file in `cayleylab/groups/`
2. Implement the `Group` protocol:
   - `name`: string
   - `identity()`: return identity state
   - `default_generators()`: return list of Gen objects
   - `parse_options(opts)`: configure from dict
   - `pretty(state)`: format state for display
3. Implement `Gen` protocol for each generator:
   - `name`: string
   - `apply(state)`: return new state
4. Register with `register(YourGroup())`
5. Import in `cayleylab/groups/__init__.py`

## License

MIT
