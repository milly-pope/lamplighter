# How to Use: Find Dead-End Elements

## Quick Start

Launch the interactive menu:
```bash
python -m cayleylab
```

Then navigate:
- **For Lamplighter**: Select `3) Lamplighter` → `4) Find dead-end elements`
- **For Wreath**: Select `6) Wreath` → `4) Find dead-end elements`

## What It Does

Finds elements on sphere S_R that are "trapped" — all one-step moves either:
- Stay at the same distance, or
- Move closer to the identity

For each trapped element, computes the minimal number of steps needed to escape.

## Example Sessions

### Lamplighter (Z/2 wr Z)

```
============================================================
  Lamplighter - Find Dead-End Elements
============================================================

Dead-end elements relative to the current generator set S:
v at distance R is a dead end if no one-step move increases distance (|v s| ≤ |v| for all s ∈ S).
Depth(v) is the smallest k ≥ 1 with a length-k word that exits B_R.
We build to radius R + depth_cap to certify detection and depth.

Block pattern [default: 2]: 2
Step mode (unit/block) [default: unit]: unit
Toggle offsets [default: 0]: 0

Generators: t, T, a

Radius R to analyze [default: 7]: 7
Depth cap (max search depth) [default: 6]: 6
How many examples to show (0 = all) [default: 10]: 10

Building ball to radius 13...
Analyzing dead ends on layer 7...

Layer size |S_7| = 123
Dead ends found: 1
Depth range among dead ends: 3 .. 3

Showing 1 of 1 dead end(s):
[vid=194] d=7  depth=3  state=p=0|-1:1;0:1;1:1  witness=t t t

Press Enter to continue...
```

**Interpretation**: 
- Layer 7 has 123 elements total
- Found 1 dead-end: three consecutive lamps lit, head at position 0
- Needs 3 steps to escape (witness word: `t t t`)
- This is the canonical lamplighter dead-end!

### Wreath Product (Z/2 wr Z/5)

```
============================================================
  Wreath - Find Dead-End Elements
============================================================

Dead-end elements relative to the current generator set S:
v at distance R is a dead end if no one-step move increases distance (|v s| ≤ |v| for all s ∈ S).
Depth(v) is the smallest k ≥ 1 with a length-k word that exits B_R.
We build to radius R + depth_cap to certify detection and depth.

Enter spec (C wr D): Z/2 wr Z/5
Offsets (comma-separated, default 'e'): e

Generators: t, T, a

Radius R to analyze [default: 7]: 4
Depth cap (max search depth) [default: 6]: 6
How many examples to show (0 = all) [default: 10]: 5

Building ball to radius 10...
Analyzing dead ends on layer 4...

Layer size |S_4| = 16
Dead ends found: 0
No dead ends found on layer 4.

Press Enter to continue...
```

**Interpretation**:
- Layer 4 has 16 elements
- No dead-ends at this radius
- Feature works correctly on finite groups

## Parameters Explained

### R (Radius)
Which sphere to analyze. Dead-ends are detected on S_R specifically.
- Larger R → more elements to check, more computation
- Lamplighter typically has dead-ends starting around R=5-7

### Depth Cap
Maximum steps to search when computing escape depth.
- If escape path longer than cap → reports "≥{cap+1}"
- Default 6 is usually sufficient
- Increase if you see many "≥7" results

### Max Examples
How many dead-ends to display.
- `0` = show all
- `10` = show first 10 (default)
- Useful when many dead-ends found

## Output Format

```
Layer size |S_R| = 123              ← Total elements at distance R
Dead ends found: 1                  ← How many are trapped
Depth range among dead ends: 3 .. 3 ← Min/max escape depths

Showing 1 of 1 dead end(s):
[vid=194]                           ← Vertex ID in the graph
d=7                                 ← Distance from identity
depth=3                             ← Steps needed to escape
state=p=0|-1:1;0:1;1:1              ← Pretty-printed state
witness=t t t                       ← Generator sequence to escape
```

## Mathematical Background

A **dead-end element** g at distance R has the property that every generator move either:
1. Keeps you at distance R: |g·s| = R
2. Decreases distance: |g·s| < R

The **depth** is the shortest word that increases distance:
- depth=1: Some single generator s with |g·s| = R+1 (not a dead-end!)
- depth=2: Need 2 moves to get to R+1
- depth=3: Need 3 moves to get to R+1
- depth≥k: Exceeds our search cap

## Typical Use Cases

### Research Questions
- "Does my group have dead-ends at radius R?"
- "What's the depth distribution of dead-ends?"
- "How does the dead-end count grow with R?"

### Verification
- Check canonical examples (e.g., lamplighter at R=7)
- Compare different generator sets
- Test theoretical predictions

### Exploration
- Find interesting elements in new groups
- Understand local geometry of Cayley graphs
- Discover patterns in wreath products

## Tips

1. **Start small**: Test at low R (3-5) first, then increase
2. **Use depth_cap wisely**: Default 6 works for most cases
3. **Check boundary size**: |S_R| shown first — if huge, consider smaller R
4. **No artifacts**: Unlike other modes, this doesn't create files
5. **Group configuration**: Uses same generator setup as other modes

## Technical Notes

- **Single BFS**: Builds to R + depth_cap once (efficient)
- **Bounded search**: Won't run forever even with infinite groups
- **Exact distances**: Uses actual BFS distances, not estimates
- **Witness words**: Shows actual generator sequence to escape
- **No duplicates**: Each dead-end reported once

## Supported Groups

✓ **Lamplighter** (Z/2 wr Z)
  - Configure: pattern, step mode, offsets
  - Example: pattern=[2], step_mode='unit', offsets=[0]

✓ **Wreath** (C wr D for any supported C, D)
  - Configure: spec string, offsets
  - Examples: 
    - "Z/2 wr Z/5"
    - "Free(2) wr Z"
    - "Z/3 wr Dn(4)"
    - "abelian([2,3]) wr Z2"

## Known Results

### Lamplighter L₂ = Z/2 wr Z
- **R=7**: Canonical dead-end at `p=0|-1:1;0:1;1:1` (depth 3)
- Pattern: Three consecutive lamps lit, head centered
- Witness: `t t t` (move right 3 times)

### Finite Groups (e.g., Z/2 wr Z/n)
- May or may not have dead-ends depending on R and n
- When they exist, usually at larger radii
- Depth can exceed cap more frequently

---

For implementation details, see `DEADENDS_IMPLEMENTATION.md`
