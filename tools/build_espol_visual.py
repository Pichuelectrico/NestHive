#!/usr/bin/env python3
"""Build New_map visual overlay in the 1000x600 graph coordinate space."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/'nestlink/backend/app/data/maps/espol_fusion.json'
SRC=ROOT/'nestlink/backend/app/data/new_map_markers.json'
OUTS=[ROOT/'nestlink/backend/app/data/maps/espol_fusion_visual.json',ROOT/'nestlink/frontend/public/maps/espol_fusion_visual.json']
X=[[0,0],[347,50],[436,95],[611,189],[853,322],[893,414],[1100,605],[1280,869],[1452,950]]
Y=[[0,0],[258,120],[395,302],[483,344],[600,410],[795,550],[1100,600]]
def warp(v, anchors):
    for (a,b),(c,d) in zip(anchors,anchors[1:]):
        if v<=c: return round(b+(v-a)*(d-b)/(c-a),2)
    a,b=anchors[-2]; c,d=anchors[-1]; return round(b+(v-a)*(d-b)/(c-a),2)
def main():
    layout=json.loads(MAP.read_text()); ids={n['id'] for n in layout['nodes']}; marks=json.loads(SRC.read_text())
    markers=[]
    roles={'morado':('paletizaje','#b96bd4'),'verde':('carga','#6dcc62'),'amarillo':('insumos','#ffc45a'),'cafe':('fuente_insumos','#7a3e0b'),'naranja':('recoleccion','#ff6b21')}
    for name,(role,color) in roles.items():
        for i,p in enumerate(marks.get(name,{}).get('puntos',[]),1):
            candidates={'morado':[f'PALET_{i:02d}'],'naranja':[f'RECO_R{i}'],'amarillo':[f'INSUMO_P{i}'],'cafe':['FUENTE_INSUMOS'],'verde':['CHARGER_1','CHARGER_2']}.get(name,[])
            for node_id in candidates:
                if node_id in ids:
                    n=next(n for n in layout['nodes'] if n['id']==node_id); markers.append({'node_id':node_id,'role':role,'color':color,'r':6,'label':None})
                    break
    labels=[{'text':t,'x':x,'y':y,'size':12} for t,x,y in [('CARGADOR',95,295),('CARGADOR',189,295),('Punto de Entrega',430,350),('Transporte afuera',50,300),('Insumos',500,540),('P1',890,60),('P2',920,300),('P3',930,550),('R1',250,120),('R2',800,300),('R3',800,500)]]
    zones=[{'id':'Z_PALET','role':'paletizaje','rect':[50,275,300,100],'color':'#b96bd4','label':'Paletizaje'},{'id':'Z_CHARGE','role':'carga','rect':[70,270,160,50],'color':'#6dcc62','label':'Carga'}]
    arrows=[{'from':[50,330],'to':[0,315],'bidir':True},{'from':[50,360],'to':[0,345],'bidir':True}]
    out={'version':1,'source':'New_map.png','canvas':{'w':1000,'h':600},'warp':{'x':X,'y':Y},'walls':[{'points':[[0,0],[1000,0],[1000,600],[0,600]],'dash':[6,4]}],'corridors':[{'points':[[50,y],[950,y]],'width':10,'oneway':True} for y in (120,300,344,410,550)],'zones':zones,'markers':markers,'labels':labels,'red_arrows':arrows,'transport':{'x':35,'y':330,'r':28,'label':'Transporte afuera'}}
    for path in OUTS: path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'markers':len(markers),'corridors':len(out['corridors']),'outputs':[str(p) for p in OUTS]}))
if __name__=='__main__': main()
