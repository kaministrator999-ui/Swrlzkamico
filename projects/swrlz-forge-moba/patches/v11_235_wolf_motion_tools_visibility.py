"""§E v11.235 · keep Astra's existing animation set / Play / key controls accessible.

The v11.119 generic mode-view CSS hides every direct inspector child except
the context workbench. Astra's Wolf Rig & Motion is such a child and can appear
to vanish on the user's Android phone, despite being installed and functional.
When choosing the native Motion category on a wolf, show that actual original
panel instead of opening a redundant generic context page. Mark skin pose edits
HD-dirty so the original single renderer actually draws animated frames.
"""
import json


def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.235',label,count,old[:130]))
    return html.replace(old,new,1)


def apply(html):
    html=once(html,
      " const chooseCategory=(category,mode)=>{\n  if(!categories.includes(category))return;\n  const choices=seAtelierModeNames(api,category);",
      """ const chooseCategory=(category,mode)=>{
  if(!categories.includes(category))return;
  panel.classList.remove('se-wolf-motion-focus');
  // Wolf motion uses its existing playable clip/key studio, not the generic
  // Context workbook which otherwise hides this inspector child entirely.
  if(category==='Motion'&&typeof se224WolfIsModel==='function'&&se224WolfIsModel()){
   const wolf=panel.querySelector('#modelAtelierWolfStudio');
   const inspector=panel.querySelector('.atelier-inspector');
   if(wolf&&inspector){
    panel.classList.add('se-inspector-mode-view','se-wolf-motion-focus');
    panel.classList.remove('atelier-tools-closed');
    inspector.setAttribute('aria-hidden','false');
    wolf.hidden=false;wolf.open=true;inspector.scrollTop=0;
    currentCategory='Motion';currentMode='Wolf Rig & Motion';
    label.textContent='Motion · Astra Wolf';
    modeBar.hidden=true;modeBar.replaceChildren();
    return;
   }
  }
  const choices=seAtelierModeNames(api,category);""",
      'switch native Motion category to original Wolf Rig & Motion panel')

    html=once(html,
      "  if(category==='More'){\n   currentCategory='';currentMode='';",
      "  if(category==='More'){\n   panel.classList.remove('se-wolf-motion-focus');\n   currentCategory='';currentMode='';",
      'restore ordinary inspector on More')

    # The wolf studio is installed once and remains the owner of the play,
    # selected clip, playhead, joint selectors, pose keys and reset controls.
    html=once(html,
      " controls.prepend(ui);\n const by=id=>document.getElementById('modelAtelierWolf'+id);",
      " controls.prepend(ui);ui.open=true;\n const by=id=>document.getElementById('modelAtelierWolf'+id);",
      'make wolf preview details discoverable on initial load')

    # The sole modeler render loop enables HD frame suppression when nothing
    # changes. Animated bones alter GPU skin transforms without changing model
    # geometry; tell that existing loop to redraw instead of relying on a
    # camera gesture to make the viewport dirty.
    html=once(html,
      ' root.updateMatrixWorld(true);se224WolfSkeleton.update();',
      ' root.updateMatrixWorld(true);se224WolfSkeleton.update();atelierHDDirty=true;',
      'invalidate HD viewport whenever the wolf pose changes')

    css="""
<style id="se235WolfMotionVisibility">
/* v11.235: preserve the existing mobile inspector placement, but let the
   wolf's actual animation panel be its focused content under Motion. */
#modelAtelierPanel.se-wolf-motion-focus.se-inspector-mode-view .atelier-inspector{
 display:flex!important;flex-direction:column!important;min-height:0!important;
}
#modelAtelierPanel.se-wolf-motion-focus.se-inspector-mode-view
 .atelier-inspector>#atelierContextWorkbench{display:none!important}
#modelAtelierPanel.se-wolf-motion-focus.se-inspector-mode-view
 .atelier-inspector>#modelAtelierWolfStudio{
 display:block!important;position:relative!important;flex:1 1 auto!important;
 width:100%!important;max-height:100%!important;min-height:0!important;
 margin:0!important;overflow-y:auto!important;overscroll-behavior:contain!important;
}
#modelAtelierPanel.se-wolf-motion-focus .atelier-wolf-panel button,
#modelAtelierPanel.se-wolf-motion-focus .atelier-wolf-panel select{
 min-height:38px!important;touch-action:manipulation;
}
@media(max-width:980px),(pointer:coarse){
 #modelAtelierPanel.se-wolf-motion-focus .atelier-inspector{
  max-width:calc(100vw - 14px)!important;
 }
}
</style>
"""
    # One document has a second literal </head> inside an embedded HTML string.
    # Inject only into the outer document head, not that nested template.
    if html.count('</head>') not in (1,2):raise AssertionError(('v11.235 HTML head locations',html.count('</head>')))
    html=html.replace('</head>',css+'</head>',1)

    old=" source.engine='§wyrl§ Engine · Maker v11.234';source.version=11.234;"
    if html.count(old)!=2:raise AssertionError(('v11.235 source provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.235';source.version=11.235;")

    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_234_WOLF_ANATOMICAL_SKINNING',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_235_WOLF_MOTION_PANEL_VISIBILITY'),
      ('ENGINE · MAKER v11.234','ENGINE · MAKER v11.235'),
      ('v11.234 · corrected Astra wolf skeletal deformation',
       'v11.235 · accessible Astra wolf Motion controls'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.234'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.235'"),
      ('<title>§wyrl§ Engine · Maker v11.234</title>',
       '<title>§wyrl§ Engine · Maker v11.235</title>')
    ]:
       html=once(html,a,b,'release marker')
    label='const SE_RELEASE_NOTES='
    pos=html.index(label)+len(label)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
      title='Astra Wolf: restore Motion menu and preview/set-play controls',
      date='2026-11-02',
      changes=[
        'On Android, choosing Motion for Astra now opens the existing Wolf Rig & Motion inspector; clip selector, Play/Stop, reset, playhead, skeleton, editable bones, and Save pose at playhead remain visible and usable.',
        'Correct native mode-view CSS hiding the Wolf Studio behind the generic context workbench; no duplicated controls or second modal added.',
        'Keep the Wolf Rig & Motion details expanded on initial wolf loading, and return to the existing context inspector when another tool category is selected.',
        'Invalidate the existing HD viewport when wolf bones change so Play, scrub and pose editing visibly animate without requiring camera orbit. Preserve the existing one-RAF, one-WebGL-renderer design.',
        'Preserve saved wolf clips, geometry, shaders, rig weights, Sheep Tag gameplay, other modeling tools, and existing single render loop.',
        'Owner Moto/Quest checks still required for UI interaction, animation quality and performance.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
