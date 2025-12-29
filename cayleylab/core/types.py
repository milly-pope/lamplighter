from typing import Any, Dict, List, Tuple, Protocol

# Core type aliases
State = Any  # must be hashable
Edge = Tuple[int, int, int]  # (u, v, gen_index)

class Gen(Protocol):
    """Generator protocol - any object that can apply itself to a state."""
    name: str
    
    def apply(self, s: State) -> State:
        """Apply this generator to state s, returning the new state."""
        ...

class Group(Protocol):
    """Group protocol - defines identity, generators, and pretty-printing."""
    name: str
    
    def identity(self) -> State:
        """Return the identity element of this group."""
        ...
    
    def default_generators(self) -> List[Gen]:
        """Return the default generator set for this group."""
        ...
    
    def parse_options(self, opts: Dict[str, Any]) -> "Group":
        """Parse user options and return a configured Group instance."""
        ...
    
    def pretty(self, s: State) -> str:
        """Pretty-print a state for display."""
        ...

# Return type for BFS
Ball = Tuple[List[State], List[Edge], List[int], List[str]]
# (V, E, dist, labels) where labels[i] is gens[i].name
