"""§E v11.512 proposal: Trigger gizmos, menu facing and native indent sculpting.
Not active until appended to source-manifest and resealed from a real build.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_512_TRIGGER_GIZMOS_MENU_FACING"

def once(html,old,new):
    n=html.count(old)
    if n!=1: raise AssertionError(("v11.512 anchor",old[:100],n))
    return html.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_511_MODEL_DOCK_VISIBILITY" in html
    src=(ROOT/"runtime/model_vr_trigger_gizmo_v11_512.js").read_text("utf8")
    assert "SE512_MODEL_VR_TRIGGER_GIZMO_END" in src
    html=once(html,"installPerformanceSettings();se189InstallPerfUI();",
              src+"\ninstallPerformanceSettings();se189InstallPerfUI();")
    # Display platform is a scene prop, distinct from the model's native root.
    platform=(ROOT/'runtime/model_display_platform_v11_512.js').read_text('utf8')
    assert 'SE512_DISPLAY_PLATFORM_END' in platform
    html=once(html,'  function point(e){',platform+'\n  function point(e){')
    html=once(html,'floor.position.y=-.07;world.add(floor);',
      'floor.position.y=-.07;world.add(floor);se512PlatformBrowserAttach(floor,stage);')
    html=once(html,'  function close(){','  function close(){se512PlatformBrowserDetach();')
    html=once(html,
      "['focus','Focus'],['aim','Aim'],['studio','Studio'],\n    ['help','Guide'],['tools','Quick tools'],['exit','Exit VR']",
      "['focus','Focus'],['aim','Aim'],['platform-toggle','Platform'],\n    ['help','Guide'],['tools','Quick tools'],['exit','Exit VR']")
    html=once(html,
      "function label(item){\n  if(item.id==='index-add')",
      "function label(item){\n  if(item.id==='platform-toggle')return state.platformVisible?'Hide platform':'Show platform';\n  if(item.id==='index-add')")
    html=once(html,
      "mode:s.mode,selectedName:selected?.name||'',hoverName:hover?.name||'',dragging:!!s.gesture,",
      "mode:s.mode,selectedName:selected?.name||'',hoverName:hover?.name||'',dragging:!!s.gesture,platformVisible:s.platform?.visible!==false,")
    html=once(html,
      "if(action==='exit'){void se340ModelXRExit();return true;}",
      "if(action==='exit'){void se340ModelXRExit();return true;}\n if(action==='platform-toggle'){if(!s.platform)return false;s.platform.visible=!s.platform.visible;se340Notice(s.platform.visible?'Display platform shown.':'Display platform hidden.');se340SyncUI();se340Publish();return true;}")
    # Quest Browser 2D alone: tolerate small controller-ray pointer jitter,
    # and exclude non-editable overlay/helper geometry from fallback picking.
    pick=(ROOT/'runtime/model_vr_browser_pick_v11_512.js').read_text('utf8')
    assert 'SE512_QUEST_BROWSER_PICK_END' in pick
    html=once(html,'  function point(e){',pick+'\n  function point(e){')
    html=once(html,
      'if(Math.hypot(dx,dy)>5)pressed.moved=true;',
      'if(Math.hypot(dx,dy)>(se512QuestBrowser2D()?16:5))pressed.moved=true;')
    html=once(html,
      'if(!pressed)return;const hit=!pressed.moved;pressed=null;',
      'if(!pressed)return;const se512Press=pressed,hit=!pressed.moved;pressed=null;')
    html=once(html,
      "const hits=raycaster.intersectObjects(meshes,false);select(hits[0]?.object?.userData?.atelierId||null);",
      "const hits=raycaster.intersectObjects(meshes,false);const first=hits.find(h=>partById(h.object?.userData?.atelierId));select(first?.object?.userData?.atelierId||se512QuestTapPick(e,se512Press)||null);")
    # §E VR sculpting: positive normal displacement stays outward Pull;
    # negative normal displacement is inward Indent using the same native
    # geometry preview, sparse vertex edits, save and Undo pipeline.
    html=once(html,
      "const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate'];",
      "const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate','indent'];")
    html=once(html,
      "Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,",
      "Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,brushFalloff:'smooth',")
    html=once(html,
      "const result=se350Surface().sculptBegin(hit.id,{operation:s.sculptTool,radius:s.brushRadius,strength:s.brushStrength});",
      "const result=se350Surface().sculptBegin(hit.id,{operation:s.sculptTool==='indent'?'push':s.sculptTool,radius:s.brushRadius,strength:s.sculptTool==='indent'?-Math.abs(s.brushStrength):s.brushStrength});")
    html=once(html,
      "strength:se340XR.brushStrength,smooth:!!se340XR.inputSample?.held['temporary-smooth']",
      "strength:se340XR.sculptTool==='indent'?-Math.abs(se340XR.brushStrength):se340XR.brushStrength,falloff:se340XR.brushFalloff,smooth:!!se340XR.inputSample?.held['temporary-smooth']")
    html=once(html,
      "operation, falloff: 'smooth', plateau: 0, taper: .5, half: false, level: false,",
      "operation, falloff: ['smooth','soft','sharp','flat'].includes(sample.falloff)?sample.falloff:'smooth', plateau: 0, taper: .5, half: false, level: false,")
    html=once(html,
      "['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],\n   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate'],\n   ['brush-radius-minus','Radius −']",
      "['sculpt-push','Pull'],['sculpt-indent','Indent'],['sculpt-smooth','Smooth'],\n   ['sculpt-flatten','Flatten'],['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],\n   ['brush-radius-minus','Radius −']")
    html=once(html,
      "['brush-strength-plus','Strength +'],['studio','Studio'],['exit','Exit VR']",
      "['brush-strength-plus','Strength +'],['sculpt-falloff','Falloff'],['exit','Exit VR']")
    html=once(html,
      "function label(item){\n  if(item.id==='index-add')",
      "function label(item){\n  if(item.id==='sculpt-falloff')return 'Falloff: '+(state.brushFalloff||'smooth');\n  if(item.id==='index-add')")
    html=once(html,
      "selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushRadius:s.brushRadius",
      "selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushFalloff:s.brushFalloff,brushRadius:s.brushRadius")
    html=once(html,
      "if(action.startsWith('sculpt-')){const tool=action.slice(7);",
      "if(action==='sculpt-falloff'){const choices=['smooth','soft','sharp','flat'];s.brushFalloff=choices[(choices.indexOf(s.brushFalloff)+1)%choices.length];se340Notice('Sculpt falloff: '+s.brushFalloff);se340SyncUI();return true;}\n if(action.startsWith('sculpt-')){const tool=action.slice(7);")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_511_MODEL_DOCK_VISIBILITY",MARKER),
      ("ENGINE · MAKER v11.511","ENGINE · MAKER v11.512"),
      ("v11.511 · restore Modeling rail and inspector layout",
       "v11.512 · trigger capture for VR gizmos and user-facing world menus"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.511'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.512'"),
      ("<title>§wyrl§ Engine · Maker v11.511</title>",
       "<title>§wyrl§ Engine · Maker v11.512</title>")
    ):html=once(html,a,b)
    old=" source.engine='§wyrl§ Engine · Maker v11.511';source.version=11.511;"
    assert html.count(old)==5,("model provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.512';source.version=11.512;")
    tag="const SE_RELEASE_NOTES="
    at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[x for x in notes.get("history",[]) if x.get("version")!="v11.511"]
    notes["history"].insert(0,{"version":"v11.511","changes":notes.get("changes",[])})
    notes.update(version="v11.512",date="2026-11-18",
      title="Native Quest selection, Trigger gizmos, menu facing, sculpt Indent and platform visibility",
      changes=[
       "Controller Trigger directly captures an aim-hovered visible transform gizmo; native Move, Rotate, Scale and Grab-axis previews use existing skin-safe model transactions and one-step Undo.",
       "Trigger release completes one native edit and suppresses the otherwise generated selection click. Cancel, tracking loss and XR cleanup discard pending previews.",
       "Movable immersive VR console maintains its placed world position while continuously facing the headset for readable front-side controls.",
       "Display platform visibility is independently adjustable in both the 2D editor and the immersive Display panel, never moving model geometry.",
       "Regular Meta Quest Browser pointer taps tolerate small ray jitter and ignore nonmodel helper meshes, without affecting immersive WebXR or desktop camera handling.",
       "Immersive sculpting now offers positive outward Pull and inward Indent with radius, strength and smooth/soft/sharp/flat falloff using the existing native signed displacement operator.",
       "Existing Grip/free grab, account project data, UV texture, and browser 2D editing behavior are untouched."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+n:]
