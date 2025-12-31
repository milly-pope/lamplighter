"""
Top (acting) group adapters for D in wreath products C ≀ D.
Each adapter provides: identity, multiply, inverse, pretty, default_gens, parse_word.
"""

from typing import Any, Dict, Tuple, List


class ZAdapter:
    """Z (integers) as top group."""
    name = "Z"
    
    def identity(self):
        return 0
    
    def multiply(self, a, b):
        return a + b
    
    def inverse(self, a):
        return -a
    
    def pretty(self, a):
        return str(a)
    
    def default_gens(self):
        return {"t": 1, "T": -1}
    
    def parse_word(self, word: str, gens: Dict[str, int]) -> int:
        """Parse space-separated generator names."""
        if not word.strip():
            return 0
        tokens = word.split()
        result = 0
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            result += gens[tok]
        return result


class Z2Adapter:
    """Z² (rank-2 free abelian) as top group."""
    name = "Z2"
    
    def identity(self):
        return (0, 0)
    
    def multiply(self, a, b):
        return (a[0] + b[0], a[1] + b[1])
    
    def inverse(self, a):
        return (-a[0], -a[1])
    
    def pretty(self, a):
        return f"({a[0]},{a[1]})"
    
    def default_gens(self):
        return {
            "x": (1, 0),
            "X": (-1, 0),
            "y": (0, 1),
            "Y": (0, -1)
        }
    
    def parse_word(self, word: str, gens: Dict[str, Tuple[int, int]]) -> Tuple[int, int]:
        if not word.strip():
            return (0, 0)
        tokens = word.split()
        result = (0, 0)
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            g = gens[tok]
            result = (result[0] + g[0], result[1] + g[1])
        return result


class ZmodAdapter:
    """Z/n (cyclic of order n) as top group."""
    name = "Zmod"
    
    def __init__(self, n):
        self.n = n
    
    def identity(self):
        return 0
    
    def multiply(self, a, b):
        return (a + b) % self.n
    
    def inverse(self, a):
        return (self.n - a) % self.n
    
    def pretty(self, a):
        return str(a)
    
    def default_gens(self):
        if self.n == 2:
            return {"t": 1}
        else:
            return {"t": 1, "T": self.n - 1}
    
    def parse_word(self, word: str, gens: Dict[str, int]) -> int:
        if not word.strip():
            return 0
        tokens = word.split()
        result = 0
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            result = (result + gens[tok]) % self.n
        return result


class DinfAdapter:
    """D∞ (infinite dihedral) as top group."""
    name = "Dinf"
    
    def identity(self):
        return (0, 0)
    
    def multiply(self, a, b):
        """Multiply using relations: s² = 1, srs = r⁻¹"""
        k, eps = a
        l, delta = b
        if eps == 0:
            return (k + l, delta)
        else:
            return (k - l, 1 - delta)
    
    def inverse(self, a):
        k, eps = a
        if eps == 0:
            return (-k, 0)
        else:
            return (k, 1)
    
    def pretty(self, a):
        k, eps = a
        if eps == 0:
            return f"r^{k}" if k != 0 else "e"
        else:
            return f"r^{k}s" if k != 0 else "s"
    
    def default_gens(self):
        return {
            "r": (1, 0),
            "R": (-1, 0),
            "s": (0, 1)
        }
    
    def parse_word(self, word: str, gens: Dict[str, Tuple[int, int]]) -> Tuple[int, int]:
        if not word.strip():
            return (0, 0)
        tokens = word.split()
        result = (0, 0)
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            result = self.multiply(result, gens[tok])
        return result


class DnAdapter:
    """Dn (dihedral of order 2n) as top group."""
    name = "Dn"
    
    def __init__(self, n):
        self.n = n
    
    def identity(self):
        return (0, 0)
    
    def multiply(self, a, b):
        """Same as D∞ but reduce mod n"""
        k, eps = a
        l, delta = b
        if eps == 0:
            return ((k + l) % self.n, delta)
        else:
            return ((k - l) % self.n, 1 - delta)
    
    def inverse(self, a):
        k, eps = a
        if eps == 0:
            return ((self.n - k) % self.n, 0)
        else:
            return (k, 1)
    
    def pretty(self, a):
        k, eps = a
        if eps == 0:
            return f"r^{k}" if k != 0 else "e"
        else:
            return f"r^{k}s" if k != 0 else "s"
    
    def default_gens(self):
        return {
            "r": (1, 0),
            "R": (self.n - 1, 0),
            "s": (0, 1)
        }
    
    def parse_word(self, word: str, gens: Dict[str, Tuple[int, int]]) -> Tuple[int, int]:
        if not word.strip():
            return (0, 0)
        tokens = word.split()
        result = (0, 0)
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            result = self.multiply(result, gens[tok])
        return result


class FreeAdapter:
    """Free group Free(k) as top group."""
    name = "Free"
    
    def __init__(self, k):
        self.k = k  # rank
        self._letters = []
        for i in range(k):
            base = chr(ord('a') + i)
            self._letters.append(base)
            self._letters.append(base.upper())
    
    def identity(self):
        return ()
    
    def _inverse_letter(self, letter):
        """Swap case of a letter."""
        if letter.islower():
            return letter.upper()
        else:
            return letter.lower()
    
    def _reduce_word(self, word):
        """Cancel adjacent inverse pairs."""
        result = []
        for letter in word:
            if result and result[-1] == self._inverse_letter(letter):
                result.pop()
            else:
                result.append(letter)
        return tuple(result)
    
    def multiply(self, a, b):
        return self._reduce_word(a + b)
    
    def inverse(self, a):
        return tuple(self._inverse_letter(letter) for letter in reversed(a))
    
    def pretty(self, a):
        return "".join(a) if a else "e"
    
    def default_gens(self):
        gens = {}
        for i in range(self.k):
            base = chr(ord('a') + i)
            gens[base] = (base,)
            gens[base.upper()] = (base.upper(),)
        return gens
    
    def parse_word(self, word: str, gens: Dict[str, Tuple]) -> Tuple:
        if not word.strip():
            return ()
        tokens = word.split()
        result = ()
        for tok in tokens:
            if tok not in gens:
                raise ValueError(f"Unknown generator '{tok}'")
            result = self.multiply(result, gens[tok])
        return result


def get_top_adapter(spec: str):
    """Parse top group spec and return adapter."""
    spec = spec.strip()
    
    if spec == "Z":
        return ZAdapter()
    elif spec == "Z2":
        return Z2Adapter()
    elif spec.startswith("Z/"):
        n = int(spec[2:])
        return ZmodAdapter(n)
    elif spec == "Dinf":
        return DinfAdapter()
    elif spec.startswith("Dn(") and spec.endswith(")"):
        n = int(spec[3:-1])
        return DnAdapter(n)
    elif spec.startswith("Free(") and spec.endswith(")"):
        k = int(spec[5:-1])
        return FreeAdapter(k)
    else:
        raise ValueError(f"Unknown top group spec: {spec}")
