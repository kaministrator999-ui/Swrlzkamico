"""Keep X-Ray/wireframe editor state stable across sculpt-undo and improve menu spacing."""
import hashlib
import json
CSS = "\n/* §E v11.105: room to read; sizing/drag/history remain owned by earlier layers. */\n@media (max-width:980px), (pointer:coarse) {\n .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector,\n .model-atelier.atelier-tools-docked.atelier-mobile-upgrade:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {\n  width:min(415px,calc(100vw - 24px))!important;\n  max-width:calc(100vw - 24px)!important;\n  gap:12px!important;\n }\n .model-atelier.atelier-tools-docked.se-mobile-inspector-expanded:not(.atelier-tools-closed) .atelier-inspector,\n .model-atelier.atelier-tools-docked.atelier-mobile-upgrade.se-mobile-inspector-expanded:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {\n  width:min(465px,calc(100vw - 20px))!important;\n  max-width:calc(100vw - 20px)!important;\n }\n .model-atelier .atelier-inspector #modelAtelierInspectorControls{\n  gap:14px!important;\n }\n .model-atelier .atelier-inspector #modelAtelierSculptBrush{\n  padding:13px!important;\n  gap:13px!important;\n }\n .model-atelier .atelier-inspector fieldset{\n  padding:13px!important;\n  margin:12px 0!important;\n }\n .model-atelier .atelier-inspector label{\n  font-size:14px!important;\n  line-height:1.5!important;\n  gap:8px!important;\n  margin-bottom:5px!important;\n }\n .model-atelier .atelier-inspector :is(.atelier-pair,.atelier-transform){\n  column-gap:12px!important;row-gap:13px!important;\n }\n .model-atelier .atelier-inspector :is(p,small) {\n  font-size:13px!important;\n  line-height:1.55!important;\n  margin:8px 0!important;\n }\n .model-atelier .atelier-inspector :is(h3,h4){\n  margin:9px 0!important;\n  line-height:1.45!important;\n }\n .model-atelier .atelier-inspector :is(.atelier-inspector-actions,.atelier-sculpt-actions){\n  gap:10px!important;\n  margin:12px 0!important;\n }\n .model-atelier .atelier-inspector :is(.atelier-inspector-actions,.atelier-sculpt-actions) button {\n  min-height:48px!important;\n  padding:10px!important;\n  line-height:1.4!important;\n }\n .model-atelier .atelier-inspector :is(input:not([type=checkbox]):not([type=radio]),select,textarea) {\n  margin-top:3px!important;\n }\n .model-atelier .atelier-inspector .atelier-tool-handle{\n  margin: -12px -23px 9px!important;\n }\n .model-atelier .atelier-inspector .atelier-tool-handle button{\n  min-height:38px!important;\n  margin-top:0!important;\n }\n .model-atelier .atelier-inspector .atelier-sculpt-picked-readout:not([hidden]){\n  margin:12px 0!important;\n }\n}\n/* Desktop benefit from consistent vertical rhythm without widening the dock. */\n@media (min-width:981px) and (pointer:fine) {\n .model-atelier .atelier-inspector .atelier-pair{row-gap:10px}\n .model-atelier .atelier-inspector #modelAtelierSculptBrush{gap:12px!important}\n}\n"

def once(s,a,b):
    n=s.count(a)
    assert n==1,(a[:130],n)
    return s.replace(a,b,1)

def apply(html):
    old="""   checkpoint();p.sculptBrushes=p.sculptBrushes.slice(0,-1);
   signalEdited();select(p.id);status('Last sculpt stroke removed; full-model Undo can restore it.');"""
    new="""   // Render/display modes belong to the viewport, not the geometry undo stack.
   // A native geometry edit must not change the user's All/Selected X-Ray mode.
   const viewGlobalBefore=atelierViewGlobal;
   const viewOverridesBefore=new Map(atelierViewOverrides);
   const viewScopeBefore=$m('ViewportScope')?.value;
   checkpoint();p.sculptBrushes=p.sculptBrushes.slice(0,-1);
   // signalEdited already rebuilds geometry, list and inspector. The previous
   // select(p.id) caused a second unnecessary rebuild after every brush undo.
   signalEdited();
   const overridesChanged=viewOverridesBefore.size!==atelierViewOverrides.size||
     [...viewOverridesBefore].some(([id,mode])=>atelierViewOverrides.get(id)!==mode);
   if(atelierViewGlobal!==viewGlobalBefore||overridesChanged){
     atelierViewGlobal=viewGlobalBefore;
     atelierViewOverrides.clear();
     for(const [id,mode] of viewOverridesBefore)atelierViewOverrides.set(id,mode);
     renderParts();
   }
   const scope=$m('ViewportScope');
   if(scope&&viewScopeBefore)scope.value=viewScopeBefore;
   atelierViewportControlsRefresh();
   status('Last sculpt stroke removed; viewport display retained. Full-model Undo can restore it.');"""
    html=once(html,old,new)
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v11105-menu-spacing">'+CSS+'</style>\n</head>',1)
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_104_PICK_MARKER_READABLE_MENUS',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_105_SCULPT_UNDO_VIEW_MENU')
    for a,b in [
      ('ENGINE · MAKER v11.104','ENGINE · MAKER v11.105'),
      ('v11.104 · visible picks and readable tool menus','v11.105 · undo view preservation and spaced menus'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.104'","window.SWRLZ_FORGE_BUILD={version:'v11.105'"),
      ('<title>§wyrl§ Engine · Maker v11.104</title>','<title>§wyrl§ Engine · Maker v11.105</title>'),
    ]:html=once(html,a,b)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Preserved render mode on brush undo and roomier menus',
      date='2026-10-24',changes=[
       'Remove redundant second mesh rebuild during Remove last stroke, and restore/synchronize the active viewport mode and scope independently of geometry history.',
       'Widen the floating mobile menu modestly with safe lateral trim while retaining draggable position and existing height.',
       'Improve section and form field spacing, legibility and touch targets without changing model objects, brush geometry, pick marker or export.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    b=html.encode('utf8')
    print('SWRLZ_V11105_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
    return html
