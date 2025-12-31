# Wreath Product Module

## Overview

The wreath product module implements general regular wreath products **C ≀ D = C^(D) ⋊ D** with finite support.

## Supported Groups

Both top (acting) group D and base (lamp) group C can be:
- **Z**: Integers
- **Z/n**: Cyclic group of order n
- **Z2**: Free abelian rank 2 (ℤ²)
- **D∞**: Infinite dihedral group
- **Dn(n)**: Finite dihedral of order 2n
- **Free(k)**: Free group of rank k
- **abelian([m1,m2,...])**: Finite abelian product

## Usage Examples

### Basic Spec Format

Specify wreath products as `"C wr D"`:

```python
"Z/2 wr Z"           # Standard lamplighter
"Z/5 wr Z2"          # Lamps Z/5 over grid
"abelian([2,4]) wr Z"  # Product base over integers
"Free(3) wr Dn(8)"   # Free base over dihedral
```

### Programmatic Usage

```python
from cayleylab.wreath.general import WreathProduct

wreath = WreathProduct()
configured = wreath.parse_options({
    "spec": "Z/3 wr Z2",
    "offsets": ["e", "x", "y"]  # Where toggles act
})

gens = configured.default_generators()
# Build ball, export, etc.
```

### Interactive UI

When selecting "Wreath" from the main menu:

1. Enter spec (e.g., `Z/2 wr Z/5`)
2. Specify offsets as words (default: `e` for identity only)
3. System generates move + toggle generators automatically
4. Build balls, analyze growth, evaluate words as usual

## State Representation

State = `(d, tape)` where:
- `d ∈ D`: Current position in top group
- `tape`: Sparse map from D → C (finite support)

Canonical form:
- Tape stored as sorted tuple `((addr, val), ...)`
- Only non-identity values included
- Addresses sorted deterministically

## Generators

### Move Generators
Act in top group D:
- **Cyclic (Z, Z/n)**: `t, T` (step forward/backward)
- **Grid (Z²)**: `x, X, y, Y` (cardinal directions)
- **Dihedral**: `r, R, s` (rotation and reflection)
- **Free**: `a, A, b, B, ...` (generators and inverses)

### Toggle Generators
Modify lamps at current position (default) or at offsets:
- Names: `a, A, b, B, c, C, ...` from base group increments
- For single offset (identity): uses base adapter names directly
- For multiple offsets: letters assigned per offset (a=first, b=second, etc.)
- Apply: Update `tape[d·offset] ← tape[d·offset] · increment`

## Export

DOT files are generated for Graphviz visualization with:
- Node labels showing words
- Edge labels showing generators
- Special layouts for Z² (Cartesian) and F₂ (tree)

## Architecture

- **adapters_top.py**: Top group operations (D)
- **adapters_base.py**: Base group operations (C)  
- **wreath.py**: Wreath product wrapper implementing Group protocol

Each adapter provides:
- Canonical element representation
- Group operations (identity, multiply, inverse)
- Pretty printing
- Default generators
- Word parsing

## Examples

### Standard Lamplighter (Z/2 ≀ Z)
```python
spec = "Z/2 wr Z"
# Generators: t, T (move in Z), a (toggle Z/2 lamp)
```

### Binary over Cyclic-5 (Z/2 ≀ Z/5)
```python
spec = "Z/2 wr Z/5"
# Generators: t, T (move in Z/5), a (toggle Z/2 lamp)
```

### Grid Lamplighter (Z/3 ≀ Z²)
```python
spec = "Z/3 wr Z2"
# Generators: x, X, y, Y (move in grid), a, A (toggle Z/3 lamp)
```

### Free Base over Integers (Free(2) ≀ Z)
```python
spec = "Free(2) wr Z"
# Generators: t, T (move in Z), a, A, b, B (Free(2) increments)
```

## Notes

- Offsets default to `["e"]` (identity only - standard semidirect product)
- Additional offsets enable toggling at relative positions (advanced usage)
- Tape automatically canonicalized (sorted, identity entries dropped)
- Works with existing BFS, export, growth, verify tools
- Consistent generator naming across all group families
