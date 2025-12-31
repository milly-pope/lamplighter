"""
General regular wreath product C ≀ D = C^(D) ⋊ D.
State = (d, tape) where d ∈ D and tape is finite-support function D → C.
"""

from typing import List, Dict, Tuple, Any
from ..core.types import Group, Gen, State
from .wreath_adapters_top import get_top_adapter
from .wreath_adapters_base import get_base_adapter


def canonicalize_tape(tape_dict, top_adapter, base_adapter):
    """
    Convert tape dict to canonical sorted tuple, dropping identity entries.
    Returns sorted tuple of ((addr, val), ...) where val ≠ base.one().
    """
    items = []
    for addr, val in tape_dict.items():
        if not base_adapter.is_one(val):
            items.append((addr, val))
    
    # Sort by some deterministic key
    # For tuples/primitives, standard sort works
    # For more complex types, may need custom key
    try:
        items.sort()
    except TypeError:
        # If not directly sortable, convert to string representation
        items.sort(key=lambda x: str(x[0]))
    
    return tuple(items)


class MoveGen:
    """Generator that moves in the top group D."""
    def __init__(self, name, d_elem, top_adapter, base_adapter):
        self.name = name
        self.d_elem = d_elem
        self.top = top_adapter
        self.base = base_adapter
    
    def apply(self, state):
        d, tape_tuple = state
        # New top position
        new_d = self.top.multiply(d, self.d_elem)
        # Tape unchanged
        return (new_d, tape_tuple)


class ToggleGen:
    """Generator that toggles lamp at offset in D."""
    def __init__(self, name, offset, increment, top_adapter, base_adapter):
        self.name = name
        self.offset = offset
        self.increment = increment
        self.top = top_adapter
        self.base = base_adapter
    
    def apply(self, state):
        d, tape_tuple = state
        # Convert tape to dict
        tape = {addr: val for addr, val in tape_tuple}
        
        # Absolute address = d · offset
        abs_addr = self.top.multiply(d, self.offset)
        
        # Update value at abs_addr
        old_val = tape.get(abs_addr, self.base.one())
        new_val = self.base.multiply(old_val, self.increment)
        
        if self.base.is_one(new_val):
            tape.pop(abs_addr, None)
        else:
            tape[abs_addr] = new_val
        
        # Re-canonicalize
        new_tape = canonicalize_tape(tape, self.top, self.base)
        return (d, new_tape)


