#!/usr/bin/env python3
"""Verify sealed v11.272 left joystick Nerd Stats VR toggle and full engine integrity."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
# Read the exactly sealed receipt, then independently compare built bytes.
META=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
SHA=META["finalSha256"]
SIZE=META["finalBytes"]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_272_SHEEP_NERD_L3_TOGGLE"
parser=argparse.ArgumentParser()
parser.add_argument("--output",required=True)
parser.add_argument("--request",action="store_true")
args=parser.parse_args()
manifest=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert manifest["name"]=="§wyrl§ Engine v11.272"
assert manifest["finalArtifact"]=="swyrl_engine_v11_272.html"
assert manifest["patches"][-1]=="patches/v11_272_sheep_nerd_l3_toggle.py"
assert len(manifest["patches"])==303
assert manifest["finalBytes"]==SIZE and manifest["finalSha256"]==SHA
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
raw=(out/"index.html").read_bytes()
assert raw==(out/"modeler.html").read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
html=raw.decode("utf8")
# Check actual assembled script syntax; source SHA and substring checks cannot catch
# v11.264-style missing JS array commas.
subprocess.run([sys.executable,str(ROOT/"scripts/check_inline_js_syntax_v11_266.py"),str(out/"index.html")],check=True)
for term in (
    "const t=angle+u*4.85+.18*Math.sin(TAU*u);",
    "const size=(.76+1.42*u)*variation;",
    "rec.material.size=cfg.preset==='vortexCore'?Math.min(.14,cfg.size):",
    "float halo=.17*(1.0-smoothstep(.02,.47,r));",
    "float ray=.46*exp(-abs(p.x)*45.0)",
    "const MIST_N=72;",
    "const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;",
    "function se270WispSpec(k,cfg){",
    "slimWispsPerEmitter:ROOT_N-ROOT_INNER",
    "g.setAttribute('color',new THREE.BufferAttribute(colors,3));",
    MARKER,
    "<title>§wyrl§ Engine · Maker v11.272</title>",
    "window.SWRLZ_FORGE_BUILD={version:'v11.272'",
    "window.SWYRL_ENGINE_EDITOR_PREVIEW_247=Object.freeze",
    "window.SWYRL_ENGINE_SHEEP_VR_LAN_268=Object.freeze",
    "window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271=Object.freeze",
    "window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze",
    "function se272LeftStickDown(record){",
    "function se272NerdToggle(){",
    "function se272NerdInputFrame(){",
    "se210PanelClose('metrics');",
    "se210PanelCreate('metrics');",

    "se271ShowBrowserButton(",
    "se271EnsurePreview(",
    "se271Discover(",
    "se271TileCreate(",
    "se271TileHit(",
    "se271PreviewLan",
    "AUTO-FIND OPEN GAMES",
    "function se268MenuActive(){",
    "function se268Rooms(){",
    "function se268Copy(){",
    "function se268StartMatch(){",
    "['lanPage','LOCAL LAN']",
    "['lanHost','HOST']",
    "['lanRooms','FIND ROOMS']",
    "['lanPaste','JOIN CODE']",
    "['lanCopy','COPY INVITE']",
    "['lanStart','START MATCH']",

    "function se223Frame(dt,t){",
    "SWYRL_ENGINE_EDITOR_PREVIEW_247?.sync?.()",
    'id="se247LivePreviewStyle"',
    "se247PreviewPanel",
    "se247-row",
    "se248AstralVortexTheme",
    "se248StarterTab-particles",
    "window.SWYRL_ENGINE_VORTEX_248",
    "Astral Vortex",
    "vortexCyan",
    "vortexCore",
    "vortexSpark",
    "se249ParticleWorkstationStyle",
    "se250DesktopDocksStyle",
    "window.SWYRL_ENGINE_PARTICLE_DOCKS_250",
    "window.SWYRL_ENGINE_PARTICLE_TRACKS_250",
    "se250Handle-left",
    "se250LayoutMode",
    "vRibbonUV",
    "se251UnifiedStudiosStyle",
    "window.SWYRL_ENGINE_PARTICLE_CURVE_RUNTIME_251",
    "window.SWYRL_ENGINE_PARTICLE_CURVES_251",
    "window.SWYRL_ENGINE_PARAMETER_TIMELINE_251",
    "window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251",
    "window.SWYRL_ENGINE_NEBULA_251",
    "window.SWYRL_ENGINE_NEBULA_SETTINGS_251",
    "se251CurveGraph",
    "se251MaterialLibrary",
    "se251ModelLibrary",
    "se251NebulaControls",
    "window.SWYRL_ENGINE_MODEL_STRESS_252",
    "window.SWYRL_ENGINE_STRESS_TEST_252",
    "se252StressDiagnosticsStyle",
    "se254ParticleDockHotfix",
    "se255ParticleViewportInput",
    "const nextPoint=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index,b.arm)",
    "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
    "nebulaDensity",
    "Smoke density",
    "blending:THREE.AdditiveBlending,",
    "float cloud=.50*n+.33*n2+.17*n3;",
    "float holes=smoothstep(.33,.61,cloud);",
    "const MIST_N=72;",
    "'varying float vMistAngle;',",
    "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
    "function se264Profile(cfg,arm){",
    "function se264Blend(u,profile,seed){",
    "function se264Tint(out,u,profile,seed){",
    "uniform float uBlueBlend;",
    "uniform float uPurpleBreak;",
    "float blueRatio=clamp(b1*(1.-uPurpleBreak*.88*patch),0.,1.);",
    "se264Tint(temp,u,se264Profile(cfg,branch)",
    "function makeInnerTendrils(cfg){",
    "function updateInnerTendrils(t,cfg,rec,origin){",
    "innerPurpleRootsPerEmitter:ROOT_INNER",
    "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265=Object.freeze",
    "function se265BatchBuilding(building){",
    "function se265Snapshot(){",
    "function se265Lines(s,page){",
    "window.SWYRL_ENGINE_QUEST_PERFORMANCE_210",
    "function makeCoreHalo(){",
    "cfg.preset==='vortexCore'&&!r.se264CoreHalo",
    "if(cfg.preset==='vortexCore'&&rec.se264CoreHalo)",
    "inner.mesh.removeFromParent();inner.g.dispose();inner.mat.dispose();",
    "attribute vec3 aMistTangent;",
    "vMistAngle=atan(direction.y,direction.x);",
    "orient.needsUpdate=true;",

    "const se263AtlasReady={value:0};",
    "const se263AtlasTexture=new THREE.TextureLoader().load(",
    "data:image/png;base64,",
    "uniform sampler2D uMistAtlas;",
    "uniform float uMistAtlasReady;",
    "attribute float aMistVariant;",
    "g.setAttribute('aMistVariant'",
    "float painted=texture2D(uMistAtlas,(tile+localUV)*.5).r;",
    "gl_PointSize=clamp(aMistSize*uMistPixels*(510.0/max(1.0,-mv.z)),4.0,116.0);",
    "atlasTiles:4,atlasSource:'owner nebula mask'",
    "function makeNebulaMist(cfg){",
    "function updateNebulaMist(m,cfg,rec,origin){",
    "if(b.kind==='smoke')b.mesh.visible=false;",
    "r.se251Nebula.mist.points.layers.mask=mask;",
    "if(band.kind==='filament')writeMesh(band,cfg,rec,origin);",
    "updateNebulaMist(rec.se251Nebula.mist,cfg,rec,origin);",
    "mist.points.removeFromParent();mist.g.dispose();mist.mat.dispose();",
    "nebulaPuffsPerColor:MIST_N",
    "float brush=mix(fallback,painted,uMistAtlasReady);",
    "float wisp=mix(haze*.70,brush,.46);",
    "float haze=(1.0-smoothstep(.17,1.04,radius))*.24;",
    "float alpha=clamp((haze*.82+wisp*.50)*edge*uMistDensity*shimmer,0.0,.265);",
    "vec2 p=rotated*vec2(1.10,.67);",
    "const u=.018+.96*(ordinal+.31+Math.random()*.24)/(MIST_N/3);",
    "lateral:side*(.014+.072*u),height:(Math.random()-.5)*(.018+.085*u)",
    "const grow=u=>b.kind==='filament'?",
    "   .034+u*.015:",
    "b.mat.uniforms.uOpacity.value=(b.kind==='filament'?1.08",
    "se264Profile(cfg,arm)",

    "float opacity=tip*uOpacity*(1.13*plume+.43*wisp);",
    "clamp(opacity,0.,.52)",
    "(.035+Math.pow(u,.83)*(.47+b.index*.18))*widthFactor;",
    "if(!b.se259UVReady)",
    "const bands=[];",
    "const a=phase+spin+arm*TAU/3+u*4.85+.18*Math.sin(TAU*u);",
    "Particle effect error:",
    "const dx=nextPoint[0]-a[0],dy=nextPoint[1]-a[1]",
    "if(window.SWYRL_ENGINE_PARTICLE_ERRORS_258?.shouldSkip(cfg))continue;",
    "projectRebinds:state.projectRebinds||0",
    "se256AIBudget.used<se256AIBudget.perFrame",
    "window.SWYRL_ENGINE_SHEEP_BUILD_RAY_256",
    "se203GroundFromForwardRay=function(){return null;}",
    "beam.renderOrder=11100",
    "se255BindViewportInput(viewing);",
    "!window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())orbit.update();",
    "Chamber ON",
    "window.SWYRL_ENGINE_PARTICLE_DOCKS_250?.init?.();",
    "const active=stageActive?!!se223State.preview:",
    "zoomDistance:state.distance",
    "const mounted=records.some(record=>",
    "if((!modelOpen&&!particleOpen&&!state.particle)||q('#seReleaseNotesDialog')?.open)",
    "Diagnostic high-poly specimen",
    "Diagnostic particle cloud",
    "window.SWYRL_ENGINE_PARTICLE_UI_249",
    "window.SWYRL_ENGINE_RIBBONS_249",
    "se249NativeHolder",
    "se249LayerRows",
    "vortexSpin",
    "vortexPull",
    "vortexGlow",
    "vortexTilt",
    "Edit-mode live previews",
    "se223State.preview=true",
    "storyPreview(0)",
    "storyExitPreview()",
    "animeUpdateCinematic=function(dt)",
    "SWYRL_ENGINE_GUI_STUDIO",
    "SWYRL_ENGINE_PARTICLE_STAGE_240",
    "SWYRL_ENGINE_PARTICLE_BOTTOM_TOGGLE_246",
):
    assert term in html,term
assert html.count("renderer.setAnimationLoop(tick);")==1
assert "const observer=new MutationObserver(()=>{\n if(!q('#se251ModelLibrary')" not in html
receipt=json.loads((out/"SOURCE.json").read_text("utf8"))
assert receipt["sourceVersion"]==manifest["name"]
assert receipt["finalSha256"]==SHA and receipt["finalBytes"]==SIZE
assert receipt["patches"]==manifest["patches"]
assert len(receipt["assets"])==69
for name,metadata in receipt["assets"].items():
    data=(out/name).read_bytes()
    assert len(data)==metadata["bytes"],name
    assert hashlib.sha256(data).hexdigest()==metadata["sha256"],name
if args.request:
    request=json.loads((ROOT/"DEPLOY_REQUEST.json").read_text("utf8"))
    assert request["releaseVersion"]=="v11.272"
    assert request["deployMarker"]==MARKER
    assert request["sourceIntegritySha256"]==SHA
    assert isinstance(request.get("sourceCommit"),str) and len(request["sourceCommit"])==40
print(json.dumps({"status":"SEALED_SOURCE_VERIFIED",
 "version":"v11.272","patches":303,"htmlBytes":SIZE,"sha256":SHA,
 "assets":len(receipt["assets"]),"preview":"Quest left L3 click toggles existing in-game Nerd Stats panel while preserving analog sheep movement",
 "ownerQuestAcceptance":False},indent=2))
