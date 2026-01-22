# Lamplighter group - wreath product C ≀ Z
# Standard definition: C is finite (lamp group), Z is the walking group


from .wreath import WreathProduct


class Lamplighter:
    # Lamplighter group C ≀ Z with configurable lamp group C
    # Just a thin wrapper around WreathProduct for convenience
    name = "Lamplighter"
    
    def __init__(self, spec="Z/2 wr Z", offsets=None):
        # Create underlying wreath product
        self.wreath = WreathProduct()
        self.wreath.is_lamplighter = True  # Mark for word-based visualization
        self.spec = spec
        self.offsets = offsets
        self._configured = None
    
    def identity(self):
        if not self._configured:
            self._configure()
        return self._configured.identity()
    
    def _configure(self):
        # Configure the underlying wreath product
        opts = {'spec': self.spec}
        if self.offsets is not None:
            opts['offsets'] = self.offsets
        self._configured = self.wreath.parse_options(opts)
    
    def default_generators(self):
        if not self._configured:
            self._configure()
        return self._configured.default_generators()
    
    def parse_options(self, opts):
        # Parse user input
        spec = opts.get("spec", "Z/2 wr Z")
        offsets = opts.get("offsets", None)
        
        # Create and configure new instance
        lamp = Lamplighter(spec=spec, offsets=offsets)
        lamp._configure()
        return lamp._configured  
    
    def pretty(self, s):
        if not self._configured:
            self._configure()
        return self._configured.pretty(s)


def dead_end_scan(group, gens, labels, R, depth_cap, bfs_build):
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
