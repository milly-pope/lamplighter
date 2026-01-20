import sys
from ..core.bfs import build_ball
from ..core.export import write_dot, write_png, display_graph


def numbered_choice(prompt, choices):
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}) {choice}")
    print("  q) Quit")
    
    while True:
        resp = input("\nChoice: ").strip().lower()
        if resp == 'q':
            return None
        idx = int(resp) - 1
        if 0 <= idx < len(choices):
            return idx
        print("Invalid choice. Try again.")


def ask_int(prompt, default=None):
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        resp = input(full_prompt).strip()
        if not resp and default is not None:
            return default
        return int(resp)


def ask_list_of_ints(prompt, default=None):
    if default is not None:
        default_str = ",".join(map(str, default))
        full_prompt = f"{prompt} [{default_str}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        resp = input(full_prompt).strip()
        if not resp and default is not None:
            return default
        parts = [p.strip() for p in resp.split(',')]
        return [int(p) for p in parts if p]


def ask_yes_no(prompt, default=True):
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        resp = input(prompt + suffix).strip().lower()
        if not resp:
            return default
        if resp in ('y', 'yes'):
            return True
        if resp in ('n', 'no'):
            return False
        print("Please enter y or n.")


def ask_choice(prompt, choices, default=None):
    choice_str = "/".join(choices)
    if default:
        full_prompt = f"{prompt} [{choice_str}, default={default}]: "
    else:
        full_prompt = f"{prompt} [{choice_str}]: "
    
    while True:
        resp = input(full_prompt).strip().lower()
        if not resp and default:
            return default
        if resp in choices:
            return resp
        print(f"Please enter one of: {choice_str}")


def print_header(title, lines=None):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    if lines:
        for line in lines:
            print(f"  {line}")
        print()


def layer_sizes(dist):
    # Count vertices at each distance
    if not dist:
        return []
    max_dist = max(dist)
    counts = [0] * (max_dist + 1)
    for d in dist:
        counts[d] += 1
    return counts


