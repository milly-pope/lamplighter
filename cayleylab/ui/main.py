import sys
import os
from ..core.bfs import build_ball
from ..core.export import write_dot, write_png, display_graph
from ..core.growth import compute_growth, classify_growth, format_growth_table


def numbered_choice(prompt, choices):
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}) {choice}")
    print("  q) Quit")
    while True:
        resp = input("\nChoice: ").strip().lower()
        if resp == 'q':
            return None
        try:
            idx = int(resp) - 1
            if 0 <= idx < len(choices):
                return idx
        except:
            pass
        print("Invalid choice.")


def print_header(title, lines=None):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    if lines:
        for line in lines:
            print(f"  {line}")
        print()


def configure_group(group):
    # Common group configuration logic
    if group.name in ("Z^2", "D∞"):
        return group
    elif group.name.startswith("F_"):
        rank_str = input("Rank of free group [2]: ").strip()
        rank = int(rank_str) if rank_str else 2
        return group.parse_options({"rank": rank})
    elif group.name == "Lamplighter":
        base = input("Base group (Z/2, Z/3, Z/2,Z/3) [Z/2]: ").strip() or "Z/2"
        offsets = input("Toggle offsets [0]: ").strip() or "0"
        return group.parse_options({
            "spec": f"{base} wr Z",
            "offsets": [s.strip() for s in offsets.split(',')]
        })
    elif group.name == "Wreath":
        spec = input("Spec (C wr D) [Z/2 wr Z]: ").strip() or "Z/2 wr Z"
        offsets = input("Offsets [e]: ").strip() or "e"
        return group.parse_options({
            "spec": spec,
            "offsets": [s.strip() for s in offsets.split(',')]
        })
    return group


def main_menu():
    from ..groups.Z2 import Z2
    from ..groups.Dinf import Dinf
    from ..groups.free import FreeGroup
    from ..groups.lamplighter import Lamplighter
    from ..groups.wreath import WreathProduct
    
    groups = [
        Z2(),
        Dinf(),
        FreeGroup(),
        Lamplighter(),
        WreathProduct()
    ]
    group_names = [g.name for g in groups]
    
    print_header("CayleyLab", [
        "Interactive Cayley Graph Explorer",
        "Choose a group to explore"
    ])
    
    idx = numbered_choice("Select a group:", group_names)
    if idx is None:
        print("Goodbye!")
        return
    
    group = groups[idx]
    group_menu(group)


def group_menu(group):
    # Group-specific menu: modes
    # Show group-specific header
    headers = {
        "Z^2": [
            "Z^2 with generators {±e1, ±e2}.",
            "State = (x,y). Distance is L1 in these generators."
        ],
        "D∞": [
            "D∞ = Z ⋊ Z/2 with generators r, R, s.",
            "State = (k, eps). Every element is r^m or r^m s."
        ],
        "Lamplighter": [
            "Lamplighter group: wreath product C ≀ Z.",
            "Specify base group C (e.g., Z/2, Z/3, Z/2,Z/3).",
            "State = (p, tape) where p ∈ Z is head position.",
            "Generators: t, T (move head) + a, b, ... (toggle lamps)"
        ],
        "Wreath": [
            "Wreath product C ≀ D = C^(D) ⋊ D with finite support.",
            "Supported: Z, Z/n, Z2, D∞, Dn(n), Free(k), abelian([m1,...]).",
            "State = (d, tape) where d ∈ D and tape: D → C with finite support.",
            "",
            "Generator conventions:",
            "  Cyclic (Z, Z/n): t, T for moves | a, A, b, ... for toggles",
            "  Grid (Z²): x, X, y, Y for moves | a, A, b, B for toggles",
            "  Dihedral (D∞, Dn): r, R, s for moves | a, A, b for toggles",
            "  Free(k): a, A, b, B, ... for moves | a, A, b, B, ... for toggles"
        ]
    }
    
    while True:
        print_header(group.name, headers.get(group.name, []))
        
        modes = [
            "Build a radius-n ball (PNG/DOT export)",
            "Analyze growth rate",
            "Evaluate word (multiply generators, find distance)",
            "Find dead-end elements",
            "Back"
        ]
        
        idx = numbered_choice("Select a mode:", modes)
        if idx is None or idx == 4:  # Quit or Back
            return
        
        if idx == 0:
            build_mode(group)
        elif idx == 1:
            growth_mode(group)
        elif idx == 2:
            evaluate_mode(group)
        elif idx == 3:
            dead_end_mode(group)


