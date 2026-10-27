#!/usr/bin/env python3
import json,math,shutil,sys
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'agv-espol/data/red_agv_grafo_actualizado.json'; APP=ROOT/'nestlink/backend/app'; MAPS=APP/'data/maps'; SEEDS=APP/'data/seeds'
ROLE_ASSIGNMENT={'L1_OUT':'ControlPoint24','L2_OUT':'ControlPoint25','E1_IN':'ControlPoint26','E2_IN':'ControlPoint18','WH_MP_1':'ControlPoint7','WH_MP_2':'X_Ruta1_5','WH_MP_3':'X_Ruta1_8','WH_MP_4':'X_Ruta16_6','WH_MP_5':'X_Ruta13_2','WH_PT_1':'X_Ruta1_3','WH_PT_2':'ControlPoint9','WH_PT_3':'X_Ruta7_9','CHARGER_1':'ControlPoint28','CHARGER_2':'ControlPoint31','BUFFER_1':'X_Ruta48_1','BUFFER_2':'X_Ruta45_1'}
FRIENDLY={'L1_OUT':'L1 Nescafé','L2_OUT':'L2 Maggi','E1_IN':'E1 Savoy','E2_IN':'E2 Lechera','WH_MP_1':'MP Savoy','WH_MP_2':'MP Lechera','WH_MP_3':'MP Nescafé','WH_MP_4':'MP Maggi','WH_MP_5':'MP Nestum','WH_PT_1':'PT 1','WH_PT_2':'PT 2','WH_PT_3':'PT 3','CHARGER_1':'Carga 1','CHARGER_2':'Carga 2','BUFFER_1':'Buffer 1','BUFFER_2':'Buffer 2'}
def main():
 raw=json.loads(SRC.read_text()); src={n['id']:n for n in raw['nodos']}; assert len(src)==96 and len(raw['aristas'])==110; renamed={v:k for k,v in ROLE_ASSIGNMENT.items()}
 xs=[n['x'] for n in src.values()]; ys=[n['y'] for n in src.values()]; x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); sx,sy=900/(x1-x0),500/(y1-y0)
 def pos(n): return [round(50+(n['x']-x0)*sx,2),round(50+(y1-n['y'])*sy,2)]
 nodes=[]
 for n in raw['nodos']:
  nid=renamed.get(n['id'],n['id']); typ='linea' if nid.startswith('L') else 'empacadora' if nid.startswith('E') else 'almacen' if nid.startswith('WH_') else 'carga' if nid.startswith('CHARGER') else 'buffer' if nid.startswith('BUFFER') else 'cruce'; p=pos(n); assert 40<=p[0]<=960 and 40<=p[1]<=560; nodes.append({'id':nid,'x':p[0],'y':p[1],'type':typ,'label':FRIENDLY.get(nid,nid)})
 edges=[]
 for e in raw['aristas']:
  u,v=renamed.get(e['origen'],e['origen']),renamed.get(e['destino'],e['destino']); z={'from':u,'to':v,'length':float(e['distancia_m']),'max_speed':1.5,'direction':'bi' if e.get('bidireccional',True) else 'one-way','blocked':False}; edges.append(z); edges.append({**z,'from':v,'to':u}) if e.get('bidireccional',True) else None
 G=nx.Graph(); G.add_nodes_from(n['id'] for n in nodes); G.add_edges_from((e['from'],e['to'],{'length':e['length']}) for e in edges); assert nx.is_connected(G)
 realistic=json.loads((MAPS/'realistic.json').read_text()); UG=nx.Graph(); UG.add_edges_from((e['from'],e['to'],{'length':e['length']}) for e in realistic['edges']); RG=nx.DiGraph(UG); DG=nx.DiGraph(); DG.add_edges_from((e['from'],e['to'],{'length':e['length']}) for e in edges); pairs=[(f'WH_MP_{i}',x) for i in range(1,6) for x in ('L1_OUT','L2_OUT','L1_OUT','L2_OUT')]; assert len(pairs)==20; old=[nx.shortest_path_length(DG,a,b,weight='length') for a,b in pairs]; ref=[nx.shortest_path_length(RG,a,b,weight='length') for a,b in pairs]; factor=sum(ref)/max(sum(old),1e-9)
 for e in edges:e['length']=round(e['length']*factor,4)
 out={'canvas':{'w':1000,'h':600,'title':'Planta ESPOL · Fusión — NestHive'},'nodes':nodes,'edges':edges,'zones':[{'id':'ZONE_MP','label':'MP · Almacén','x':60,'y':60,'w':320,'h':220,'color':'#EAD3A9'},{'id':'ZONE_LINES','label':'Líneas','x':360,'y':60,'w':300,'h':220,'color':'#FBC866'},{'id':'ZONE_PT','label':'Producto terminado','x':660,'y':60,'w':280,'h':220,'color':'#FBFBF8'},{'id':'ZONE_CHARGE','label':'Carga','x':660,'y':340,'w':280,'h':180,'color':'#EAD3A9'}],'walls':[],'lines':[{'id':x,'buffer_nodes':['BUFFER_1','BUFFER_2']} for x in ('L1_OUT','L2_OUT','E1_IN','E2_IN')],'pedestrians':[]}; MAPS.mkdir(parents=True,exist_ok=True); (MAPS/'espol_fusion.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 seed=json.loads((SEEDS/'seed_realistic.json').read_text()); cruces=[n['id'] for n in nodes if n['type']=='cruce']
 for i,a in enumerate(seed['amrs']):a.update(home_zone=cruces[i%len(cruces)],posicion_nodo='CHARGER_1' if i%2==0 else 'CHARGER_2')
 (SEEDS/'seed_espol.json').write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n'); public=ROOT/'nestlink/frontend/public/maps'; public.mkdir(parents=True,exist_ok=True); shutil.copy2(MAPS/'espol_fusion.json',public/'espol_fusion.json')
 sys.path.insert(0,str(APP.parent)); from app.data_maps import build_plant_graph,load_layout_raw
 loaded=load_layout_raw('espol_fusion'); gg,_=build_plant_graph(loaded); assert len(loaded['nodes'])==96 and len(loaded['edges'])>=110 and nx.is_connected(nx.Graph(gg)); assert all(nx.shortest_path(gg,f'WH_MP_{i}','L1_OUT') for i in range(1,4)); mean_new=sum(old)*factor/20; mean_ref=sum(ref)/20; assert abs(mean_new-mean_ref)<=.2*mean_ref; print(json.dumps({'nodes':96,'edges':len(edges),'factor':round(factor,4),'mean_espol':round(mean_new,3),'mean_realistic':round(mean_ref,3),'asserts':'PASS'}))
if __name__=='__main__':main()
