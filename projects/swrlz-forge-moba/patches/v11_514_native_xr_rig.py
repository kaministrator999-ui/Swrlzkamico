"""§E v11.514 — integrate generic rig posing and weight painting into
the existing WebXR 3D spatial menu + Trigger/Grip input architecture.
No DOM menu, no new WebXR session or parallel menu event model.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_514_NATIVE_XR_RIG'
def once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.514',label,n,old[:120]))
 return s.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_513_RIG_SKIN_WEIGHT_STUDIO' in html
 js=(ROOT/'runtime/model_vr_native_rig_v11_514.js').read_text('utf8')
 assert 'SE514_NATIVE_XR_RIG_END' in js
 # Hook into the SAME renderer, scene, menu, hitTest, controller profile and
 # lifetime used by the previous §E immersive Model Studio.
 html=once(html,'installPerformanceSettings();se189InstallPerfUI();',
               js+'\ninstallPerformanceSettings();se189InstallPerfUI();','native WebXR extension')
 begin=html.index('/* SE360_MODEL_VR_UI_START */')
 end=html.index('/* SE360_MODEL_VR_UI_END */',begin)
 ui=html[begin:end]
 pages="""   rig:[
    ['rig-prev','Previous bone'],['rig-next','Next bone'],['rig-undo','Undo rig edit'],
    ['rig-pose-x-minus','Pose X −5°'],['rig-pose-x-plus','Pose X +5°'],
    ['rig-pose-y-minus','Pose Y −5°'],['rig-pose-y-plus','Pose Y +5°'],
    ['rig-pose-z-minus','Pose Z −5°'],['rig-pose-z-plus','Pose Z +5°'],
    ['rig-weights','Weight painting'],['studio','Studio'],['exit','Exit VR']
   ],
   'rig-weights':[
    ['rig-weight-add','Add influence'],['rig-weight-erase','Erase influence'],['rig-weight-stop','Stop brush'],
    ['rig-radius-minus','Radius −'],['rig-radius-plus','Radius +'],
    ['rig-strength-minus','Step −'],['rig-strength-plus','Step +'],
    ['rig-prev','Previous bone'],['rig-next','Next bone'],
    ['rig-undo','Undo rig edit'],['rig','Bone posing'],['exit','Exit VR']
   ],
