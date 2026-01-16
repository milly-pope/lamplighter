# Group Implementation Guide (For Dissertation)

## General Concepts Across All Groups

### Why Canonical Representation Matters

**The fundamental problem:** Computers cannot manipulate abstract group elements directly. We need concrete data structures (tuples, integers, dictionaries) to represent elements, but the same group element can be reached via many different operation sequences.

**Example in any group:**
- Path 1: identity → apply generator a → apply generator b
- Path 2: identity → apply generator b → apply generator a  
- If ab = ba in the group, these reach the same element

**Critical requirement for BFS:** The hash table `visited = {}` must recognize when we've reached the same element via different paths. This requires:

1. **Uniqueness:** Each group element has exactly one representation
2. **Deterministic:** Same element always produces same representation
3. **Hashable:** Representation can be used as dictionary key in Python

**This is NOT about algebra** - computers don't "understand" that ab = ba algebraically. We must ensure that when we compute ab and ba, we get identical Python tuples (or whatever data structure we use) so the hash table recognizes them as the same.

### How Different Groups Achieve Canonicalization

**Each group has different challenges:**

**Z²** - Simple, already canonical:
- State: `(x, y)` just integer coordinates
- Multiplication: `(x₁, y₁) + (x₂, y₂) = (x₁+x₂, y₁+y₂)`
- Already canonical - addition commutes, result is unique

**D∞** - Minimal normalization:
- State: `(k, ε)` where k ∈ Z, ε ∈ {0,1}
- Every element is uniquely r^k or r^k·s
- Almost canonical - just track rotation count and reflection bit

**Free Group F₂** - Active reduction:
- State: tuple of letters `('a', 'b', 'A')`
- Must cancel adjacent inverses: aA → ε, Bb → ε
- Reduction happens during construction, not after

**Lamplighter (Z/m ≀ Z)** - Complex canonicalization:
- State: `(p, tape)` where tape is sparse map
- **Requires explicit normalization:** sort positions, drop zeros, reduce mod m
- Why complex: infinite tape must be represented sparsely and consistently

**Wreath Products (C ≀ D)** - Generalizes lamplighter:
- State: `(d, tape)` where d is in top group, tape maps D → C
- Same sparse canonicalization issues as lamplighter
- Different groups D have their own canonical forms too

### What's Universal vs Group-Specific

**Universal (every group must provide):**
- `identity()` - starting state
- `default_generators()` - list of generator objects
- `pretty(state)` - human-readable string
- Each generator must have `apply(state)` method

**Group-specific:**
- How states are represented (tuples? dicts? integers?)
- Whether canonicalization is needed after operations
- How generators transform states

**The "tape" representation is NOT universal** - only lamplighter and wreath products use it. Z² uses coordinates, free groups use letter sequences, etc.

---

## Lamplighter-Specific Implementation

Now we focus on the lamplighter group specifically, which has the most complex canonicalization requirements.

## 1. State Representation (Lamplighter Only)

### Mathematical Definition
The lamplighter group L_m = Z/m ≀ Z consists of elements (p, f) where:
- p ∈ Z is the "head position"
- f: Z → Z/m is a function with **finite support** (only finitely many non-zero values)

### Computational Representation
**State format:** `(p, tape)` where:
- `p` is an integer (head position)
- `tape` is a **sorted tuple** of `(position, value)` pairs

**Example:** Head at position 0 with lamps lit at positions -1, 0, 1:
```
(0, ((-1, 1), (0, 1), (1, 1)))
```

### Why This Representation?

**Canonical form is essential:** Multiple sequences of operations can reach the same group element. For BFS to work correctly, identical elements must have identical representations (so the hash table recognizes them as the same).

**Canonicalization rules:**
1. **Sorted:** Positions in increasing order `(-1, 0, 1)` not `(1, -1, 0)`
2. **Sparse:** Only store non-zero values (empty positions assumed 0)
3. **Reduced modulo m:** Each value in range `0, 1, ..., m-1`
4. **Tuple (immutable):** Allows hashing for dictionary lookup

