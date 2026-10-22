"""Expand the native world to 256 m and bring sheep back to the sanctuary."""
from pathlib import Path
import copy,json,math,random
root=Path(__file__).resolve().parents[1]
scene=json.loads((root/'scenes/sheep-tag-wildwood-v11-79.swyrl.json').read_text())
scene['engine']='§wyrl§ Engine · Maker v11.80'
scene['project']['name']='Sheep Tag · Vast Moonbell Wildwood'
scene['project']['sheepTag']['bounds']=128
scene['project']['environmentSettings'].update(fogNear=260,fogFar=600)
sheep=0
for a in scene['scene']['actors']:
    kind=a['type'];x,_,z=a['position']
    if kind=='st-sheep':
        angle=(sheep+.5)*math.pi/4;a['position']=[round(math.sin(angle)*9.5,4),0,round(math.cos(angle)*9.5,4)];sheep+=1
    elif kind not in ['st-pen','st-wolf'] and not a['name'].startswith('Sanctuary waystone'):
        a['position']=[x*2,0,z*2]
    if kind=='st-meadow':a['name']='Vast Moonbell Wildwood · 256 m buildable pasture';a['scale']=[3.2,1,3.2]
    elif kind in ['st-pond','st-zone']:a['scale'][0]*=2;a['scale'][2]*=2
    elif kind=='st-road':a['scale'][2]*=2
    elif kind=='st-rock' and 'Escape passage' in a['name']:
        # Expand the distance to the passage, retaining its actual 1 m gap.
        sign=int(a['name'].split('stone ')[1]);a['position'][0]-=sign*2.3
rng=random.Random(1180);trees=[a for a in scene['scene']['actors'] if a['type']=='st-tree']
# Wider groves, preserving native sizes and every existing navigable road.
for i in range(48):
    source=trees[i%len(trees)];a=copy.deepcopy(source)
    x,_,z=source['position'];x+=rng.choice([-1,1])*4.5;z+=rng.choice([-1,1])*3
    if abs(x)>124 or abs(z)>124 or min(abs(x),abs(z))<10:continue
    # Keep all diagonal spokes and their surrounding travel lanes clear.
    if abs(abs(x)-abs(z))<8:continue
    a['id']='vast-grove-'+str(i);a['position']=[round(x,3),0,round(z,3)];a['name']=a['name'].split(' · ')[0]+' · outer grove';scene['scene']['actors'].append(a)
path=root/'scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json';path.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
print('VAST_SCENE',len(scene['scene']['actors']),'actors',sheep,'central sheep',scene['project']['sheepTag']['bounds']*2,'metres')
