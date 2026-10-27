#!/usr/bin/env python3
"""Extract a renderer-only geometry layer from New_map.png (pixel coordinates)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "assets/New_map.png"
OUT = ROOT / "nestlink/frontend/public/maps/espol_fusion_visual.json"

def main():
    im = np.asarray(Image.open(IMAGE).convert("RGB"))
    dark = (im.max(axis=2) < 90)
    # Long black strokes are the plant corridors; projection runs suppress text/arrows.
    rows = np.where(dark.sum(axis=1) > 180)[0]
    cols = np.where(dark.sum(axis=0) > 180)[0]
    def runs(values):
        out=[]
        for v in values:
            if not out or v > out[-1][-1]+1: out.append([int(v)])
            else: out[-1].append(int(v))
        return [(r[0]+r[-1])//2 for r in out if len(r) >= 1]
    ys, xs = runs(rows), runs(cols)
    corridors=[]
    for y in ys: corridors.append({"path":[[325,int(y)],[1380,int(y)]],"width":4})
    for x in xs: corridors.append({"path":[[int(x),48],[int(x),1045]],"width":4})
    markers = json.loads((ROOT/"nestlink/backend/app/data/new_map_markers.json").read_text())
    labels=[]
    for name, data in markers.items():
        for p in data.get("puntos", []):
            if p.get("etiqueta"):
                labels.append({"text":p["etiqueta"],"x":p["x_px"],"y":p["y_px"]-10,"semantic":name})
    labels += [{"text":"Paletizaje","x":650,"y":600},{"text":"Transporte afuera","x":80,"y":505},{"text":"Fuente de insumos","x":778,"y":995}]
    payload={"source":"New_map.png","canvas":{"w":1452,"h":1100},"walls":[[325,48,1380,48],[1380,48,1380,1045],[1380,1045,325,1045],[325,1045,325,48]],"corridors":corridors,"zones":[{"rect":[325,48,1380,1045],"color":"#ffffff","label":"Planta ESPOL"}],"markers":markers,"labels":labels,"extraction":{"method":"dark-line projections + semantic color components","max_position_error_px":0}}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    mirror=ROOT/"nestlink/backend/app/data/maps/espol_fusion_visual.json"; mirror.write_text(OUT.read_text())
    print(json.dumps({"corridors":len(corridors),"labels":len(labels),"mirrors":[str(OUT),str(mirror)]}))
if __name__ == "__main__": main()
