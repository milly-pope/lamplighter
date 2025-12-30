from typing import List, Tuple
from ..core.types import Group, Gen, State


# State = tuple of letters: ('a', 'b', 'A', 'b', ...) in reduced form


def reduce_word(word):
    """
    Reduce a word by canceling inverse pairs.
    word is a tuple of letters.
    """
    stack = []
    inverses = {'a': 'A', 'A': 'a', 'b': 'B', 'B': 'b'}
    
    for letter in word:
        if stack and stack[-1] == inverses.get(letter, None):
            stack.pop()
        else:
            stack.append(letter)
    
    return tuple(stack)


class FreeGen:
    """Generator for free group: appends a letter and reduces."""
    def __init__(self, name, letter):
        self.name = name
        self.letter = letter
    
    def apply(self, s):
        # s is a tuple of letters
        # Append our letter and reduce
        return reduce_word(s + (self.letter,))


class FreeGroup:
    """
    Free group F_2 with generators a and b.
    
    State = tuple of letters in fully reduced form (no adjacent inverses)
    Identity = ()
    
    Generators: a, b, A (a^-1), B (b^-1)
    """
    name = "F_2 (Free Group)"
    
    def __init__(self):
        pass
    
    def identity(self):
        return ()
    
    def default_generators(self):
        return [
            FreeGen("a", "a"),
            FreeGen("A", "A"),
            FreeGen("b", "b"),
            FreeGen("B", "B"),
        ]
    
    def parse_options(self, opts):
        return FreeGroup()
    
    def pretty(self, s):
        if not s:
            return "e"
        return "".join(s)


# Register this group
from .base import register
register(FreeGroup())
