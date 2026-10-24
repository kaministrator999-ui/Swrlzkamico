#!/usr/bin/env python3
"""Release verifier for §E v11.113 live sculpt radius and depth guides."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
out=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.113'
assert m['finalArtifact']=='swyrl_engine_v11_113.html'
assert len(m['patches'])==145
assert m['patches'][-3:]==['patches/v11_111_true_bowling_holes.py','patches/v11_112_manual_precision_hole_tools.py','patches/v11_113_general_precision_circle.py']
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
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_113_GENERAL_PRECISION_CIRCLE',
 '<title>§wyrl§ Engine · Maker v11.113</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.113'",
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
print('SWRLZ_V11113_VERIFIED',len(raw),m['finalSha256'],'145_PATCHES_68_ASSETS')
