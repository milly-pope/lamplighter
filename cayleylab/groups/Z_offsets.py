# Z with custom offsets for dissertation exercises

class OffsetGenerator:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset
    
    def apply(self, n):
        return n + self.offset


class Z_Offsets:
    name = "Z"
    
    def __init__(self, offsets=None):
        self.offsets = offsets or {'a': 1}
    
    def identity(self):
        return 0
    
    def default_generators(self):
        gens = []
        for name, offset in sorted(self.offsets.items()):
            gens.append(OffsetGenerator(name, offset))
            inverse_name = name.upper() if name.islower() else name.lower()
            gens.append(OffsetGenerator(inverse_name, -offset))
        return gens
    
    def parse_options(self, opts):
        return Z_Offsets(opts.get('offsets', self.offsets))
    
    def pretty(self, n):
        return f"{n}"
