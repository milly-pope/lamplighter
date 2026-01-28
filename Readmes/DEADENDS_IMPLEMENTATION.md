# Dead-End Element Detection

## What It Does

Finds elements on sphere S_R that are "trapped" - where all one-step generator moves keep you at the same distance or move you closer to identity.

For each dead-end found, computes the minimum number of steps needed to escape the ball B_R.

## Mathematical Definition

An element g at distance R is a **dead-end** if:
- ∀s ∈ S: |gs| ≤ R

where S is the generator set and |·| denotes word length.

The **depth** of a dead-end is:
- min{k ≥ 1 : ∃ word w of length k with |gw| ≥ R+1}

## Implementation

### Core Algorithm (`cayleylab/features/deadends.py`)

**analyze_dead_ends(group, gens, labels, R, depth_cap, V, dist, visited)**
- Scans sphere S_R for vertices with no outward edges
- For each dead-end, runs local BFS to find escape depth
- Returns dict with counts and examples

**_compute_depth(start_vid, V, dist, visited, gens, labels, R, depth_cap)**  
- Local BFS from dead-end vertex
- Searches for shortest path exiting ball B_R
- Bounded by depth_cap to avoid infinite search
- Returns (depth, witness_word)

**print_dead_end_results(results, max_examples)**
- Formats output for terminal display
- Shows statistics and individual examples

### Helper Function (`cayleylab/core/bfs.py`)

**transitions_from(gens, state)**
- Yields (gen_index, next_state) for each generator
- Used by both main BFS and dead-end depth search

## Menu Integration

Dead-end detection is available in the interactive menu for groups that support it:

```
Select a mode:
  1) Build a radius-n ball (PNG/DOT export)
  2) Analyze growth rate
  3) Evaluate a word
  4) Find dead-end elements
  5) Back
```

## Usage Flow

1. Select group (Lamplighter or Wreath)
2. Configure generators/offsets
3. Choose "Find dead-end elements"
4. Specify:
   - R: radius to analyze
   - depth_cap: maximum depth to search
   - max_examples: how many to display
5. System builds ball to R + depth_cap
6. Analyzes sphere S_R for dead-ends
7. Displays results with witness words

## Example Output

```
Layer size |S_7| = 123
Dead ends found: 1
Depth range among dead ends: 3 .. 3

Showing 1 of 1 dead end(s):
[vid=194] d=7  depth=3  state=p=0|-1:1;0:1;1:1  witness=t t t
```

## Known Dead-End Examples

### Lamplighter (Z/2 ≀ Z)
- **State**: Three consecutive lamps lit, head at position 0
- **Configuration**: pattern=[2], unit step, gens={a,t,T}
- **Radius**: Appears at R=7
- **Depth**: 3 (witness: t t t)

This is the canonical lamplighter dead-end studied in the literature.

## Performance Notes

- Must build ball to R + depth_cap (can be expensive for large R)
- Depth computation uses local BFS from each dead-end
- Bounded search prevents infinite loops in groups without escape paths
