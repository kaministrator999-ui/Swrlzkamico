"""§E v11.546: anatomy-first UV robot and full 4K UV export controls.

Preserves prior historical starter assets and user project copies. Applies only
after verified standalone asset generation; no UV changes to loaded saves.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_545_HUMANOID_UV_ANATOMY_VIEW'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_546_ANATOMY_ROBOT_UV_4K'
def once(html,a,b,name):
    count=html.count(a)
    if count!=1:raise AssertionError(('se546',name,count,a[:100]))
    return html.replace(a,b,1)
def apply(html):
    starter=(ROOT/'runtime/humanoid_anatomical_robot_v11_546.js').read_text('utf8')
    assert 'SE546_ANATOMY_ROBOT_STARTER_END' in starter
    assert (ROOT/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json').exists()
    assert (ROOT/'assets/models/futuristic-humanoid-v11-546-uv-guide-4096.png').exists()
    # Reuse the 13,932-triangle anatomy view, only change its export controls.
    # Avoid introducing a parallel UV renderer with guessed/mismatched islands.
    start=html.index('function se545Export(){')
    end=html.index('function se545Install(){',start)
    old=html[start:end]
    assert 'se336SaveCanvas' in old
    export_js="""async function se546SavePNG(canvas,name){
 const blob=await new Promise((resolve,reject)=>canvas.toBlob(
   b=>b?resolve(b):reject(Error('PNG encoding failed')),'image/png'));
 const url=URL.createObjectURL(blob);
 const link=document.createElement('a');
 link.href=url;link.download=name.replace(/[^a-z0-9_.-]+/gi,'-').slice(0,110);
 document.body.append(link);link.click();link.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function se546ChosenSize(){
 const n=Number(document.getElementById('se545ExportSize')?.value);
 if(n!==2048&&n!==4096)throw Error('Choose 2048 or 4096 PNG export.');
 return n;
}
async function se545Export(){
 const part=se545Target();if(!part)return;
 try{
  const data=se545Faces(part),canvas=document.createElement('canvas');
  const size=se546ChosenSize();canvas.width=canvas.height=size;
  se545Draw(canvas,data,se545Active,true);
  if(se545Target()!==part)throw Error('Model selection changed during UV export.');
  await se546SavePNG(canvas,part.name+'-TRUE-UV-ANATOMY-'+size+'.png');
  status('Exported '+size+'px native anatomical UV reference from current model coordinates. Not a painted texture.');
 }catch(e){status('UV anatomy export: '+e.message,true);}
}
async function se546ExportUVGuide(){
 const target=se336SelectedMesh(),part=se545Target();
 if(!target||!part||target.part!==part)return;
 try{
  const size=se546ChosenSize(),canvas=document.createElement('canvas');
  canvas.width=canvas.height=size;
  se336UVLayout(target.mesh,canvas);
  if(se545Target()!==part)throw Error('Model selection changed during UV guide export.');
  await se546SavePNG(canvas,part.name+'-CURRENT-UV-WIREFRAME-'+size+'.png');
  status('Exported '+size+'px actual UV wireframe. Paint under this guide and remove the wireframe layer before importing artwork.');
 }catch(e){status('UV wireframe export: '+e.message,true);}
}
"""
    html=html[:start]+export_js+html[end:]
    html=once(html,
      "'<button type=\"button\" id=\"se545AnatomyExport\">Export anatomy guide · 2048px</button>'+",
      "'<label>Export PNG size <select id=\"se545ExportSize\"><option value=\"4096\" selected>4096 px · 4K</option><option value=\"2048\">2048 px</option></select></label> '+"
      "'<button type=\"button\" id=\"se545AnatomyExport\">Export anatomy guide</button> '+"
      "'<button type=\"button\" id=\"se546CurrentUVGuide\">Export current UV wireframe</button>'+",
      'anatomy export controls')
    html=once(html,
       "root.querySelector('#se545AnatomyExport').addEventListener('click',se545Export);",
       "root.querySelector('#se545AnatomyExport').addEventListener('click',se545Export);\\n root.querySelector('#se546CurrentUVGuide').addEventListener('click',se546ExportUVGuide);".replace('\\\\n','\\n'),
       '4k guide event')
    html=once(html,
       'window.SWRLZ_FORGE_BUILD=',starter+'\\nwindow.SWRLZ_FORGE_BUILD='.replace('\\\\n','\\n'),
       'starter loader')
    html=once(html,'<strong>Futuristic Humanoid · Surface-Mapped Robot</strong>',
       '<strong>Futuristic Humanoid · Anatomical Robot</strong>','starter card')
    html=once(html,
       '<span class="template-tag">STARTER MODEL · REAL 3D-TO-UV ROBOT PAINT</span>',
       '<span class="template-tag">STARTER MODEL · ANATOMICAL UV · NEW ROBOT SKIN · 4K GUIDE</span>',
       'starter category')
    html=once(html,
      "'robotic-humanoid-mannequin':['Futuristic Humanoid · Surface-Mapped Robot','model-atelier','model-atelier']",
      "'robotic-humanoid-mannequin':['Futuristic Humanoid · Anatomical Robot','model-atelier','model-atelier']",
      'VR model library')
    for a,b in (
      (OLD,MARKER),
      ('ENGINE · MAKER v11.545','ENGINE · MAKER v11.546'),
      ('v11.545 · inspect real UV anatomy without disturbing the texture',
       'v11.546 · anatomy-mapped UV robot skin and true 4K export'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.545'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.546'"),
      ('<title>§wyrl§ Engine · Maker v11.545</title>',
       '<title>§wyrl§ Engine · Maker v11.546</title>')
    ):
      html=once(html,a,b,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.545';source.version=11.545;"
    assert html.count(old)==5,('source provenance',html.count(old))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.546';source.version=11.546;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes['history'] if x.get('version')!='v11.545']
    notes['history'].insert(0,{'version':'v11.545','changes':notes['changes']})
    notes.update(
      version='v11.546',date='2026-11-22',
      title='Anatomy-mapped humanoid with new robot material and full 4K UV export',
      changes=[
        'Introduced an anatomy-oriented xatlas unwrapped humanoid starter. True UV charts grouped by head, torso, arms and legs, subject to the native mesh budget; preserves the original connected 3D surface and 13,932 triangles.',
        'Authored a completely new white ceramic, graphite, cyan sensor/actuator robot skin directly from 3D locations and normals. No texture from the old atlas is reused on changed UV coordinates.',
        'Published exact 4096 by 4096 wireframe and color-coded anatomical UV reference PNGs matching the new scene, plus 1024px native embedded robot paint and inspected front/back/side projections.',
        'The native humanoid UV inspector now exports either 4096px (default) or 2048px, for both actual UV wireframe and body region overlays. Heatmap diagnostic already supports 4K.',
        'Historical starter assets and user projects are preserved. Only new starter instances use the new UV/skin pairing. No geometry sculpting or rigging implied.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[at+size:]
