"""§E v11.8: governed model and functional curve authoring, preserving historic scenes."""
import json
import re
from pathlib import Path

def once(text, old, new):
    n=text.count(old)
    if n!=1:
        raise AssertionError(f"v11.8 anchor {old[:85]!r} count={n}")
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    source=json.loads((root/'scenes/model-atelier-prism-jester-festival-v11-8.swyrl.json').read_text('utf-8'))
    parts=source['project']['modelAtelier']['parts']
    assert source['version']==11.8 and len(parts)==749
    assert len({p['id'] for p in parts})==749
    lofts=[p for p in parts if p['kind']=='loft']
    assert len(lofts)==6 and sum(p.get('surfaceStyle')=='pinata-twisted' for p in lofts)==2
    assert sum(p.get('surfaceStyle')=='anatomy-smooth' for p in lofts)==4
    assert all(not p['name'].endswith('kneecap') for p in parts)
    regex=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    encoded='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(source,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,n=re.subn(regex,lambda _:encoded,html,count=1,flags=re.DOTALL)
    assert n==1,'v11.8 native model insertion missed'
    renderer=(root/'runtime/model_atelier_twist_v11_8.js').read_text('utf-8')
    anchor="  function geometry(part){\n    if(part.kind==='loft'&&part.surfaceStyle==='pinata-stacked')return atelierPinataStack(part);"
    html=once(html,anchor,renderer+"\n"+anchor.replace("  function geometry(part){","  function geometry(part){\n    if(part.kind==='loft'&&part.surfaceStyle==='pinata-twisted')return atelierPinataTwist(part);"))
    editor='''<section id="modelAtelierSculptEditor" hidden aria-label="Sculpt and spline editing">
    <h3>Curve studio · twist, mirror, smooth and fringe</h3>
    <p>Adjust selected native loft; exported JSON preserves all curve controls. This is procedural geometry, not skeletal rigging.</p>
    <div class="atelier-pair"><label>Axial twist (degrees)<input id="modelAtelierSculptTwist" type="number" min="-360" max="360" step="5" value="0"></label>
    <label>Depth/profile scale<input id="modelAtelierSculptDepth" type="number" min="0.5" max="2" step="0.05" value="1"></label></div>
    <div class="atelier-sculpt-actions">
      <button id="modelAtelierSculptApply" type="button">Apply twist & depth</button>
      <button id="modelAtelierSculptSmooth" type="button">Smooth spline</button>
      <button id="modelAtelierSculptMirror" type="button">Mirror as new loft</button>
      <button id="modelAtelierSculptFringe" type="button">Generate paper fringe</button>
    </div>
    <button id="modelAtelierSculptLimb" type="button">Add smooth anatomical loft</button>
    </section>'''
    html=once(html,"'<div id=\"modelAtelierInspectorControls\" hidden>","'"+''.join(editor.splitlines())+'<div id="modelAtelierInspectorControls" hidden>')
    html=once(html,"    const loft=$m('LoftEditor');", """    const sculpt=$m('SculptEditor');
    if(sculpt){sculpt.hidden=!p||p.kind!=='loft';if(p&&p.kind==='loft'){
      $m('SculptTwist').value=String(p.twistDegrees||0);
      $m('SculptDepth').value=String(p.depthScale||1);
    }}
    const loft=$m('LoftEditor');""")
    actions="""    action('SculptApply',()=>{
      const p=partById(selection);if(!p||p.kind!=='loft')return;
      const twist=Number($m('SculptTwist').value),depth=Number($m('SculptDepth').value);
      if(!Number.isFinite(twist)||Math.abs(twist)>360||!Number.isFinite(depth)||depth<.5||depth>2){
        status('Twist must be within ±360 degrees; depth from 0.5 to 2.',true);return;
      }
      checkpoint();p.twistDegrees=twist;p.depthScale=depth;
      if(p.surfaceStyle==='pinata-stacked')p.surfaceStyle='pinata-twisted';
      signalEdited();select(p.id);
    });
    action('SculptSmooth',()=>{
      const p=partById(selection);if(!p||p.kind!=='loft'||p.path.length<3)return;
      const old=p.path;
      checkpoint();p.path=old.map((q,i)=>i===0||i===old.length-1?q.slice():q.map((v,k)=>+(old[i-1][k]*.2+v*.6+old[i+1][k]*.2).toFixed(4)));
      signalEdited();select(p.id);
    });
    action('SculptMirror',()=>{
      const p=partById(selection),data=model();if(!p||p.kind!=='loft'||data.parts.length>=MODEL_ATELIER_LIMIT)return;
      checkpoint();const c=structuredClone(p);
      c.id='atelier-mirror-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);
      c.name=p.name+' · mirrored';c.group='Custom mirrored';
      c.position[0]*=-1;c.path=p.path.map(([x,y,z])=>[-x,y,z]);
      c.twistDegrees=-(p.twistDegrees||0);
      data.parts.push(c);selection=c.id;signalEdited();select(c.id);
    });
    action('SculptFringe',()=>{
      const p=partById(selection),data=model();if(!p||p.kind!=='loft')return;
      const steps=14;if(data.parts.length+steps>MODEL_ATELIER_LIMIT){status('Not enough capacity for fringe.',true);return;}
      const curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal');
      checkpoint();
      for(let i=0;i<steps;i++){
        const t=(i+.5)/steps,q=curve.getPoint(t);
        const radius=p.radii[Math.min(p.radii.length-1,Math.round(t*(p.radii.length-1)))];
        data.parts.push({id:'atelier-fringe-'+Date.now().toString(36)+'-'+i+'-'+Math.random().toString(36).slice(2,5),
          name:'Generated paper fringe '+(i+1),kind:'box',group:p.group||'Fringe',
          position:[q.x,q.y,q.z+radius*.95],rotation:[0,0,Math.sin(t*7)*.17],
          scale:[Math.max(.07,radius*.74),.14,.045],
          color:i%2?p.color:'#f0dfb3',material:'matte'});
      }
      signalEdited();
    });
    action('SculptLimb',()=>{
      const data=model();if(!data||data.parts.length>=MODEL_ATELIER_LIMIT)return;
      checkpoint();const id='atelier-limb-'+Date.now().toString(36);
      data.parts.push({id,name:'Smooth anatomical limb (editable curve)',kind:'loft',group:'Custom anatomy',
        position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color:'#f2c3a8',material:'silk',surfaceStyle:'anatomy-smooth',
        path:[[0,1.9,0],[0,1.55,0],[0,1.2,.02],[0,.82,.04]],radii:[.17,.14,.135,.09],segments:48,radialSegments:16});
      selection=id;signalEdited();select(id);
    });
"""
    html=once(html,"    action('ApplyLoft',()=>{",actions+"    action('ApplyLoft',()=>{")
    html=once(html,'V11_7_STACKED_PINATA_SCULPT','V11_8_TWISTED_SCULPT_STUDIO')
    html=once(html,'v11.7 · layered piñata sculpture','v11.8 · twisted sculpt studio')
    html=html.replace('Maker v11.7','Maker v11.8').replace('MAKER v11.7','MAKER v11.8')
    html=html.replace("version:'v11.7'","version:'v11.8'").replace('version:11.7','version:11.8')
    return html
