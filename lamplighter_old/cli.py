import argparse
import sys
from .core import build_ball, make_modulus_func
from .adapters import export_dot, draw_png


def parse_pattern(s):
    # Takes i.e '2,4' and returns [2,4] 
    parts = [p.strip() for p in s.split(',')]
    return [int(x) for x in parts]


def char_to_primitive(ch, step, pattern):
    # Returns single-primitive list for character
    # 't' and 'T' are always expected as the step size i.e block size
    if ch == 't':
        return [{'move': step}]
    if ch == 'T':
        return [{'move': -step}]
    # toggles: a->offset0, b->1, c->2, ...; uppercase denotes inverse toggle
    if ch.isalpha():
        lower = ch.lower()
        offset = ord(lower) - ord('a') #this is the logic that implements required offset for generators
        if offset < 0 or offset >= len(pattern):
            raise ValueError(f"Toggle '{ch}' out of range for block size {len(pattern)}")
        modulus = pattern[offset]
        if 'a' <= ch <= 'z':
            return [{'toggle': {'offset': offset, 'delta': 1}}]
        else:
            # Uppercase = inverse toggle (delta -1)
            if modulus == 2:
                raise ValueError(f"Toggle '{ch}' uppercase not needed for mod 2 at offset {offset} (self-inverse)")
            return [{'toggle': {'offset': offset, 'delta': -1}}]
    raise ValueError(f"Unknown macro character: {ch}")


def build_generator_spec(spec, step, pattern):
    # Parse shorthand generator spec to list of GenSpec dicts
    # Take user input like 'a,t,T' and return list of GenSpec
    gens = []
    for token in [t.strip() for t in spec.split(',')]:
        word = []
        # token like 'att' => sequence of chars
        for ch in token:
            prims = char_to_primitive(ch, step, pattern) # returns list with one primitive
            word.extend(prims) # had to use so we dont nest lists
        gens.append({'name': token, 'word': word})
    return gens


def main(argv=None):
    p = argparse.ArgumentParser(prog="lamplighter")
    p.add_argument('--n', required=True, type=int, help='radius')
    p.add_argument('--pattern', default='2', help='comma-separated block pattern, e.g. 2,4')
    p.add_argument('--gens', required=True, help='comma-separated gens shorthand, e.g. a,t,T')
    p.add_argument('--dot', default=None, help='DOT output path (default ball{n}.dot)')
    p.add_argument('--png', default=None, help='PNG output path (default ball{n}.png)')
    p.add_argument('--self-test', action='store_true', help='run internal tests')
    args = p.parse_args(argv)


    pattern = parse_pattern(args.pattern)
    step = len(pattern)
    gens = build_generator_spec(args.gens, step, pattern)

    V, E, dist, labels, words = build_ball(args.n, gens, block_pattern=pattern)

    print(f"Cayley ball radius={args.n}: |V|={len(V)} |E|={len(E)}")
    # Group vertices by distance, dist is an array where dist[i] is distance of vertex i
    layers = {}
    for i, d in enumerate(dist):  #i is vertex ID, d is distance
        if d not in layers:
            layers[d] = []
        layers[d].append(i)
    #i.e if dist=[0,1,1,2], layers={0:[0],1:[1,2],2:[3]}

    for d in sorted(layers.keys()):
        print(f'\nLayer {d} (dist={d}):')
        for vid in layers[d]:
            p_, tape = V[vid]
            tape_str = '{' + ', '.join(f'{idx}:{val}' for idx, val in tape) + '}' if tape else '{}'
            print(f'  {vid}: p={p_}, tape={tape_str}')

    print('\nAdjacency:')
    # Build adjacency lists: E is [(u, v, gi)...] where u=source, v=target, gi=generator index
    adj = {}
    for (u, v, gi) in E:
        if u not in adj:
            adj[u] = []
        adj[u].append((v, labels[gi]))  # store (target, generator_name) pairs
    # adj = {u: [(v1, gen1), (v2, gen2), ...]} maps each vertex to its outgoing edges
    
    for u in range(len(V)):
        outs = adj.get(u, [])
        if not outs:
            print(f'  {u}: <no outgoing>')
            continue
        outs_str = ', '.join(f"{v}[{lab}]" for v, lab in outs)
        print(f'  {u} -> {outs_str}')

#@ add the verticies to show the words. which would grow quicker if i had i.e c2xc2 vs jusr c2 wth more generators, give option to play around with these things by just asking how many elements
#£cab use it to answer questions about the growth rate of the group with different generating sets. diameter of finite, how long does that take '''
   
    # Export DOT and optionally PNG
    dot_path = args.dot or f'ball{args.n}.dot'
    try:
        export_dot(V, E, dist, labels, words, dot_path)
        print(f'Wrote DOT: {dot_path}')
    except Exception as e:
        print('Failed to write DOT:', e)

    png_path = args.png or f'ball{args.n}.png'
    try:
        draw_png(V, E, dist, labels, words, png_path)
        print(f'Wrote PNG: {png_path}')
    except Exception as e:
        print('Could not create PNG with Python plotting libraries:', e)
        print('You can render the DOT using Graphviz:')
        print(f'  dot -Tpng {dot_path} -o {png_path}')


if __name__ == '__main__':
    main()
