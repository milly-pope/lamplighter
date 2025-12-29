from typing import Dict, Any, List
from ..core.types import Group

# Registry to plug groups into the UI
REGISTRY = {}


def register(group):
    """Register a group instance for use in the UI."""
    REGISTRY[group.name] = group


def all_groups():
    """Return list of all registered groups."""
    return list(REGISTRY.values())
