"""§E v11.66 usability repair: selection outline, safe drags, Undo, movable UI."""
import json
from pathlib import Path

OLD="SWYRL_ENGINE_DEPLOY_MARKER: V11_65_SELECTION_MESH_GIZMOS"
NEW="SWYRL_ENGINE_DEPLOY_MARKER: V11_66_MESH_SELECTION_UX_REPAIR"
CANONICAL="const MODEL_ATELIER_CANONICAL_PROJECT="

def once(text,before,after):
    n=text.count(before)
    assert n==1,(before[:120],n)
    return text.replace(before,after,1)

def replace_block(text,start,end,replacement):
    assert text.count(start)==1,(start,text.count(start))
    assert text.count(end)==1,(end,text.count(end))
    a=text.index(start);b=text.index(end)
    assert a<b,(start,end)
    return text[:a]+replacement+"\n"+text[b:]

def scene(html):
    assert html.count(CANONICAL)==1
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]

def apply(html):
    original=scene(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_selection_refine_v11_66.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_selection_refine_v11_66.css').read_text(encoding='utf-8')
    # v11.65 duplicated the original native outline. Its helper was parented to a
    # translated gizmo root and then offset *again*, creating the remote box.
    begin=" for(const mesh of meshes){\n  const outline=new THREE.BoxHelper(mesh,0xf3cf86);"
    end="\n}\nfunction atelierMeshToolbarPosition(){"
    assert html.count(begin)==1 and html.count(end)==1
    a=html.index(begin);b=html.index(end,a)
    html=html[:a]+"\n // Native Model Atelier already renders a selection BoxHelper.\n // Never add a second transformed helper to the gizmo group."+html[b:]
    html=replace_block(html,"function atelierMeshToolbarPosition(){","function atelierMeshToolbarRefresh(){",js)
    # Thin drag limit: v11.65 allowed 25 world units when zoomed out. Bound
    # total displacement per gesture to 0.45 units and use gentle pixel gain.
    html=once(html,"atelierMeshClamp(pixels*.007*orbit.distance,-25,25)",
         "atelierMeshClamp(pixels*.0009*Math.min(orbit.distance,8),-.45,.45)")
    # Recovery shortcuts live with the floating transform tools, not buried
    # in the original native inspector (which stays untouched).
    html=once(html,
         "'<div class=\"amq-count\" data-mesh-count></div>'+",
         "'<div class=\"amq-line amq-recovery\"><button type=\"button\" data-mesh-undo>↶ Undo</button>'+\n"+
         "  '<button type=\"button\" data-mesh-redo>↷ Redo</button><button type=\"button\" data-mesh-frame>◎ Frame mesh</button></div>'+"
         "\n  '<div class=\"amq-count\" data-mesh-count></div>'+")
    html=once(html,
         " if(density)density.hidden=!atelierMeshDensityOpen;",
         " if(density)density.hidden=!atelierMeshDensityOpen;\n"
         " const back=atelierMeshStrip.querySelector('[data-mesh-undo]');if(back)back.disabled=!undo.length;\n"
         " const forward=atelierMeshStrip.querySelector('[data-mesh-redo]');if(forward)forward.disabled=!redo.length;")
    html=once(html,
         " viewport.append(strip);atelierMeshStrip=strip;",
         " viewport.append(strip);atelierMeshStrip=strip;atelierMeshDialogInstall();")
    html=once(html,
         "  else if(btn.hasAttribute('data-mesh-hide'))atelierMeshHidden=true;",
         "  else if(btn.hasAttribute('data-mesh-undo'))atelierMeshHistoryShortcut(true);\n"
         "  else if(btn.hasAttribute('data-mesh-redo'))atelierMeshHistoryShortcut(false);\n"
         "  else if(btn.hasAttribute('data-mesh-frame'))atelierMeshFrameSelected();\n"
         "  else if(btn.hasAttribute('data-mesh-hide'))atelierMeshHidden=true;")
    # Save position through hide/open and project changes, not through the
    # model JSON. No personalized UI setting leaks into saved game projects.
    html=once(html,"  function close(){\n    atelierMeshGizmoCancel();",
         "  function close(){\n    atelierMeshDialogDrag=null;\n    atelierMeshGizmoCancel();")
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierMeshRefineV1166">'+css+'</style>\n</head>',1)
    for before,after in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.65','ENGINE · MAKER v11.66'),
        ('v11.65 · selection mesh gizmos','v11.66 · cyber mesh gizmos'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.65'","window.SWRLZ_FORGE_BUILD={version:'v11.66'"),
        ('<title>§wyrl§ Engine · Maker v11.65</title>','<title>§wyrl§ Engine · Maker v11.66</title>')
    ):
        html=once(html,before,after)
    assert scene(html)==original
    assert html.count(NEW)==1 and html.count('function atelierMeshDialogInstall()')==1
    assert "atelierMeshClamp(pixels*.007*orbit.distance,-25,25)" not in html
    return html
