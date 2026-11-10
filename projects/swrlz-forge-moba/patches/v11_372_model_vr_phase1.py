"""§E v11.372: VR manipulation, UI and authenticated project saving."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_372_MODEL_VR_PHASE1'
def one(s,old,new,label):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.372 anchor',label,count,old[:110]))
    return s.replace(old,new,1)
def section(s,start,end,replacement,label):
    a=s.find(start)
    if a<0 or s.count(start)!=1:raise AssertionError(('v11.372 section start',label,s.count(start)))
    b=s.find(end,a+len(start))
    if b<0:raise AssertionError(('v11.372 section end',label))
    return s[:a]+replacement+s[b:]
def apply(html):
    helper=(ROOT/'runtime/model_vr_phase1_v11_372.js').read_text('utf8')
    assert 'SE372_MODEL_VR_PHASE1_START' in helper and 'function se372Frame(s)' in helper
    html=section(html,'function se340PlacePalette(viewer){','function se340Recenter(',
        helper+"\nfunction se340PlacePalette(viewer){se372MenuPlace(viewer);}\n",
        'independent world workspace menu')
    html=one(html,
        "const side=record.input?.handedness,pose=se340GripPose(record);if(!pose)return false;",
        "const side=record.input?.handedness,pose=se340GripPose(record);if(!pose)return false;\n  if(se372MenuDragStart(record,pose))return true;",
        'grip menu before view/model')
    html=one(html,
        "const result=tools.beginGroup(undefined,s.mode);if(result?.ok===false)return se350Result(result,'',record);",
        "const axis=se372GizmoHit(record);\n  const result=tools.beginGroup(undefined,s.mode);if(result?.ok===false)return se350Result(result,'',record);",
        'axis handle hit')
    html=one(html,
        "s.gesture={kind:'group',record,id:chosen.primaryId||chosen.ids[0],mode:s.mode,hand:pose,rootInverse:root.matrixWorld.clone().invert(),rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion())};",
        "s.gesture={kind:'group',record,id:chosen.primaryId||chosen.ids[0],mode:s.mode,hand:pose,rootInverse:root.matrixWorld.clone().invert(),rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion()),axis};se372GuideStart(s.gesture);",
        'grip-only controller feedback')
    html=one(html,
        "if(!g||!['view','group','two-hand','extrude'].includes(g.kind))return false;",
        "if(!g||!['view','menu','group','two-hand','extrude'].includes(g.kind))return false;",
        'menu drag gesture completion')
    # Both group-grip and trigger drawing commit with this expression;
    # patch the earlier group-grip routine only.
    needle="se340UpdateGesture();if(s.gesture!==g)return false;s.gesture=null;"
    if html.count(needle)!=2:raise AssertionError(('finish functions changed',html.count(needle)))
    html=html.replace(needle,needle+"se372GuideStop(g);",1)
    html=one(html,
        "if(g.kind==='view'){se340Notice('Workbench placed · model data unchanged.');",
        "if(g.kind==='menu'){se372MenuDragFinish(g,true);se340Notice('VR menu placed.');se340Publish();return true;}\n  if(g.kind==='view'){se340Notice('Workbench placed · model data unchanged.');",
        'commit spatial menu placement')
    html=one(html,
        "if(!g)return false;\n s.gesture=null;",
        "if(!g)return false;\n if(g.kind==='menu')se372MenuDragFinish(g,false);se372GuideStop(g);s.se372Sweep=null;\n s.gesture=null;",
        'cancel preview and restore menu')
    html=one(html,
        "const pose=se340GripPose(g.record);if(!pose)return;\n const gain=",
        "const pose=se340GripPose(g.record);if(!pose)return;\n if(g.kind==='menu'){se372MenuDragUpdate(g,pose);return;}\n const gain=",
        'apply grip menu delta')
    html=one(html,
        "const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:rotation.toArray(),scale});",
        "se372Constrain(g,translation,rotation);se372GuideUpdate(g,translation,rotation,scale);\n  const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:rotation.toArray(),scale});",
        'controller guide reflects actual edit delta')
    html=one(html,
        "if(['select','multiselect'].includes(event.action)&&record)se340Trigger(record,event.action==='multiselect');",
        """if(['select','multiselect'].includes(event.action)&&record){
   const before=event.action==='multiselect'?[...se350Tools().selection().ids]:null;
   se340Trigger(record,event.action==='multiselect');
   if(before)se372SweepStart(record,before);
  }""",
        'left trigger selection sweep')
    html=one(html,
        "s.yaw+=orbit.x*dt*1.35*gain*turn;s.pitch=THREE.MathUtils.clamp(s.pitch-orbit.y*dt*1.05*gain*turn,-1.54,1.54);",
        """const magnitude=Math.min(1,Math.hypot(orbit.x,orbit.y));
   const smooth=Math.pow(magnitude,1.45)/Math.max(magnitude,.0001);
   s.yaw-=orbit.x*smooth*dt*1.35*gain*turn;
   s.pitch=THREE.MathUtils.clamp(s.pitch-orbit.y*smooth*dt*1.05*gain*turn,-1.54,1.54);""",
        'correct inverse horizontal orbit and add analog response')
    html=one(html,
        "se360AdvanceMenu(dt);se362Frame(s);renderer.render(s.scene,s.camera);",
        "se372Frame(s);se360AdvanceMenu(dt);se362Frame(s);renderer.render(s.scene,s.camera);",
        'one frame loop')
    html=one(html,
        "for(const r of s.controllers){\n  se362ControllerDisconnected(r);",
        "se372Dispose();\n for(const r of s.controllers){\n  se362ControllerDisconnected(r);",
        'dispose phase 1 visual resources')
    html=one(html,
        "s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;",
        "s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;s.se372MenuBase=null;s.se372Gizmo=null;s.se372Sweep=null;s.se372ProjectBusy=false;",
        'reset phase 1 state on XR entry')
    html=one(html,
        "if(action==='exit'){void se340ModelXRExit();return true;}",
        """if(action==='exit'){void se340ModelXRExit();return true;}
  if(['save-account','save-local','clone-project'].includes(action)){void se372ProjectAction(action);return true;}
  if(action==='menu-reset'){if(s.gesture)se340CancelGesture();se372ResetMenu();se340SyncUI();return true;}
  if(action==='menu-hide'){s.paletteVisible=false;s.ui.root.visible=false;se340Publish();return true;}""",
        'VR project and menu actions')
    # Reuse existing 12 slots, keep all native navigation and accessible tools.
    start="  studio:[\n   ['mesh','Mesh tools']"
    end="  sculpt:[\n"
    studio="""  studio:[
   ['mesh','Mesh tools'],['sculpt','Sculpt'],['draw','Draw mesh'],
   ['views','Display'],['aim','Pointer aim'],['help','Guide'],
   ['save-local','Save project'],['save-account','Save to account'],['clone-project','Clone project'],
   ['menu-reset','Reset menu'],['menu-hide','Hide menu'],['exit','Exit VR']
  ],
