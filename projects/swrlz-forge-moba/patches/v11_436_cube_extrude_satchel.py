"""§E v11.436: direct cube Extrude entry and connected satchel cavity tutorial."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_436_CUBE_EXTRUDE_SATCHEL_CAVITY'
def one(src,old,new):
 count=src.count(old)
 if count!=1:raise AssertionError(('v11.436 anchor',count,old[:120]))
 return src.replace(old,new,1)
def apply(html):
 cavity=(ROOT/'runtime/se436_satchel_cavity.js').read_text('utf8')
 handoff=(ROOT/'runtime/se436_vr_cube_extrude.js').read_text('utf8')
 html=one(html,'/* SE416_SATCHEL_ACADEMY_START',cavity+'\n/* SE416_SATCHEL_ACADEMY_START')
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',handoff+'\ninstallPerformanceSettings();se189InstallPerfUI();')
 html=one(html,
  "{title:'Shape a hollow opening',tool:'Topology · Face / Extrude',task:'Turn the solid body into an open-top pouch. Select the top face, inset its boundary, then extrude the inner face downward; inspect inside from above.',why:'An inset creates an inner border. A downward extrusion makes an interior. A dark top surface alone is not a cavity.',hint:'Use the actual topology/face editing controls. If the chosen mesh cannot be inset yet, convert it to editable topology first. Do not mark this complete until you can see interior walls.'},",
  "{title:'Inset and extrude one hollow body',tool:'Manual mesh · Convert / Inset / Extrude',task:'Keep your original practice cube as one body. Convert it to editable mesh, Trigger or tap its top face, apply Inset to create a rim, then Extrude the retained inner face inward. Preview and Apply each step; leave a floor.',why:'A connected inset and inward extrusion make a real open cavity in ONE mesh. No floor box or four wall cubes are needed.',hint:'In VR use Mesh tools → Manual modeling → Make editable. Trigger the top face, choose Inset (about 0.2), Preview and Apply. Then Extrude, press In/out for negative depth (try −0.3), Preview and Apply. In the flat editor use Topology → Manual mesh modeling. Inspect from above.'},")
 html=one(html,
  "   const all=parts(),s=structure(),boxCount=s.boxes.length;",
  "   const all=parts(),s=structure(),boxCount=s.boxes.length,cavity=window.SWYRL_E_SATCHEL_CAVITY_436?.inspect(all)||{ok:false,body:null};")
 html=one(html,
  "if(all.some(p=>p.kind==='box'&&finite3(p.scale)&&p.scale[0]>=1.2&&p.scale[1]>=.85&&p.scale[2]>=.35))",
  "if(all.some(p=>['box','topologyMesh'].includes(p.kind)&&finite3(p.scale)&&p.scale[0]>=1.2&&p.scale[1]>=.85&&p.scale[2]>=.35))")
 html=one(html,
  "if(s.floor&&s.walls.length===4)return {ok:true,message:'You have already progressed beyond the blockout to an open-top body.'};",
  "if(cavity.ok||s.floor&&s.walls.length===4)return {ok:true,message:'You have already progressed to a hollow open-top body.'};")
 html=one(html,
  "return {ok:false,message:'Enlarge the practice cube: width ≥1.2, height ≥0.85, depth ≥0.35, before reshaping it into a floor.'};",
  "return {ok:false,message:'Scale the original practice cube/body to width ≥1.2, height ≥0.85 and depth ≥0.35. Keep this same mesh for its inset cavity.'};")
 html=one(html,
"""   if(index===1){
    if(!s.floor)return {ok:false,message:'First make a thin box floor (height about 0.1). The current model has no detectable floor slab.'};
    if(s.walls.length<4)return {ok:false,message:'Detected '+s.walls.length+'/4 surrounding thin walls. Add the missing left/right/front/back wall boxes; keep the center empty.'};
    if(s.roof)return {ok:null,message:'Four walls detected, but another slab may cover the top. Inspect from above to verify the opening, then mark manually.'};
    return {ok:true,message:'A thin floor and four surrounding wall boxes form an open top. Visually inspect wall joins for gaps.'};
   }""",
"""   if(index===1){
    if(cavity.ok)return {ok:true,message:'Verified connected editable topology: inset rim, inward walls and a recessed inner floor all belong to one mesh.'};
    // Existing learner saves remain valid; no forced migration or loss of prior quest progress.
    if(s.floor&&s.walls.length===4&&!s.roof)return {ok:true,message:'Your earlier multi-box pouch is still valid. New lessons teach a connected inset-and-extrude body instead.'};
    if(cavity.body)return {ok:false,message:'Editable body detected, but no recessed inner floor and connected cavity walls. Select the top face, Inset its border, then Extrude the inner face inward and Apply.'};
    return {ok:false,message:'Select your single practice cube, Make editable, select its top face, Inset, then inward Extrude. No separate floor/wall cubes required.'};
   }""")
 html=one(html,
  "if(!s.floor||s.walls.length<4)return {ok:false,message:'Finish the floor and surrounding walls before checking the flap.'};",
  "if(!cavity.ok&&(!s.floor||s.walls.length<4))return {ok:false,message:'Finish a hollow connected body with Inset then inward Extrude before checking the flap.'};")
 html=one(html,
  "if(s.flap)return {ok:true,message:'Separate thin flap-like mesh detected above the front opening. Check that its free end actually covers the pouch.'};",
  "if(s.flap||all.some(p=>p!==cavity.body&&p.kind==='box'&&finite3(p.scale)&&finite3(p.position)&&p.scale[1]<.27&&p.scale[0]>=.5&&p.position[1]>(cavity.body?.position?.[1]??1.5)+.25))return {ok:true,message:'Separate thin flap-like mesh detected above the opening. Check that it actually covers the pouch.'};")
 html=one(html,
"""   if(index===1){
    add([1.4,.10,.65],[0,1.09,0]);
    add([1.4,.76,.07],[0,1.52,.30]);add([1.4,.76,.07],[0,1.52,-.30]);
    add([.07,.76,.54],[-.66,1.52,0]);add([.07,.76,.54],[.66,1.52,0]);
   }""",
"""   if(index===1){
    window.SWYRL_E_SATCHEL_CAVITY_436?.makeGhost(group);
   }""")
 html=one(html,
  "const page=action==='create-box'?'create':action==='save-local'?'projects':action==='cameras'?'views':'tools';",
  "const page=action==='manual-mesh'?'mesh':action==='create-box'?'create':action==='save-local'?'projects':action==='cameras'?'views':'tools';")
 html=one(html,"   if(vr){\n    if(index===5)", "   if(vr){\n    if(index===5)") if False else html
 html=one(html,
  "   for(const ref of refs){\n    const element=document.querySelector(ref.flat||'');",
  "   if(index===1)window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');\n   for(const ref of refs){\n    const element=document.querySelector(ref.flat||'');")
 html=one(html,
  "   save:{name:'Save Project',flat:'[data-se371-controls] button:first-child',vr:'save-local',vrName:'Save project'}",
  "   save:{name:'Save Project',flat:'[data-se371-controls] button:first-child',vr:'save-local',vrName:'Save project'},\n   convert:{name:'Make editable',flat:'#modelAtelierWorkshopConvert',vr:'manual-mesh',vrName:'Manual modeling'},\n   inset:{name:'Inset',flat:'#modelAtelierWorkshopOperation',vr:'manual-inset',vrName:'Inset'},\n   extrude:{name:'Extrude',flat:'#modelAtelierWorkshopPreview',vr:'manual-extrude',vrName:'Extrude'}")
 html=one(html,
  "   ['scale'],['add','shape','move'],['add','shape','scale'],['add','move','rotate'],",
  "   ['scale'],['convert','inset','extrude'],['add','shape','scale'],['add','move','rotate'],")
 html=one(html,
  "   help.textContent=[1,2,3].includes(index)",
  "   help.textContent=index===1?'Use the SAME cube: Make editable → select its top face → Inset, Preview, Apply → Extrude inward, Preview, Apply. VR: Mesh tools → Manual modeling.'\n    :[2,3].includes(index)")
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_435_MODEL_VR_GRAB_GIZMO',MARKER),
  ('ENGINE · MAKER v11.435','ENGINE · MAKER v11.436'),
  ('v11.435 · VR Grab gizmos and constrained axis grips','v11.436 · working cube extrusion and connected satchel tutorial'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.435'","window.SWRLZ_FORGE_BUILD={version:'v11.436'"),
  ('<title>§wyrl§ Engine · Maker v11.435</title>','<title>§wyrl§ Engine · Maker v11.436</title>')]:html=one(html,before,after)
 old=" source.engine='§wyrl§ Engine · Maker v11.435';source.version=11.435;"
 assert html.count(old)==5,('v11.436 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.436';source.version=11.436;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.435']
 notes['history'].insert(0,{'version':'v11.435','changes':notes.get('changes',[])})
 notes.update(version='v11.436',date='2026-11-12',title='Cube face Extrude and one-mesh Satchel tutorial',changes=[
  'In immersive Model Studio, choosing the existing Extrude tool on a selected cube now opens the native face-editing workshop and safely converts its plain geometry. Trigger selects the face, then Preview and Apply perform a real native Extrude; authored Draw-outline extrusion is unchanged.',
  'Apprentice Satchel step 2 now instructs one cube → editable topology → select top face → Inset rim → inward Extrude to retain a floor. The ghost is one connected native-topology cavity, not five separate wall boxes.',
  'Tutorial inspection recognizes the connected recessed cap and actual rim-to-floor walls. Prior saved five-box tutorial bodies remain accepted; progress, checkpoint history, materials, VR menus, native Undo, mobile modeling and existing Sheep Tag are retained.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
