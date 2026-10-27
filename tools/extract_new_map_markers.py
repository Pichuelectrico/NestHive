#!/usr/bin/env python3
"""Extract New_map.png semantic marker components into reviewable JSON."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/"assets/New_map.png"; OUTPUT=ROOT/"nestlink/backend/app/data_maps/new_map_markers.json"
# Reference hues sampled from the drawing; tolerances intentionally exclude near-white canvas/text.
PALETTE={"morado":"#b96bd4","verde":"#6dcc62","azul":"#536ff0","amarillo":"#ffc45a","cafe":"#7a3e0b","naranja":"#ff6b21","rojo":"#ff302c"}
def rgb(hexv): return np.array([int(hexv[i:i+2],16) for i in (1,3,5)],dtype=np.int16)
def main():
 im=np.asarray(Image.open(IMAGE).convert("RGB"),dtype=np.int32); result={}
 for name,hexv in PALETTE.items():
  ref=rgb(hexv); dist=np.sqrt(((im-ref)**2).sum(axis=2))
  mask=dist<(48 if name in ("rojo","naranja") else 75)
  # Remove thin antialiasing/text strokes: components need enough area, but retain
  # small circles by using a 2px closing before component labeling.
  mask=ndimage.binary_closing(mask,iterations=1)
  labels,n=ndimage.label(mask,structure=np.ones((3,3),int)); points=[]
  for i in range(1,n+1):
   yy,xx=np.where(labels==i); area=len(xx)
   if area<18: continue
   x0,x1,y0,y1=xx.min(),xx.max(),yy.min(),yy.max(); w,h=x1-x0+1,y1-y0+1
   # Text strokes are wide/long low-density components; retain marker-sized blobs.
   fill=area/(w*h)
   if area>3000 or (max(w,h)>90 and fill<0.18) or w<7 or h<7 or fill<0.28: continue
   points.append({"x_px":int(x0),"y_px":int(y0),"w":int(w),"h":int(h)})
  result[name]={"color":hexv,"puntos":sorted(points,key=lambda p:(p["y_px"],p["x_px"]))}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({k:len(v["puntos"]) for k,v in result.items()},ensure_ascii=False))
 for k,v in result.items(): print(k,":"," ".join(f"({p['x_px']},{p['y_px']},{p['w']}x{p['h']})" for p in v["puntos"]))
if __name__=="__main__":main()