**Example of why sorting matters:**
- Operation sequence 1: Start at identity → move right → toggle → move left
- Operation sequence 2: Start at identity → toggle → move right → move left
- Both reach same element: head at 0, lamp at position 0 lit
- Must produce same representation: `(0, ((0, 1),))`

---

## 2. Generator Classes (Step and Toggle)

### Old System (genspec)
Previously used a JSON-like specification where generators could be complex "words" (sequences of primitives). This was flexible but complicated.

### New System (Simple Classes)
Generators are now simple objects with an `apply(state)` method:

**Step generators** - Move the head:
```python
class Step:
    def __init__(self, name, step_amount, pattern):
        self.name = name           # e.g., "t" or "T"
        self.step = step_amount    # e.g., +1 or -1
        self.pattern = pattern     # moduli pattern [2] or [2,3]
    
    def apply(self, state):
        p, tape = state
        new_p = p + self.step
        return encode_state(new_p, tape_dict, modulus_at)
```

**Toggle generators** - Flip a lamp:
```python
class Toggle:
    def __init__(self, name, offset, delta, pattern):
        self.name = name           # e.g., "a" or "A"
        self.offset = offset       # where to toggle (0 = at head)
        self.delta = delta         # +1 or -1
        self.pattern = pattern
    
    def apply(self, state):
        p, tape = state
        idx = p + self.offset      # absolute position
        new_value = (old_value + delta) % modulus
        # Update tape at idx, re-canonicalize
        return encode_state(p, new_tape_dict, modulus_at)
```

### Why This Design?

**Generators as objects:** Each generator knows how to transform states. BFS just calls `g.apply(state)` without knowing what g does internally.

**Single operations only:** Unlike the old genspec system where generators could be "words" (sequences), each generator now performs one atomic operation:
- `t`: move right one step
- `T`: move left one step  
- `a`: toggle lamp at current position

**Compound words built by BFS:** The word "tat" (move right, toggle, move right) is created by BFS applying three separate generators, not by having a compound generator.

---

## 3. Canonicalization Process

### The encode_state Function

Every operation ends with canonicalization:

```python
def encode_state(p, tape_dict, modulus_at):
    # Input: p (int), tape_dict (dict from position → value)
    # Output: canonical (p, tape_tuple)
    
    out = []
    for i in sorted(tape_dict.keys()):    # SORT positions
        v = tape_dict[i]
        m = modulus_at(i)                 # Get modulus for this position
        r = v % m                         # REDUCE mod m
        if r != 0:                        # Only store NON-ZERO
            out.append((i, r))
    
    return (p, tuple(out))                # Return as TUPLE
```

**Step-by-step example:**

Starting state: `(0, ())`  [identity]

Apply toggle at position 0:
1. Convert to dict: `tape = {}`
2. Set `tape[0] = 0 + 1 = 1`
3. Canonicalize:
   - Sort keys: [0]
   - Reduce: 1 % 2 = 1
   - Non-zero: include it
   - Result: `(0, ((0, 1),))`

Apply move right (+1):
1. Head: 0 + 1 = 1
2. Tape unchanged: `{0: 1}`
3. Canonicalize:
   - Sort: [0]
   - Result: `(1, ((0, 1),))`

Apply toggle at new position (1):
1. Tape[1] = 0 + 1 = 1
2. Now tape = `{0: 1, 1: 1}`
3. Canonicalize:
   - Sort: [0, 1]
   - Result: `(1, ((0, 1), (1, 1)))`

### Why Canonicalize After Every Operation?

**Hash table correctness:** BFS uses `visited = {}` dictionary to track seen states. Python hashes tuples efficiently, but only if they're canonical:
- `((0, 1), (1, 1))` and `((1, 1), (0, 1))` would hash differently
- Must ensure same element always produces same tuple

---

## 4. How BFS Uses These Generators

### The Flow

1. **BFS starts** with identity: `state = (0, ())`

