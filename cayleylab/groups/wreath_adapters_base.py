"""
Base (lamp) group adapters for C in wreath products C ≀ D.
Each adapter provides: one, is_one, multiply, inverse, pretty, default_increments.
"""

from typing import Any, Dict, Tuple, List


class ZBaseAdapter:
    """Z (integers) as base group."""
    name = "Z"
    
    def one(self):
        return 0
    
    def is_one(self, c):
        return c == 0
    
    def multiply(self, a, b):
        return a + b
    
    def inverse(self, a):
        return -a
    
    def pretty(self, a):
        return str(a)
    
    def default_increments(self):
        return [("a", 1), ("A", -1)]


class ZmodBaseAdapter:
    """Z/n (cyclic) as base group."""
    name = "Zmod"
    
    def __init__(self, n):
        self.n = n
    
    def one(self):
        return 0
    
    def is_one(self, c):
        return c == 0
    
    def multiply(self, a, b):
        return (a + b) % self.n
    
    def inverse(self, a):
        return (self.n - a) % self.n
    
    def pretty(self, a):
        return str(a)
    
    def default_increments(self):
        if self.n == 2:
            return [("a", 1)]
        else:
            return [("a", 1), ("A", self.n - 1)]


class Z2BaseAdapter:
    """Z² (rank-2 free abelian) as base group."""
    name = "Z2"
    
    def one(self):
        return (0, 0)
    
    def is_one(self, c):
        return c == (0, 0)
    
    def multiply(self, a, b):
        return (a[0] + b[0], a[1] + b[1])
    
    def inverse(self, a):
        return (-a[0], -a[1])
    
    def pretty(self, a):
        return f"({a[0]},{a[1]})"
    
    def default_increments(self):
        # Two independent increments for Z²
        return [
            ("a", (1, 0)),
            ("A", (-1, 0)),
            ("b", (0, 1)),
            ("B", (0, -1))
        ]


class AbelianProductAdapter:
    """Finite abelian product Z/m1 × Z/m2 × ... as base group."""
    name = "AbelianProduct"
    
    def __init__(self, moduli):
        self.moduli = tuple(moduli)
    
    def one(self):
        return tuple(0 for _ in self.moduli)
    
    def is_one(self, c):
        return all(x == 0 for x in c)
    
    def multiply(self, a, b):
        return tuple((a[i] + b[i]) % self.moduli[i] for i in range(len(self.moduli)))
    
    def inverse(self, a):
        return tuple((self.moduli[i] - a[i]) % self.moduli[i] for i in range(len(self.moduli)))
    
    def pretty(self, a):
        return f"({','.join(map(str, a))})"
    
    def default_increments(self):
        """One increment per factor."""
        result = []
        for i, m in enumerate(self.moduli):
            name = chr(ord('a') + i)
            unit = tuple(1 if j == i else 0 for j in range(len(self.moduli)))
            result.append((name, unit))
            
            if m > 2:
                inv_name = name.upper()
                inv_unit = tuple((m - 1) if j == i else 0 for j in range(len(self.moduli)))
                result.append((inv_name, inv_unit))
        
        return result


class DinfBaseAdapter:
    """D∞ (infinite dihedral) as base group."""
    name = "Dinf"
    
    def one(self):
        return (0, 0)
    
    def is_one(self, c):
        return c == (0, 0)
    
    def multiply(self, a, b):
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
    
    def default_increments(self):
        return [
            ("a", (1, 0)),
            ("A", (-1, 0)),
            ("b", (0, 1))
        ]


class DnBaseAdapter:
    """Dn (finite dihedral) as base group."""
    name = "Dn"
    
    def __init__(self, n):
        self.n = n
    
    def one(self):
        return (0, 0)
    
    def is_one(self, c):
        return c == (0, 0)
    
    def multiply(self, a, b):
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
    
    def default_increments(self):
        return [
            ("a", (1, 0)),
            ("A", (self.n - 1, 0)),
            ("b", (0, 1))
        ]


class FreeBaseAdapter:
    """Free group Free(k) as base group."""
    name = "Free"
    
    def __init__(self, k):
        self.k = k
    
    def one(self):
        return ()
    
    def is_one(self, c):
        return c == ()
    
    def _inverse_letter(self, letter):
        if letter.islower():
            return letter.upper()
        else:
            return letter.lower()
    
    def _reduce_word(self, word):
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
    
    def default_increments(self):
        result = []
        for i in range(self.k):
            base = chr(ord('a') + i)
            result.append((base, (base,)))
            result.append((base.upper(), (base.upper(),)))
        return result


def get_base_adapter(spec: str):
    """Parse base group spec and return adapter."""
    spec = spec.strip()
    
    if spec == "Z":
        return ZBaseAdapter()
    elif spec == "Z2":
        return Z2BaseAdapter()
    elif spec.startswith("Z/"):
        n = int(spec[2:])
        return ZmodBaseAdapter(n)
    elif spec.startswith("abelian([") and spec.endswith("])"):
        # Parse abelian([2,3,4])
        nums_str = spec[9:-2]
        moduli = [int(x.strip()) for x in nums_str.split(',')]
        return AbelianProductAdapter(moduli)
    elif spec == "Dinf":
        return DinfBaseAdapter()
    elif spec.startswith("Dn(") and spec.endswith(")"):
        n = int(spec[3:-1])
        return DnBaseAdapter(n)
    elif spec.startswith("Free(") and spec.endswith(")"):
        k = int(spec[5:-1])
        return FreeBaseAdapter(k)
    else:
        raise ValueError(f"Unknown base group spec: {spec}")