class WreathProduct:
    """
    Regular wreath product C ≀ D with finite support.
    
    Configuration via parse_options():
    {
        "spec": "C wr D",  # e.g., "Z/5 wr Z2", "Free(3) wr Dn(8)"
        "top_gens": Optional[List[str]],  # override default top generators
        "offsets": Optional[List[str]],   # offset words in top group (default ["e"])
    }
    """
    name = "Wreath"
    
    def __init__(self, base_adapter=None, top_adapter=None, 
                 top_gens=None, offsets=None, spec_str=""):
        self.base = base_adapter
        self.top = top_adapter
        self.spec_str = spec_str
        
        # Top generators (default or custom)
        if top_gens is None and top_adapter:
            self.top_gens = top_adapter.default_gens()
        else:
            self.top_gens = top_gens or {}
        
        # Offsets: Default to ONLY identity (standard semidirect product behavior)
        # Additional offsets allow toggling at d·offset instead of just d
        if offsets is None and top_adapter:
            self.offsets = [top_adapter.identity()]
        else:
            self.offsets = offsets or []
    
    def identity(self):
        return (self.top.identity(), ())
    
    def default_generators(self):
        """Build move + toggle generators."""
        gens = []
        
        # Move generators from top group
        for name, d_elem in self.top_gens.items():
            gens.append(MoveGen(name, d_elem, self.top, self.base))
        
        # Toggle generators: one set of base increments per offset
        base_increments = self.base.default_increments()
        
        # If only one offset (identity), use simple names from base adapter
        if len(self.offsets) == 1:
            for inc_name, inc_val in base_increments:
                gens.append(ToggleGen(inc_name, self.offsets[0], inc_val, self.top, self.base))
        else:
            # Multiple offsets: use offset index to determine letter
            for offset_idx, offset in enumerate(self.offsets):
                for inc_idx, (inc_name, inc_val) in enumerate(base_increments):
                    # For first increment at each offset: use letters a, b, c, ...
                    # For additional increments: use a2, b2, c2, ... (if needed)
                    if inc_idx == 0:
                        base_letter = chr(ord('a') + offset_idx)
                    else:
                        base_letter = chr(ord('a') + offset_idx) + str(inc_idx + 1)
                    
                    # Handle uppercase for inverses (when increment has uppercase in name)
                    if inc_name.isupper():
                        gen_name = base_letter.upper() if len(base_letter) == 1 else base_letter[0].upper() + base_letter[1:]
                    else:
                        gen_name = base_letter
                    
                    gens.append(ToggleGen(gen_name, offset, inc_val, self.top, self.base))
        
        return gens
    
    def parse_options(self, opts: Dict) -> 'WreathProduct':
        """
        Parse wreath product specification.
        opts = {
            "spec": "C wr D",
            "top_gens": Optional[List[str]],
            "offsets": Optional[List[str]]
        }
        """
        spec = opts.get("spec", "Z/2 wr Z")
        
        # Parse spec: "C wr D"
        if " wr " not in spec:
            raise ValueError("Spec must be in format 'C wr D'")
        
        base_spec, top_spec = spec.split(" wr ", 1)
        base_adapter = get_base_adapter(base_spec.strip())
        top_adapter = get_top_adapter(top_spec.strip())
        
        # Parse top generators
        top_gen_names = opts.get("top_gens")
        if top_gen_names:
            # Use provided generator names
            default_gens = top_adapter.default_gens()
            top_gens = {name: default_gens[name] for name in top_gen_names}
        else:
            top_gens = top_adapter.default_gens()
        
        # Parse offsets as words
        offset_words = opts.get("offsets", ["e"])
        offsets = []
        for word in offset_words:
            if word == "e" or word == "":
                offsets.append(top_adapter.identity())
            else:
                offsets.append(top_adapter.parse_word(word, top_gens))
        
        return WreathProduct(
            base_adapter=base_adapter,
            top_adapter=top_adapter,
            top_gens=top_gens,
            offsets=offsets,
            spec_str=spec
        )
    
    def pretty(self, state):
        """Format state as d=<top> | addr:val; ..."""
        d, tape_tuple = state
        d_str = self.top.pretty(d)
        
        if not tape_tuple:
            return f"d={d_str}"
        
        tape_parts = []
        for addr, val in tape_tuple:
            addr_str = self.top.pretty(addr)
            val_str = self.base.pretty(val)
            tape_parts.append(f"{addr_str}:{val_str}")
        
        tape_str = ";".join(tape_parts)
        return f"d={d_str}|{tape_str}"
    
    def get_metadata(self):
        """Return metadata dict for export."""
        return {
            "family": "wreath_regular",
            "spec": self.spec_str,
            "top": {
                "kind": self.top.name,
                "gens": list(self.top_gens.keys())
            },
            "base": {
                "kind": self.base.name
            },
            "offsets": [self.top.pretty(o) for o in self.offsets]
        }


# Register the wreath product group
from ..groups.base import register
register(WreathProduct())


def run_dead_end_mode_wreath(group, gens, labels, R, depth_cap, bfs_build):
    """
    Find dead-end elements on layer R for a wreath product.
    
    Builds to R + depth_cap, analyzes dead ends, and prints results.
    No JSON/PNG artifacts generated.
    
    Args:
        group: Configured wreath product instance
        gens: List of generator objects
        labels: Generator names
        R: Target radius to analyze
        depth_cap: Maximum depth to search for escape paths
        bfs_build: BFS build function (e.g., build_ball)
    """
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

