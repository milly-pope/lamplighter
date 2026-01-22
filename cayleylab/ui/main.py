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


def select_generators(configured):
    """Allow user to select subset of default generators, or create composite generators."""
    all_gens = configured.default_generators()
    print(f"\nDefault generators: {', '.join(g.name for g in all_gens)}")
    
    print("\nOptions:")
    print("  1) Use all default generators")
    print("  2) Select subset of defaults")
    print("  3) Create composite generators (e.g., 'tat', 'tt')")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "2":
        # Select subset
        print("\nSelect which primitive generators to include:")
        for i, g in enumerate(all_gens):
            print(f"  {i+1}) {g.name}")
        
        selection = input("Enter numbers (comma-separated) or 'all' [all]: ").strip()
        if selection and selection.lower() != 'all':
            try:
                indices = [int(x.strip())-1 for x in selection.split(',')]
                gens = [all_gens[i] for i in indices if 0 <= i < len(all_gens)]
                if gens:
                    print(f"Using: {', '.join(g.name for g in gens)}")
                    return gens
                else:
                    print("Invalid selection, using all")
            except (ValueError, IndexError):
                print("Invalid selection, using all")
        return all_gens
    
    elif choice == "3":
        # Create composite generators
        from ..groups.wreath import CompositeGen
        
        gen_map = {g.name: g for g in all_gens}
        print(f"\nAvailable primitives: {', '.join(gen_map.keys())}")
        print("Define composite generators as words (space-separated)")
        print("Examples: 't a t', 't t', 'a t a T'")
        print("Enter one per line, empty line to finish:")
        
        composites = []
        while True:
            line = input(f"  Generator {len(composites)+1}: ").strip()
            if not line:
                break
            
            # Parse the word
            word_parts = line.split()
            try:
                primitive_sequence = [gen_map[p] for p in word_parts]
                # Create composite name (concatenate)
                comp_name = ''.join(word_parts)
                composites.append(CompositeGen(comp_name, primitive_sequence))
                print(f"    Created: {comp_name}")
            except KeyError as e:
                print(f"    Error: Unknown generator {e}")
                continue
        
        if composites:
            print(f"\nUsing composite generators: {', '.join(g.name for g in composites)}")
            return composites
        else:
            print("No composites defined, using all defaults")
            return all_gens
    
    else:
        # Use all defaults
        return all_gens


