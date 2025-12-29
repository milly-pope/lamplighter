"""
CayleyLab - Interactive Cayley Graph Explorer

A small, extensible library for exploring Cayley graphs of groups.
Supports Z^2, D∞, and Lamplighter groups with interactive CLI.
"""

__version__ = "1.0.0"

# Import groups to trigger registration
from . import groups

__all__ = ['core', 'groups', 'ui', 'verify']
