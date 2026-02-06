# Quick Reference: Running the ℤ Offset Exercises

## For Your Dissertation

### Exercise 9: ⟨a,b | a² = b³, ab=ba⟩

**Mathematical setup:**
- Primitive generator: t
- a = t³, b = t²
- Offsets: a → +3, b → +2

**Command:**
```bash
python3 growth_cli.py --ex9
```

**Or with custom radius:**
```bash
python3 growth_cli.py --ex9 --radius 12
```

---

### Exercise 10: ⟨a,b | a² = b^(2k+1), ab=ba⟩

**Mathematical setup:**
- Primitive generator: t
- a = t^(2k+1), b = t²
- Offsets: a → +(2k+1), b → +2

**Command (k=2):**
```bash
python3 growth_cli.py --Z-k 2
```

**Or with custom radius:**
```bash
python3 growth_cli.py --Z-k 3 --radius 10
```

---

### Custom Offsets

For any presentation with offsets a and b:

```bash
python3 growth_cli.py --Z-offsets A B --radius N
```

**Example:** offsets a=7, b=3, radius=10:
```bash
python3 growth_cli.py --Z-offsets 7 3 --radius 10
```

---

## Expected Output Format

```
Group: Z with offsets a=+3, b=+2 (inverses auto)
Radius N = 8

r:         0   1   2   3   4   5   6   7   8
sigma_r:   1   4   8   6   6   6   6   6   6
b_r:       1   5  13  19  25  31  37  43  49

S_<=N(z): 1 + 4 z + 8 z^2 + 6 z^3 + 6 z^4 + 6 z^5 + 6 z^6 + 6 z^7 + 6 z^8
B_<=N(z): 1 + 5 z + 13 z^2 + 19 z^3 + 25 z^4 + 31 z^5 + 37 z^6 + 43 z^7 + 49 z^8
Check B == S/(1−z) mod z^(N+1): OK
```

---

## Programmatic Usage

```python
from cayleylab.groups.Z_offsets import Z_Offsets
from cayleylab.core.growth import analyze_growth, format_growth_table

# Create group with offsets
group = Z_Offsets({'a': 3, 'b': 2})
gens = group.default_generators()

# Analyze growth with series
result = analyze_growth(group, gens, radius=8, mode="investigate", show_series=True)
print(format_growth_table(result))

# Access raw data
print(f"σ_r: {result['sigma']}")
print(f"b_r: {result['b']}")
print(f"S(z) = {result['S_series']}")
print(f"B(z) = {result['B_series']}")
print(f"Verified: {result['series_identity_ok']}")
```

---

## Verification

The identity B(z) = S(z)/(1-z) is verified by:
1. Computing b_r from recursion: b_0 = σ_0, b_r = σ_r + b_{r-1}
2. Checking: b_r == Σ(σ_i for i=0..r) for all r ≤ N

This is mathematically equivalent to the polynomial division check.

---

## File Locations

**New code for exercises:**
- `cayleylab/groups/Z_offsets.py` - ℤ with custom offsets
- `cayleylab/core/growth.py` - Growth analysis and generating series  
- `growth_cli.py` - Command-line interface

**Existing code used:**
- `cayleylab/core/bfs.py` - Generic BFS algorithm
- `cayleylab/core/growth.py` - Growth analysis (optional)

---

## Example Session

```bash
$ python3 growth_cli.py --ex9
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