def configure_group(group):
    # Common group configuration logic
    if group.name in ("Z^2", "D∞"):
        return group
    elif group.name.startswith("F_"):
        rank_str = input("Rank of free group [2]: ").strip()
        rank = int(rank_str) if rank_str else 2
        return group.parse_options({"rank": rank})
    elif group.name == "Lamplighter":
        print("\nExamples:")
        print("  Z/2 wr Z       → binary lamps on all of Z")
        print("  Z/3 wr Z       → 3-state lamps on all of Z")
        print("  Z/2 wr 2Z      → binary lamps, walk in steps of 2")
        print("  Z/2,Z/3 wr 2Z  → different lamp at each position (a²=e, b³=e)")
        print("  Z/2,Z/3,Z/4 wr 3Z → 3 different lamps (a²=e, b³=e, c⁴=e)")
        
        # Ask for walking group first (determines block structure)
        walking = input("\nWalking group D [Z]: ").strip() or "Z"
        
        # Determine if blocks are needed based on walking group
        num_blocks = None
        if walking.lower() != 'z' and walking.lower().endswith('z'):
            # Walking on nZ creates n blocks
            try:
                n = int(walking[:-1]) if walking[:-1] else 1
                if n > 1:
                    num_blocks = n
                    print(f"\nWalking on {n}Z creates {n} positions")
                    print(f"You can specify:")
                    print(f"  • Same lamp at all {n} positions: e.g., 'Z/2'")
                    print(f"  • Different lamp at each position: e.g., 'Z/2,Z/3{',Z/4' if n > 2 else ''}'")
            except ValueError:
                pass
        
        # Now ask for lamp specification
        base = input("Lamp group(s) C [Z/2]: ").strip() or "Z/2"
        
        # Validate block count if needed
        if ',' in base:
            lamp_count = len(base.split(','))
            print(f"\nUsing {lamp_count} different lamp types at positions {list(range(lamp_count))}")
            
            if num_blocks is not None and lamp_count != num_blocks:
                print(f"\n⚠️  Warning: Walking on {walking} creates {num_blocks} positions.")
                print(f"    You specified {lamp_count} lamp types. They should match!")
                proceed = input("    Continue anyway? (y/n) [n]: ").strip().lower()
                if proceed != 'y':
                    return None
        elif num_blocks is not None:
            print(f"\nUsing same lamp type at all {num_blocks} positions")
            print(f"This creates generators: t (walk), a, b, c, ... (one per position)")
        
        # Build spec and configure
        # Note: This generates default generators based on the spec
        # Advanced users can specify custom generators via parse_options
        opts = {"spec": f"{base} wr {walking}"}
        
        try:
            return group.parse_options(opts)
        except ValueError as e:
            print(f"\n❌ Invalid specification: {e}")
            print("\nPlease check your input and try again.")
            return None
        except Exception as e:
            print(f"\nError: {e}")
            return None
    elif group.name == "Wreath":
        print("\nExamples:")
        print("  Z/2 wr Z         → classic lamplighter")
        print("  Z/2 wr 2Z        → binary lamps, walk in steps of 2")
        print("  Z/2 wr Z2        → 2D lamplighter")
        print("  Z/3 wr Z         → 3-state lamps on Z")
        print("  Z/2 wr Dinf      → lamps on infinite dihedral")
        print("  Z/2 wr Free(2)   → lamps on free group F₂")
        spec = input("\nWreath product (C wr D) [Z/2 wr Z]: ").strip() or "Z/2 wr Z"
        return group.parse_options({"spec": spec})
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
    
    while True:
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
            "Z^2 with generators x, X, y, Y .",
            "State = (x,y). "
        ],
        "D∞": [
            "D∞ = Z ⋊ Z/2 with generators r, R, s.",
            "State = (k, eps). Every element is r^m or r^m s."
        ],
        "Lamplighter": [
            "Lamplighter group C ≀ D (wreath product)",
            "",
            "Mathematical structure:",
            "  C = lamp/fiber group (finite cyclic or multiple lamps)",
            "  D = walking group (Z or subgroup like 2Z, 3Z)",
            "",
            "Standard configurations:",
            "  • Z/2 ≀ Z: binary lamps, walk on all integers",
            "  • Z/3 ≀ Z: 3-state lamps, walk on all integers",
            "",
            "Walking subgroups create blocks (Ex 2.2):",
            "  • Z/2 ≀ 2Z: walk in steps of 2, creates 2 blocks",
            "    - Generators: t (move by 2), a (offset 0), b (offset +1)",
            "",
            "Different lamp types per position:",
            "  • Z/2,Z/3 ≀ 2Z: different lamp at each of 2 positions",
            "    - Position 0: Z/2 lamp (a² = e)",
            "    - Position 1: Z/3 lamp (b³ = e)",
            "  • Z/2,Z/3,Z/4 ≀ 3Z: 3 different lamps at 3 positions",
            "    - Generators: t, a (Z/2), b (Z/3), c (Z/4)",
            "",
            "Standard generators:",
            "  • t, T: move on walking group D",
            "  • a, b, c, ...: toggle lamps (order depends on lamp type)",
            "",
            "State = (position, tape) where tape has finite support"
        ],
        "Wreath": [
            "General wreath product C ≀ D = C^(D) ⋊ D",
            "",
            "Mathematical structure:",
            "  C = lamp/fiber group (finite cyclic: Z/2, Z/3, ...)",
            "  D = walking group or subgroup",
            "",
            "Supported lamp groups C:",
            "  • Z/n: single lamp type with n states",
            "",
            "Supported walking groups D:",
            "  • Z: integers (classic lamplighter)",
            "  • 2Z, 3Z, nZ: subgroups (creates n blocks)",
            "  • Z2: integer lattice Z² (2D lamplighter)",
            "  • Dinf: infinite dihedral D∞",
            "  • Dn(n): dihedral Dn (e.g., Dn(5))",
            "  • Free(k): free group Fₖ",
            "  • abelian([m1,m2,...]): finitely generated abelian",
            "",
            "Walking subgroups:",
            "  • nZ creates n blocks, need n offsets [0,1,...,n-1]",
            "  • Generators: a, b, c, ... for each block",
            "",
            "Standard generators:",
            "  • D's generators (for movement)",
            "  • C's generators at each offset (for toggling)",
            "",
            "State = (d, tape) where d ∈ D, tape: D → C (finite support)"
        ]
    }
    
    while True:
        print_header(group.name, headers.get(group.name, []))
        
        modes = [
            "Build a radius-n ball and export graph",
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
    if configured is None:
        return
    
    # Select generators (default or custom)
    gens = select_generators(configured)
    
    radius_str = input("\nRadius: ").strip()
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
    if configured is None:
        return
    
    # Select generators
    gens = select_generators(configured)
    
    max_r_str = input("\nMaximum radius [10]: ").strip()
    max_r = int(max_r_str) if max_r_str else 10
    
    print(f"Computing balls for radii 0..{max_r}...")
    results = compute_growth(configured, gens, max_r)
    growth_type = classify_growth(results)
    print(format_growth_table(results, growth_type))
    
    input("\nPress Enter to continue...")


def evaluate_mode(group):
    print_header(f"{group.name} - Evaluate Word")
    
    configured = configure_group(group)
    if configured is None:
        return
    
    # Select generators
    gens = select_generators(configured)
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
    if configured is None:
        return
    
    # Select generators
    gens = select_generators(configured)
    
    R_str = input("\nRadius: ").strip()
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
