# Dead-End Element Detection - Implementation Summary

## What Was Implemented

Added "Find dead-end elements" feature to both **Lamplighter** and **Wreath** groups in the interactive menu system.

### Menu Structure
```
Lamplighter / Wreath Menu:
1) Build a radius-n ball (PNG/DOT export)
2) Analyze growth rate
3) Evaluate a word
4) Find dead-end elements          ← NEW
5) Verify (quick checks)
6) Back
```

## Files Created

### 1. `cayleylab/features/__init__.py`
Module initialization for features package.

### 2. `cayleylab/features/deadends.py` (164 lines)
Core dead-end detection algorithm:
- **`analyze_dead_ends()`**: Main analysis function
  - Identifies vertices on sphere S_R with no outward edges
  - Computes minimal depth to escape using local BFS
  - Returns structured results dictionary
  
- **`_compute_depth()`**: Local BFS from dead-end vertex
  - Searches for shortest path exiting ball B_R
  - Bounded by depth_cap
  - Returns (depth, witness_word)
  
- **`print_dead_end_results()`**: Terminal output formatter
  - Summary statistics (layer size, count, depth range)
  - Per-element details with witness words

## Files Modified

### 3. `cayleylab/core/bfs.py`
Added helper function:
```python
def transitions_from(gens, state):
    """Yield (gen_idx, next_state) for each generator applied to state."""
```

### 4. `cayleylab/groups/lamplighter.py`
Added:
```python
def run_dead_end_mode_lamplighter(group, gens, labels, R, depth_cap, bfs_build):
    """Find dead-end elements for lamplighter group."""
```

### 5. `cayleylab/groups/wreath.py`
Added:
```python
def run_dead_end_mode_wreath(group, gens, labels, R, depth_cap, bfs_build):
    """Find dead-end elements for wreath products."""
```

### 6. `cayleylab/ui/main.py`
- Added "Find dead-end elements" to mode list
- Implemented `dead_end_mode()` function with:
  - Standard blurb about dead-ends
  - Configuration for Lamplighter (pattern, step mode, offsets)
  - Configuration for Wreath (spec, offsets)
  - Parameter input (R, depth_cap, max_examples)
  - Calls appropriate group-specific handler

## Mathematical Specification

### Definitions
- **Dead-end element**: g at distance R where ∀s∈S, |g·s| ≤ |g|
  - No one-step edge from g leaves the ball B_R
  
- **Dead-end depth**: Smallest k ≥ 1 such that ∃ word w of length k with |g·w| ≥ R+1
  - Minimal steps needed to escape the ball

### Algorithm
1. Build ball to radius R + depth_cap (single BFS)
2. For each vertex v on sphere S_R:
   - Check all generator neighbors
   - If none reach distance R+1 → mark as dead-end
3. For each dead-end v:
   - Run local BFS from v (bounded by depth_cap)
   - Stop at first vertex with distance ≥ R+1
   - Record path length (depth) and generator sequence (witness)

### Output Format
```
Layer size |S_R| = <count>
Dead ends found: <count>
Depth range among dead ends: <min> .. <max>

Showing N of M dead end(s):
[vid=123] d=R  depth=3  state=<pretty>  witness=t t a
```

## Test Results

### Test 1: Lamplighter Canonical (PASSED ✓)
- Group: L₂ = Z/2 wr Z with generators {t, T, a}
- Parameters: R=7, depth_cap=6
- Result: Found 1 dead-end on layer 7
- Canonical element: `p=0|-1:1;0:1;1:1` (three consecutive lamps)
- Depth: 3, witness: `t t t`

### Test 2: Finite Wreath Product (PASSED ✓)
- Group: Z/2 wr Z/5 with generators {t, T, a}
- Tested at R=3,4,5 with depth_cap=6
- Results: Feature runs correctly, produces valid output
- No dead-ends found at these radii (as expected for finite group)

### Test 3: Correctness Properties (PASSED ✓)
Verified:
1. No vertex has dist > R + depth_cap ✓
2. Every vertex at R has geodesic parent at R-1 ✓
3. Non-dead-ends have at least one neighbor at R+1 ✓

### Additional Test: Z/2 wr Z/3
- Radius R=6, depth_cap=5
- Found: 1 dead-end at depth ≥6 (exceeds cap)
- State: `d=0|0:1;1:1;2:1` (all lamps lit in finite base)

## User Interface Copy

### Blurb (shown when selecting option 4):
```
Dead-end elements relative to the current generator set S:
v at distance R is a dead end if no one-step move increases distance (|v s| ≤ |v| for all s ∈ S).
Depth(v) is the smallest k ≥ 1 with a length-k word that exits B_R.
We build to radius R + depth_cap to certify detection and depth.
```

### Interactive Prompts:

**For Lamplighter:**
- Block pattern [default: 2]
- Step mode (unit/block) [default: unit]
- Toggle offsets [default: 0]
- Radius R to analyze [default: 7]
- Depth cap [default: 6]
- How many examples to show (0 = all) [default: 10]

**For Wreath:**
- Enter spec (C wr D)
- Offsets (comma-separated, default 'e')
- Radius R to analyze [default: 7]
- Depth cap [default: 6]
- How many examples to show (0 = all) [default: 10]

## Performance Notes

- **Single BFS**: Builds to R + depth_cap once (not per-vertex)
- **O(1) lookups**: Uses visited dict for state→vid mapping
- **Bounded search**: Local BFS capped at depth_cap steps
- **Early termination**: Stops on first successful escape path
- **No artifacts**: Terminal output only (no JSON/PNG)

## Compliance with Requirements

✅ Added to both Lamplighter and Wreath menus  
✅ Terminal output only (no JSON/PNG artifacts)  
✅ Uses existing BFS infrastructure (build_ball)  
✅ Correct mathematical definitions in comments/docstrings  
✅ Uses verbatim UI copy from master prompt  
✅ Handles depth_cap correctly (reports "≥cap+1" when exceeded)  
✅ Shows witness words with generator labels  
✅ Respects max_examples parameter (0 = show all)  
✅ Validates on canonical lamplighter example  
✅ Works with finite groups (Z/2 wr Z/n)  
✅ Existing modes remain unchanged  

## Example Usage

```bash
python -m cayleylab
# Select: 3) Lamplighter
# Select: 4) Find dead-end elements
# Configure: pattern=[2], offsets=[0], R=7, depth_cap=6
# Result: Finds p=0|-1:1;0:1;1:1 with depth 3
```

```bash
python -m cayleylab
# Select: 6) Wreath
# Select: 4) Find dead-end elements
# Configure: spec="Z/2 wr Z/5", R=4, depth_cap=6
# Result: Analysis runs, reports counts
```
