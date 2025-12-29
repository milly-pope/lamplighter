def export_dot(V, E, dist, labels, words, path):
    """Write a DOT file with simple record node labels."""
    def _escape_label(s):
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



def to_networkx(V, E, dist, labels, words):
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


def draw_png(V, E, dist, labels, words, path_png):
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except Exception as e:
        raise ImportError("networkx and matplotlib are required for draw_png")
    G = to_networkx(V, E, dist, labels, words)
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
    # Scale figure based on graph size
    width = max(12, len(V) * 0.8)
    height = max(8, maxd * 3)
    plt.figure(figsize=(width, height))
    
    # Draw nodes with word labels - bigger nodes for readability
    node_size = max(800, 1500 / (1 + len(V) / 20))  # Scale down for large graphs
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='lightblue', edgecolors='black', linewidths=2)
    
    # Use words as labels instead of vertex IDs
    word_labels = {i: words[i] for i in range(len(V))}
    font_size = max(8, 12 - len(V) / 30)  # Scale down font for large graphs
    nx.draw_networkx_labels(G, pos, labels=word_labels, font_size=font_size, font_weight='bold')
    
    # Draw edges with curves to avoid overlap
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, 
                          connectionstyle='arc3,rad=0.1', edge_color='gray', width=1.5, alpha=0.6)
    
    # Draw edge labels
    edge_labels = {(u, v): G[u][v]['gen'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=font_size-1)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(path_png, dpi=200, bbox_inches='tight')
    plt.close()

