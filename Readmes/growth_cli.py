#!/usr/bin/env python3
import sys
import argparse
from cayleylab.groups.Z_offsets import Z_Offsets
from cayleylab.core.growth import analyze_growth, format_growth_table


def analyze_Z_offsets(offsets, N, label=""):
    group = Z_Offsets(offsets)
    gens = group.default_generators()
    
    desc = label if label else f"Z with offsets {offsets}"
    print(f"\n{desc}")
    print("=" * 60)
    
    result = analyze_growth(group, gens, N, mode="auto", show_series=True)
    print(format_growth_table(result))
    
    return result


def exercise_9(N=8):
    print("\nEXERCISE 9: <a,b | a^2 = b^3, ab=ba>")
    return analyze_Z_offsets({'a': 3, 'b': 2}, N, "Z with offsets a=+3, b=+2")


def exercise_10(k=2, N=8):
    print(f"\nEXERCISE 10: <a,b | a^2 = b^(2k+1), ab=ba> with k={k}")
    offset_a = 2*k + 1
    return analyze_Z_offsets({'a': offset_a, 'b': 2}, N, 
                            f"Z with offsets a=+{offset_a}, b=+2")


def main():
    parser = argparse.ArgumentParser(
        description='Growth analysis for Z with custom offsets'
    )
    parser.add_argument('--Z-offsets', nargs=2, type=int, metavar=('A', 'B'),
                       help='Offsets for generators a and b')
    parser.add_argument('--Z-k', type=int, metavar='K',
                       help='Parameter k for Exercise 10 (a=2k+1, b=2)')
    parser.add_argument('--radius', '-N', type=int, default=8,
                       help='Maximum radius (default: 8)')
    parser.add_argument('--ex9', action='store_true',
                       help='Run Exercise 9 demo')
    parser.add_argument('--ex10', action='store_true',
                       help='Run Exercise 10 demo with k=2')
    
    args = parser.parse_args()
    
    if args.ex9:
        exercise_9(args.radius)
    elif args.ex10:
        exercise_10(2, args.radius)
    elif args.Z_k is not None:
        exercise_10(args.Z_k, args.radius)
    elif args.Z_offsets:
        a_offset, b_offset = args.Z_offsets
        analyze_Z_offsets({'a': a_offset, 'b': b_offset}, args.radius)
    else:
        # Default: show both exercises
        exercise_9()
        print("\n\n")
        exercise_10()


if __name__ == '__main__':
    main()