"""
 import re
 hits=list(re.finditer(r'(?m)^[ \t]*sculpt\s*:\s*\[',ui))
 if len(hits)!=1:raise AssertionError(('native rig page insertion',len(hits)))
 ui=ui[:hits[0].start()]+pages+ui[hits[0].start():]
 ui=once(ui,"['views','Display'],['aim','Pointer aim'],['help','Guide'],",
            "['views','Display'],['rig','Rigging'],['help','Guide'],",'studio tab entry')
 ui=once(ui,"['views','Display'],['aim','Pointer aim'],['help','Guide']]",
            "['views','Display'],['aim','Pointer aim'],['help','Guide'],['rig','Rigging']]",'native studio wheel entry')
 ui=once(ui,"const pageTitles={objects:",
           "const pageTitles={rig:['Rigging · skeletal posing','SELECT BONES · GRIP ROTATE · AXIS NUDGE'],'rig-weights':['Rigging · weight painting','TRIGGER BRUSH · UNDO · FOUR INFLUENCES'],objects:",
           'native page header labels')
 ui=once(ui,"const details={objects:",
           """const details={rig:'Choose real joints; Right Grip changes the pose',
   'rig-prev':'Select previous bone in current hierarchy',
   'rig-next':'Select next bone in current hierarchy',
   'rig-undo':'Undo the last native immersive rig edit',
   'rig-weights':'Paint actual per-vertex GPU skin influences',
   'rig-weight-add':'Increase influence of the selected bone',
   'rig-weight-erase':'Reduce influence of the selected bone',
   'rig-weight-stop':'Return to bone pose editing',
   'rig-radius-minus':'Smaller brush influence region',
   'rig-radius-plus':'Larger brush influence region',
   'rig-strength-minus':'Less weight per stroke',
   'rig-strength-plus':'More weight per stroke',
   'rig-pose-x-minus':'Rotate selected joint X −5° (pose only)',
   'rig-pose-x-plus':'Rotate selected joint X +5° (pose only)',
   'rig-pose-y-minus':'Rotate selected joint Y −5° (pose only)',
   'rig-pose-y-plus':'Rotate selected joint Y +5° (pose only)',
   'rig-pose-z-minus':'Rotate selected joint Z −5° (pose only)',
   'rig-pose-z-plus':'Rotate selected joint Z +5° (pose only)',
   objects:""",'native rig tool descriptions')
 ui=once(ui,"if(id==='objects')return 'layers';",
    "if(id==='rig'||id==='rig-undo'||id==='rig-prev'||id==='rig-next')return 'hands';\n   if(id.startsWith('rig-weight')||id.startsWith('rig-radius')||id.startsWith('rig-strength'))return 'brush';\n   if(id.startsWith('rig-pose-'))return 'rotate';\n   if(id==='objects')return 'layers';",
    'reuse existing native icon renderer')
 ui=once(ui,' function enabled(id){',' function enabled(id){\n  if(id===\'rig\'||id.startsWith(\'rig-\'))return !!state.rigAvailable;', 'native menu enabled state')
 ui=once(ui,' function active(item){const id=item.id;',
    """ function active(item){const id=item.id;
  if(id==='rig')return ['rig','rig-weights'].includes(state.page);
  if(id==='rig-weights')return state.page==='rig-weights';
  if(id==='rig-weight-add')return state.rigPaintMode==='add';
  if(id==='rig-weight-erase')return state.rigPaintMode==='erase';""",
    'native menu selected/active state')
 ui=once(ui,'  if(wheelKind)return hoveredItem?', 
    """  if(!wheelKind&&state.page==='rig')return 'Joint '+clean(state.rigBoneName,40)+' · Trigger selects · Right Grip turns pose · B cancels';
   if(!wheelKind&&state.page==='rig-weights')return 'Painting '+state.rigPaintMode+' · Trigger on skinned mesh · B cancels';
   if(wheelKind)return hoveredItem?""",
    'native status footer')
 ui=once(ui,"const context=page==='objects'?",
    """const context=['rig','rig-weights'].includes(page)?
    'JOINT '+state.rigBoneIndex+'/'+state.rigBoneCount+' · '+clean(state.rigBoneName,38)+
    (page==='rig-weights'?' · '+state.rigPaintMode.toUpperCase()+' R '+Number(state.rigRadius).toFixed(2)+' S '+Math.round(Number(state.rigStrength)*100)+'%':' · POSE / NOT REST'):page==='objects'?""",
    'native rig header')
 ui=once(ui,"const controller=page==='objects'&&",
    """const controller=page==='rig'?'Right Trigger: choose joint · Right Grip: pose rotation · Y: Undo':
    page==='rig-weights'?'Right Trigger: paint surface · B: cancel · Y: Undo':page==='objects'&&""",
    'native controller help')
 html=html[:begin]+ui+html[end:]
 html=once(html,'const state={selectedRegionId:se350Surface().inspect().selectedRegionId',
               'const state={...se514RigXR.uiState(),selectedRegionId:se350Surface().inspect().selectedRegionId',
               'menu UI state supplied from existing XR frame')
 html=once(html,"'draw-finish','draw-clear','lasso','lasso-clear']",
    """'draw-finish','draw-clear','lasso','lasso-clear',
   'rig','rig-prev','rig-next','rig-undo','rig-weights','rig-weight-add','rig-weight-erase',
   'rig-weight-stop','rig-radius-minus','rig-radius-plus','rig-strength-minus','rig-strength-plus',
   'rig-pose-x-minus','rig-pose-x-plus','rig-pose-y-minus','rig-pose-y-plus','rig-pose-z-minus','rig-pose-z-plus']""",
    'native scene actions registry')
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_513_RIG_SKIN_WEIGHT_STUDIO',MARKER),
  ('ENGINE · MAKER v11.513','ENGINE · MAKER v11.514'),
  ('v11.513 · precise skin weights and independent rig mesh bindings',
   'v11.514 · native spatial Rigging and Weight Painting in immersive WebXR'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.513'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.514'"),
  ('<title>§wyrl§ Engine · Maker v11.513</title>',
   '<title>§wyrl§ Engine · Maker v11.514</title>')
 ):html=once(html,old,new,'version identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.513';source.version=11.513;"
 if html.count(old)!=5:raise AssertionError(('v11.514 model provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.514';source.version=11.514;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.513']
 notes['history'].insert(0,{'version':'v11.513','changes':notes.get('changes',[])})
 notes.update(version='v11.514',date='2026-11-18',
  title='Native immersive Rigging Studio bone manipulation and weight painting',
  changes=[
   'Existing immersive WebXR 12-slot spatial console and Studio wheel now offer Rigging, an exact native bone-pose page and a real per-bone Weight Painting page. No new DOM popup, detached spatial panel, secondary controller dispatcher or project workspace is created.',
   'Visible 3D joint pivot/shaft guides are viewer-side gizmos only. Trigger picks native skeleton joints; right controller Grip rotates an articulated joint in pose space while keeping its parent chain intact. B/tracking loss cancels, release commits and Y/VR Undo restores the prior rig pose.',
   'The native pose page also provides precise ±5 degree joint rotations independently on X, Y and Z, selection of previous and next rig bones, and an explicit pose-not-rest distinction.',
   'Weight Painting reuses authored four-slot per-vertex skin indices/weights and a local smooth falloff brush, selectable Add/Erase influence, radius and step, a live GPU deforming preview, cancellation rollback, current-project saved weights and in-VR Undo.',
   'Existing platform, sculpt, object/pose transforms, camera orbit, menu hit blockers, controller input profiles, hover, Trigger/Grip, and full source/UV/rig asset lineage are preserved.',
   'Desktop 2D rigging stays unchanged. Physical Quest immersive selection/paint/rotation and large-mesh performance still require device acceptance; other outstanding 12-item VR QA work remains open.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
