"""§E v11.506: fix UV button ownership and atlas prerequisite deadlocks."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_506_UV_BUTTON_OWNERSHIP'
PREVIOUS_SHA256='f79e880e7c6c780fa06dd8ac6d969763faa17e656c41e5508950a832e970c43e'
def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.506 '+label, n,old[:120]))
    return html.replace(old,new,1)
def apply(html):
    assert hashlib.sha256(html.encode('utf8')).hexdigest()==PREVIOUS_SHA256,'v11.505 source chain changed'
    # Old v11.336 update scanned all descendants. That includes the much newer
    # v11.356 Preview controls and v11.503 Atlas controls, making them dead.
    # Only the five native v11.336 toolbar buttons belong to that updater.
    html=once(html,
       "for (const button of root.querySelectorAll('button'))\n    button.disabled = !target || (button.id === 'se336UVRemove' && !target.part.uvPaintPNG);",
       "for (const button of root.querySelectorAll('.se336-uv-actions > button'))\n    button.disabled = !target || (button.id === 'se336UVRemove' && !target.part.uvPaintPNG);",
       'legacy UV toolbar ownership')
    # Candidate atlas is generated directly from serialized topologyMesh. It
    # does not need a rendered Three.js mesh instance to be present.
    html=once(html,
       'const se503Target=()=>se336SelectedMesh();',
       """const se503Target=()=>{
 const rendered=se336SelectedMesh();
 if(rendered)return rendered;
 const part=partById(selection);
 return part?{part,mesh:null}:null;
};""",
       'UV atlas serialized part fallback')
    # A disabled primary action cannot explain which prerequisite is missing.
    # Keep it clickable and let the shared gate offer conversion, selection, or
    # a clear blocking reason. Apply/Export/Cancel remain independently gated.
    html=once(html,
       """  if(button){
   const plan=inspect();
   if(['native','textured-copy','reuse','auto-select'].includes(plan.kind)){""",
       """  if(button){
   const plan=inspect();
   button.disabled=false;
   if(['native','textured-copy','reuse','auto-select'].includes(plan.kind)){""",
       'preview primary action enable')
    html=once(html,
       """   }else {
    button.textContent='Preview UV atlas';
    if(plan.kind==='blocked'&&!se503Preview){
     button.disabled=true;
     root.querySelector('#se503AtlasStatus').textContent=plan.reason;
    }
   }""",
       """   }else {
    button.textContent='Preview UV atlas';
    button.title=plan.kind==='blocked'?(plan.reason||'Select a supported mesh'):'Preview the current editable mesh UV islands.';
    if(plan.kind==='blocked'&&!se503Preview)
     root.querySelector('#se503AtlasStatus').textContent=(plan.reason||'Unavailable prerequisite')+
      ' Tap Preview UV atlas for details. Other atlas actions become available after preview.';
   }""",
       'no silent blocked primary action')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_505_ACTION_PREREQUISITES',MARKER),
      ('ENGINE · MAKER v11.505','ENGINE · MAKER v11.506'),
      ('v11.505 · confirmed editable prerequisites with automatic continuation',
       'v11.506 · UV atlas preview button and editable prerequisite repair'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.505'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.506'"),
      ('<title>§wyrl§ Engine · Maker v11.505</title>',
       '<title>§wyrl§ Engine · Maker v11.506</title>'),
    ):html=once(html,old,new,'release identity')
    prior=" source.engine='§wyrl§ Engine · Maker v11.505';source.version=11.505;"
    assert html.count(prior)==5,('v11.506 project provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.506';source.version=11.506;")
    key='const SE_RELEASE_NOTES='
    index=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[index:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.505']
    notes['history'].insert(0,{'version':'v11.505','changes':notes.get('changes',[])})
    notes.update(version='v11.506',date='2026-11-18',
      title='UV Editor button ownership and actionable atlas preview',
      changes=[
        'Restrict legacy UV toolbar disabled-state updates to its own five native buttons, not nested UV Preview or Atlas controls.',
        'Allow the UV island preview to use the selected saved topology mesh even when its 3D render instance is temporarily missing.',
        'Keep the primary Preview UV atlas action clickable; safely offer conversion and continuation or explain a blocked prerequisite.',
        'Leave Apply, Cancel and Export guide disabled until a valid atlas preview exists; never apply geometry or texture changes without confirmation.',
        'Preserve prior UV tools and texture workflow, project revision history, rigging and animation.'
      ])
    return html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[index+width:]
