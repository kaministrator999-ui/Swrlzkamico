"""§E v11.527 — contextual immersive Draw menu; one native face/extrude workflow.

Keep Draw Outline, Make Face, Thicken Outline, Discard Outline. Remove duplicate
Undo, expose disabled state in the actual world-space operation rail, and
reuse the native nonmutating outline topology checks for extrusion readiness.
"""
import json
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_527_DRAW_MENU_CLEANUP'

def one(s,old,new,reason):
 count=s.count(old)
 if count!=1:raise AssertionError(('v11.527',reason,count,old[:180]))
 return s.replace(old,new,1)

def section(s,start,end,transform):
 a=s.index(start);b=s.index(end,a+len(start))
 return s[:a]+transform(s[a:b])+s[b:]

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_526_CREATE_MENU_CLEANUP' in html
 def surface(s):
  a=s.index('   function extrudeBegin(id) {')
  b=s.index('   function extrudeData(g, depth) {',a)
  s=s[:a]+"""   // SE527_DRAW_OUTLINE_ELIGIBILITY: a read-only predicate shared by the
   // native extrusion gesture and the spatial Draw menu. No preview or save.
   function outlineEligibility(part, mesh) {
     const invalid=reason=>({ok:false,reason});
     if (part.kind !== 'topologyMesh' || !atelierTopologyValid(part)) return invalid('EXTRUDE_REQUIRES_NATIVE_OUTLINE_FACE');
     if (mesh.isSkinnedMesh && !skinAtBindPose(mesh)) return invalid('EXTRUDE_REQUIRES_BIND_POSE');
     if (part.sculptVertexEdits?.length || part.sculptBrushes?.length || part.sculptLassos?.length || part.refinementLayers?.some(l => l.enabled)) return invalid('EXTRUDE_REQUIRES_UNDEFORMED_OUTLINE');
     const t=part.topologyMesh, audit=atelierTopologyAudit(t);
     const points=Array.from({length:t.positions.length/3},(_,i)=>new THREE.Vector3(...t.positions.slice(i*3,i*3+3)));
     if (!audit.ok || audit.zeroAreaFaces || audit.nonManifoldEdges || audit.oppositeWindingErrors || audit.boundaryEdges !== points.length || t.indices.length/3 !== points.length-2) return invalid('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE');
     const normal=points[t.indices[1]].clone().sub(points[t.indices[0]]).cross(points[t.indices[2]].clone().sub(points[t.indices[0]])).normalize();
     const origin=points[t.indices[0]];
     if (points.some(p=>Math.abs(p.clone().sub(origin).dot(normal))>1e-5)) return invalid('EXTRUDE_REQUIRES_PLANAR_OUTLINE');
     const boundary=[...audit.edges.values()].filter(e=>e.length===1).map(e=>e[0]);
     const outgoing=new Map(boundary.map(e=>[e.from,e.to])),visited=new Set();
     let next=boundary[0].from;
     for(let i=0;i<points.length;i++){if(visited.has(next)||!outgoing.has(next))return invalid('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE');visited.add(next);next=outgoing.get(next);}
     if(next!==boundary[0].from||visited.size!==points.length)return invalid('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE');
     return {ok:true,normal,boundary};
   }
   function canExtrude(id) {
     if(!id || !ready() || active || se340ModelBridge.inspect().gesture)return false;
     const part=partById(id);
     const mesh=modelRoot.children.find(m=>m.isMesh && m.userData?.atelierId===id);
     return !!part && !!mesh?.geometry?.attributes?.position && outlineEligibility(part,mesh).ok;
   }
   function extrudeBegin(id) {
     const g=capture(id);if(!g.ok)return g;
     const eligibility=outlineEligibility(g.part,g.mesh);
     if(!eligibility.ok)return fail(eligibility.reason);
     const {normal,boundary}=eligibility;
     const preview=g.original.clone();g.mesh.geometry=preview;
     active={...g,type:'extrude',preview,normal,boundary,next:null,depth:0,bindPoseSkin:!!g.mesh.isSkinnedMesh};lastError='';lastAction='Pull outline thickness';
     return {ok:true,id,normal:normal.toArray(),mesh:g.mesh};
   }
"""+s[b:]
  s=one(s,
    'drawBegin, drawUpdate, drawEnd, extrudeBegin, extrudeUpdate',
    'drawBegin, drawUpdate, drawEnd, canExtrude, extrudeBegin, extrudeUpdate',
    'surface API exposes nonmutating eligibility')
  return s
 html=section(html,'/* SE350_MODEL_VR_SURFACE_START','/* SE350_MODEL_VR_SURFACE_END',surface)
 def stage(s):
  s=one(s,
   "    draw:[['draw','Draw outline'],['draw-finish','Make face'],['extrude','Thicken outline'],['draw-clear','Discard outline'],['undo','Undo']],",
   "    // SE527_DRAW_ACTIONS: four tools, global Undo/Redo remain on the far-right rail.\n    draw:[['draw','Draw Outline'],['draw-finish','Make Face'],['extrude','Thicken Outline'],['draw-clear','Discard Outline']],",
   'four Draw operations, no history duplication')
  s=one(s,
   '   function paintRow(item){',
   """   // SE527_DRAW_STATE: disabled actions are visible but do not accept a ray press.
   function drawEnabled(action){
     if(category!=='draw')return true;
     if(action==='draw-finish')return !!lastState?.drawGestureActive && (lastState.drawPointCount||0)>=3;
     if(action==='draw-clear')return !!lastState?.drawGestureActive && (lastState.drawPointCount||0)>0;
     if(action==='extrude')return !!lastState?.canExtrudeOutline;
     return true;
   }
   function paintRow(item){""",'contextual Draw eligibility')
  s=one(s,
   '    const hovered=item===lastHover,selected=!!item.active;',
   "    const hovered=item===lastHover,selected=!!item.active,disabled=item.role==='submenu'&&!drawEnabled(action);",
   'disabled visual state')
  s=one(s,
   "    c.fillStyle=hovered?'#38665a':selected?'#295449':'#263345';c.fillRect(0,0,w,h);",
   "    c.fillStyle=disabled?'#202a33':hovered?'#38665a':selected?'#295449':'#263345';c.fillRect(0,0,w,h);",
   'dim unavailable Draw actions')
  s=one(s,
   "    c.strokeStyle=hovered?'#c7fff2':selected?'#8fe5c5':'#586e7f';",
   "    c.strokeStyle=disabled?'#485564':hovered?'#c7fff2':selected?'#8fe5c5':'#586e7f';",
   'disabled border')
  s=one(s,
   "    c.fillStyle='#deeffb';c.textBaseline='middle';",
   "    c.fillStyle=disabled?'#758898':'#deeffb';c.textBaseline='middle';",
   'disabled text')
  s=one(s,
   '    item.texture.needsUpdate=true;mesh.userData.se340Selected=selected;',
   '    item.texture.needsUpdate=true;mesh.userData.se340Selected=selected;mesh.userData.se527Disabled=disabled;',
   'disabled ray metadata')
  s=one(s,
   '   function chooseOperation(item){',
   "   function chooseOperation(item){\n    if(category==='draw'&&!drawEnabled(item.action))return;",
   'guard draw selection')
  s=one(s,
   "detailPage=choosePage(item.action);detailsOpen=category==='inspect'?item.action==='selector-lasso':category==='create-menu'?item.action==='create-pouch':true;",
   "detailPage=choosePage(item.action);detailsOpen=category==='inspect'?item.action==='selector-lasso':category==='create-menu'?item.action==='create-pouch':category==='draw'?false:true;",
   'Draw is direct action, not an obsolete duplicated settings page')
  s=one(s,
   '    lastState=next||{};',
   """    lastState=next||{};
    if(category==='draw')for(const item of submenuRows)if(item.mesh.visible){
     const unavailable=!drawEnabled(item.action);
     if(item.se527LastDisabled!==unavailable){item.se527LastDisabled=unavailable;item.paint();}
    }""",'repaint when native gesture/selection changes')
  s=one(s,
   '    if(secondary){\n',
   "    if(secondary){\n     if(category==='draw'&&!drawEnabled(secondary.action))return false;\n",
   'prevent invalid ray press from dispatching')
  return s
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)
 def native(s):
  s=one(s,
   "id==='draw-finish'?(state.drawPointCount||0)>=3:id==='draw-clear'?(state.drawPointCount||0)>0:true;",
   "id==='draw-finish'?!!state.drawGestureActive&&(state.drawPointCount||0)>=3:id==='draw-clear'?!!state.drawGestureActive&&(state.drawPointCount||0)>0:id==='extrude'?!!state.canExtrudeOutline:true;",
   'native settings action eligibility mirrors Draw menu')
  return s
 html=section(html,'/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END',native)
 def xr(s):
  s=one(s,
   "drawPointCount:['draw','lasso'].includes(s.gesture?.kind)?s.gesture.points.length:0,twoHand:",
   "drawPointCount:['draw','lasso'].includes(s.gesture?.kind)?s.gesture.points.length:0,drawGestureActive:s.gesture?.kind==='draw',canExtrudeOutline:selectedIds.size===1&&se350Surface().canExtrude(native.selectedId),twoHand:",
   'publish real readiness to spatial UI')
  s=one(s,
   "if(action==='draw-clear'){se340CancelGesture('Outline discarded.');se340SyncUI();return true;}",
   "if(action==='draw-clear'){if(s.gesture?.kind!=='draw'||!s.gesture.points.length)return false;se340CancelGesture('Outline discarded.');se340SyncUI();return true;}",
   'discard only unfinished drawing')
  s=one(s,
   "if(action==='draw-finish'){if(s.gesture?.kind==='draw')return se350FinishTrigger(s.gesture.record);return false;}",
   "if(action==='draw-finish'){if(s.gesture?.kind==='draw'&&s.gesture.points.length>=3)return se350FinishTrigger(s.gesture.record);return false;}",
   'face creation needs at least three traced corners')
  s=one(s,
   "if(action==='extrude'){se340CancelGesture();s.mode='extrude';s.page='draw';se340Notice('Point at a drawn face, hold grip and pull to add thickness.');se340SyncUI();se340Publish();return true;}",
   "if(action==='extrude'){const id=se340Bridge().inspect().selectedId;if(s.gesture||se350Tools().selection().ids.length!==1||!se350Surface().canExtrude(id))return false;s.mode='extrude';s.page='draw';se340Notice('Point at the valid outline face, hold grip and pull to add thickness.');se340SyncUI();se340Publish();return true;}",
   'arm existing extrusion gesture only for eligible selected geometry')
  return s
 html=section(html,'/* SE350_MODEL_VR_WORKSPACE_START','/* SE350_MODEL_VR_WORKSPACE_END',xr)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_526_CREATE_MENU_CLEANUP',MARKER),
  ('ENGINE · MAKER v11.526','ENGINE · MAKER v11.527'),
  ('v11.526 · five Create choices with primitive/accessory separator','v11.527 · contextual immersive Draw tools, global history only'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.526'","window.SWRLZ_FORGE_BUILD={version:'v11.527'"),
  ('<title>§wyrl§ Engine · Maker v11.526</title>','<title>§wyrl§ Engine · Maker v11.527</title>')
 ):
  html=one(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.526';source.version=11.526;"
 if html.count(old)!=5:raise AssertionError(('source provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.527';source.version=11.527;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.526']
 notes['history'].insert(0,{'version':'v11.526','changes':notes.get('changes',[])})
 notes.update(version='v11.527',date='2026-11-19',
  title='Contextual immersive Draw menu with native extrusion eligibility',
  changes=[
   'Modeling Lab → Draw has exactly Draw Outline, Make Face, Thicken Outline and Discard Outline. Global Undo/Redo stay in the persistent rail.',
   'Make Face requires an active draw gesture with at least three points. Discard Outline requires a nonempty unfinished outline; both actions visibly disable otherwise.',
   'Thicken Outline is available only for a selected face whose topology is a valid planar open outline; the same read-only eligibility checks guard the existing native Grip extrusion handler.',
   'Draw actions operate in the middle spatial rail without opening a redundant third-stage panel; active gestures, native checkpoints, cancellation, project history and other Labs remain unchanged.',
   'Quest hands-on visual acceptance pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
