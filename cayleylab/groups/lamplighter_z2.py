

# State = ((x, y): position in Z², tape: tuple of ((i,j), val) pairs)


def encode_state(p, tape_dict):
    # Normalize tape and return canonical state (p, tape_tuple)
    # Tape is sorted tuple of ((x,y), val) pairs with zeros dropped
    out = []
    for pos in sorted(tape_dict.keys()):
        v = tape_dict[pos]
        if v % 2 != 0:  # C₂, so only 0 or 1
            out.append((pos, 1))
    return (p, tuple(out))


class Toggle:
    # Toggle generator: flips lamp at current position + offset
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset  # (dx, dy)
    
    def apply(self, s):
        (px, py), tape_tuple = s
        # Convert tape to dict
        tape = {pos: v for pos, v in tape_tuple}
        # Toggle at position (px + dx, py + dy)
        dx, dy = self.offset
        idx = (px + dx, py + dy)
        old_val = tape.get(idx, 0)
        new_val = (old_val + 1) % 2
        if new_val == 0:
            tape.pop(idx, None)
        else:
            tape[idx] = new_val
        return encode_state((px, py), tape)


class Step:
    # Step generator: moves head position in Z²
    def __init__(self, name, step):
        self.name = name
        self.step = step  # (dx, dy)
    
    def apply(self, s):
        (px, py), tape_tuple = s
        tape = {pos: v for pos, v in tape_tuple}
        dx, dy = self.step
        new_p = (px + dx, py + dy)
        return encode_state(new_p, tape)


class LamplighterZ2:
    # C₂ ℘ Z² (Lamplighter over Z²)
    # State = ((x,y): head position in Z², tape: sorted tuple of ((i,j), val) pairs)
    # Default generators: x, X (move right/left), y, Y (move up/down), a (toggle lamp at current position)
    name = "C₂ ≀ Z²"
    
    def __init__(self):
        pass
    
    def identity(self):
        return ((0, 0), ())
    
    def default_generators(self):
        return [
            Step("x", (1, 0)),    # right
            Step("X", (-1, 0)),   # left
            Step("y", (0, 1)),    # up
            Step("Y", (0, -1)),   # down
            Toggle("a", (0, 0)),  # toggle at current position
        ]
    
    def parse_options(self, opts):
        return LamplighterZ2()
    
    def pretty(self, s):
        (px, py), tape = s
        if not tape:
            return f"({px},{py})"
        lamps = ";".join(f"({i},{j}):{v}" for (i, j), v in tape)
        return f"({px},{py})|{lamps}"
