"""§E v11.113: make precision circles reusable on multiple native shapes."""
from pathlib import Path
import hashlib,json

def once(text,old,new):
    count=text.count(old)
    assert count==1,(old[:100],count)
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    old=(root/'runtime/model_atelier_manual_round_holes_v11_112.js').read_text(encoding='utf8')
    new=(root/'runtime/model_atelier_precision_circle_v11_113.js').read_text(encoding='utf8')
    html=once(html,old,new)
    # The original bootstrap call lies outside the injected function source.
    html=once(html,' atelierBowlingInstall();\n',' atelierPrecisionCircleInstall();\n')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_112_MANUAL_ROUND_HOLE_SCULPT',
              'SWYRL_ENGINE_DEPLOY_MARKER: V11_113_GENERAL_PRECISION_CIRCLE')
    for old,new in [
      ('ENGINE · MAKER v11.112','ENGINE · MAKER v11.113'),
      ('v11.112 · manual precision circle carve','v11.113 · general precision circle cut'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.112'","window.SWRLZ_FORGE_BUILD={version:'v11.113'"),
      ('<title>§wyrl§ Engine · Maker v11.112</title>','<title>§wyrl§ Engine · Maker v11.113</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="General hand-placed precision circles for spheres, box faces and cylinder caps",
      date='2026-10-24',changes=[
       "Replace bowling-ball-only terminology with reusable Precision circle cut controls.",
       "Manually place an independent circle, adjust radius/depth and choose flat or rounded bottom; keep native, undoable preview/apply workflow.",
       "Support real indexed recessed cuts on spherical surfaces, planar box faces and cylinder end caps, with up to six saved cuts on a flat face.",
       "Conserve every previous cut on the same chosen surface, and require an explicit relocation checkbox before moving an existing cut.",
       "Keep numeric/manifold/mobile budget validation, editing recipe, prior sculpt brush, render modes, exports, and all 68 assets; imported arbitrary-mesh Boolean operations remain unsupported."
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V11113_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