def build_mode(group):
    print_header(f"{group.name} - Build Ball")
    
    configured = configure_group(group)
    gens = configured.default_generators()
    print(f"Generators: {', '.join(g.name for g in gens)}")
    
    radius_str = input("Radius [3]: ").strip()
    radius = int(radius_str) if radius_str else 3
    
    print("Building ball...")
    V, E, dist, labels, words = build_ball(configured, gens, radius)
    
    print(f"\n|V| = {len(V)}, |E| = {len(E)}")
    max_d = max(dist) if dist else 0
    for d in range(max_d + 1):
        count = sum(1 for x in dist if x == d)
        print(f"  Layer {d}: {count} vertices")
    
    os.makedirs("graphs", exist_ok=True)
    
    # Generate filename
    if hasattr(configured, 'spec_str'):
        fname = configured.spec_str.replace(' ', '').replace('/', '')
    else:
        fname = group.name.replace(' ', '_').replace('∞', 'inf').lower()
    fname = f"{fname}_r{radius}"
    
    write_dot(V, E, dist, labels, words, configured, f"graphs/{fname}.dot")
    write_png(V, E, dist, labels, words, configured, f"graphs/{fname}.png")
    print(f"\nWrote graphs/{fname}.dot and graphs/{fname}.png")
    
    show = input("Display graph? [Y/n]: ").strip().lower()
    if show != 'n':
        display_graph(V, E, dist, labels, words, configured, png_path=f"graphs/{fname}.png")
    
    input("\nPress Enter to continue...")


def growth_mode(group):
    print_header(f"{group.name} - Growth Analysis")
    
    configured = configure_group(group)
    gens = configured.default_generators()
    print(f"Generators: {', '.join(g.name for g in gens)}")
    
    max_r_str = input("Maximum radius [10]: ").strip()
    max_r = int(max_r_str) if max_r_str else 10
    
    print(f"Computing balls for radii 0..{max_r}...")
    results = compute_growth(configured, gens, max_r)
    growth_type = classify_growth(results)
    print(format_growth_table(results, growth_type))
    
    input("\nPress Enter to continue...")


def evaluate_mode(group):
    print_header(f"{group.name} - Evaluate Word")
    
    configured = configure_group(group)
    gens = configured.default_generators()
    gen_map = {g.name: g for g in gens}
    
    print(f"Generators: {', '.join(gen_map.keys())}")
    word = input("Word (space-separated): ").strip().split()
    
    state = configured.identity()
    for w in word:
        state = gen_map[w].apply(state)
    
    print(f"Result: {configured.pretty(state)}")
    
    if state == configured.identity():
        print("Distance: 0 (identity)")
    else:
        for r in range(1, 51):
            V, E, dist, labels, word_list = build_ball(configured, gens, r)
            if state in V:
                vid = V.index(state)
                print(f"Distance: {dist[vid]}")
                print(f"Shortest word: {word_list[vid]}")
                if len(word) == dist[vid]:
                    print("Your word is optimal")
                break
        else:
            print("Not found within radius 50")
    
    input("\nPress Enter to continue...")


def dead_end_mode(group):
    print_header(f"{group.name} - Find Dead-End Elements")
    print("v at distance r is a dead end if all neighbors have distance ≤ r.")
    
    configured = configure_group(group)
    gens = configured.default_generators()
    print(f"Generators: {', '.join(g.name for g in gens)}")
    
    R_str = input("Radius [7]: ").strip()
    R = int(R_str) if R_str else 7
    
    V, E, dist, labels, words = build_ball(configured, gens, R)
    visited = {V[i]: i for i in range(len(V))}
    
    from ..features.deadends import analyze_dead_ends, print_dead_end_results
    results = analyze_dead_ends(configured, gens, [g.name for g in gens], R, None, V, dist, visited)
    print_dead_end_results(results, max_examples=10)
    
    input("\nPress Enter to continue...")


def main():
    # Entry point for cayleylab
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
