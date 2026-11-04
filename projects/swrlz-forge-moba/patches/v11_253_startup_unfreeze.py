"""§E v11.253 — prevent release-notes startup freeze by ending self-triggering
page-wide editor boot observers and idling diagnostics until an editor is open.

Append-only source hotfix: historical shipped patch modules remain untouched.
"""
import json

def once(html, old, new, reason):
    count=html.count(old)
    if count!=1:
        raise AssertionError(("v11.253",reason,count,old[:140]))
    return html.replace(old,new,1)

def apply(html):
    # v11.251 shared-workstation boot used to run on every childList change.
    # boot() invokes sync(), which sets textContent for active dock toggles.
    # That creates another childList change and can recurse indefinitely before
    # the version's modal Continue button gets a chance to receive an event.
    old="""const observer=new MutationObserver(()=>{
 if(!q('#se251ModelLibrary')||!q('#se251MaterialLibrary')||!q('#se251UnifiedMode'))boot();
});
observer.observe(document.body,{childList:true,subtree:true});"""
    new="""const observer=new MutationObserver(records=>{
 // Only a newly mounted workspace can require adding controls. Ignore
 // our own textContent, sliders, timeline redraws and release-notes DOM.
 const mounted=records.some(record=>Array.from(record.addedNodes).some(node=>
  node.nodeType===1&&(
   node.matches?.('#modelAtelierPanel,#se225Shell,#se225MaterialsPanel,#se249Root')||
   node.querySelector?.('#modelAtelierPanel,#se225Shell,#se225MaterialsPanel,#se249Root')
  )
 ));
 if(mounted&&(!q('#se251ModelLibrary')||!q('#se251MaterialLibrary')||!q('#se251UnifiedMode')))boot();
});
observer.observe(document.body,{childList:true,subtree:true});"""
    html=once(html,old,new,"limit shared dock observer to newly mounted workspaces")
    # v11.252 diagnostics also watched every DOM mutation, unnecessarily
    # rechecking editors before either existed.
    old="""const observer=new MutationObserver(()=>{if(!q('#se252-model')||!q('#se252-particles'))boot();});"""
    new="""const observer=new MutationObserver(records=>{
 if(!records.some(record=>Array.from(record.addedNodes).some(node=>
  node.nodeType===1&&(
   node.matches?.('#modelAtelierPanel,#se249Root')||
   node.querySelector?.('#modelAtelierPanel,#se249Root')
  )
 )))return;
 boot();
});"""
    html=once(html,old,new,"limit stress-panel boot to editor mounts")
    # The diagnostic fps sampler is not part of engine startup, and must do
    # no DOM updates or inspection while the modal is in charge.
    old="""function frame(now){
 state.raf=requestAnimationFrame(frame);
 if(!state.started)state.started=now;"""
    new="""function frame(now){
 state.raf=requestAnimationFrame(frame);
 const modelOpen=!!q('#modelAtelierPanel:not([hidden])');
 const particleOpen=document.body.dataset.se225Workspace==='particles';
 if((!modelOpen&&!particleOpen&&!state.particle)||q('#seReleaseNotesDialog')?.open){
  state.frames=0;state.sample=0;state.last=now;return;
 }
 if(!state.started)state.started=now;"""
    html=once(html,old,new,"keep diagnostics idle during boot and release-notes dialog")
    old=" source.engine='§wyrl§ Engine · Maker v11.252';source.version=11.252;"
    assert html.count(old)==2,("v11.253 provenance",html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.253';source.version=11.253;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_252_STRESS_DIAGNOSTICS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_253_STARTUP_UNFREEZE"),
        ("ENGINE · MAKER v11.252","ENGINE · MAKER v11.253"),
        ("v11.252 · model and particle stress diagnostics",
         "v11.253 · release dialog and editor boot freeze hotfix"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.252'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.253'"),
        ("<title>§wyrl§ Engine · Maker v11.252</title>",
         "<title>§wyrl§ Engine · Maker v11.253</title>")
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Startup unfreeze — responsive release-notes Continue",
      date="2026-11-04",changes=[
       "Fix a possible startup event-loop starvation caused by the shared workstation DOM observer repeatedly handling its own layout changes. Workspace initialization now runs only when a relevant editor container mounts.",
       "The model/particle stress-test panel observer also runs only on editor mounts, not on every document change.",
       "The temporary diagnostic frame sampler stays idle while the release notes dialog is open or no supported editor is active.",
       "No change to saved models, particles, Sheep Tag game logic, multiplayer, WebXR controller bindings, or ordinary emitter limits. Please verify startup on the Moto and Quest."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
