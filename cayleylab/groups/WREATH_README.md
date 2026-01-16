# Wreath Product Implementation

## Overview

General regular wreath products **C ≀ D = C^(D) ⋊ D** with finite support.

The wreath product has states (d, tape) where:
- d ∈ D is the current position in the top group
- tape: D → C is a finite-support function (sparse map)

## Supported Groups

Both C (base/lamp group) and D (top/acting group) can be:

- **Z**: Integers
- **Z/n**: Cyclic group mod n
- **Z2**: Z² (free abelian rank 2)
- **D∞**: Infinite dihedral
- **Dn(n)**: Dihedral group of order 2n
- **Free(k)**: Free group on k generators

## Specification Format

Wreath products are specified as strings: `"C wr D"`

Examples:
- `"Z/2 wr Z"` - Standard lamplighter
- `"Z/5 wr Z/3"` - Finite wreath product
- `"Z wr Z2"` - Lamps over the grid
- `"Free(2) wr Dn(4)"` - Free base over dihedral

## Usage

### Interactive Mode

```
Select: Wreath
Enter spec (C wr D): Z/3 wr Z/5
Offsets (comma-separated, default 'e'): e, t, t t
```

The system then:
1. Parses the spec into base and top adapters
2. Creates move generators from D
3. Creates toggle generators at specified offsets
4. Returns configured wreath product ready for BFS

### Programmatic

```python
from cayleylab.groups.wreath import WreathProduct

wreath = WreathProduct()
configured = wreath.parse_options({
    "spec": "Z/3 wr Z2",
    "offsets": ["e", "x", "y"]
})

gens = configured.default_generators()
# Use with build_ball, etc.
```

## State Representation

States are `(d, tape)`:
- `d`: Current position in top group D
- `tape`: Sparse map D → C (only non-identity values stored)

Canonicalization:
- Tape stored as sorted tuple `((address, value), ...)`
- Only includes non-identity values
- Ensures same element = same representation

## Generators

**Move generators** (act in D):
- Z, Z/n: t, T (forward/back)
- Z²: x, X, y, Y (grid directions)
- D∞, Dn: r, R, s (rotation/reflection)
- Free: a, A, b, B, ...

**Toggle generators** (modify tape):
- Single offset: a, A, b, B, ... (from base group)
- Multiple offsets: Letters per offset (a=first, b=second, c=third, ...)
- Action: `tape[d·offset] ← tape[d·offset] · increment`

## Implementation Files

- wreath.py - Main class
- wreath_adapters_top.py - Top group D operations
- wreath_adapters_base.py - Base group C operations

## Examples

Standard lamplighter (Z/2 ≀ Z):
```python
spec = "Z/2 wr Z"
# Generators: t, T (move), a (toggle)
```

Grid lamplighter (Z/3 ≀ Z²):
```python
spec = "Z/3 wr Z2"
# Generators: x, X, y, Y (move), a, A (toggle Z/3)
```

Free base (Free(2) ≀ Z):
```python
spec = "Free(2) wr Z"
# Generators: t, T (move), a, A, b, B (Free(2) toggles)
```

## Notes

- Offsets default to `["e"]` (identity) - standard construction
- Tape auto-canonicalized (sorted, identity values dropped)
- Works with all existing tools (BFS, export, growth analysis)
