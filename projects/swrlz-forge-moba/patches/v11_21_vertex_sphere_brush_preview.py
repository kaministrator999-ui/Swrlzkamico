"""Optional native vertex sculpt brush layered on the officially sealed v11.20 head."""
from pathlib import Path

def once(html, before, after):
    n=html.count(before)
    assert n==1, ("Missing or duplicate v11.20 injection point", before[:120], n)
    return html.replace(before,after,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_HEAD" in html
    module=(root/"runtime/model_atelier_sculpt_brush_v11_21.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_brush_ops_v11_27.js").read_text(encoding="utf-8")+"\\n"+(root/"runtime/model_atelier_viewport_v11_21.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_reference_studio_v11_22.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_surface_targeting_v11_22.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_surface_lasso_v11_22.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_local_refinement_v11_23.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_face_sheet_v11_23.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_numeric_gizmos_v11_23.js").read_text(encoding="utf-8")+"\n"+(root/"runtime/model_atelier_face_volume_v11_23.js").read_text(encoding="utf-8")
    html=once(html, "  function refreshList(){", module+"\n  function refreshList(){")
    html=once(html,"  function geometry(part){",
         "  function geometry(part){\n    if(part.kind==='faceSheet')return atelierFaceSheetGeometry(part);")
    html=once(html,"function material(part){\n if(!part.hdFinish)",
         "function material(part){\n if(part.kind==='faceSheet')return atelierFaceSheetMaterial(part);\n if(!part.hdFinish)")
    html=once(html,"  function checkPart(p){",
         "  function checkPart(p){\n    if(!atelierSculptValid(p)||!atelierFaceSheetValid(p))return false;")
    html=once(html,"if(key==='kind'){delete p.headAnatomy;delete p.portraitFinish;",
         "if(key==='kind'){delete p.sculptBrushes;delete p.sculptVertexEdits;delete p.sculptLassos;delete p.refinementLayers;delete p.faceSheet;delete p.headAnatomy;delete p.portraitFinish;")
    html=once(html,"atelierHeadAnatomyRefresh();",
         "atelierHeadAnatomyRefresh();atelierSculptRefresh();atelierViewportControlsRefresh();atelierRefPaint();atelierFaceSheetRefresh();")
    html=once(html,"atelierHeadAnatomyInstall();",
         "atelierHeadAnatomyInstall();atelierSculptInstall();atelierViewportInstall();atelierRefInstall();atelierFaceSheetInstall();")
    brush = ('<fieldset id="modelAtelierFaceSheetControls" hidden aria-label="Editable UV image face sheet">'
             '<legend>Triangulated image face sheet · UV preserved</legend>'
             '<p>This is an opt-in editable surface created from a reference. It does NOT replace the original head or automatically build a complete skull.</p>'
             '<label>Silhouette<select id="modelAtelierFaceSheetShape"><option value="oval">Oval face outline</option>'
             '<option value="rectangle">Rectangular image crop</option></select></label>'
             '<div class="atelier-pair"><label>Segments / grid U<input id="modelAtelierFaceSheetGridU" type="number" min="8" max="128" step="1" value="48"></label>'
             '<label>Rings / grid V<input id="modelAtelierFaceSheetGridV" type="number" min="4" max="128" step="1" value="20"></label></div>'
             '<div class="atelier-pair"><label>Crop X (0–1)<input id="modelAtelierFaceSheetCropX" type="number" min="0" max="1" step=".01" value="0"></label>'
             '<label>Crop Y (0–1)<input id="modelAtelierFaceSheetCropY" type="number" min="0" max="1" step=".01" value="0"></label>'
             '<label>Crop W (0–1)<input id="modelAtelierFaceSheetCropW" type="number" min=".03" max="1" step=".01" value="1"></label>'
             '<label>Crop H (0–1)<input id="modelAtelierFaceSheetCropH" type="number" min=".03" max="1" step=".01" value="1"></label></div>'
             '<button type="button" id="modelAtelierFaceSheetApply">Update UV mesh / crop</button>'
             '<label>Closed head depth (0 = open sheet, oval only)<input id="modelAtelierFaceSheetHeadDepth" type="number" step=".05" min="0" max="2" value="0"></label>'
             '<label><input id="modelAtelierFaceSheetUVHeatmap" type="checkbox"> Show UV distortion heatmap (shaded viewport)</label>'
             '<p id="modelAtelierFaceSheetUVStats" role="status"></p>'
             '<p id="modelAtelierFaceSheetInfo" role="status"></p></fieldset>'
             '<section id="modelAtelierSculptBrush" hidden><h3>Vertex sphere brush · editable mesh</h3>'
             '<p>Choose mesh. Arm <b>Pick center</b> and tap its surface. Drag normally to orbit.</p>'
             '<div class="atelier-pair"><label>Action<select id="modelAtelierSculptBrushMode"><option value="extrude">Extrude outward</option>'
             '<option value="intrude">Intrude inward</option>'
             '<option value="smooth">Smooth surface vertices</option>'
             '<option value="flatten">Flatten toward brush plane</option>'
             '<option value="inflate">Inflate along vertex normals</option>'
             '<option value="pinch">Pinch toward brush center</option>'
             '<option value="translate">Translate along brush direction</option></select></label>'
             '<label>Falloff<select id="modelAtelierSculptBrushFalloff"><option value="smooth">Smooth quartic</option>'
             '<option value="soft">Soft Gaussian</option>'
             '<option value="flat">Flat plateau</option>'
             '<option value="sharp">Sharp taper</option></select></label></div>'
             '<label><input id="modelAtelierSculptBrushMirrorX" type="checkbox"> Mirror brush across object-local X (retain base asymmetry)</label>'
             '<div class="atelier-pair"><label>Radius · local units<input id="modelAtelierSculptBrushRadius" type="number" min=".03" max="2.5" step=".05" value=".4"></label>'
             '<label>Depth · local units<input id="modelAtelierSculptBrushAmount" type="number" min="0" max=".5" step=".025" value=".12"></label></div>'
             '<fieldset aria-label="Surface-aware brush selection"><legend>Surface targeting · avoid opposite head shell</legend>'
             '<label>Selection mode<select id="modelAtelierSculptBrushSurfaceMode">'
             '<option value="front">Front-facing surface (default)</option>'
             '<option value="connected">Connected surface · geodesic</option>'
             '<option value="inside">Inside shell · opposite-facing normals</option>'
             '<option value="through">Through-volume · both sides intentionally</option></select></label>'
             '<div class="atelier-pair"><label>Selection radius<input id="modelAtelierSculptBrushSelectRadius" type="number" min=".03" max="2.5" step=".05" value=".4"></label>'
             '<label>Falloff-center offset U<input id="modelAtelierSculptBrushOffsetU" type="number" min="-.5" max=".5" step=".025" value="0"></label>'
             '<label>Falloff-center offset V<input id="modelAtelierSculptBrushOffsetV" type="number" min="-.5" max=".5" step=".025" value="0"></label></div>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierSculptBrushPreview">Preview selected surface</button>'
             '<button type="button" id="modelAtelierSculptBrushPreviewClear">Hide preview</button></div>'
             '<p id="modelAtelierSurfaceSelectionInfo" role="status">Pick a surface point for the highlighted footprint.</p></fieldset>'
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
             '<fieldset id="modelAtelierLassoTools" aria-label="Editable surface lasso and boundary pins">'
             '<legend>Surface lasso · 📌 editable boundary pins</legend>'
             '<p>Tap polygon points or trace freehand on the selected mesh; both create editable surface-attached 📌 boundary pins. The smaller 📍 pins move mesh vertices separately.</p>'
             '<label>Region name<input id="modelAtelierLassoName" type="text" maxlength="90" value="Face detail"></label>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierLassoStart">Start polygon lasso</button>'
             '<button type="button" id="modelAtelierLassoStartFreehand">Trace freehand</button>'
             '<button type="button" id="modelAtelierLassoFinish">Finish polygon</button>'
             '<button type="button" id="modelAtelierLassoCancel">Cancel draft</button></div>'
             '<label>Selected region<select id="modelAtelierLassoRegion" aria-label="Saved editable lasso regions"></select></label>'
             '<label>Boundary pin<select id="modelAtelierLassoPinIndex" aria-label="Selected boundary pin"></select></label>'
             '<label>Precise boundary XYZ · local object coordinates (snapped to real triangles)</label>'
             '<div class="atelier-transform"><input id="modelAtelierLassoPinXYZ0" type="number" aria-label="Boundary pin X" step=".01" value="0">'
             '<input id="modelAtelierLassoPinXYZ1" type="number" aria-label="Boundary pin Y" step=".01" value="0">'
             '<input id="modelAtelierLassoPinXYZ2" type="number" aria-label="Boundary pin Z" step=".01" value="0"></div>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierLassoAddXYZ">Add 📌 from XYZ</button>'
             '<button type="button" id="modelAtelierLassoMoveXYZ">Move selected 📌 to XYZ</button></div>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierLassoInsertPin">Add 📌 pin after selected</button>'
             '<button type="button" id="modelAtelierLassoDeletePin">Remove selected 📌 pin</button></div>'
             '<div class="atelier-pair"><label>Normal displacement<input id="modelAtelierLassoMorph" type="number" step=".01" min="-.35" max=".35" value="0"></label>'
             '<label>Feather border<input id="modelAtelierLassoFeather" type="number" step=".01" min="0" max=".3" value=".04"></label></div>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierLassoApplyMorph">Apply region morph</button>'
             '<button type="button" id="modelAtelierLassoToggle">Enable / disable region</button>'
             '<button type="button" id="modelAtelierLassoDeleteRegion">Delete region</button></div>'
             '<p id="modelAtelierLassoInfo" role="status"></p>'
             '<p>📌 Region pins change selection boundaries without moving mesh vertices until an explicit morph or refinement action.</p></fieldset>'
             '<fieldset id="modelAtelierRefineTools" aria-label="Local mesh refinement layers">'
             '<legend>Local detail density · conforming triangles</legend>'
             '<p>Add actual triangles inside the selected surface lasso. Neighbor edges split automatically so adjoining polygons have no T-junctions.</p>'
             '<label>Local density<select id="modelAtelierRefineLevel">'
             '<option value="1">1 level · approximately 4× selected triangles</option>'
             '<option value="2">2 levels · approximately 16× selected triangles</option></select></label>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierRefinePreview">Preview triangles / vertex budget</button>'
             '<button type="button" id="modelAtelierRefineAdd">Apply local refinement</button></div>'
             '<p id="modelAtelierRefineBudget" role="status" aria-live="polite">Preview measured local topology before applying.</p>'
             '<label>Saved detail layer<select id="modelAtelierRefineLayer"></select></label>'
             '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierRefineToggle">Show / hide detail</button>'
             '<button type="button" id="modelAtelierRefineUp">Move detail earlier</button>'
             '<button type="button" id="modelAtelierRefineRemove">Remove layer</button></div>'
             '<p id="modelAtelierRefineStats" role="status"></p>'
             '<p>New topology is evaluated from the unchanged native base and saved with the project; Undo can restore the previous detail stack. UVs and vertex colors are interpolated.</p></fieldset>'
             '<section aria-label="Vertex mapping and drag gizmo"><h4>Vertex matrix · point and group edits</h4>'
             '<p>Choose grid U/V, show source vertices, tap a point, then drag the yellow gizmo. Use multi-selection to move groups.</p>'
             '<div class="atelier-pair"><label>Vertex map U<input id="modelAtelierSculptBrushGridU" type="number" min="16" max="256" step="8" value="192"></label>'
             '<label>Vertex map V<input id="modelAtelierSculptBrushGridV" type="number" min="12" max="192" step="8" value="128"></label></div>'
             '<button id="modelAtelierSculptBrushGridApply">Re-sample vertex grid</button>'
             '<label>Pick vertex indices (comma-separated)<input id="modelAtelierSculptBrushIndices" type="text" value="" placeholder="0, 55, 106"></label>'
             '<button id="modelAtelierSculptBrushIndicesApply">Select these vertices</button>'
             '<div class="atelier-inspector-actions"><button id="modelAtelierSculptBrushVertexToggle">Show vertex map</button>'
             '<button id="modelAtelierSculptBrushVertexClear">Clear selected vertices</button>'
             '<button id="modelAtelierSculptBrushVertexUndo">Remove last vertex move</button></div>'
             '<label><input id="modelAtelierSculptBrushMulti" type="checkbox"> Select multiple points</label>'
             '<label>Gizmo drag axis<select id="modelAtelierSculptBrushVertexAxis"><option value="free">Free camera plane</option>'
             '<option value="x">Local X</option><option value="y">Local Y</option><option value="z">Local Z</option></select></label>'
             '<fieldset id="modelAtelierGroupTools" aria-label="Precise numeric mesh vertex transforms">'
             '<legend>📍 Vertex group transforms · Codex controls</legend>'
             '<label>Operation<select id="modelAtelierGroupMode"><option value="translate">Translate</option>'
             '<option value="rotate">Rotate</option><option value="scale">Scale</option></select></label>'
             '<label>Space<select id="modelAtelierGroupSpace"><option value="object">Object-local</option>'
             '<option value="world">World</option><option value="surface">Average surface-normal</option></select></label>'
             '<div class="atelier-transform"><input id="modelAtelierGroupValue0" type="number" aria-label="Vertex group X transform" step=".01" value="0">'
             '<input id="modelAtelierGroupValue1" type="number" aria-label="Vertex group Y transform" step=".01" value="0">'
             '<input id="modelAtelierGroupValue2" type="number" aria-label="Vertex group Z transform" step=".01" value="0"></div>'
             '<p id="modelAtelierGroupHelp">Translation XYZ in local or world units (±0.5)</p>'
             '<button type="button" id="modelAtelierGroupApply">Apply numeric group transform</button>'
             '<small>Works on selected source vertices; refined overlay layers must be disabled to protect source indices.</small>'
             '</fieldset>'
             '<p id="modelAtelierSculptBrushVertexInfo"></p></section>'
             '<p id="modelAtelierSculptBrushInfo"></p>'
             '<p>Strokes affect nearby vertices with a smooth center-to-edge falloff; Undo and native JSON/OBJ export retain geometry.</p></section>')
    html=once(html,'<section id="modelAtelierPortraitFinish"',brush+'<section id="modelAtelierPortraitFinish"')
    html=once(html,"const mesh=new THREE.Mesh(geometry(p),material(p));",
         "const mesh=new THREE.Mesh(atelierSculptApply(geometry(p),p),material(p));atelierViewModeApply(mesh,p);")
    html=once(html, "const h=Math.cos(orbit.pitch),focusY=model()?.assemblies?2.8:2.35,target=atelierDetailTarget||new THREE.Vector3(0,focusY,0);",
         "const h=Math.cos(orbit.pitch),focusY=model()?.assemblies?2.8:2.35,target=(atelierDetailTarget||new THREE.Vector3(0,focusY,0)).clone().add(atelierCameraPan);")
    html=once(html, "camera.lookAt(target);atelierHDDirty=true;",
         "camera.lookAt(target);atelierHDDirty=true;atelierViewportCameraInfoUpdate();")
    html=once(html, "atelierDetailTarget=box.getCenter(new THREE.Vector3());",
         "atelierCameraPan.set(0,0,0);atelierDetailTarget=box.getCenter(new THREE.Vector3());")
    html=once(html, "action('ResetCamera',()=>{atelierDetailTarget=null;orbit=",
         "action('ResetCamera',()=>{atelierDetailTarget=null;atelierCameraPan.set(0,0,0);orbit=")
    nav = ('<div id="modelAtelierViewportModes" class="atelier-viewbar" role="toolbar" aria-label="3D viewport display and camera controls">'
           '<label>Render mode<select id="modelAtelierViewportMode" aria-label="Mesh display mode">'
           '<option value="shaded">Shaded</option><option value="overlay">Shaded + wireframe</option>'
           '<option value="wireframe">Wireframe</option><option value="xray">X-Ray</option></select></label>'
           '<label>Target<select id="modelAtelierViewportScope" aria-label="Display mode target">'
           '<option value="all">All meshes</option><option value="selected">Selected mesh</option></select></label>'
           '<label class="atelier-display-switch"><input id="modelAtelierViewportColors" aria-label="Show original mesh colors" type="checkbox" checked> Colors</label>'
           '<label class="atelier-display-switch"><input id="modelAtelierViewportTextures" aria-label="Show original mesh textures" type="checkbox" checked> Textures</label>'
           '<label class="atelier-display-switch"><input id="modelAtelierViewportWireContrast" aria-label="Use high contrast wireframe" type="checkbox" checked> Contrast wire</label>'
           '<label>Wire tint<input id="modelAtelierViewportWireTint" aria-label="Wireframe and overlay line color" type="color" value="#d9f5ff"></label>'
           '<div class="atelier-view-presets" aria-label="Camera view directions">'
           '<button type="button" data-at-view="front">Front</button><button type="button" data-at-view="right">Right</button>'
           '<button type="button" data-at-view="left">Left</button><button type="button" data-at-view="back">Back</button>'
           '<button type="button" data-at-view="top">Top</button><button type="button" data-at-view="bottom">Bottom</button>'
           '<button type="button" data-at-view="three">3/4</button></div>'
           '<button type="button" id="modelAtelierViewportPanReset">Center pan</button>'
           '<fieldset class="atelier-clip-tools" aria-label="Camera clipping and interior inspection">'
           '<legend>Interior / clipping</legend>'
           '<label>Near plane<input id="modelAtelierViewportClipNear" type="number" step=".005" min=".005" max=".5" value=".1"></label>'
           '<label>Far plane<input id="modelAtelierViewportClipFar" type="number" step="1" min="4" max="300" value="100"></label>'
           '<button type="button" id="modelAtelierViewportClipApply">Apply clip planes</button>'
           '<button type="button" id="modelAtelierViewportInsideEnter">Inspect inside selected</button>'
           '<button type="button" id="modelAtelierViewportInsideExit" disabled>Exit interior</button>'
           '</fieldset>'
           '</div><p id="modelAtelierViewportNavHint" class="atelier-view-hint">1 finger orbit · 2 fingers pinch to zoom or slide to pan · Shift-drag pan</p>')
    html=once(html,'<div class="atelier-viewport-controls"><button id="modelAtelierZoomIn"',nav+'<div class="atelier-viewport-controls"><button id="modelAtelierZoomIn"')
    html=html.replace('</head>',"""<style>
.model-atelier .atelier-viewbar{position:relative;z-index:180;pointer-events:auto;display:flex;flex-wrap:wrap;gap:6px;align-items:end;padding:8px;background:#131c30;border:1px solid #37435d;border-radius:10px;margin:5px 0}
.model-atelier .atelier-viewbar label{display:flex;flex-direction:column;gap:3px;font-size:11px;color:#cbdaeb}
.model-atelier .atelier-clip-tools{display:flex;gap:4px;align-items:flex-end;flex-wrap:wrap;border:1px solid #516580;border-radius:8px;padding:5px;margin:0;max-width:100%}
.model-atelier .atelier-clip-tools legend{font-size:10px;color:#ddedfc}
.model-atelier .atelier-clip-tools input{width:65px;background:#202c42;color:#f3f7ff;border:1px solid #7283a0;border-radius:6px;padding:5px;font-size:12px}
.model-atelier .atelier-viewbar select{background:#202c42;color:#f3f7ff;border:1px solid #7283a0;border-radius:6px;padding:6px;font-size:12px;max-width:168px}
.model-atelier .atelier-view-presets{display:flex;gap:4px;flex-wrap:wrap}
.model-atelier .atelier-display-switch{display:flex;flex-direction:row;align-items:center;gap:4px;padding:6px 2px;font-size:12px;min-height:32px;white-space:nowrap}
.model-atelier .atelier-display-switch input{width:15px;height:15px;accent-color:#46d0e4;flex:0 0 auto}
.model-atelier .atelier-viewbar input[type=color]{width:38px;height:30px;padding:1px;border-radius:5px;border:1px solid #7283a0;background:#202c42}

.model-atelier .atelier-viewbar button{border-radius:6px;padding:6px 9px;min-height:32px;background:#293b56;color:#fff;border:1px solid #5b7494;font-size:12px}
.model-atelier .atelier-viewbar button:focus-visible,.model-atelier .atelier-viewbar select:focus-visible{outline:2px solid #5ce2ef}
.model-atelier #modelAtelierSculptBrush fieldset{border:1px solid #496f8b;border-radius:8px;margin:6px 0;padding:7px}
.model-atelier #modelAtelierSculptBrush fieldset legend{font-size:12px;color:#9ce9f3}
.model-atelier #modelAtelierSculptBrush fieldset label{display:block;padding:4px}
.model-atelier .atelier-view-hint{position:relative;z-index:70;pointer-events:none;font-size:11px;color:#cad7ed;padding:2px 5px;margin:0 0 5px}
@media(max-width:600px){.model-atelier .atelier-viewbar{gap:4px;padding:5px}.model-atelier .atelier-view-presets{max-width:100%;overflow-x:auto;flex-wrap:nowrap}.model-atelier .atelier-viewbar button{white-space:nowrap}}
</style></head>""",1)
    # Treat imported references as portable native model state, using the
    # exact same Undo/Redo transaction snapshots as mesh parts.
    # v11.13 already saves the entire native model (including assemblies and
    # pose frames) on Undo/Redo. Preserve that established implementation and
    # only refresh the reference overlay after a restored snapshot.
    html=once(html,
       "dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;signalEdited();atelierAssemblyRefresh();",
       "dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;signalEdited();atelierAssemblyRefresh();atelierRefTransient.clear();atelierRefPaint();")
    # v11.11 + v11.13 import already validates and restores poses and
    # attachments. Add reference validation BEFORE checkpoint/mutation, then
    # restore the reference set without clobbering any existing payloads.
    html=once(html,"      const assemblies=atelierValidateAssemblies(source.assemblies,source.parts);",
       "      const importedRefs=atelierRefReadImport(source);\n      const assemblies=atelierValidateAssemblies(source.assemblies,source.parts);")
    html=once(html,
       "selection=null;signalEdited();atelierRefreshPoseChoices();atelierAssemblyRefresh();status('Validated model, poses and independent attachments imported. Undo restores all model data.');",
       "model().references=importedRefs.references;model().referenceLayout=importedRefs.referenceLayout;atelierRefTransient.clear();selection=null;signalEdited();atelierRefreshPoseChoices();atelierAssemblyRefresh();atelierRefPaint();status('Validated model, poses, attachments and portable reference images imported. Undo restores all model data.');")
    # Reference studio dock is an overlay inside the interactive viewport,
    # not a replacement for the user's existing wireframe/pan toolbar.
    studio = ('<div id="modelAtelierReferenceDock" class="atelier-ref-dock" hidden role="region" aria-label="Floating image references">'
      '<div id="modelAtelierReferenceHandle" class="atelier-ref-handle"><strong>🖼 Reference views</strong><img id="modelAtelierReferenceThumbnail" alt="Tap to expand image reference" hidden>'
      '<div><button id="modelAtelierReferenceCollapse" type="button">Minimize</button>'
      '<button id="modelAtelierReferenceClose" type="button" aria-label="Close reference studio">×</button></div></div>'
      '<div id="modelAtelierReferenceBody" class="atelier-ref-body">'
      '<label class="atelier-ref-import">Add front/side images<input id="modelAtelierReferenceFile" type="file" multiple accept="image/jpeg,image/png,image/webp"></label>'
      '<div class="atelier-ref-tabs" id="modelAtelierReferenceTabs"></div>'
      '<button id="modelAtelierFaceSheetCreate" type="button">Create sculptable UV face sheet</button>'
      '<p id="modelAtelierReferenceEmpty" class="atelier-ref-empty">Add up to 4 local JPEG, PNG or WebP references. Images save with your model JSON.</p>'
      '<div id="modelAtelierReferenceDetail">'
      '<div id="modelAtelierReferenceImageFrame" class="atelier-ref-imageframe" title="Drag inside image to pan">'
      '<img id="modelAtelierReferenceImage" alt="Image reference" draggable="false"></div>'
      '<p id="modelAtelierReferenceName" class="atelier-ref-name"></p>'
      '<div class="atelier-ref-controls"><label>Angle<select id="modelAtelierReferenceAngle">'
      '<option value="front">Front</option><option value="right">Right profile</option><option value="left">Left profile</option>'
      '<option value="three">Three-quarter</option><option value="back">Back</option><option value="top">Top</option>'
      '<option value="free">Other</option></select></label>'
      '<button id="modelAtelierReferenceCamera" type="button">Match camera</button></div>'
      '<label>Image zoom<input id="modelAtelierReferenceZoom" type="range" min=".25" max="5" step=".05" value="1"></label>'
      '<label>Opacity<input id="modelAtelierReferenceOpacity" type="range" min=".15" max="1" step=".05" value=".85"></label>'
      '<div class="atelier-ref-buttons"><button id="modelAtelierReferenceRotateLeft" type="button">↶ 90°</button>'
      '<button id="modelAtelierReferenceRotateRight" type="button">↷ 90°</button>'
      '<button id="modelAtelierReferenceFlip" type="button">Mirror</button>'
      '<button id="modelAtelierReferenceReset" type="button">Reset</button></div>'
      '<div class="atelier-ref-buttons"><label><input id="modelAtelierReferenceShow" type="checkbox" checked> Visible</label>'
      '<button id="modelAtelierReferenceDelete" type="button">Remove image</button></div></div>'
      '<small id="modelAtelierReferenceCount">0/4 images</small></div></div>')
    html=once(html,'<div id="modelAtelierViewport" class="atelier-viewport" aria-label="Interactive 3D model viewport"></div>',
       '<div id="modelAtelierViewport" class="atelier-viewport" aria-label="Interactive 3D model viewport">'+studio+'</div>')
    html=once(html,'<button type="button" id="modelAtelierViewportPanReset">Center pan</button>',
       '<button type="button" id="modelAtelierViewportPanReset">Center pan</button>'
       '<button type="button" id="modelAtelierReferenceToggle" aria-expanded="false">🖼 References</button>')
    html=html.replace('</head>',"""<style>
.model-atelier .atelier-ref-dock{position:absolute;z-index:150;top:12px;left:12px;width:min(255px,calc(100% - 15px));max-height:calc(100% - 12px);overflow:auto;background:#17233cee;color:#e5f0ff;border:1px solid #70a0c3;border-radius:11px;box-shadow:0 5px 18px #0009;touch-action:pan-y}
.model-atelier .atelier-ref-dock[hidden]{display:none!important}
.model-atelier .atelier-ref-handle{padding:8px;display:flex;align-items:center;justify-content:space-between;gap:6px;background:#264161;cursor:move;touch-action:none;user-select:none}
.model-atelier .atelier-ref-handle div{display:flex;gap:3px}
.model-atelier .atelier-ref-handle img{width:36px;height:30px;border:1px solid #83b9d1;border-radius:5px;object-fit:cover;cursor:pointer}
.model-atelier .atelier-ref-collapsed .atelier-ref-handle strong{display:none}
.model-atelier .atelier-ref-handle button{padding:3px 6px;min-height:27px;font-size:11px;border:1px solid #6f93b6;border-radius:6px;background:#334b6b;color:#fff}
.model-atelier .atelier-ref-body{padding:8px;display:grid;gap:6px;font-size:11px}
.model-atelier .atelier-ref-body label{font-size:11px;display:flex;flex-direction:column;gap:3px}
.model-atelier .atelier-ref-import{padding:5px;background:#283d59;border-radius:6px}
.model-atelier .atelier-ref-import input{max-width:100%;font-size:11px;color:#fff}
.model-atelier .atelier-ref-tabs{display:flex;gap:4px;overflow-x:auto}
.model-atelier .atelier-ref-tabs button{font-size:10px;white-space:nowrap;flex:0 0 auto;padding:4px}
.model-atelier .atelier-ref-tabs .atelier-ref-active{background:#31698d;border-color:#6be4f4}
.model-atelier .atelier-ref-body button{background:#2c4564;color:#fff;border:1px solid #6084a4;border-radius:5px;padding:5px 6px}
.model-atelier .atelier-ref-imageframe{height:175px;position:relative;display:grid;place-items:center;overflow:hidden;background:repeating-conic-gradient(#34415a 0 25%,#202b40 0 50%) 50%/18px 18px;touch-action:none;cursor:grab}
.model-atelier .atelier-ref-imageframe img{width:100%;height:100%;object-fit:contain;pointer-events:none;user-select:none;transform-origin:center}
.model-atelier .atelier-ref-buttons,.model-atelier .atelier-ref-controls{display:flex;gap:4px;flex-wrap:wrap;align-items:center}
.model-atelier .atelier-ref-controls select{width:110px;background:#263a55;color:#fff;border-radius:6px}
.model-atelier .atelier-ref-body input[type=range]{width:100%;accent-color:#58cee4}
.model-atelier .atelier-ref-name{margin:0;color:#cad6e9;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.model-atelier .atelier-ref-collapsed{width:145px;max-height:50px;overflow:hidden}
.model-atelier .atelier-ref-collapsed .atelier-ref-body{display:none}
@media(max-width:600px){.model-atelier .atelier-ref-dock{width:min(230px,calc(100% - 14px))}.model-atelier .atelier-ref-imageframe{height:128px}.model-atelier .atelier-ref-collapsed{width:145px}}
</style></head>""",1)
    html=once(html,"  function pointerDown(e){if(e.button!==0)return;",
         "  function pointerDown(e){if(atelierSculptOnPointerDown(e))return;if(e.button!==0)return;")
    html=once(html,"  function pointerMove(e){\n    if(!pressed)return;",
         "  function pointerMove(e){\n    if(atelierSculptOnPointerMove(e))return;\n    if(!pressed)return;")
    html=once(html,"  function pointerUp(e){\n    if(!pressed)return;",
         "  function pointerUp(e){\n    if(atelierSculptOnPointerUp(e))return;\n    if(!pressed)return;")
    html=once(html, "  function pointerDown(e){if(atelierSculptOnPointerDown(e))return;",
         "  function pointerDown(e){if(atelierCameraPointerDown(e))return;if(atelierLassoPointerDown(e))return;if(atelierSculptOnPointerDown(e))return;")
    html=once(html, "  function pointerMove(e){\n    if(atelierSculptOnPointerMove(e))return;",
         "  function pointerMove(e){\n    if(atelierCameraPointerMove(e))return;\n    if(atelierLassoPointerMove(e))return;\n    if(atelierSculptOnPointerMove(e))return;")
    html=once(html, "  function pointerUp(e){\n    if(atelierSculptOnPointerUp(e))return;",
         "  function pointerUp(e){\n    if(atelierCameraPointerUp(e))return;\n    if(atelierLassoPointerUp(e))return;\n    if(atelierSculptOnPointerUp(e))return;")
    html=once(html,"renderer.domElement.addEventListener('pointercancel',()=>pressed=null);",
         "renderer.domElement.addEventListener('pointercancel',e=>{atelierLassoPointerCancel(e);atelierCameraPointerCancel(e);if(atelierSculptDrag){atelierSculptDrag=null;renderParts();}pressed=null;});")
    html=once(html, "mesh.geometry?.dispose();if(!mesh.material?.userData?.atelierHDMaterial)mesh.material?.dispose();",
         "for(const child of mesh.children)if(child.isMesh&&child.userData.atelierHelper)child.material?.dispose();mesh.geometry?.dispose();if(!mesh.material?.userData?.atelierHDMaterial)mesh.material?.dispose();")
    html=once(html,"function onWheel(e){e.preventDefault();orbit.distance=Math.min(22,Math.max(atelierDetailTarget?.4:3.7,",
         "function onWheel(e){e.preventDefault();orbit.distance=Math.min(24,Math.max(atelierCameraMinDistance(),")
    html=once(html,"action('ZoomIn',()=>{orbit.distance=Math.max(atelierDetailTarget?.4:3.7,",
         "action('ZoomIn',()=>{orbit.distance=Math.max(atelierCameraMinDistance(),")
    html=once(html,
         "const hits=raycaster.intersectObjects(meshes,false);select(hits[0]?.object?.userData?.atelierId||null);",
         "if(atelierSculptVertexPick(e))return;const hits=raycaster.intersectObjects(meshes,false);if(atelierLassoPick(hits[0]))return;if(atelierSculptPick(hits[0]))return;select(hits[0]?.object?.userData?.atelierId||null);")
    html=once(html,"  function close(){\n    if(!panel||panel.hidden)return;",
         "  function close(){\n    atelierSurfacePreviewClear();atelierLassoOverlayClear();if(!panel||panel.hidden)return;atelierSculptOverlayClear();")
    key="renderParts();refreshList();refreshInspector();"
    assert key in html
    html=html.replace(key,"renderParts();atelierSculptOverlayRefresh();atelierLassoOverlayRefresh();refreshList();refreshInspector();")
    html=once(html,"const g=atelierHDGeometry(head),material=",
         "const g=atelierSculptApply(atelierHDGeometry(head),head),material=")
    html=once(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_HEAD",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW")
    html=html.replace("Maker v11.20","Maker v11.21 preview")
    return html
