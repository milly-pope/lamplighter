# State = (p: int, tape: tuple of (i, val) pairs) -- sorted for canonical form


def make_modulus_func(pattern):
    # Returns a function that gives the modulus at position i
    def modulus_at(i):
        return pattern[i % len(pattern)]
    return modulus_at


def encode_state(p, tape_dict, modulus_at):
    # Normalize tape: sorted tuple of (index, residue) pairs, zeros dropped
    out = []
    for i in sorted(tape_dict.keys()):
        v = tape_dict[i]
        m = modulus_at(i)
        r = v % m
        if r != 0:
            out.append((i, r))
    return (p, tuple(out))


class Toggle:
    # Toggle generator: modifies tape at a specific offset
    def __init__(self, name, offset, delta, pattern):
        self.delta = delta
        self.pattern = pattern
        self.modulus_at = make_modulus_func(pattern)
    
    def apply(self, s):
        p, tape_tuple = s
        # Convert tape to dict
        tape = {i: v for i, v in tape_tuple}
        # Toggle at position p + offset
        idx = p + self.offset
        old_val = tape.get(idx, 0)
        new_val = old_val + self.delta
        if new_val == 0:
            tape.pop(idx, None)
        else:
            tape[idx] = new_val
        # Re-encode
        return encode_state(p, tape, self.modulus_at)


class Step:
    # Step generator: moves the head position
    def __init__(self, name, step_amount, pattern):
        self.name = name
        self.step = step_amount
        self.modulus_at = make_modulus_func(pattern)
    
    def apply(self, s):
        p, tape_tuple = s
        # Convert tape to dict
        tape = {i: v for i, v in tape_tuple}
        # Move head
        new_p = p + self.step
        # Re-encode (tape unchanged)
        return encode_state(new_p, tape, self.modulus_at)


class Lamplighter:
    # Lamplighter group over Z
    # State = (p, tape) where tape is canonical tuple of (i, val) pairs
    # Options: pattern (list of moduli), step_mode ("unit" or "block"), offsets (for toggles)
    name = "Lamplighter"
    
    def __init__(self, pattern=None, step_mode="unit", offsets=None):
        self.pattern = pattern or [2]
        self.step_mode = step_mode
        self.offsets = offsets or [0]
    
    def identity(self):
        return (0, ())
    
    def _step_size(self):
        return 1 if self.step_mode == "unit" else len(self.pattern)
    
    def default_generators(self):
        gens = []
        step = self._step_size()
        
        # Step generators t, T
        gens.append(Step("t", +step, self.pattern))
        gens.append(Step("T", -step, self.pattern))
        
        # Toggle generators at specified offsets
        for j in self.offsets:
            if j < 0 or j >= len(self.pattern):
                continue
            name = chr(ord('a') + j)
            gens.append(Toggle(name, j, +1, self.pattern))
            
            # Add uppercase inverse if modulus > 2
            m = self.pattern[j]
            if m > 2:
                inv_name = chr(ord('A') + j)
                gens.append(Toggle(inv_name, j, -1, self.pattern))
        
        return gens
    
    def parse_options(self, opts):
        pat = opts.get("pattern", [2])
        mode = opts.get("step_mode", "unit")
        offs = opts.get("offsets", [0])
        return Lamplighter(pattern=pat, step_mode=mode, offsets=offs)
    
    def pretty(self, s):
        p, tape = s
        if not tape:
            return f"p={p}"
        body = ";".join(f"{i}:{v}" for (i, v) in tape)
        return f"p={p}|{body}"


# Register this group
from .base import register
register(Lamplighter())


def dead_end_scan(group, gens, labels, R, depth_cap, bfs_build):
    # Builds to R + depth_cap, analyzes dead ends, and prints results
    # No JSON/PNG artifacts generated
    from ..features.deadends import analyze_dead_ends, print_dead_end_results
    
    # Build ball to R + depth_cap
    print(f"\nBuilding ball to radius {R + depth_cap}...")
    V, E, dist, labels_bfs, words = bfs_build(group, gens, R + depth_cap)
    
    # Create state → vid mapping
    visited = {V[i]: i for i in range(len(V))}
    
    # Analyze dead ends
    print(f"Analyzing dead ends on layer {R}...")
    results = analyze_dead_ends(group, gens, labels, R, depth_cap, V, dist, visited)
    
    # Print results
    return results
