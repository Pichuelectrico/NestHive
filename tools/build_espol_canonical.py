"""Build the ESPOL simulation map from one orthogonal corridor network.

The drawing and vehicle graph must use the same nodes and edges. Run this
script after editing the route segments; it writes identical backend/frontend
JSON mirrors. Realistic and the other plants are intentionally untouched.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "nestlink/backend/app/data/maps/espol_fusion.json"
FRONTEND = ROOT / "nestlink/frontend/public/maps/espol_fusion.json"
VISUAL_BACKEND = ROOT / "nestlink/backend/app/data/maps/espol_fusion_visual.json"
VISUAL_FRONTEND = ROOT / "nestlink/frontend/public/maps/espol_fusion_visual.json"

# Reference geometry in the 1000 x 600 canvas. Each segment is a real lane.
LANES = [
    # Upper production corridor: two horizontal lanes and P1 branch.
    ((164, 116), (870, 116)), ((164, 130), (870, 130)),
    ((400, 116), (400, 550)), ((413, 130), (413, 550)),
    ((400, 116), (413, 116)), ((400, 130), (413, 130)),
    ((870, 50), (870, 130)),
    # Left palletizing block, four horizontal rows and two side aisles.
    ((50, 302), (320, 302)), ((50, 344), (413, 344)),
    ((50, 410), (413, 410)), ((50, 468), (413, 468)),
    ((50, 550), (413, 550)), ((50, 302), (50, 550)),
    ((320, 302), (320, 550)), ((320, 302), (413, 302)),
    ((94, 255), (94, 302)), ((189, 255), (189, 302)),
    # Right production lanes, with visible connections to center.
    ((400, 278), (927, 278)), ((413, 294), (927, 294)),
    ((413, 344), (927, 344)), ((927, 278), (927, 344)),
    ((877, 344), (877, 365)),
    ((680, 344), (680, 368)), ((680, 368), (800, 368)),
    # Lower R3/P3 region joins the middle network at x413.
    ((413, 410), (500, 410)), ((500, 410), (500, 550)),
    ((413, 468), (500, 468)), ((413, 550), (950, 550)),
    ((500, 468), (950, 468)), ((725, 468), (725, 550)),
    ((896, 468), (896, 550)), ((950, 468), (950, 550)),
    ((725, 500), (896, 500)),
    # Source of materials and the left transport dock outside the perimeter.
    ((350, 520), (400, 520)), ((20, 344), (50, 344)),
    ((20, 344), (20, 410)), ((20, 410), (50, 410)),
]

PALET_X = (80, 110, 140, 170, 200)
PALET_ROWS = ((319, 344), (387, 410), (445, 468))

# Functional station IDs remain stable for seeds, missions, and API consumers.
STATIONS = {
    "CHARGER_1": (94, 255, "carga"), "CHARGER_2": (189, 255, "carga"),
    "FUENTE_INSUMOS": (350, 520, "almacen"),
    "INSUMO_P1": (870, 50, "almacen"), "INSUMO_P2": (877, 365, "almacen"),
    "INSUMO_P3": (896, 550, "almacen"),
    "RECO_R1": (164, 116, "almacen"), "RECO_R2": (680, 368, "almacen"),
    "RECO_R3": (725, 500, "almacen"),
    "TRANSPORTE": (20, 377, "buffer"),
    "E1_IN": (750, 278, "empacadora"), "L2_OUT": (700, 278, "linea"),
    "L1_OUT": (650, 278, "linea"), "E2_IN": (750, 344, "empacadora"),
    "BUFFER_1": (850, 294, "buffer"), "BUFFER_2": (810, 294, "buffer"),
    "WH_PT_1": (400, 355, "almacen"), "WH_PT_2": (400, 380, "almacen"),
    "WH_PT_3": (400, 400, "almacen"),
    "ControlPoint1": (50, 344, "cruce"), "ControlPoint2": (50, 410, "cruce"),
    "ControlPoint3": (50, 468, "cruce"), "ControlPoint4": (320, 344, "cruce"),
    "ControlPoint5": (320, 410, "cruce"), "ControlPoint6": (320, 468, "cruce"),
}


def on_segment(point, start, end):
    x, y = point
    return ((start[0] == end[0] == x and min(start[1], end[1]) <= y <= max(start[1], end[1]))
            or (start[1] == end[1] == y and min(start[0], end[0]) <= x <= max(start[0], end[0])))


def intersections(a, b, c, d):
    if a[0] == b[0] and c[1] == d[1]:
        point = (a[0], c[1])
        return [point] if on_segment(point, a, b) and on_segment(point, c, d) else []
    if a[1] == b[1] and c[0] == d[0]:
        return intersections(c, d, a, b)
    if a[0] == b[0] == c[0] or a[1] == b[1] == c[1]:
        return [p for p in (a, b, c, d) if on_segment(p, a, b) and on_segment(p, c, d)]
    return []


def build():
    old = json.loads(BACKEND.read_text())
    old_blue = {(n["x"], n["y"]): n["id"] for n in old["nodes"]
                if n["id"].startswith("B") and n["id"][1:].isdigit()}
    lanes = list(LANES)
    for top, row in PALET_ROWS:
        for x in PALET_X:
            lanes.append(((x, top), (x, row)))
    points = {p for lane in lanes for p in lane}
    points.update((x, y) for x, y, _ in STATIONS.values())
    for i, (a, b) in enumerate(lanes):
        for c, d in lanes[i + 1:]:
            points.update(intersections(a, b, c, d))

    # Keep the IDs the operator has already reviewed. New geometry must never
    # renumber every surviving blue point after a deletion.
    points_sorted = sorted(points, key=lambda p: (p[1], p[0]))
    blue = {}
    next_number = max(int(value[1:]) for value in old_blue.values()) + 1
    for point in points_sorted:
        if point == (400, 520):
            blue[point] = "J_INSUMOS"  # real junction without a redundant blue marker
        elif point in old_blue:
            blue[point] = old_blue[point]
        else:
            while next_number == 34:
                next_number += 1
            blue[point] = f"B{next_number:02d}"
            next_number += 1
    nodes = [{"id": name, "x": x, "y": y, "type": "cruce", "label": name}
             for (x, y), name in blue.items()]
    nodes += [{"id": name, "x": x, "y": y, "type": kind, "label": name}
              for name, (x, y, kind) in STATIONS.items()]
    for row_index, (top, _) in enumerate(PALET_ROWS):
        for col_index, x in enumerate(PALET_X):
            n = row_index * 5 + col_index + 1
            nodes.append({"id": f"PALET_{n:02d}", "x": x, "y": top,
                          "type": "buffer", "label": f"PALET_{n:02d}"})

    edges = []
    seen = set()
    def link(u, v, **extra):
        if u == v or (u, v) in seen or (v, u) in seen:
            return
        seen.add((u, v))
        edges.append({"from": u, "to": v, "direction": "bi", **extra})

    for a, b in lanes:
        parts = sorted((p for p in points if on_segment(p, a, b)),
                       key=lambda p: p[1] if a[0] == b[0] else p[0])
        for u, v in zip(parts, parts[1:]):
            link(blue[u], blue[v])
    for name, (x, y, _) in STATIONS.items():
        link(name, blue[(x, y)], **({"allowed_types": ["AGV"], "length": 150}
                                    if name == "TRANSPORTE" else {}))
    for row_index, (top, _) in enumerate(PALET_ROWS):
        for col_index, x in enumerate(PALET_X):
            n = row_index * 5 + col_index + 1
            link(f"PALET_{n:02d}", blue[(x, top)])

    result = {
        "canvas": {"w": 1000, "h": 600, "title": "Planta ESPOL Fusion — NestHive"},
        "nodes": nodes, "edges": edges,
        "walls": [
            {"id": "W_MID_LEFT", "x": 50, "y": 188, "w": 250, "h": 2,
             "label": "Pared intermedia izquierda", "color": "#a8a29e"},
            {"id": "W_MID_RIGHT", "x": 430, "y": 188, "w": 520, "h": 2,
             "label": "Pared intermedia derecha", "color": "#a8a29e"},
        ],
        "zones": [
            {"id": "ZONE_PALET", "label": "Paletizaje", "x": 65, "y": 310,
             "w": 150, "h": 158, "color": "#b96bd4"},
        ],
        "lines": [
            {"id": "R1", "nombre": "Cookies", "buffer_nodes": ["RECO_R1"]},
            {"id": "R2", "nombre": "Chocolates", "buffer_nodes": ["RECO_R2"]},
            {"id": "R3", "nombre": "Wafer", "buffer_nodes": ["RECO_R3"]},
        ],
        "pedestrians": [],
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    BACKEND.write_text(encoded)
    FRONTEND.write_text(encoded)
    visual = json.loads(VISUAL_BACKEND.read_text())
    visual["legend"]["rojo"] = "Ruta AMR entre paletizaje y transporte"
    visual["layout_spec"]["transport"]["edge_domain"] = "AMR"
    visual["corridors"] = [{"points": [list(a), list(b)], "width": 9, "oneway": False}
                           for a, b in lanes]
    visual["zones"] = [
        {"id": "Z_PALET", "role": "paletizaje", "rect": [65, 310, 150, 158],
         "color": "#b96bd4", "label": "Paletizaje"},
        {"id": "Z_CHARGE", "role": "carga", "rect": [80, 245, 120, 20],
         "color": "#6dcc62", "label": "Carga"},
    ]
    visual_encoded = json.dumps(visual, ensure_ascii=False, indent=2) + "\n"
    VISUAL_BACKEND.write_text(visual_encoded)
    VISUAL_FRONTEND.write_text(visual_encoded)
    print(f"ESPOL: {len(nodes)} nodes, {len(edges)} edges; mirrors identical")


if __name__ == "__main__":
    build()