2. **BFS loops** through generators:
   ```python
   for gi, g in enumerate(gens):
       new_state = g.apply(state)
   ```

3. **Generator applies operation:**
   - Step: changes p, keeps tape
   - Toggle: keeps p, modifies tape
   - Both return **canonical state**

4. **BFS checks hash table:**
   ```python
   if new_state in visited:
       # Already seen this element
   else:
       # New element, add to queue
   ```

5. **Canonical representation ensures:**
   - Same element from different paths → same hash → recognized as duplicate
   - Different elements → different hashes → correctly distinguished

### Example BFS Trace

Starting from `e = (0, ())` with generators `[t, T, a]`:

```
Queue: [(0, ())]
Visited: {(0, ()): 0}

Process (0, ()):
  Apply t → (1, ())         [new, add to queue]
  Apply T → (-1, ())        [new, add to queue]
  Apply a → (0, ((0,1),))   [new, add to queue]

Queue: [(1, ()), (-1, ()), (0, ((0,1),))]

Process (1, ()):
  Apply t → (2, ())         [new]
  Apply T → (0, ())         [SEEN - don't add]
  Apply a → (1, ((1,1),))   [new]

...and so on
```

**Key insight:** When T is applied to `(1, ())`, it produces `(0, ())` which is already in visited, so BFS correctly recognizes this as creating an edge back to the identity rather than a new vertex.

---

## 5. Pattern (Variable Moduli)

### Single Modulus (Standard Lamplighter)

`pattern = [2]` means all positions are mod 2:
- Position 0: Z/2
- Position 1: Z/2
- Position -5: Z/2
- Every lamp is binary

### Block Pattern (Generalization)

`pattern = [2, 3]` means moduli repeat:
- Position 0: Z/2 (0 % 2 = 0 → pattern[0])
- Position 1: Z/3 (1 % 2 = 1 → pattern[1])
- Position 2: Z/2 (2 % 2 = 0 → pattern[0])
- Position 3: Z/3 (3 % 2 = 1 → pattern[1])

The `modulus_at(i)` function computes: `pattern[i % len(pattern)]`

**Why this matters:**
- Allows studying Z/m ≀ Z for m > 2
- Enables mixed-modulus configurations
- Toggles need inverse generators when m > 2

---

## 6. Default Generators

```python
def default_generators(self):
    gens = []
    step = self._step_size()    # 1 for "unit", len(pattern) for "block"
    
    # Movement
    gens.append(Step("t", +step, self.pattern))
    gens.append(Step("T", -step, self.pattern))
    
    # Toggles at specified offsets
    for j in self.offsets:
        name = chr(ord('a') + j)                    # a, b, c, ...
        gens.append(Toggle(name, j, +1, self.pattern))
        
        if self.pattern[j] > 2:                     # Need inverse
            inv_name = chr(ord('A') + j)            # A, B, C, ...
            gens.append(Toggle(inv_name, j, -1, self.pattern))
    
    return gens
```

**Standard configuration** `pattern=[2], step_mode="unit", offsets=[0]`:
- Generators: `t` (move right 1), `T` (move left 1), `a` (toggle at head)
- This is the classical lamplighter L_2

**Extended configuration** `pattern=[3], step_mode="unit", offsets=[0]`:
- Generators: `t`, `T`, `a` (toggle +1 mod 3), `A` (toggle -1 mod 3)
- This is Z/3 ≀ Z

---

## For Your Dissertation: General Introduction

### Suggested Opening for Implementation Section

**Section 2.4: Group Implementations and Canonical Representation**

"A fundamental challenge in computational group theory is representing abstract group elements as concrete data structures. While mathematically we work with elements g ∈ G, computationally we must use tuples, integers, or other Python objects. The critical requirement is **canonical representation**: the same group element must always be represented by the same Python object, regardless of which sequence of operations produced it.

This canonicality is essential for BFS, which uses a hash table to track visited states. When two different operation sequences reach the same group element, the hash table must recognize them as identical. This requires not algebraic understanding, but exact equality of data structures—the computer cannot deduce that ab = ba; we must ensure both computations produce identical tuples.

