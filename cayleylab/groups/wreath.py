# General regular wreath product C ℘ D = C^(D) ⋊ D
# State = (d, tape) where d ∈ D and tape is finite-support function D → C

from .wreath_adapters_top import get_top_adapter
from .wreath_adapters_base import get_base_adapter


def canonicalize_tape(tape_dict, top_adapter, base_adapter):
    # Convert tape dict to canonical sorted tuple, dropping identity entries
    # Returns sorted tuple of ((addr, val), ...) where val ≠ base.one()
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
    # Generator that moves in the top group D
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
    # Generator that toggles lamp at offset in D
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
    # Regular wreath product C ℘ D with finite support
    # Standard definition: generators from D (movement) + generators from C acting at identity
    # Configuration via parse_options(): {"spec": "C wr D", "top_gens": [...]}
    name = "Wreath"
    
    def __init__(self, base_adapter=None, top_adapter=None, 
                 top_gens=None, offsets=None, base_adapters=None, spec_str="", is_lamplighter=False):
        self.base = base_adapter  # Single base (same lamp at all positions)
        self.base_adapters = base_adapters  # List of bases (different lamp per position)
        self.top = top_adapter
        self.spec_str = spec_str
        self.offsets = offsets  # Offsets for walking subgroup blocks
        self.is_lamplighter = is_lamplighter  # Flag for visualization (words vs states)
        
        # Top generators (default or custom)
        if top_gens is None and top_adapter:
            self.top_gens = top_adapter.default_gens()
        else:
            self.top_gens = top_gens or {}
    
    def identity(self):
        return (self.top.identity(), ())
    
    def default_generators(self):
        # Build move + toggle generators
        # Different lamp types: different lamp at each position
        gens = []
        
        # Move generators from top group D
        for name, d_elem in self.top_gens.items():
            gens.append(MoveGen(name, d_elem, self.top, self.base or self.base_adapters[0]))
        
        # Toggle generators: possibly different base group at each offset
        if self.base_adapters:
            # Different lamps: different lamp type per position
            if self.offsets is None or len(self.offsets) == 0:
                offsets = [self.top.identity()]
                base_list = [self.base_adapters[0]]
            else:
                offsets = self.offsets
                # Match base_adapters to offsets
                if len(self.base_adapters) == len(offsets):
                    base_list = self.base_adapters
                else:
                    # Repeat pattern or truncate
                    base_list = [self.base_adapters[i % len(self.base_adapters)] for i in range(len(offsets))]
            
            offset_names = ['a', 'b', 'c', 'd', 'e']
            for i, (offset, base_adapter) in enumerate(zip(offsets, base_list)):
                # For different lamp types, use only the primary increment (forward generator)
                base_increments = base_adapter.default_increments()
                suffix = offset_names[i] if i < len(offset_names) else f'{i}'
                # Only use the first increment (forward direction) for clean naming
                inc_name, inc_val = base_increments[0]
                toggle_name = suffix
                gens.append(ToggleGen(toggle_name, offset, inc_val, self.top, base_adapter))
        else:
            # Same lamp: same lamp type at all positions
            base_increments = self.base.default_increments()
            
            if self.offsets is None or len(self.offsets) == 0:
                offsets = [self.top.identity()]
            else:
                offsets = self.offsets
            
            if len(offsets) == 1:
                # Single offset (standard case)
                identity_offset = offsets[0]
                for inc_name, inc_val in base_increments:
                    gens.append(ToggleGen(inc_name, identity_offset, inc_val, self.top, self.base))
            else:
                # Multiple offsets (block case) - use a, b, c, d, e for different positions
                # Use only forward generator for clean naming
                offset_names = ['a', 'b', 'c', 'd', 'e']
                for i, offset in enumerate(offsets):
                    suffix = offset_names[i] if i < len(offset_names) else f'{i}'
                    # Only use first increment (forward direction)
                    inc_name, inc_val = base_increments[0]
                    toggle_name = suffix
                    gens.append(ToggleGen(toggle_name, offset, inc_val, self.top, self.base))
        
        return gens
    
    def _validate_wreath_spec(self, base_spec, top_spec, opts):
        """Validate wreath product specification for common errors."""
        # Check for invalid lamp groups (subgroups like 2Z, 3Z as base)
        if base_spec in ['2Z', '3Z', '4Z', '5Z'] or (base_spec.endswith('Z') and base_spec[0].isdigit()):
            raise ValueError(
                f"Invalid lamp group '{base_spec}'. "
                f"Lamps must be finite groups like Z/2, Z/3, etc.\n"
                f"Did you mean to use '{base_spec}' as the walking group?\n"
                f"For walking on {base_spec}, use: 'Z/2 wr {base_spec}' (you may also need to specify offsets/blocks)"
            )
        
        # Check for restricted walking groups without proper block specification
        if top_spec in ['2Z', '3Z', '4Z', '5Z'] or (top_spec.endswith('Z') and top_spec[0].isdigit() and len(top_spec) <= 3):
            # Walking on a subgroup like 2Z, 3Z - need to specify blocks
            n = int(top_spec[:-1])  # Extract the number
            
            # Check if different lamps specified
            if ',' in base_spec:
                num_blocks = len(base_spec.split(','))
                if num_blocks != n:
                    raise ValueError(
                        f"Block count mismatch: walking on {top_spec} creates {n} positions, "
                        f"but you specified {num_blocks} lamp types.\n"
                        f"For {top_spec}, specify {n} lamp types: e.g., 'Z/2,Z/3{',Z/4' if n > 2 else ''}' or use same lamp 'Z/2 wr {top_spec}'"
                    )
            # For same lamp at all positions, offsets will be auto-generated
            elif 'offsets' not in opts:
                # This is OK - we'll auto-generate offsets
                pass
        
        # Check for finite walking group (less common but possible issue)
        if top_spec.startswith('Z/') and ',' not in base_spec:
            # Finite walking group - unusual but valid for finite wreath products
            # No error, but this creates a finite group
            pass
    
    def parse_options(self, opts):
        # Parse wreath product specification
        # opts = {"spec": "C wr D", "top_gens": [...], "offsets": [...]}
        spec = opts.get("spec", "Z/2 wr Z")
        
        # Parse spec: "C wr D" where C can be multiple lamp types
        base_spec, top_spec = spec.split(" wr ", 1)
        base_spec = base_spec.strip()
        top_spec_clean = top_spec.strip()
        
        # Validate specification
        self._validate_wreath_spec(base_spec, top_spec_clean, opts)
        
        top_adapter = get_top_adapter(top_spec_clean)
        
        # Check if base_spec has multiple lamp types (e.g., "Z/2,Z/3,Z/4")
        base_adapter = None
        base_adapters = None
        
        if ',' in base_spec:
            # Multiple lamps: parse each lamp type
            base_specs = [s.strip() for s in base_spec.split(',')]
            base_adapters = [get_base_adapter(s) for s in base_specs]
            # Auto-generate offsets based on block size
            if 'offsets' not in opts:
                opts['offsets'] = list(range(len(base_adapters)))
        else:
            # Single lamp: same lamp type at all positions
            base_adapter = get_base_adapter(base_spec)
            # Check if walking on nZ subgroup - auto-generate offsets
            if top_spec_clean in ['2Z', '3Z', '4Z', '5Z'] or (top_spec_clean.endswith('Z') and top_spec_clean[0].isdigit() and len(top_spec_clean) <= 3):
                if 'offsets' not in opts:
                    n = int(top_spec_clean[:-1])
                    opts['offsets'] = list(range(n))
        
        # Parse top generators
        top_gen_names = opts.get("top_gens")
        if top_gen_names:
            # Use provided generator names
            default_gens = top_adapter.default_gens()
            top_gens = {name: default_gens[name] for name in top_gen_names}
        else:
            top_gens = top_adapter.default_gens()
        
        # Parse offsets for walking subgroup blocks
        offsets = opts.get('offsets', None)
        if offsets and top_adapter:
            # Convert offset specs to actual elements
            offset_elems = []
            for off in offsets:
                if isinstance(off, str) and off == 'e':
                    offset_elems.append(top_adapter.identity())
                elif isinstance(off, int):
                    # For Z-like groups, interpret as position
                    offset_elems.append(off)
                else:
                    offset_elems.append(off)
            offsets = offset_elems
        
        return WreathProduct(
            base_adapter=base_adapter,
            top_adapter=top_adapter,
            top_gens=top_gens,
            offsets=offsets,
            base_adapters=base_adapters,
            spec_str=spec,
            is_lamplighter=self.is_lamplighter if hasattr(self, 'is_lamplighter') else False
        )
    
    def pretty(self, state):
        # Format state as <top> | addr:val; ...
        d, tape_tuple = state
        d_str = self.top.pretty(d)
        
        if not tape_tuple:
            return d_str
        
        tape_parts = []
        for addr, val in tape_tuple:
            addr_str = self.top.pretty(addr)
            # Find the appropriate base adapter for this address
            if self.base_adapters and self.offsets:
                # Multiple lamps: find which offset this address corresponds to
                try:
                    offset_idx = self.offsets.index(addr)
                    base_adapter = self.base_adapters[offset_idx % len(self.base_adapters)]
                except (ValueError, IndexError):
                    # Address not in offsets, use first base adapter
                    base_adapter = self.base_adapters[0]
                val_str = base_adapter.pretty(val)
            else:
                # Single lamp: use single base adapter
                val_str = self.base.pretty(val)
            tape_parts.append(f"{addr_str}:{val_str}")
        
        tape_str = ";".join(tape_parts)
        return f"{d_str}|{tape_str}"
    
    def get_metadata(self):
        # Return metadata dict for export
        return {
            "family": "wreath_regular",
            "spec": self.spec_str,
            "top": {
                "kind": self.top.name,
                "gens": list(self.top_gens.keys())
            },
            "base": {
                "kind": self.base.name
            }
        }

