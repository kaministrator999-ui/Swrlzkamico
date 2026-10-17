"""Opt-in native anatomical head/ear study. Preserve predecessor assets and save schemas."""
from pathlib import Path
import json
import re

def once(html, before, after):
    count = html.count(before)
    assert count == 1, ("Expected unique v11.19 injection point", before[:100], count)
    return html.replace(before, after, 1)

def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = json.loads((root / "scenes/model-atelier-festival-anatomy-v11-20.swyrl.json").read_text(encoding="utf-8"))
    assert len(scene["project"]["modelAtelier"]["parts"]) == 283
    encoded = json.dumps(scene, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    found = re.search(pattern, html, re.S)
    assert found, "Missing governed canonical Model Atelier source"
    html = html[:found.start()] + "const MODEL_ATELIER_CANONICAL_PROJECT=" + encoded + ";\n" + html[found.end():]

    module = (root / "runtime/model_atelier_anatomical_v11_20.js").read_text(encoding="utf-8") + "\n" + (root / "runtime/model_atelier_sculpt_brush_v11_20.js").read_text(encoding="utf-8")
    html = once(html, "  function refreshList(){", module + "\n  function refreshList(){")
    html = once(html, "function atelierHDGeometry(p){\n if(!p.hdFinish)return null;",
        "function atelierHDGeometry(p){\n if(p.anatomyStudy)return atelierAnatomicalHead(p);\n"
        " if(p.earStudy)return atelierAnatomicalEar(p);\n if(!p.hdFinish)return null;")
    html = once(html, "  function checkPart(p){", "  function checkPart(p){\n    if(!atelierAnatomyValid(p)||!atelierSculptValid(p))return false;")
    html = once(html, "if(key==='kind'){delete p.portraitFinish;",
        "if(key==='kind'){delete p.sculptBrushes;delete p.sculptVertexEdits;delete p.anatomyStudy;delete p.earStudy;delete p.portraitFinish;")
    html = once(html, "if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.portraitFinish=undefined;",
        "if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head'){values.portraitFinish=undefined;values.anatomyStudy=undefined;}")
    html = once(html, "atelierReferenceLegRefresh();atelierPortraitRefresh();",
        "atelierReferenceLegRefresh();atelierPortraitRefresh();atelierAnatomyRefresh();atelierSculptRefresh();")
    html = once(html, "atelierReferenceLegInstall();atelierPortraitInstall();",
        "atelierReferenceLegInstall();atelierPortraitInstall();atelierAnatomyInstall();atelierSculptInstall();")
    keys = ("jaw", "malar", "orbit", "nose", "chin", "temple")
    labels = ("Jaw and mandible", "Zygomatic cheeks", "Orbital recesses",
              "Bridge and nose tip", "Soft chin plane", "Temporal contour")
    def input_line(k,label,value):
        return '<label>' + label + '<input id="modelAtelierAnatomy' + k + '" type="number" min="0" max="1" step=".05" value="' + value + '"></label>'
    head = ''.join(input_line(k, lab, ".5") for k,lab in zip(keys, labels))
    ear = ''.join(input_line(k,lab,".6") for k,lab in
                 zip(("helix","concha","lobe"),("Helix rim","Concha bowl","Lobule relief")))
    deck = ('<section id="modelAtelierAnatomyEditor" hidden><h3>Anatomical stylization</h3>'
            '<div id="modelAtelierAnatomyHead"><p>Saved continuous head anatomy, not default SphereGeometry.</p>'
            + head + '<button id="modelAtelierAnatomyHeadApply">Apply anatomical head</button></div>'
            '<div id="modelAtelierAnatomyEar" hidden><p>Shaped outer ear relief.</p>'
            + ear + '<button id="modelAtelierAnatomyEarApply">Apply anatomical ear</button></div>'
            '</section>')
    brush = ('<section id="modelAtelierSculptBrush" hidden><h3>Vertex sphere brush · editable mesh</h3>'
             '<p>Choose mesh. Arm <b>Pick center</b> and tap its surface. Drag normally to orbit.</p>'
             '<div class="atelier-pair"><label>Action<select id="modelAtelierSculptBrushMode"><option value="extrude">Extrude outward</option>'
             '<option value="intrude">Intrude inward</option></select></label>'
             '<label>Falloff<select id="modelAtelierSculptBrushFalloff"><option value="smooth">Smooth quartic</option>'
             '<option value="soft">Soft Gaussian</option></select></label></div>'
             '<div class="atelier-pair"><label>Radius · local units<input id="modelAtelierSculptBrushRadius" type="number" min=".03" max="2.5" step=".05" value=".4"></label>'
             '<label>Depth · local units<input id="modelAtelierSculptBrushAmount" type="number" min="0" max=".5" step=".025" value=".12"></label></div>'
             '<div class="atelier-pair"><label>Full-strength inner radius<input id="modelAtelierSculptBrushPlateau" type="number" min="0" max="1" step=".1" value=".25"></label>'
             '<label>Edge taper strength<input id="modelAtelierSculptBrushTaper" type="number" min="0" max="1" step=".1" value=".5"></label></div>'
             '<label><input id="modelAtelierSculptBrushLevel" type="checkbox"> Level to brush plane (off keeps uneven relief)</label>'
             '<label><input id="modelAtelierSculptBrushHalf" type="checkbox"> Rotatable half-sphere (vertex group on one side)</label>'
             '<div class="atelier-pair"><label>Yaw · degrees<input id="modelAtelierSculptBrushYaw" type="number" min="-180" max="180" step="5" value="0"></label>'
             '<label>Pitch · degrees<input id="modelAtelierSculptBrushPitch" type="number" min="-180" max="180" step="5" value="0"></label></div>'
             '<label>Snap vertex displacement<select id="modelAtelierSculptBrushSnap">'
             '<option value="0">Off · continuous</option><option value=".001">0.001</option>'
             '<option value=".005">0.005</option><option value=".01">0.01</option></select></label>'
             '<strong>Brush center · local XYZ</strong><div class="atelier-transform">'
             '<input id="modelAtelierSculptBrushCenter0" aria-label="Sculpt center X" type="number" step=".05" value="0">'
             '<input id="modelAtelierSculptBrushCenter1" aria-label="Sculpt center Y" type="number" step=".05" value="-.70">'
             '<input id="modelAtelierSculptBrushCenter2" aria-label="Sculpt center Z" type="number" step=".05" value=".7">'
             '<strong>Extrusion axis · XYZ</strong>'
             '<input id="modelAtelierSculptBrushAxis0" aria-label="Brush normal X" type="number" step=".05" value="0">'
             '<input id="modelAtelierSculptBrushAxis1" aria-label="Brush normal Y" type="number" step=".05" value="0">'
             '<input id="modelAtelierSculptBrushAxis2" aria-label="Brush normal Z" type="number" step=".05" value="1"></div>'
             '<div class="atelier-inspector-actions"><button id="modelAtelierSculptBrushPick">Pick center on mesh</button>'
             '<button id="modelAtelierSculptBrushApply">Apply brush</button>'
             '<button id="modelAtelierSculptBrushUndoStroke">Remove last stroke</button></div>'
             '<section aria-label="Vertex mapping and drag gizmo"><h4>Vertex matrix · point and group edits</h4>'
             '<p>Choose grid U/V, show source vertices, tap a point, then drag the yellow gizmo. Use multi-selection to move groups.</p>'
             '<div class="atelier-pair"><label>Vertex map U<input id="modelAtelierSculptBrushGridU" type="number" min="16" max="256" step="8" value="192"></label>'
             '<label>Vertex map V<input id="modelAtelierSculptBrushGridV" type="number" min="12" max="192" step="8" value="128"></label></div>'
             '<button id="modelAtelierSculptBrushGridApply">Re-sample vertex grid</button>'
             '<div class="atelier-inspector-actions"><button id="modelAtelierSculptBrushVertexToggle">Show vertex map</button>'
             '<button id="modelAtelierSculptBrushVertexClear">Clear selected vertices</button>'
             '<button id="modelAtelierSculptBrushVertexUndo">Remove last vertex move</button></div>'
             '<label><input id="modelAtelierSculptBrushMulti" type="checkbox"> Select multiple points</label>'
             '<label>Gizmo drag axis<select id="modelAtelierSculptBrushVertexAxis"><option value="free">Free camera plane</option>'
             '<option value="x">Local X</option><option value="y">Local Y</option><option value="z">Local Z</option></select></label>'
             '<p id="modelAtelierSculptBrushVertexInfo"></p></section>'
             '<p id="modelAtelierSculptBrushInfo"></p>'
             '<p>Strokes affect nearby vertices with a smooth center-to-edge falloff; Undo and native JSON/OBJ export retain geometry.</p></section>')
    html = once(html, '<section id="modelAtelierPortraitFinish"', deck + brush + '<section id="modelAtelierPortraitFinish"')
    html = once(html, "  function pointerDown(e){if(e.button!==0)return;",
        "  function pointerDown(e){if(atelierSculptOnPointerDown(e))return;if(e.button!==0)return;")
    html = once(html, "  function pointerMove(e){\n    if(!pressed)return;",
        "  function pointerMove(e){\n    if(atelierSculptOnPointerMove(e))return;\n    if(!pressed)return;")
    html = once(html, "  function pointerUp(e){\n    if(!pressed)return;",
        "  function pointerUp(e){\n    if(atelierSculptOnPointerUp(e))return;\n    if(!pressed)return;")
    html = once(html, "const hits=raycaster.intersectObjects(meshes,false);if(atelierSculptPick(hits[0]))return;",
        "if(atelierSculptVertexPick(e))return;const hits=raycaster.intersectObjects(meshes,false);if(atelierSculptPick(hits[0]))return;")
    html = once(html, "  function close(){\n    if(!panel||panel.hidden)return;",
        "  function close(){\n    if(!panel||panel.hidden)return;atelierSculptOverlayClear();")
    assert "renderParts();refreshList();refreshInspector();" in html
    html = html.replace("renderParts();refreshList();refreshInspector();",
        "renderParts();atelierSculptOverlayRefresh();refreshList();refreshInspector();")
    html = once(html, "const mesh=new THREE.Mesh(geometry(p),material(p));",
        "const mesh=new THREE.Mesh(atelierSculptApply(geometry(p),p),material(p));")
    html = once(html, "const hits=raycaster.intersectObjects(meshes,false);select(hits[0]?.object?.userData?.atelierId||null);",
        "const hits=raycaster.intersectObjects(meshes,false);if(atelierSculptPick(hits[0]))return;select(hits[0]?.object?.userData?.atelierId||null);")
    # When surface-fitting lips/brows to an edited head, use the actual sculpt
    # rather than the unmodified procedural cranial surface.
    html = once(html, "const g=atelierHDGeometry(head),material=",
        "const g=atelierSculptApply(atelierHDGeometry(head),head),material=")
    html = once(html, "v11.19 · portrait & body polish", "v11.20 · anatomical face study")
    html = html.replace("Maker v11.19", "Maker v11.20").replace("MAKER v11.19", "MAKER v11.20")
    html = html.replace("version:'v11.19'", "version:'v11.20'").replace("version:11.19", "version:11.20")
    html = once(html, "SWYRL_ENGINE_DEPLOY_MARKER: V11_19_PORTRAIT_BODY_POLISH",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_FACE_STUDY")
    return html
