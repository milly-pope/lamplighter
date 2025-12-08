import json
from typing import List, Tuple

from .core import State


def export_json(V: List[State], E: List[Tuple[int, int, int]], dist: List[int], labels: List[str], path: str) -> None:
    """
    Export graph to JSON. See spec in repository.
    """
    vertices = []
    for i, (p, tape) in enumerate(V):
        vertices.append({
            "id": i,
            "p": p,
            "tape": [[int(idx), int(val)] for idx, val in tape],
            "dist": int(dist[i]),
        })

    edges = []
    for (u, v, gi) in E:
        edges.append({"u": int(u), "v": int(v), "gen": labels[gi]})

    out = {"generators": labels, "vertices": vertices, "edges": edges}
    with open(path, 'w', encoding='utf8') as f:
        json.dump(out, f, indent=2, sort_keys=False)


def _escape_label(s: str) -> str:
    return s.replace('"', '\\"')


def export_dot(V: List[State], E: List[Tuple[int, int, int]], dist: List[int], labels: List[str], path: str) -> None:
    """
    Directed .dot with vertex labels 'id|p|tape|d' and edge labels as generator names.
    """
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
