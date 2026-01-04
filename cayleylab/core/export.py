def write_png(V, E, dist, labels, words, group, path):
    # Write PNG using Graphviz for proper edge label positioning
    # Falls back to matplotlib if Graphviz is not available
    import os
    import subprocess
    
    # First, generate DOT file
    dot_path = path.replace('.png', '.dot')
    write_dot(V, E, dist, labels, words, group, dot_path)
    
    # Use Graphviz to render PNG
    result = subprocess.run(['dot', '-Tpng', dot_path, '-o', path])
    if result.returncode == 0:
        return
    
    # If that didn't work, try matplotlib
    import networkx as nx
    import matplotlib.pyplot as plt
    
    # Build networkx graph
    G = nx.DiGraph()
    for i in range(len(V)):
        G.add_node(i)
    for u, v, gi in E:
        G.add_edge(u, v, gen=labels[gi])
    
    # Position layout: cartesian for Z², layered for others
    pos = {}
    if group.name == "Z^2":
        # Use actual (x, y) coordinates as position
        for i in range(len(V)):
            x, y = V[i]
            pos[i] = (x, y)
        # Scale figure based on coordinate range
        xs = [V[i][0] for i in range(len(V))]
        ys = [V[i][1] for i in range(len(V))]
        width = max(8, (max(xs) - min(xs) + 3) * 1.5)
        height = max(8, (max(ys) - min(ys) + 3) * 1.5)
    else:
        # Layer layout by distance
        maxd = max(dist) if dist else 0
        layer_counts = {d: [] for d in range(maxd + 1)}
        for i, d in enumerate(dist):
            layer_counts[d].append(i)
        
        for d in range(maxd + 1):
            nodes = layer_counts[d]
            n = len(nodes)
            for idx, node in enumerate(nodes):
                pos[node] = (idx - n / 2, -d)
        
        # Scale figure
        width = max(12, len(V) * 0.8)
        height = max(8, maxd * 3)
    
    plt.figure(figsize=(width, height))
    
    # Draw nodes
    node_size = max(800, 1500 / (1 + len(V) / 20))
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='lightblue', 
                          edgecolors='black', linewidths=2)
    
    # Node labels
    node_labels = {i: words[i] for i in range(len(V))}
    font_size = max(8, 12 - len(V) / 30)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=font_size, font_weight='bold')
    
    # Draw edges with minimal curve
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=12,
                          connectionstyle='arc3,rad=0.15', edge_color='gray', 
                          width=1.0, alpha=0.7)
    
    # Edge labels
    edge_labels = {(u, v): G[u][v]['gen'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, 
                                font_size=max(8, font_size-1))
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()


def display_graph(V, E, dist, labels, words, group, png_path=None):
    # Display Graphviz-rendered PNG in matplotlib window
    # png_path: Path to PNG file to display. If None, generates a temporary PNG.
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    
    # If no PNG provided, create a temporary one using Graphviz
    if png_path is None:
        import tempfile
        import subprocess
        dot_path = tempfile.mktemp(suffix='.dot')
        png_path = dot_path.replace('.dot', '.png')
        
        # Generate DOT and PNG
        write_dot(V, E, dist, labels, words, group, dot_path)
        subprocess.run(['dot', '-Tpng', dot_path, '-o', png_path])
    
    # Load and display the PNG
    img = mpimg.imread(png_path)
    
    # Create figure with appropriate size
    dpi = 80
    height, width = img.shape[:2]
    figsize = width / dpi, height / dpi
    
    plt.figure(figsize=figsize, dpi=dpi)
    plt.imshow(img)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.show()  # Opens window, blocks until user closes it


def write_dot(V, E, dist, labels, words, group, path):
    # Write Graphviz DOT file with word labels on nodes
    def escape(s):
        return s.replace('"', '\\"').replace('|', '\\|')
    
    lines = []
    lines.append('digraph G {')
    
    # For Cartesian layout (Z^2 only), use neato with fixed positions
    if group.name == "Z^2":
        lines.append('  layout=neato;')
        lines.append('  node [shape=circle, style=filled, fillcolor=lightblue, width=0.35, fixedsize=true, fontsize=9];')
        lines.append('  edge [fontsize=8, color=gray, arrowsize=0.6];')
        
        # Add nodes with positions
        for i in range(len(V)):
            label = escape(words[i])
            x, y = V[i]
            # Scale positions for better visualization (Graphviz uses inches)
            px, py = x * 0.8, y * 0.8
            lines.append(f'  v{i} [label="{label}", pos="{px},{py}!"];')
    elif group.name == "F_2 (Free Group)":
        # Tree layout - vertical with identity at top
        lines.append('  layout=dot;')
        lines.append('  rankdir=TB;')  # Top to bottom
        lines.append('  node [shape=circle, style=filled, fillcolor=lightblue, width=0.35, fixedsize=true, fontsize=9];')
        
        # Add nodes
        for i in range(len(V)):
            label = escape(words[i])
            lines.append(f'  v{i} [label="{label}"];')
        
        # Add colored edges based on generator
        edge_colors = {'a': 'red', 'A': 'blue', 'b': 'green', 'B': 'orange'}
        for u, v, gi in E:
            gen_name = escape(labels[gi])
            color = edge_colors.get(gen_name, 'gray')
            lines.append(f'  v{u} -> v{v} [label="{gen_name}", color={color}, fontcolor={color}, fontsize=8, arrowsize=0.6];')
        
        lines.append('}')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return
    else:
        # Default tree layout
        lines.append('  rankdir=TB;')
        lines.append('  node [shape=circle, style=filled, fillcolor=lightblue, width=0.35, fixedsize=true, fontsize=9];')
        lines.append('  edge [fontsize=8, color=gray, arrowsize=0.6];')
        
        for i in range(len(V)):
            label = escape(words[i])
            lines.append(f'  v{i} [label="{label}"];')
    
    for u, v, gi in E:
        gen_name = escape(labels[gi])
        lines.append(f'  v{u} -> v{v} [label="{gen_name}"];')
    
    lines.append('}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
