"""Annotate ESPOL transport edges for the presentation layer."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for rel in ("nestlink/backend/app/data/maps/espol_fusion.json", "nestlink/frontend/public/maps/espol_fusion.json"):
    path = ROOT / rel
    data = json.loads(path.read_text())
    for edge in data["edges"]:
        if "TRANSPORTE" in (edge.get("from"), edge.get("to")) and edge.get("to", "").startswith("PALET_"):
            edge["domain"] = "AMR"
            edge["length"] = 150
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
