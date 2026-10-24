"""v11.114: opt-in radius/depth viewport handles for native precision cuts."""
from pathlib import Path
import json,hashlib

CSS=r"""
/* §E v11.114: touch-sized, independent viewport gizmo toggles. */
#modelAtelierBoreTools .atelier-precision-gizmo-controls{
 display:grid;gap:7px;padding:10px;margin:12px 0;
 background:#162c40;border:1px solid #44677b;border-radius:9px;
}
#modelAtelierBoreTools .atelier-precision-gizmo-controls strong{
 font-size:13px;color:#e5f3ff;line-height:1.4;
}
#modelAtelierBoreTools .atelier-precision-gizmo-controls small{
 color:#acc9df;font-size:12px;line-height:1.5;
}
#modelAtelierBoreTools .atelier-precision-gizmo-row{
 display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;
}
#modelAtelierBoreTools .atelier-precision-gizmo-row button{
 min-height:44px;padding:8px 6px;white-space:normal;
 border:1px solid #617b98;border-radius:7px;background:#243b5a;
 color:#e4efff;font-size:12px;font-weight:650;
}
#modelAtelierBoreGizmoRadius[aria-pressed=true]{
 border-color:#ffdc69!important;box-shadow:inset 0 0 0 1px #ffdc69;
 background:#534522!important;
}
#modelAtelierBoreGizmoDepth[aria-pressed=true]{
 border-color:#bf93ff!important;box-shadow:inset 0 0 0 1px #bf93ff;
 background:#383056!important;
}
"""
def once(src,old,new):
    n=src.count(old)
    assert n==1,(old[:110],n)
    return src.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    gizmos=(root/'runtime/model_atelier_circle_gizmos_v11_114.js').read_text(encoding='utf8')
    html=once(html,'function atelierSculptGhostInstall(){',
      gizmos+'\nfunction atelierSculptGhostInstall(){')
    html=once(html,' atelierPrecisionCircleInstall();\n',
      ' atelierPrecisionCircleInstall();\n atelierPrecisionGizmoInstall();\n')
    html=once(html,
      'atelierSculptHit={partId:selection,center:local.toArray(),axis:normal.toArray()};',
      'atelierSculptHit={partId:selection,center:local.toArray(),axis:normal.toArray()};\n atelierPrecisionGizmoQueue();')
    html=once(html,'</head>','<style id="se-v11114-circle-gizmos">'+CSS+'</style>\n</head>')
    html=once(html,
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_113_GENERAL_PRECISION_CIRCLE',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_114_CIRCLE_VIEWPORT_HANDLES')
    for old,new in [
      ('ENGINE · MAKER v11.113','ENGINE · MAKER v11.114'),
      ('v11.113 · general precision circle cut','v11.114 · radius/depth viewport handles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.113'","window.SWRLZ_FORGE_BUILD={version:'v11.114'"),
      ('<title>§wyrl§ Engine · Maker v11.113</title>','<title>§wyrl§ Engine · Maker v11.114</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Optional touch draggable radius and depth handles in the precision-cut viewport',
      date='2026-10-24',changes=[
       'Toggle amber Radius or violet Depth viewport gizmos on/off independently in Precision circle cut.',
       'Touch/drag the circular footprint or its grip to resize cut radius; drag the depth grip to change drilling depth directly in the model view.',
       'Keep numeric radius/depth fields synchronized; when the pointer releases, rebuild the exact non-destructive editable-mesh preview.',
       'Provide intuitive vertical depth drag for straight-on views where the drill direction projects to a point.',
       'Consume viewport pointer gestures only while actively grabbing the colored handles; preserve ordinary orbit, picking, saved cuts, Undo, mesh views, 68 assets and all previous modeling tools.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V11114_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