"""
    html=section(html,start,end,studio,'studio menu slots')
    html=one(html,
        "recenter:'Reset the workbench',tools:'Your editing toolkit',",
        "recenter:'Reset the workbench',tools:'Your editing toolkit','save-local':'On-device project save','save-account':'Sync cloud model and textures','clone-project':'Independent project copy','menu-reset':'Restore menu position','menu-hide':'X button brings it back',",
        'menu tool descriptions')
    html=one(html,
        "exit:'exit',precision:'precision',snap:'snap'}[id]||id;",
        "exit:'exit',precision:'precision',snap:'snap','save-local':'cube','save-account':'display','clone-project':'cube','menu-reset':'focus','menu-hide':'eye'}[id]||id;",
        'VR project menu icons')
    # Existing §E Save Project already attempts account sync, but expose an
    # explicit account-only command in the main studio toolbar too.
    html=one(html,
        "for(const [label,mode] of [['Save Project','save'],['Clone Project','clone']]){",
        "for(const [label,mode] of [['Save Project','save'],['Save to Account','account'],['Clone Project','clone']]){",
        'desktop project account action')
    html=one(html,
        "let name;\n if(mode==='clone'){",
        """if(mode==='account'&&(!ready||!se176AccountConnected)){
  if(!ready&&frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
  se371Display('Account not connected. Sign in through §E before Save to Account.',true);return;
 }
 let name;
 if(mode==='clone'){""",
        'explicit desktop cloud prerequisite')
    html=one(html,
        "  se371Display((mode==='clone'?'Cloned ':'Saved ')+se371ProjectName()+",
        "  se371Display((mode==='clone'?'Cloned ':mode==='account'?(synced?'Saved to account: ':'Account save not confirmed: '):'Saved ')+se371ProjectName()+",
        'clarify account save status')
    for old,new,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_371_SAFE_SAVE_CLONE_PROJECTS',MARKER,'marker'),
      ('ENGINE · MAKER v11.371','ENGINE · MAKER v11.372','header'),
      ('v11.371 · safe Save Project and Clone Project','v11.372 · VR editing, reversible sweep and account save','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.371'","window.SWRLZ_FORGE_BUILD={version:'v11.372'",'build'),
      ('<title>§wyrl§ Engine · Maker v11.371</title>','<title>§wyrl§ Engine · Maker v11.372</title>','title')
    ]:html=one(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.371';source.version=11.371;"
    n=html.count(old)
    if n not in (3,5,6):raise AssertionError(('v11.372 native provenance count',n))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.372';source.version=11.372;")
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.371' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.371','changes':notes.get('changes',[])})
    notes.update(version='v11.372',date='2026-11-09',
      title='Quest 2 Model Studio phase 1: intuitive manipulation and account save',
      changes=[
       'Left-trigger press retains tap select; holding and sweeping collects additional model meshes up to the existing 32 limit. Retracing the same sweep removes only meshes added in that hold, without touching earlier selections.',
       'Move, Rotate and Scale now display a selected-object gizmo; grip presents a temporary pointer-side transform guide with baseline and applied movement/rotation.',
       'VR tool menu stays independent of model geometry and real head movement, follows virtual orbit only, supports grip drag, hidden/restored state, persistent placement and reset.',
       'Right-stick horizontal orbit follows left/right input with analog progressive precision while existing vertical camera orbit stays intact.',
       '§E displays Save to Account directly in the native studio toolbar and immersive menu. It reuses authenticated account RPC and revision safeguards without requiring the chat panel.',
       'VR Save Project and Clone Project retain native independent project IDs and saved model, UV and material content. Quest Touch controller models and labels are preserved.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