def main_menu():
    # Top-level menu: select a group
    from ..groups.Z2 import Z2
    from ..groups.Dinf import Dinf
    from ..groups.free import FreeGroup
    from ..groups.lamplighter import Lamplighter
    from ..groups.lamplighter_z2 import LamplighterZ2
    from ..groups.wreath import WreathProduct
    
    groups = [
        Z2(),
        Dinf(),
        FreeGroup(),
        Lamplighter(),
        LamplighterZ2(),
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
            "Evaluate a word",
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
    # Build a radius-n ball and export
    print_header(f"{group.name} - Build Ball")
    
    # Parse group-specific options
    if group.name in ("Z^2", "D∞", "C₂ ≀ Z²"):
        configured = group
        gens = configured.default_generators()
    elif group.name.startswith("F_"):
        rank = ask_int("\nRank of free group", default=2, min_val=1)
        configured = group.parse_options({"rank": rank})
        gens = configured.default_generators()
    elif group.name == "Lamplighter":
        print("Enter base group (examples: Z/2, Z/3, Z/4)")
        print("For product bases, use commas: Z/2,Z/3")
        base_spec = input("Base group [Z/2]: ").strip() or "Z/2"
        
        print("Offsets for toggle generators (comma-separated, 0 = at head)")
        offsets_input = input("Toggle offsets [0]: ").strip() or "0"
        offsets = [int(x.strip()) for x in offsets_input.split(',')]
        
        # Convert base_spec to wreath product spec
        spec = f"{base_spec} wr Z"
        
        configured = group.parse_options({
            "spec": spec,
            "offsets": [str(o) for o in offsets]
        })
        gens = configured.default_generators()
    elif group.name == "Wreath":
        print("\nWreath product C ≀ D = C^(D) ⋊ D with finite support")
        print("Supported: Z, Z/n, Z2, D∞, Dn(n), Free(k), abelian([m1,...])")
        print("Examples: 'Z/5 wr Z', 'abelian([2,4]) wr Z2', 'Free(3) wr Dn(8)'")
        
        spec = input("\nEnter spec (C wr D): ").strip()
        if not spec:
            spec = "Z/2 wr Z"
        
        # Parse to get top adapter for offset examples
        from ..groups.wreath_adapters_top import get_top_adapter
        from ..groups.wreath_adapters_base import get_base_adapter
        
        if " wr " in spec:
            _, top_spec = spec.split(" wr ", 1)
            top_adapter = get_top_adapter(top_spec.strip())
            
            # Show examples for offsets
            examples = {
                "Z": "e, t, T",
                "Z2": "e, x, y, x x",
                "Zmod": "e, t, t t",
                "Dinf": "e, r, s",
                "Dn": "e, r, s",
                "Free": "e, a, b, a b"
            }
            example = examples.get(top_adapter.name, "e")
            print(f"Offset examples for {top_adapter.name}: {example}")
        
        offsets_input = input(f"Offsets (space-separated words, default 'e'): ").strip()
        if not offsets_input:
            offset_list = ["e"]
        else:
            offset_list = offsets_input.split(',')
            offset_list = [o.strip() for o in offset_list]
        
        configured = group.parse_options({
            "spec": spec,
            "offsets": offset_list
        })
        gens = configured.default_generators()
    else:
        configured = group
        gens = configured.default_generators()
    
    # Confirm generators
    gen_names = [g.name for g in gens]
    print(f"\nGenerators: {', '.join(gen_names)}")
    
    # Ask radius
    radius = ask_int("Radius", default=3)
    
    # Build ball
    print(f"\nBuilding ball...")
    V, E, dist, labels, words = build_ball(configured, gens, radius)
    
    # Print summary
    print(f"\n|V| = {len(V)}, |E| = {len(E)}")
    layers = layer_sizes(dist)
    for d, count in enumerate(layers):
        print(f"  Layer {d}: {count} vertices")
    
    # Create graphs directory if it doesn't exist
    import os
    graphs_dir = "graphs"
    os.makedirs(graphs_dir, exist_ok=True)
    
    # Auto-generate filename
    group_short = group.name.replace(' ', '_').replace('∞', 'inf').replace('/', '_').lower()
    if group.name == "Lamplighter":
        pattern_str = "_".join(map(str, configured.pattern))
        mode_str = configured.step_mode[0]  # 'u' or 'b'
        offset_str = "".join(chr(ord('a') + o) for o in configured.offsets)
        filename = f"{group_short}_p{pattern_str}_{mode_str}_{offset_str}_r{radius}"
    else:
        filename = f"{group_short}_r{radius}"
    
    dot_path = os.path.join(graphs_dir, f"{filename}.dot")
    png_path = os.path.join(graphs_dir, f"{filename}.png")
    
    write_dot(V, E, dist, labels, words, configured, dot_path)
    print(f"Wrote DOT: {dot_path}")
    
    write_png(V, E, dist, labels, words, configured, png_path)
    print(f"Wrote PNG: {png_path}")
    
    # Ask if they want to display
    show = ask_yes_no("\nDisplay graph in live window?", default=True)
    if show:
        print("Opening graph... (close window to continue)")
        display_graph(V, E, dist, labels, words, configured, png_path=png_path)
    
    input("\nPress Enter to continue...")


def growth_mode(group):
    # Analyze growth rate of Cayley balls
    print_header(f"{group.name} - Growth Analysis")
    
    # Parse group-specific options
    if group.name in ("Z^2", "D∞", "C₂ ≀ Z²"):
        configured = group
        gens = configured.default_generators()
    elif group.name.startswith("F_"):
        rank = ask_int("\nRank of free group", default=2, min_val=1)
        configured = group.parse_options({"rank": rank})
        gens = configured.default_generators()
    elif group.name == "Wreath":
        print("\nWreath product C ≀ D")
        spec = input("Enter spec (C wr D): ").strip()
        if not spec:
            spec = "Z/2 wr Z"
        
        offsets_input = input("Offsets (comma-separated words, default 'e'): ").strip()
        if not offsets_input:
            offset_list = ["e"]
        else:
            offset_list = [o.strip() for o in offsets_input.split(',')]
        
        configured = group.parse_options({
            "spec": spec,
            "offsets": offset_list
        })
        gens = configured.default_generators()
    elif group.name == "Lamplighter":
        pattern = ask_list_of_ints("Block pattern (comma-separated ints)", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        max_offset = len(pattern) - 1
        print(f"Offsets range from 0 to {max_offset} (a={0}, b={1}, c={2}, ...)")
        offsets = ask_list_of_ints("Toggle offsets to expose", default=[0])
        offsets = [o for o in offsets if 0 <= o < len(pattern)]
        
        configured = group.parse_options({
            "pattern": pattern,
            "step_mode": step_mode,
            "offsets": offsets
        })
        gens = configured.default_generators()
    else:
        configured = group
        gens = configured.default_generators()
    
    # Confirm generators
    gen_names = [g.name for g in gens]
    print(f"\nGenerators: {', '.join(gen_names)}")
    
    # Ask max radius
    max_radius = ask_int("Maximum radius", default=10)
    
    # Compute growth
    print(f"\nComputing balls for radii 0..{max_radius}...")
    results = compute_growth(configured, gens, max_radius)
    growth_type = classify_growth(results)
    
    # Display results
    print(format_growth_table(results, growth_type))
    
    input("\nPress Enter to continue...")


def evaluate_mode(group):
    # Evaluate a word in the group
    print_header(f"{group.name} - Evaluate Word")
    
    # Get configured group and generators
    if group.name == "Lamplighter":
        pattern = ask_list_of_ints("Block pattern", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        offsets = ask_list_of_ints("Toggle offsets", default=[0])
        offsets = [o for o in offsets if 0 <= o < len(pattern)]
        
        configured = group.parse_options({
            "pattern": pattern,
            "step_mode": step_mode,
            "offsets": offsets
        })
    elif group.name == "Wreath":
        spec = input("Enter spec (C wr D): ").strip()
        if not spec:
            spec = "Z/2 wr Z"
        
        offsets_input = input("Offsets (comma-separated, default 'e'): ").strip()
        offset_list = [o.strip() for o in offsets_input.split(',')] if offsets_input else ["e"]
        
        configured = group.parse_options({
            "spec": spec,
            "offsets": offset_list
        })
    else:
        configured = group
    
    gens = configured.default_generators()
    gen_map = {g.name: g for g in gens}
    gen_names = [g.name for g in gens]
    
    print(f"\nAvailable generators: {', '.join(gen_names)}")
    print("Enter word as space-separated generator names (e.g., 't a T' or 'x y X')")
    
    word_str = input("\nWord: ").strip()
    if not word_str:
        print("Empty word = identity")
        state = configured.identity()
    else:
        tokens = word_str.split()
        state = configured.identity()
        
        for token in tokens:
            if token not in gen_map:
                print(f"Unknown generator '{token}'. Available: {', '.join(gen_names)}")
                input("\nPress Enter to continue...")
                return
            state = gen_map[token].apply(state)
    
    print(f"\nResult: {configured.pretty(state)}")
    print(f"Raw: {state}")
    
    # Find geodesic distance and shortest word
    if state == configured.identity():
        print(f"\nGeodesic distance: 0 (this is the identity)")
        if word_str:
            print(f"Your word length: {len(tokens)} (not optimal - reduces to identity)")
    else:
        # Run BFS to find this element
        print("\nSearching for shortest path...")
        max_search = 50  # reasonable limit
        found = False
        
        for r in range(1, max_search + 1):
            V, E, dist, words, edges_list = build_ball(configured, gens, r)
            if state in V:
                found = True
                geodesic_dist = dist[state]
                shortest_word = words[state]
                
                print(f"\nGeodesic distance: {geodesic_dist}")
                print(f"Shortest word: {' '.join(shortest_word)}")
                
                input_length = len(tokens) if word_str else 0
                if input_length == geodesic_dist:
                    print(f"Your word length: {input_length} ✓ (optimal!)")
                elif input_length > geodesic_dist:
                    print(f"Your word length: {input_length} (not optimal - can be shortened)")
                
                break
        
        if not found:
            print(f"\nElement not found within radius {max_search}")
            print("(Either very far from identity, or search limit too small)")
    
    input("\nPress Enter to continue...")


def dead_end_mode(group):
    # Find dead-end elements on a sphere
    print_header(f"{group.name} - Find Dead-End Elements")
    
    # Print blurb
    print("\nDead-end elements relative to the current generator set S:")
    print("v at distance R is a dead end if no one-step move increases distance (|v s| ≤ |v| for all s ∈ S).")
    print("Depth(v) is the smallest k ≥ 1 with a length-k word that exits B_R.")
    print("We build to radius R + depth_cap to certify detection and depth.")
    
    # Get configured group and generators
    if group.name == "Lamplighter":
        pattern = ask_list_of_ints("Block pattern", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        offsets = ask_list_of_ints("Toggle offsets", default=[0])
        offsets = [o for o in offsets if 0 <= o < len(pattern)]
        
        configured = group.parse_options({
            "pattern": pattern,
            "step_mode": step_mode,
            "offsets": offsets
        })
    elif group.name == "Wreath":
        spec = input("Enter spec (C wr D): ").strip()
        if not spec:
            spec = "Z/2 wr Z"
        
        offsets_input = input("Offsets (comma-separated, default 'e'): ").strip()
        offset_list = [o.strip() for o in offsets_input.split(',')] if offsets_input else ["e"]
        
        configured = group.parse_options({
            "spec": spec,
            "offsets": offset_list
        })
    else:
        configured = group
    
    gens = configured.default_generators()
    gen_names = [g.name for g in gens]
    
    print(f"\nGenerators: {', '.join(gen_names)}")
    
    # Ask for parameters
    R = ask_int("Radius R to analyze", default=7)
    depth_cap = ask_int("Depth cap (max search depth)", default=6)
    max_examples = ask_int("How many examples to show (0 = all)", default=10)
    
    # Build ball and analyze
    V, E, dist, label_list, words = build_ball(configured, gens, radius=R)
    visited = {V[i]: i for i in range(len(V))}
    
    from ..features.deadends import analyze_dead_ends, print_dead_end_results
    results = analyze_dead_ends(configured, gens, gen_names, R, depth_cap, V, dist, visited)
    print_dead_end_results(results, max_examples)
    
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
