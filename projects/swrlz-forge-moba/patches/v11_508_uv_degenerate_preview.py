"""§E v11.508: let the UV preview survive zero-area faces in real model projects."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_508_UV_DEGENERATE_PREVIEW'
PARENT_SHA='1f0385df04afb2d066b9b1d89bb52fc36ee8b66dc516d7ae7b01581ee57a8e42'
def once(source,old,new,label):
    n=source.count(old)
    if n!=1:raise AssertionError(('v11.508 '+label,n,old[:110]))
    return source.replace(old,new,1)
def apply(html):
    assert hashlib.sha256(html.encode('utf8')).hexdigest()==PARENT_SHA,'v11.506 sealed source changed'
    # Generate atlas bounds using valid triangles but retain degenerate faces and
    # vertex order for reversibility. Never delete or reshape mesh geometry.
    html=once(html,
      '  const tris=[],stats=layouts.map((x,id)=>({id,name:x.name,color:x.color,',
      '  let degenerate3D=0,valid3D=0;\n  const tris=[],stats=layouts.map((x,id)=>({id,name:x.name,color:x.color,',
      'degenerate source counters')
    html=once(html,
      "   if(Math.hypot(...normal)<1e-13)throw Error('Source contains a zero-area 3D triangle.');",
      """   if(Math.hypot(...normal)<1e-13)degenerate3D++;
   else valid3D++;""",
      'nonfatal degenerate source faces')
    html=once(html,
      """  for(const s of stats){
   if(!s.count)continue;""",
      """  if(!valid3D)throw Error('Every source triangle has zero area; the mesh requires geometry repair before UV mapping.');
  for(const s of stats){
   if(!s.count)continue;""",
      'all-degenerate guard')
    html=once(html,
      "   preset,brimFraction:cutFraction};",
      "   degenerate3D,valid3D,preset,brimFraction:cutFraction};",
      'persist 3D degeneracy metrics')
    html=once(html,
      """ const risk=m.collapsed?' WARNING: '+m.collapsed+' near-flat UV triangles. Inspect before applying.':'';""",
      """ const risk=(m.degenerate3D||m.collapsed)?
   ' WARNING: '+(m.degenerate3D?m.degenerate3D+' zero-area source triangles preserved. ':'')+
   (m.collapsed?m.collapsed+' collapsed UV triangles. ':'')+
   'The valid surface is previewable, but inspect these areas before applying.':'';""",
      'visible preview topology warnings')
    html=once(html,
      """function se503Prepare(){
 const root=document.getElementById('se503AtlasTool');
 try{
  const p=se503Candidate();se503Preview=p;se503ShowPreview(p);se503Refresh();
  status('Previewed '+p.plan.stats.length+' UV islands; model and texture unchanged. Apply when ready.');
 }catch(e){se503Preview=null;se503Refresh();root.querySelector('#se503AtlasStatus').textContent=e.message;
  status('UV island preview: '+e.message,true);}
}""",
      """function se503Prepare(){
 const root=document.getElementById('se503AtlasTool');
 const hadPreview=!!se503Preview;
 try{
  const p=se503Candidate();se503Preview=p;se503ShowPreview(p);se503Refresh();
  if(!hadPreview)root.querySelector('#se503AtlasCanvas')?.scrollIntoView?.({block:'nearest',behavior:'smooth'});
  status('Preview ready: '+p.plan.stats.length+' UV islands. '+
   (p.plan.degenerate3D?p.plan.degenerate3D+' zero-area source faces flagged. ':'')+
   'Model and texture unchanged. Inspect the preview below before Apply.');
 }catch(e){
  se503Preview=null;
  const canvas=root?.querySelector('#se503AtlasCanvas');if(canvas)canvas.hidden=true;
  se503Refresh();
  if(root)root.querySelector('#se503AtlasStatus').textContent='Preview could not be generated: '+e.message;
  status('UV island preview: '+e.message,true);
 }
}""",
      'mobile preview visibility and error cleanup')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_507_MODEL_TOOL_RAIL_RECOVERY',MARKER),
      ('ENGINE · MAKER v11.507','ENGINE · MAKER v11.508'),
      ('v11.507 · restore modeling toolset rail on mobile',
       'v11.508 · UV preview tolerates degenerate source triangles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.507'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.508'"),
      ('<title>§wyrl§ Engine · Maker v11.507</title>',
       '<title>§wyrl§ Engine · Maker v11.508</title>'),
    ):html=once(html,old,new,'release identity')
    prior=" source.engine='§wyrl§ Engine · Maker v11.507';source.version=11.507;"
    assert html.count(prior)==5,('v11.508 project provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.508';source.version=11.508;")
    key='const SE_RELEASE_NOTES='
    index=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[index:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.507']
    notes['history'].insert(0,{'version':'v11.507','changes':notes.get('changes',[])})
    notes.update(version='v11.508',date='2026-11-18',
      title='UV previews with degenerate model triangles and visible diagnostics',
      changes=[
        'Zero-area 3D source triangles no longer abort UV preview when other usable triangles exist.',
        'Preserve all original mesh positions, faces, and triangle order; count and disclose degenerate source faces and collapsed UV triangles.',
        'Reject entirely zero-area meshes with an explicit geometry-repair explanation instead of a blank preview.',
        'Scroll the UV Editor to the actual preview canvas after a successful initial Preview on mobile, without automatically applying UV data.',
        'Keep Apply, Export and Cancel governed by a valid candidate; existing artwork remains untouched until explicit Apply.',
        'Works on any supported editable indexed §E mesh, subject to native mesh limits and safety checks.'
      ])
    return html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[index+width:]
