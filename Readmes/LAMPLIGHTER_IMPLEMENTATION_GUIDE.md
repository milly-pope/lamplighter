# Group Implementation Guide (For Dissertation)

## General Concepts Across All Groups

### Why Normalized Representation Matters

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

### How Different Groups Achieve Normalization

**Each group has different challenges:**

**Z²** - Simple, already normalized:
- State: `(x, y)` just integer coordinates
- Multiplication: `(x₁, y₁) + (x₂, y₂) = (x₁+x₂, y₁+y₂)`
- Already normalized - addition commutes, result is unique

**D∞** - Minimal normalization:
- State: `(k, ε)` where k ∈ Z, ε ∈ {0,1}
- Every element is uniquely r^k or r^k·s
- Just track rotation count and reflection bit

**Free Group F₂** - Active reduction:
- State: tuple of letters `('a', 'b', 'A')`
- Must cancel adjacent inverses: aA → ε, Bb → ε
- Reduction happens during construction, not after

**Lamplighter (Z/m ≀ Z)** - Complex normalization:
- State: `(p, tape)` where tape is sparse map
- **Requires explicit normalization:** sort positions, drop zeros, reduce mod m
- Why complex: infinite tape must be represented sparsely and consistently

**Wreath Products (C ≀ D)** - Generalizes lamplighter:
- State: `(d, tape)` where d is in top group, tape maps D → C
- Same sparse normalization issues as lamplighter
- Different groups D have their own normalized forms too

### What's Universal vs Group-Specific

**Universal (every group must provide):**
- `identity()` - starting state
- `default_generators()` - list of generator objects
- `pretty(state)` - human-readable string
- Each generator must have `apply(state)` method

**Group-specific:**
- How states are represented (tuples? dicts? integers?)
- Whether normalization is needed after operations
- How generators transform states

**The "tape" representation is NOT universal** - only lamplighter and wreath products use it. Z² uses coordinates, free groups use letter sequences, etc.

---

## For Your Dissertation

### Section 2.4: Group Implementations and Normalized Representation

"A fundamental challenge in computational group theory is representing abstract group elements as concrete data structures. While mathematically we work with elements g ∈ G, computationally we must use tuples, integers, or other Python objects. The critical requirement is **normalized representation**: the same group element must always be represented by the same Python object, regardless of which sequence of operations produced it.

This normalization is essential for BFS, which uses a hash table to track visited states. When two different operation sequences reach the same group element, the hash table must recognize them as identical. This requires not algebraic understanding, but exact equality of data structures—the computer cannot deduce that ab = ba; we must ensure both computations produce identical tuples.

Different groups achieve normalization in different ways depending on their structure. The integer lattice Z² naturally has unique representation via coordinates. The free group F₂ requires active reduction (canceling adjacent inverses). The lamplighter group has the most complex requirements: infinite sparse tapes must be normalized consistently."

### Subsections for Each Group

**2.4.1 Integer Lattice Z²**
"States are pairs (x, y) ∈ Z². Generators move in cardinal directions. Representation is inherently normalized—integer arithmetic produces unique results."

**2.4.2 Free Group F₂**  
"States are reduced words, represented as tuples of letters from {a, b, A, B}. Generators append letters with automatic reduction: if the new letter is the inverse of the previous, both cancel. This ensures words remain reduced throughout BFS."

**2.4.3 Infinite Dihedral Group D∞**
"Elements have unique form r^k or r^k·s. States are pairs (k, ε) where k ∈ Z counts rotations and ε ∈ {0,1} indicates reflection. Generators apply via group multiplication with minimal normalization needed."

**2.4.4 Lamplighter Group Z/m ≀ Z**

The lamplighter group is mathematically defined as C ≀ Z (wreath product of C with Z). The implementation treats it as a wreath product with top group Z and base group C.

**User interface:** Specify base group using standard notation:
- `Z/2 wr Z` → classical binary lamplighter
- `Z/3 wr Z` → ternary lamplighter  
- `Z/2,Z/3 wr Z` → product base (Z/2 × Z/3) ≀ Z

**State Representation:**

States are pairs (p, τ) where:
- p ∈ Z is the head position
- τ: Z → C is a finite-support function (the "tape")

Computationally: `(p, tape)` where `p` is an integer and `tape` is a sorted tuple of `(position, value)` pairs storing only non-identity values (sparse representation).

Example for Z/2 ≀ Z with lamps at {-1, 0, 1}:
```
(0, ((-1, 1), (0, 1), (1, 1)))
```

**Generators:**

Move generators (act on Z):
- `t`: head position p ↦ p + 1
- `T`: head position p ↦ p - 1

Toggle generators (act on C):
- `a`: lamp at position p changes f(p) ↦ f(p) + 1 mod m
- `A`: (for m > 2) lamp at position p changes f(p) ↦ f(p) - 1 mod m

Additional toggles `b`, `c`, ... can be configured for offsets relative to head position.

**Normalization:**

After each operation, states are normalized:
1. **Sorted:** Tape positions in increasing order
2. **Sparse:** Only non-identity values stored
3. **Reduced:** Values in range 0, 1, ..., m-1
4. **Immutable:** Tuple format for hashing

This ensures the same group element always has the same representation regardless of operation sequence, which is critical for BFS hash table lookups.

**Example configurations:**
- Standard lamplighter: `Z/2 wr Z` with generators {t, T, a}
- Ternary lamplighter: `Z/3 wr Z` with generators {t, T, a, A}
- Mixed moduli: `Z/2,Z/3 wr Z` alternating binary and ternary lamps

**2.4.5 General Wreath Products C ≀ D**
"Generalizes the lamplighter approach: states (d, τ) where d ∈ D and τ: D → C is a finite-support function. The system supports various choices for C and D (cyclic groups, Z², dihedral groups, free groups). Normalization follows the same principles as lamplighter but adapts to the structure of D."
