#!/usr/bin/env python3
import json,math,shutil,sys
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'agv-espol/data/red_agv_grafo_actualizado.json'; APP=ROOT/'nestlink/backend/app'; MAPS=APP/'data/maps'; SEEDS=APP/'data/seeds'
ROLE_ASSIGNMENT={'L1_OUT':'ControlPoint1','L2_OUT':'ControlPoint2','E1_IN':'ControlPoint3','E2_IN':'ControlPoint4','WH_MP_1':'ControlPoint5','WH_MP_2':'ControlPoint6','WH_MP_3':'ControlPoint7','WH_MP_4':'ControlPoint8','WH_MP_5':'ControlPoint9','WH_PT_1':'ControlPoint10','WH_PT_2':'ControlPoint11','WH_PT_3':'ControlPoint12','CHARGER_1':'ControlPoint13','CHARGER_2':'ControlPoint14','BUFFER_1':'ControlPoint15','BUFFER_2':'ControlPoint16'}
def main():
 raw=json.loads(SRC.read_text()); src={n['id']:n for n in raw['nodos']}; assert len(src)==96 and len(raw['aristas'])==110; renamed={v:k for k,v in ROLE_ASSIGNMENT.items()}
 xs=[n['x'] for n in src.values()]; ys=[n['y'] for n in src.values()]; x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); sx,sy=900/(x1-x0),500/(y1-y0)
 def pos(n): return [round(50+(n['x']-x0)*sx,2),round(50+(y1-n['y'])*sy,2)]
 nodes=[]
 for n in raw['nodos']:
  nid=renamed.get(n['id'],n['id']); typ='linea' if nid.startswith('L') else 'empacadora' if nid.startswith('E') else 'almacen' if nid.startswith('WH_') else 'carga' if nid.startswith('CHARGER') else 'buffer' if nid.startswith('BUFFER') else 'cruce'; p=pos(n); assert 40<=p[0]<=960 and 40<=p[1]<=560; nodes.append({'id':nid,'x':p[0],'y':p[1],'type':typ,'label':nid})
 edges=[]
 for e in raw['aristas']:
  u,v=renamed.get(e['origen'],e['origen']),renamed.get(e['destino'],e['destino']); z={'from':u,'to':v,'length':float(e['distancia_m']),'max_speed':1.5,'direction':'bi' if e.get('bidireccional',True) else 'one-way','blocked':False}; edges.append(z); edges.append({**z,'from':v,'to':u}) if e.get('bidireccional',True) else None
 G=nx.Graph(); G.add_nodes_from(n['id'] for n in nodes); G.add_edges_from((e['from'],e['to'],{'length':e['length']}) for e in edges); assert nx.is_connected(G)
 realistic=json.loads((MAPS/'realistic.json').read_text()); RG=nx.Graph(); RG.add_edges_from((e['from'],e['to'],{'length':e['length']}) for e in realistic['edges']); old=[nx.shortest_path_length(G,f'WH_MP_{i}','L1_OUT',weight='length') for i in range(1,6)]; ref=[nx.shortest_path_length(RG,f'WH_MP_{i}','L1_OUT',weight='length') for i in range(1,6)]; factor=sum(ref)/max(sum(old),1e-9)
 for e in edges:e['length']=round(e['length']*factor,4)
 out={'canvas':{'w':1000,'h':600,'title':'Planta ESPOL · Fusión — NestHive'},'nodes':nodes,'edges':edges,'zones':[],'walls':[],'lines':[{'id':x,'buffer_nodes':['BUFFER_1','BUFFER_2']} for x in ('L1_OUT','L2_OUT','E1_IN','E2_IN')],'pedestrians':[]}; MAPS.mkdir(parents=True,exist_ok=True); (MAPS/'espol_fusion.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 seed=json.loads((SEEDS/'seed_realistic.json').read_text()); cruces=[n['id'] for n in nodes if n['type']=='cruce']
 for i,a in enumerate(seed['amrs']):a.update(home_zone=cruces[i%len(cruces)],posicion_nodo='CHARGER_1' if i%2==0 else 'CHARGER_2')
 (SEEDS/'seed_espol.json').write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n'); public=ROOT/'nestlink/frontend/public/maps'; public.mkdir(parents=True,exist_ok=True); shutil.copy2(MAPS/'espol_fusion.json',public/'espol_fusion.json')
 sys.path.insert(0,str(APP.parent)); from app.data_maps import build_plant_graph,load_layout_raw
 loaded=load_layout_raw('espol_fusion'); gg,_=build_plant_graph(loaded); assert len(loaded['nodes'])==96 and len(loaded['edges'])>=110 and nx.is_connected(nx.Graph(gg)); assert all(nx.shortest_path(gg,f'WH_MP_{i}','L1_OUT') for i in range(1,4)); print(json.dumps({'nodes':96,'edges':len(edges),'factor':round(factor,4),'mean_espol':round(sum(old)*factor/5,3),'mean_realistic':round(sum(ref)/5,3),'asserts':'PASS'}))
if __name__=='__main__':main()
