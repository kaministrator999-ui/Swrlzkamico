#!/usr/bin/env python3
"""Release verifier for §E v11.124 live sculpt radius and depth guides."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
out=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.124'
assert m['finalArtifact']=='swyrl_engine_v11_124.html'
assert len(m['patches'])==156
assert m['patches'][-12:]==['patches/v11_113_general_precision_circle.py','patches/v11_114_circle_viewport_handles.py','patches/v11_115_preview_selection_guard.py','patches/v11_116_precision_touch_camera.py','patches/v11_117_editor_native_callout.py','patches/v11_118_semantic_tool_organization.py','patches/v11_119_unified_mode_inspector.py','patches/v11_120_toolbar_layers_touch.py','patches/v11_121_uncover_component_toolbar.py','patches/v11_122_sitewide_touch_guard.py','patches/v11_123_sheep_lanes_toolbar_controls.py','patches/v11_124_sheep_passable_placement.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes();s=raw.decode()
r=json.loads((out/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
for p,meta in r['assets'].items():
 b=(out/p).read_bytes();assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],p
for token in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_124_FLUSH_OR_PASSABLE_SHEEP_BUILD_PLACEMENT',
 '<title>§wyrl§ Engine · Maker v11.124</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.124'",
 'function atelierSculptPreviewFieldsInstall(){',
 'function atelierSculptGhostDraw(){',
 'attribute vec3 brushSource;',
 'uniform float brushRadius;',
 'smoothstep(brushRadius*0.61,brushRadius,radial)',
 'function addRadiusClippedEdge(first,second){',
 'attribute float brushMove;',
 'uniform float brushMaxMove;',
 'float motionFade=smoothstep(0.025,0.22',
 'triangleMoves.push(motion[i]);',
 'if(triangles.length&&affected>0){',
 'function atelierSculptGhostInstall(){',
 'function atelierPrecisionCircleBuild(',
 'function atelierPrecisionCircleInstall(){',
 'atelierPrecisionCircleInstall();',
 'modelAtelierBoreTools',
 'roundHolePlan:plan',
 'function atelierBorePlanValid(part){',
 'function atelierBoreCoordinates(plan,point){',
 'atelierTopologyAudit(data);',
 'Precision circle cut · reusable shape tool',
 'surface===\'box\'',
 'surface===\'cylinder\'',
 'const max=plan.surface===\'sphere\'||!plan.surface?3:6;',
 'modelAtelierBoreRelocate',
 'function atelierPrecisionGizmoDraw(){',
 'function atelierPrecisionGizmoDown(event){',
 'function atelierPrecisionGizmoMove(event){',
 'function atelierPrecisionGizmoUp(event){',
 'atelierPrecisionGizmoInstall();',
 'modelAtelierBoreGizmoRadius',
 'modelAtelierBoreGizmoDepth',
 'function atelierPrecisionGuardInstall(){',
 'function seAtelierCalloutInstall(){',
 'function atelierToolRailArrange(panel){',
 'function seAtelierModeToolbarInstall(panel){',
 'function seAtelierModeChoose(panel,category,mode){',
 'function seAtelierTopBarArrange(panel){',
 "const seComponentToolbarAnchor=panel.querySelector('#modelAtelierViewportModes');",
 'seComponentToolbarAnchor.after(row);',
 "row.classList.add('se-component-inline');",
 'se-v11121-component-row',
 'se-v11122-site-touch-guard',
 'se-v11122-site-touch-script',
 'se-v11123-workflow-safe-lanes',
 'stBuildGridPreviousCanBuild',
 'stBuildGridPreviousClarityGap',
 'Safe snapped sheep lanes ',
 'stSafeLaneWidth()',
 'seMainToolbarOrganize()',
 'window.seEngineIsEditable=isEditable;',
 'if(activeScope(event.target)&&!window.seEngineIsEditable(event.target))event.preventDefault();',
 'function seAtelierQuickstripSafeTop(stage){',
 'function seAtelierBottomRailCenter(panel){',
 'function seAtelierTopMenuExclusivity(panel){',
 'seAtelierBottomRailCenter(panel);',
 'seAtelierTopMenuExclusivity(panel);',
 'se-v11120-toolbar-layer',
 'const safeTop=seAtelierQuickstripSafeTop(stage);',
 'touch-action:manipulation',

 'seAtelierModeToolbarInstall(panel);',
 'seAtelierTopBarArrange(panel);',
 'inspector.append(ui);',
 'se-v11119-unified-mode-layout',
 'seAtelierExportMenu',
 'seAtelierViewMenu',
 'seAtelierModes',
 'window.seAtelierCalloutInstall=function seAtelierCalloutInstall(){',
 'window.seAtelierCalloutInstall();',

 "GROUPS.Sculpt.splice(1,0,['Precision circle cut'",
 "GROUPS.Face.unshift(['Portrait & anatomy'",
 "GROUPS.Appearance=[",
 'function detectGroup(id,fallback=\'Meshes\'){',
 'const buckets={};',
 'atelierToolRailArrange(panel);',

 'seAtelierCalloutInstall();',
 'se-v11117-native-callout',
 'modelAtelierPanel',
 'seMobileNumberPad',
 "document.addEventListener('contextmenu',event=>{",
 "document.addEventListener('selectstart',event=>{",
 '-webkit-touch-callout:none!important;',

 'const atelierCameraMinDistance=()=>{',
 'atelierCameraTouches.set(d.id,',
 "const threshold=event.pointerType==='touch'?18:12;",
 "atelierCameraPointerUp(event);",
 "if(event?.type==='pointercancel'&&drag.changed){",
 'atelierMeshGizmoClear();return;',

 'function atelierPrecisionGuardPointerUp(event){',
 'atelierPrecisionGuardInstall();',
 'atelierMeshNudge=function(...args){',
 'renderParts=function(...args){',
 'atelierPrecisionGizmoQueue();',
 'for(let level=0;level<(surface===\'sphere\'?2:1);level++){',
 'modelAtelierSculptGhostEnabled',
 'atelierSculptGhostSchedule();',
 'atelierSculptPreviewFieldsInstall();',
 'const form=atelierSculptForm();',
 'const radius=hasForm?form.radius:.055;',
 "const signedDepth=hasForm&&form.operation==='push'?form.strength:0;",
 'lineLoop(radius,0,0xffdc69,.98,990);',
 'lineLoop(depthRadius,signedDepth,0xbf93ff,.95,992);',
 'document.addEventListener(\'change\',update,true);',
 'helper.userData.atelierHelper=true;',
 'atelierSculptPickMarkerRefresh();',
 'const holdMilliseconds=380;',
 'function atelierViewEnsureAfterGeometryEdit(){',
 'height:min(68dvh,700px)!important;',
]:assert token in s,token
# New preview does not itself call checkpoint, mutate native model data,
# or apply the brush until the pre-existing explicit Apply handler fires.
start=s.index('function atelierSculptPickMarkerRefresh(){')
end=s.index('function atelierSculptPreviewFieldsInstall(){',start)
preview=s[start:end]
assert 'checkpoint()' not in preview and 'p.sculptBrushes=' not in preview
Path(str(out)+'-module.mjs').write_text(s.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11124_VERIFIED',len(raw),m['finalSha256'],'156_PATCHES_68_ASSETS')
