from typing import List, Tuple

from .core import State


def export_dot(V: List[State], E: List[Tuple[int, int, int]], dist: List[int], labels: List[str], path: str) -> None:
    """Write a DOT file with simple record node labels."""
    def _escape_label(s: str) -> str:
        return s.replace('"', '\\"')

    lines = []
    lines.append('digraph G {')
    lines.append('  node [shape=record];')
    for i, (p, tape) in enumerate(V):
        tape_str = ";".join(f"{idx}:{val}" for idx, val in tape)
        lab = f"{i}|p={p}|{tape_str}|d={dist[i]}"
        lines.append(f'  v{i} [label="{_escape_label(lab)}"];')
    for (u, v, gi) in E:
        gname = _escape_label(labels[gi])
        lines.append(f'  v{u} -> v{v} [label="{gname}"];')
    lines.append('}')
    with open(path, 'w', encoding='utf8') as f:
        f.write('\n'.join(lines))



def to_networkx(V: List[State], E: List[Tuple[int, int, int]], dist: List[int], labels: List[str]):
    try:
        import networkx as nx
    except Exception as e:
        raise ImportError("networkx is required for to_networkx")
    G = nx.DiGraph()
    for i, (p, tape) in enumerate(V):
        G.add_node(i, p=p, tape=tuple(tape), dist=dist[i])
    for (u, v, gi) in E:
        G.add_edge(u, v, gen=labels[gi])
    return G


def draw_png(V: List[State], E: List[Tuple[int, int, int]], dist: List[int], labels: List[str], path_png: str):
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except Exception as e:
        raise ImportError("networkx and matplotlib are required for draw_png")
    G = to_networkx(V, E, dist, labels)
    pos = {}
    # simple layer layout by dist
    maxd = max(dist) if dist else 0
    layer_counts = {d: [] for d in range(maxd + 1)}
    for i, d in enumerate(dist):
        layer_counts[d].append(i)
    for d in range(maxd + 1):
        nodes = layer_counts[d]
        n = len(nodes)
        for idx, node in enumerate(nodes):
            pos[node] = (idx - n / 2, -d)
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, max(4, maxd)))
    nx.draw(G, pos, with_labels=True, labels={i: i for i in range(len(V))}, node_size=200)
    edge_labels = {(u, v): G[u][v]['gen'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig(path_png)
    plt.close()
