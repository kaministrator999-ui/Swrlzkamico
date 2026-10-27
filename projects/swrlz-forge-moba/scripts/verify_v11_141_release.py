#!/usr/bin/env python3
"""§E v11.141: meadow-first touch build placement, Rapid regression and 68 assets."""
import argparse,hashlib,json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
out=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.141'
assert m['finalArtifact']=='swyrl_engine_v11_140.html'
assert len(m['patches'])==173
assert m['patches'][-29:-17]==['patches/v11_113_general_precision_circle.py','patches/v11_114_circle_viewport_handles.py','patches/v11_115_preview_selection_guard.py','patches/v11_116_precision_touch_camera.py','patches/v11_117_editor_native_callout.py','patches/v11_118_semantic_tool_organization.py','patches/v11_119_unified_mode_inspector.py','patches/v11_120_toolbar_layers_touch.py','patches/v11_121_uncover_component_toolbar.py','patches/v11_122_sitewide_touch_guard.py','patches/v11_123_sheep_lanes_toolbar_controls.py','patches/v11_124_sheep_passable_placement.py']
assert m['patches'][-17]=='patches/v11_125_gap_builder_exit.py'
assert m['patches'][-16]=='patches/v11_126_centered_build_permanent_routes_skills.py'
assert m['patches'][-15]=='patches/v11_127_clover_sheep_editor_boot.py'
assert m['patches'][-14]=='patches/v11_128_default_starter_checkbox.py'
assert m['patches'][-13]=='patches/v11_129_project_touch_zoom_guard.py'
assert m['patches'][-12]=='patches/v11_130_second_touch_sheep_seed.py'
assert m['patches'][-11]=='patches/v11_131_directed_mirror_decoy.py'
assert m['patches'][-10]=='patches/v11_132_meadow_rapid_underpass_wireframe.py'
assert m['patches'][-9]=='patches/v11_133_rapid_tappable_sheep_ghost.py'
assert m['patches'][-8]=='patches/v11_134_rapid_cancel_sheep_seed_skills_house_swap.py'
assert m['patches'][-7]=='patches/v11_135_sheep_ghost_relative_drag_hud.py'
assert m['patches'][-6]=='patches/v11_136_sheep_drag_capture_cleanup.py'
assert m['patches'][-5]=='patches/v11_137_meadow_first_build_input.py'
assert m['patches'][-4]=='patches/v11_138_rapid_screen_anchor.py'
assert m['patches'][-3]=='patches/v11_139_rapid_safe_corner_snap.py'
assert m['patches'][-2]=='patches/v11_140_sheep_main_menu.py'
assert m['patches'][-1]=='patches/v11_141_editable_sheep_levels.py'
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
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_141_EDITABLE_MENU_AND_GAME_LEVELS',
 '<title>§wyrl§ Engine · Maker v11.141</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.141'",
 'function st140MenuOpen(){',
 'const ST141_CANONICAL_MENU=',
 'schema:\'se-levels-v1\'',
 'function seLevelsSwitch(id){',
 'function seLevelsCreate(name){',
 'function seLevelsTransition(to,autoPlay=true){',
 'function seLevelsPlayMenu(){',
 'st140MenuTick=function(dt){seLevelsMenuTick(dt);}',
 'id="se141-sheep-editable-levels"',
 'function st140MenuStart(){',
 'function st140MenuClose(){',
 'function st140MenuTick(dt){',
 'animeUpdateCinematic(dt);st140MenuTick(dt);',
 "menu.id='st140MainMenu'",
 'id="se140-sheep-main-menu"',
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
 'st133RememberBuildTouch',
 'st133CanAimSkillAt',
 'st133MoveMobileBuildControls',
 'se133-rapid-and-skill-click',
 'st132InstallRapid',
 'st132CameraBlocked',
 'st132GroundUnderDeck',
 'st132RotateCanonicalCrossings',
 'st132OccludedSheepWireframe',
 'st134RapidBase=st132SetRapid',
 'st134SeedBase=st126SeedAtSheep',
 'st134ChooseBase=stUiChooseBuild',
 'st134AbilitiesBase=stUiRefreshArchive',
 'se134-build-skill-layout',
 'st131MirrorDirection',
 'st131InstallMirrorControl',
 'st131-mirror-cooldown',
 'se130InstallSecondTapProtection',
 'if(stBuildInput.source===\'skill\'&&event.pointerType!==\'mouse\')return;',
 'se129InstallProjectTapGuard',
 'se129-project-zoom-guard',
 'se129-project-tap-guard',
 'se128InstallStarterChoices',
 'se128LaunchStartupProject',
 'SE128_DEFAULT_KEY',
 'st127BuildOrganicPrototype',
 'st127AfterUpdateBase',
 'se127InstallBootGate',
 'se127-editor-boot',
 'st126InstallStarterRoutes',
 'st126SeedAtSheep',
 'stArchiveTotemReady=function(',
 'stHonestGapLocalClear',
 'SHEEP CLEAR',
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
assert 'stLanesEjection=()=>null;' not in s
subprocess.run(['node',str(ROOT/'tests/sheep_gap_builder_exit_v11_125.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/sheep_centered_world_routes_magic_v11_126.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/sheep_ghost_relative_drag_hud_v11_135.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/sheep_drag_camera_capture_perf_v11_136.mjs')],check=True)
# New preview does not itself call checkpoint, mutate native model data,
# or apply the brush until the pre-existing explicit Apply handler fires.
start=s.index('function atelierSculptPickMarkerRefresh(){')
end=s.index('function atelierSculptPreviewFieldsInstall(){',start)
preview=s[start:end]
assert 'checkpoint()' not in preview and 'p.sculptBrushes=' not in preview
Path(str(out)+'-module.mjs').write_text(s.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11141_VERIFIED',len(raw),m['finalSha256'],'173_PATCHES_68_ASSETS')