Different groups achieve canonicalization in different ways depending on their structure. The integer lattice Z² naturally has unique representation via coordinates. The free group F₂ requires active reduction (canceling adjacent inverses). The lamplighter group has the most complex requirements: infinite sparse tapes must be normalized consistently."

### Then Subsections for Each Group

**2.4.1 Integer Lattice Z²**
"States are pairs (x, y) ∈ Z². Generators move in cardinal directions: x±e₁, X±e₁, y±e₂, Y±e₂. Representation is inherently canonical—integer arithmetic produces unique results."

**2.4.2 Free Group F₂**  
"States are reduced words, represented as tuples of letters from {a, b, A, B}. Generators append letters with automatic reduction: if the new letter is the inverse of the previous, both cancel. This ensures words remain reduced throughout BFS."

**2.4.3 Infinite Dihedral Group D∞**
"Elements have unique form r^k or r^k·s. States are pairs (k, ε) where k ∈ Z counts rotations and ε ∈ {0,1} indicates reflection. Generators apply via group multiplication with minimal normalization needed."

**2.4.4 Lamplighter Group Z/m ≀ Z** (detailed below)

**2.4.5 General Wreath Products C ≀ D**
"Generalizes the lamplighter approach: states (d, τ) where d ∈ D and τ: D → C is a finite-support function. The system supports various choices for C and D (cyclic groups, Z², dihedral groups, free groups) using adapter patterns for each group family."

---

## Lamplighter-Specific Details (For Subsection 2.4.4)

Now the detailed explanation specific to lamplighter:

### What to Include in Your Lamplighter Subsection

**Describe state representation (1-2 paragraphs):**
"Elements of the lamplighter group Z/m ≀ Z are represented as pairs (p, τ) where p ∈ Z is the head position and τ is a finite list of lit lamps. Computationally, I represent states as (p, tape) where tape is a sorted tuple of (position, value) pairs, storing only non-zero lamp values. This canonical form ensures that different operation sequences reaching the same group element produce identical representations, which is essential for the hash-based duplicate detection in BFS."

**Explain generator operations (1 paragraph):**
"Generators are of two types: Step generators move the head position without changing lamps, while Toggle generators increment a lamp value at a fixed offset from the head. Each generator has an apply(state) method that performs its operation and returns a canonicalized state. For example, the generator 't' moves the head right by one position, while generator 'a' increments the lamp at the current head position modulo m."

**Mention canonicalization (1 sentence):**
"After each operation, states are canonicalized by sorting lamp positions and reducing values modulo their respective moduli."

### What NOT to Include

- The actual Python code for encode_state
- Details of dictionary internals or hashing
- The chr(ord('a') + j) logic for naming
- Modulus_at function implementation

### Example Dissertation Text

**Section 2.4.2: Lamplighter Group Implementation**

The lamplighter group L_m = Z/m ≀ Z consists of pairs (p, f) where p ∈ Z is a "head position" and f: Z → Z/m has finite support. States are represented computationally as (p, τ) where τ is a sorted tuple of (i, v) pairs recording lit lamp positions and their values. Only non-zero values are stored, providing a sparse representation.

Generators are implemented as two types: Step generators that translate the head position (t: p ↦ p+1, T: p ↦ p-1), and Toggle generators that modify lamp values (a: f(p) ↦ f(p)+1 mod m). Each generator provides an apply(state) method used by BFS. After each operation, states are canonicalized—lamps are sorted by position, values reduced modulo m, and zeros removed—ensuring unique representation of group elements.

For the standard configuration with m=2 and generators S = {t, t⁻¹, a}, this produces the classical lamplighter Cayley graph. The system also supports variable moduli via a pattern parameter (e.g., [2,3] alternates Z/2 and Z/3 lamps) and configurable toggle offsets for different generator sets.

---

**That's all you need!** Keep it concise, mathematical, and focused on the essential ideas rather than implementation details.
