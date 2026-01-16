

# State = (k: int, eps: int in {0, 1})


class R:
    # Rotation generator r: (k, eps) -> (k+1, eps)
    name = "r"
    
    def apply(self, s):
        k, e = s
        return (k + 1, e)


class Rinv:
    # Inverse rotation R: (k, eps) -> (k-1, eps)
    name = "R"
    
    def apply(self, s):
        k, e = s
        return (k - 1, e)


class S:
    # Reflection s: (k, eps) -> (-k, 1-eps)
    name = "s"
    
    def apply(self, s):
        k, e = s
        return (-k, 1 - e)


class Dinf:
    # D∞ = Z ⋊ Z/2 with generators r, R, s
    name = "D∞"
    
    def identity(self):
        return (0, 0)
    
    def default_generators(self):
        return [R(), Rinv(), S()]
    
    def parse_options(self, opts):
        return Dinf()
    
    def pretty(self, s):
        k, e = s
        return f"k={k}|eps={e}"
