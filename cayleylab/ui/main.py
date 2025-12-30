import sys
from ..groups.base import all_groups, REGISTRY
from ..core.bfs import build_ball
from ..core.export import write_dot, write_png, display_graph
from ..core.growth import compute_growth, classify_growth, format_growth_table
from ..verify.checks import (
    check_generic, layer_sizes,
    check_Z2_counts, check_Dinf_counts, check_L2_counts_small
)
from .screens import (
    numbered_choice, ask_int, ask_list_of_ints,
    ask_yes_no, ask_choice, print_header
)


def main_menu():
    """Top-level menu: select a group."""
    # Ensure groups are registered
    import cayleylab.groups
    
    groups = all_groups()
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
    """Group-specific menu: modes."""
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
        "Lamplighter / Wreath": [
            "State = (p, tape). pattern=[m0,...,m_{B-1}].",
            "Step mode = unit (±1) or block (±B).",
            "Toggles a,b,c act at offsets 0,1,2; uppercase are inverse toggles at mod>2 sites."
        ]
    }
    
    while True:
        print_header(group.name, headers.get(group.name, []))
        
        modes = [
            "Build a radius-n ball (PNG/DOT export)",
            "Analyze growth rate",
            "Evaluate a word",
            "Verify (quick checks)",
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
            verify_mode(group)


def build_mode(group):
    """Build a radius-n ball and export."""
    print_header(f"{group.name} - Build Ball")
    
    # Parse group-specific options
    if group.name in ("Z^2", "D∞", "C₂ ≀ Z²", "F_2 (Free Group)"):
        configured = group
        gens = configured.default_generators()
    elif group.name == "Lamplighter / Wreath":
        pattern = ask_list_of_ints("Block pattern (comma-separated ints)", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        max_offset = len(pattern) - 1
        print(f"Offsets range from 0 to {max_offset} (a={0}, b={1}, c={2}, ...)")
        offsets = ask_list_of_ints("Toggle offsets to expose", default=[0])
        
        # Validate offsets
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
    if group.name == "Lamplighter / Wreath":
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
    """Analyze growth rate of Cayley balls."""
    print_header(f"{group.name} - Growth Analysis")
    
    # Parse group-specific options
    if group.name == "Z^2" or group.name == "D∞" or group.name == "C₂ ≀ Z²" or group.name == "F_2 (Free Group)":
        configured = group
        gens = configured.default_generators()
    elif group.name == "Lamplighter / Wreath":
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
    """Evaluate a word in the group."""
    print_header(f"{group.name} - Evaluate Word")
    
    # Get configured group and generators
    if group.name == "Lamplighter / Wreath":
        pattern = ask_list_of_ints("Block pattern", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        offsets = ask_list_of_ints("Toggle offsets", default=[0])
        offsets = [o for o in offsets if 0 <= o < len(pattern)]
        
        configured = group.parse_options({
            "pattern": pattern,
            "step_mode": step_mode,
            "offsets": offsets
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


def verify_mode(group):
    """Run verification checks on the group."""
    print_header(f"{group.name} - Verify")
    
    # Get configured group and generators
    if group.name == "Lamplighter / Wreath":
        pattern = ask_list_of_ints("Block pattern", default=[2])
        step_mode = ask_choice("Step mode", ["unit", "block"], default="unit")
        offsets = ask_list_of_ints("Toggle offsets", default=[0])
        offsets = [o for o in offsets if 0 <= o < len(pattern)]
        
        configured = group.parse_options({
            "pattern": pattern,
            "step_mode": step_mode,
            "offsets": offsets
        })
    else:
        configured = group
    
    gens = configured.default_generators()
    
    # Ask radius
    radius = ask_int("Radius to test", default=3)
    
    # Build ball
    print(f"\nBuilding ball...")
    V, E, dist, labels, words = build_ball(configured, gens, radius)
    
    # Run generic checks
    print(f"\nRunning generic checks...")
    errors = check_generic(V, E, dist)
    if errors:
        print("FAIL:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("PASS: All generic checks passed")
    
    # Run family-specific checks
    print(f"\nRunning {group.name}-specific checks...")
    if group.name == "Z^2":
        err = check_Z2_counts(radius, len(V))
        if err:
            print(f"FAIL: {err}")
        else:
            print(f"PASS: Ball size matches expected 2n(n+1)+1 = {len(V)}")
    
    elif group.name == "D∞":
        err = check_Dinf_counts(radius, len(V))
        if err:
            print(f"FAIL: {err}")
        else:
            expected = 1 if radius == 0 else 4 * radius
            print(f"PASS: Ball size matches expected {expected}")
    
    elif group.name == "Lamplighter / Wreath":
        # Check if configuration matches L2 known values
        if configured.pattern == [2] and configured.step_mode == "unit" and configured.offsets == [0]:
            err = check_L2_counts_small(radius, len(V))
            if err:
                print(f"FAIL: {err}")
            else:
                print(f"PASS: L2 ball size matches known value {len(V)}")
        else:
            print("No known count formula for this configuration")
    
    input("\nPress Enter to continue...")


def main():
    """Entry point for cayleylab."""
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
