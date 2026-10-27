import json, math, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MAP=ROOT/'nestlink/backend/app/data/maps/espol_fusion.json'; MARK=ROOT/'nestlink/backend/app/data/new_map_markers.json'
X=[[0,0],[347,50],[436,95],[611,189],[853,322],[893,414],[1100,605],[1280,869],[1452,950]]; Y=[[0,0],[258,120],[395,302],[483,344],[600,410],[795,550],[1100,600]]
def w(v,a):
 for (p,q),(r,s) in zip(a,a[1:]):
  if v<=r:return round(q+(v-p)*(s-q)/(r-p),2)
 p,q=a[-2];r,s=a[-1];return round(q+(v-p)*(s-q)/(r-p),2)
d=json.loads(MAP.read_text());m=json.loads(MARK.read_text()); ns={n['id']:n for n in d['nodes']}; ids=[]
for i,p in enumerate(m['morado']['puntos'],1):ids.append((f'PALET_{i:02d}',p))
for i,p in enumerate(m['naranja']['puntos'],1):ids.append((f'RECO_R{i}',p))
for i,p in enumerate(m['amarillo']['puntos'],1):ids.append((f'INSUMO_P{i}',p))
ids.append(('FUENTE_INSUMOS',m['cafe']['puntos'][0])); S={x for x,_ in ids}
for k,p in ids:
 if k in ns:ns[k]['x']=w(p['x_px'],X);ns[k]['y']=w(p['y_px'],Y)
for e in d['edges']:
 if e['from'] in S or e['to'] in S:
  if 'TRANSPORTE' in (e['from'],e['to']) and e.get('domain')=='AMR':e['length']=150
  else:
   a,b=ns[e['from']],ns[e['to']];e['length']=round(max(.01,math.hypot(a['x']-b['x'],a['y']-b['y'])),4)
MAP.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');shutil.copy2(MAP,ROOT/'nestlink/frontend/public/maps/espol_fusion.json')
print(len(S),len(d['nodes']),len(d['edges']))
