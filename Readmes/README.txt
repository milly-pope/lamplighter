Lamplighter package

Model (Turing-tape):
- State is (p, tape) where p in Z is lamplighter head position and tape is a finite-support map Z -> Z/m(i)Z.
- block_pattern: repeating list [m0,m1,...] determines modulus at absolute index i by m(i)=block_pattern[i mod len(block_pattern)].
- Canonical state: stored as (p, sorted tuple of (i,val)) where val in 1..m(i)-1; entries with val==0 dropped.

Generators:
- Primitives: move(k) moves head by k; toggle(offset,delta) increments site at absolute index p+offset by delta modulo m(site).
- Macros: finite words (sequences) of primitives; generators are macros applied as single labelled edges.

Step size and toggles:
- The CLI assumes a single step size equal to the block size (the length of `--pattern`).
    - `t` and `T` are reserved: they move by +block_size and -block_size respectively.
    - Toggles are specified by letters `a,b,c,...` corresponding to offsets `0,1,2,...` within the block; uppercase `A,B,C,...` denote the inverse toggle (delta = -1).
    - Example: `--pattern 2,4` has block size 2; `--gens a,b,B,t,T` means
        - `a`: toggle at offset 0 (even sites, mod 2)
        - `b`: toggle at offset 1 (odd sites, mod 4)
        - `B`: inverse toggle of `b` (i.e. -1 mod 4)
        - `t`: move +2, `T`: move -2
    - The CLI no longer auto-symmetrizes; pass inverses explicitly when you want an undirected Cayley graph.

BFS ball:
- build_ball(radius, gens, block_pattern, symmetrize) does BFS on the Cayley graph starting at identity (p=0, empty tape), expanding nodes with dist < radius.
- Vertices are canonical states; equality is literal equality of canonical representation.
- Deterministic: traversal order is gens order (with inverses appended if symmetrize), FIFO queue.

CLI:
- Run: python -m lamplighter --n 3 --pattern 2 --gens a,t,T --out ball3.json --dot ball3.dot
- Shorthand chars: t/T=move +/-1, s/S=move +/-N, a/b/c... = toggles at offsets 0/1/2/...
- Use --gens-file to supply structured JSON genspec list.

Tests:
- Run with --self-test or python -m lamplighter.tests
