"""
Demo: Interactive usage of dead-end detection feature

This shows what users will see when selecting option 4 in the menu.
"""

print("=" * 60)
print("DEMO: Find Dead-End Elements")
print("=" * 60)
print()
print("When users select option 4) Find dead-end elements, they see:")
print()
print("-" * 60)
print()

print("Dead-end elements relative to the current generator set S:")
print("v at distance R is a dead end if no one-step move increases distance (|v s| ≤ |v| for all s ∈ S).")
print("Depth(v) is the smallest k ≥ 1 with a length-k word that exits B_R.")
print("We build to radius R + depth_cap to certify detection and depth.")
print()

print("Example session for Lamplighter:")
print("-" * 60)
print("Block pattern [default: 2]: 2")
print("Step mode (unit/block) [default: unit]: unit")
print("Toggle offsets [default: 0]: 0")
print()
print("Generators: t, T, a")
print()
print("Radius R to analyze [default: 7]: 7")
print("Depth cap (max search depth) [default: 6]: 6")
print("How many examples to show (0 = all) [default: 10]: 10")
print()

from cayleylab.groups.lamplighter import Lamplighter, run_dead_end_mode_lamplighter
from cayleylab.core.bfs import build_ball
from cayleylab.features.deadends import print_dead_end_results

lamp = Lamplighter()
config = lamp.parse_options({'pattern': [2], 'step_mode': 'unit', 'offsets': [0]})
gens = config.default_generators()
labels = [g.name for g in gens]

results = run_dead_end_mode_lamplighter(config, gens, labels, R=7, depth_cap=6, bfs_build=build_ball)
print_dead_end_results(results, max_examples=10)

print()
print("-" * 60)
print()
print("Example session for Wreath (Z/2 wr Z/3):")
print("-" * 60)
print("Enter spec (C wr D): Z/2 wr Z/3")
print("Offsets (comma-separated, default 'e'): e")
print()
print("Generators: t, T, a")
print()
print("Radius R to analyze [default: 7]: 6")
print("Depth cap (max search depth) [default: 6]: 5")
print("How many examples to show (0 = all) [default: 10]: 5")
print()

from cayleylab.groups.wreath import WreathProduct, run_dead_end_mode_wreath

wreath = WreathProduct()
config = wreath.parse_options({'spec': 'Z/2 wr Z/3', 'offsets': ['e']})
gens = config.default_generators()
labels = [g.name for g in gens]

results = run_dead_end_mode_wreath(config, gens, labels, R=6, depth_cap=5, bfs_build=build_ball)
print_dead_end_results(results, max_examples=5)

print()
print("=" * 60)
print("The feature is terminal-only (no JSON/PNG artifacts)")
print("Existing build/export modes remain unchanged")
print("=" * 60)
