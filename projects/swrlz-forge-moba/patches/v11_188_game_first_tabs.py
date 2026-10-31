"""§E v11.188: Game Engine is the default landing tab on the main entrypoint.

Protect the native model editor's explicit route while preventing historical
default-starter and saved-model autoload from covering the main Game Engine.
Preserve preferences, model projects, chat and scene/project storage.
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.188 source anchor',old[:155],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/engine_game_first_tabs_v11_188.css').read_text(encoding='utf8')
    html=html.replace('</head>','<style id="se188GameFirstTabs">\n'+css+'\n</style>\n</head>',1)
    # The native Model Atelier open() can be called by historical *automatic*
    # project loaders. A landing on / or /index.html is ALWAYS the Game page;
    # only an explicit workspace tab switch or direct /modeler.html enables it.
    html=once(html,
        """  function open(){
    if(!model()){status('Open Model Atelier from Projects first.',true);return false;}""",
        """  function open(){
    const workspaces=window.SWYRL_ENGINE_WORKSPACES;
    if((workspaces?.active?.()!=='modeler') &&
       !/\\/modeler\\.html$/i.test(location.pathname))return false;
    if(!model()){status('Open Model Atelier from Projects first.',true);return false;}""")
    # Tabs are the FIRST items in the native top toolbar on Game, and the top
    # of the full-page Modeler. Rename the second tab to match the requested UI.
    html=once(html,
        "for(const [id,label] of [['game','Game Engine'],['modeler','Modeler']]){",
        "for(const [id,label] of [['game','Game Engine'],['modeler','Modeling']]){")
    html=once(html,
        """ function boot(){
  installTabs();
  if(active==='modeler')change('modeler',false);
  renderTabs();
 }""",
        """ function boot(){
  installTabs();
  if(active==='modeler')change('modeler',false);
  else{
   // A legacy startup loader may have mounted Modeler before the tab router
   // was installed. Only an explicit Modeler tab may open that surface.
   ModelAtelier.close();
  }
  renderTabs();
 }""")
    # Treat a remembered *model starter* as belonging to the Modeler route.
    # Game Engine retains its default Dragon Den world instead; never erase
    # the selected preference and never load/replace a user-saved model here.
    html=once(html,
        """ if(window.SWYRL_ENGINE_SAVED_DEFAULT?.launch())return;
 const requested=se128ReadDefault();""",
        """ if(window.SWYRL_ENGINE_SAVED_DEFAULT?.launch())return;
 const requested=se128ReadDefault();
 if(!/\\/modeler\\.html$/i.test(location.pathname) &&
    ['model-atelier','blank-model','wolf-model','sheep-model','festival-girl-saved'].includes(requested)){
   loadCanonicalGlitchDen();
   window.se128StartupPending=false;
   return;
 }""")
    # On-device saved-model defaults also must not put Modeler on the main
    # game page. Preserve the user's checkbox and the saved model in storage.
    html=once(html,
        """   if(!row?.data?.project||!Array.isArray(row.data.scene?.actors))throw Error('Saved project not found on this device');
   if(!state.pending||boot!==state)return;""",
        """   if(!row?.data?.project||!Array.isArray(row.data.scene?.actors))throw Error('Saved project not found on this device');
   if(!state.pending||boot!==state)return;
   if(!/\\/modeler\\.html$/i.test(location.pathname) && row.data.project.kind==='model-atelier'){
    loadCanonicalGlitchDen();
    complete(state,true);
    return;
   }""")
    # Cloud default kind is only available AFTER the native loader returns;
    # if it is a model, restore the game landing world without touching cloud
    # source, selection, or authored user project records.
    html=once(html,
        """   if(!state.pending||boot!==state)return false;
   complete(state,result===true,result===true?'':'Could not open the account default; open it from My Projects.');""",
        """   if(!state.pending||boot!==state)return false;
   if(result===true && !/\\/modeler\\.html$/i.test(location.pathname) &&
      currentProject?.kind==='model-atelier'){
    ModelAtelier.close();
    loadCanonicalGlitchDen();
   }
   complete(state,result===true,result===true?'':'Could not open the account default; open it from My Projects.');""")
    # The legacy Edit Model shortcut remains a deliberate user interaction:
    # it opens the proper Modeling tab rather than invoking a hidden dialog.
    html=once(html,
        "    button.addEventListener('click',open);document.body.append(button);syncProject();",
        """    button.addEventListener('click',()=>{
      if(window.SWYRL_ENGINE_WORKSPACES?.change)
       window.SWYRL_ENGINE_WORKSPACES.change('modeler');
      else open();
    });document.body.append(button);syncProject();""")
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_187_GAME_MODELER_WORKSPACES','SWYRL_ENGINE_DEPLOY_MARKER: V11_188_GAME_FIRST_WORKSPACE_TABS'),
        ('ENGINE · MAKER v11.187','ENGINE · MAKER v11.188'),
        ('v11.187 · Game Engine and Modeler workspaces','v11.188 · Game Engine default landing tab'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.187'","window.SWRLZ_FORGE_BUILD={version:'v11.188'"),
        ('<title>§wyrl§ Engine · Maker v11.187</title>','<title>§wyrl§ Engine · Maker v11.188</title>')
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Game Engine first: stable top tabs and route-aware Modeler startup',
        date='2026-10-31',changes=[
        'Opening the main §E page / or index.html always begins on the Game Engine tab, with the Modeling tab second in the fixed top toolbar.',
        'Historic model-starter or saved-model defaults no longer automatically open Modeler over the Game Engine entrypoint; the preference and saved model remain available.',
        'The dedicated modeler.html entrypoint and explicit Modeling tab still enter the full native Modeler with project-free untitled drafts.',
        'A legacy Edit 3D Model shortcut now switches through the Modeling tab rather than bypassing workspace routing.',
        'Neither startup fix changes saved model assets, game scene storage, VR, native model tools, or project ownership.',
        'Android and Quest physical device acceptance remains with the owner.'
        ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
