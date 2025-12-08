import argparse
import json
import sys
from typing import List

from .core import build_ball, m_at_factory
from .adapters import export_dot, draw_png


def parse_pattern(s: str) -> List[int]:
    parts = [p.strip() for p in s.split(',') if p.strip()]
    return [int(x) for x in parts]


def char_to_primitive(ch: str, step: int, block_size: int) -> List[dict]:
    # returns a single-primitive list for character
    # 't' and 'T' are reserved as the step move of size `step` (block size)
    if ch == 't':
        return [{'move': step}]
    if ch == 'T':
        return [{'move': -step}]
    # toggles: a->offset0, b->1, c->2, ...; uppercase denotes inverse toggle
    if ch.isalpha():
        lower = ch.lower()
        offset = ord(lower) - ord('a')
        if offset < 0 or offset >= block_size:
            raise ValueError(f"Toggle '{ch}' out of range for block size {block_size}")
        if 'a' <= ch <= 'z':
            return [{'toggle': {'offset': offset, 'delta': 1}}]
        else:
            return [{'toggle': {'offset': offset, 'delta': -1}}]
    raise ValueError(f"Unknown macro character: {ch}")


def parse_gens_shorthand(spec: str, step: int, block_size: int) -> List[dict]:
    gens = []
    for token in [t.strip() for t in spec.split(',') if t.strip()]:
        word = []
        # token like 'att' => sequence of chars
        for ch in token:
            prims = char_to_primitive(ch, step, block_size)
            word.extend(prims)
        gens.append({'name': token, 'word': word})
    return gens


def load_gens_file(path: str):
    with open(path, 'r', encoding='utf8') as f:
        data = json.load(f)
    # basic validation
    gens = []
    for g in data:
        gens.append({'name': g['name'], 'word': g['word']})
    return gens


def main(argv: List[str] = None):
    p = argparse.ArgumentParser(prog="lamplighter")
    p.add_argument('--n', required=True, type=int, help='radius')
    p.add_argument('--pattern', default='2', help='comma-separated block pattern, e.g. 2,4')
    p.add_argument('--gens', default=None, help='comma-separated gens shorthand, e.g. a,t,T')
    p.add_argument('--gens-file', default=None, help='JSON file with full gens spec')
    p.add_argument('--dot', default=None, help='DOT output path (default ball{n}.dot)')
    p.add_argument('--png', default=None, help='PNG output path (default ball{n}.png)')
    p.add_argument('--self-test', action='store_true', help='run internal tests')
    args = p.parse_args(argv)

    if args.self_test:
        # run tests module
        import importlib
        t = importlib.import_module('lamplighter.tests')
        t.run_tests()
        return

    pattern = parse_pattern(args.pattern)
    block_size = len(pattern)
    step = block_size
    if args.gens_file:
        gens = load_gens_file(args.gens_file)
    else:
        if not args.gens:
            p.error('either --gens-file or --gens must be provided')
        gens = parse_gens_shorthand(args.gens, step, block_size)

    # By design, the CLI expects the user to provide any formal inverses
    # explicitly (e.g., 't' and 'T'). We do not auto-symmetrize.
    V, E, dist, labels = build_ball(args.n, gens, block_pattern=pattern)

    # Print a clean textual representation grouped by BFS layer
    print(f"Cayley ball radius={args.n}: |V|={len(V)} |E|={len(E)}")
    # Group vertices by distance
    layers = {}
    for i, d in enumerate(dist):
        layers.setdefault(d, []).append(i)

    use_color = False
    try:
        use_color = sys.stdout.isatty()
    except Exception:
        use_color = False

    # simple ANSI color palette
    colors = ["\033[95m", "\033[94m", "\033[92m", "\033[93m", "\033[91m"]
    reset = "\033[0m"

    for d in sorted(layers.keys()):
        header = f"Layer {d} (dist={d}):"
        if use_color:
            header = colors[d % len(colors)] + header + reset
        print('\n' + header)
        for vid in layers[d]:
            p_, tape = V[vid]
            tape_str = '{' + ', '.join(f'{idx}:{val}' for idx, val in tape) + '}' if tape else '{}'
            print(f'  {vid}: p={p_}, tape={tape_str}')

    print('\nAdjacency:')
    # adjacency lists
    adj = {}
    for (u, v, gi) in E:
        adj.setdefault(u, []).append((v, labels[gi]))
    for u in range(len(V)):
        outs = adj.get(u, [])
        if not outs:
            print(f'  {u}: <no outgoing>')
            continue
        outs_str = ', '.join(f"{v}[{lab}]" for v, lab in outs)
        print(f'  {u} -> {outs_str}')

    # Export DOT and optionally PNG
    dot_path = args.dot or f'ball{args.n}.dot'
    try:
        export_dot(V, E, dist, labels, dot_path)
        print(f'Wrote DOT: {dot_path}')
    except Exception as e:
        print('Failed to write DOT:', e)

    png_path = args.png or f'ball{args.n}.png'
    try:
        draw_png(V, E, dist, labels, png_path)
        print(f'Wrote PNG: {png_path}')
    except Exception as e:
        print('Could not create PNG with Python plotting libraries:', e)
        print('You can render the DOT using Graphviz:')
        print(f'  dot -Tpng {dot_path} -o {png_path}')


if __name__ == '__main__':
    main()
