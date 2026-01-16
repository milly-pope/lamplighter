

# State = (x, y) tuple of ints


class Move:
    # Generator that moves in Z^2 by a fixed vector
    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy
    
    def apply(self, s):
        x, y = s
        return (x + self.dx, y + self.dy)


class Z2:
    # Z^2 with standard basis generators {x, X, y, Y}
    name = "Z^2"
    
    def __init__(self, gens=None):
        self._gens = gens
    
    def identity(self):
        return (0, 0)
    
    def default_generators(self):
        # Symmetric standard basis: x, X, y, Y
        return [
            Move("x", +1, 0),
            Move("X", -1, 0),
            Move("y", 0, +1),
            Move("Y", 0, -1),
        ]
    
    def parse_options(self, opts):
        # No extra options for Z^2 right now
        return Z2()
    
    def pretty(self, s):
        x, y = s
        return f"p=({x},{y})"
