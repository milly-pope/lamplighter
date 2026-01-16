# Dead-End Elements Usage

## Quick Start

```bash
python -m cayleylab
```

Navigate to:
- Lamplighter → Find dead-end elements
- Wreath → Find dead-end elements

## What It Does

Finds elements at radius R where all generator moves either stay at distance R or move closer to identity.

For each dead-end, computes minimum steps needed to escape to radius R+1.

## Example: Lamplighter (Z/2 ≀ Z)

```
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
```

**Interpretation**: 
- Layer 7 has 123 elements
- Found 1 dead-end (three lamps lit, head at center)
- Needs 3 steps to escape (move right 3 times: `t t t`)

## Example: Wreath (Z/2 ≀ Z/5)

```
Enter spec (C wr D): Z/2 wr Z/5
Offsets (comma-separated, default 'e'): e

Generators: t, T, a

Radius R to analyze [default: 7]: 4
Depth cap (max search depth) [default: 6]: 6

Building ball to radius 10...

Layer size |S_4| = 16
Dead ends found: 0
```

No dead-ends at radius 4 for this finite group.

## Parameters

**R (Radius)**: Which sphere to analyze
- Larger R → more computation
- Lamplighter has dead-ends starting around R=5-7

**Depth Cap**: Maximum escape distance to search
- Default 6 usually sufficient
- If escape longer than cap, reports "≥{cap+1}"

**Max Examples**: How many to display (0 = all)

## Output Format

```
[vid=194]              ← Vertex ID
d=7                    ← Distance from identity
depth=3                ← Steps to escape
state=p=0|-1:1;0:1;1:1 ← State representation
witness=t t t          ← Escape sequence
```

## Mathematical Background

**Dead-end element** g at distance R: every generator s satisfies |g·s| ≤ R

**Depth**: Shortest word length to reach R+1 from g
- depth=1: Not a dead-end (some s gives |g·s| = R+1)
- depth≥2: Actual dead-end

## Use Cases

**Research**: "Does my group have dead-ends at radius R?"

**Verification**: Check canonical examples (lamplighter at R=7 has one)

**Exploration**: Find interesting elements in new groups

## Tips

- Start small: Test at R=3-5 first
- Default depth cap (6) works for most cases
- Check |S_R| first - if huge, use smaller R
- No files created (unlike export modes)

## Supported Groups

**Lamplighter** (Z/2 ≀ Z): Configure pattern, step mode, offsets

**Wreath** (C ≀ D): Specify using spec strings like "Z/2 wr Z/5", "Free(2) wr Z"

## Known Results

**Lamplighter L₂ = Z/2 ≀ Z at R=7**:
- One dead-end: `p=0|-1:1;0:1;1:1` (three lamps lit, head centered)
- Depth 3, witness: `t t t`
