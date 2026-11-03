"""§E v11.232 — selected native model starters must open Modeling, not an empty Game scene.

Owner Android screenshots showed Game Engine selected, only World Ground in the
outliner, and the new model's title/background in the game viewport. Native
ModelAtelier.open() is deliberately blocked from the game route by v11.188.
Explicit starter loaders must first activate the existing Modeling workspace.

Do not alter game-first automatic startup, saved model records, project geometry,
or the native renderer. The existing workspace router opens the model exactly once.
"""
import json


def once(s, old, new, name):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.232',name,old[:130],count))
    return s.replace(old,new,1)


def scoped(html, start, end, old, new, name):
    a=html.index(start)
    b=html.index(end,a)
    return html[:a]+once(html[a:b],old,new,name)+html[b:]


def apply(html):
    helper="""// Explicit Model Atelier starter selection only. Do not change automatic Game first boot.
function se232ActivateSelectedModelWorkspace(){
 const ws=window.SWYRL_ENGINE_WORKSPACES;
 if(!ws?.change||ws.change('modeler')!==true||!ModelAtelier.status().open)
  throw Error('Modeling workspace could not open this starter.');
}
"""
    html=once(html,'const SE226_BUILDINGS=Object.freeze([',helper+'const SE226_BUILDINGS=Object.freeze([','install startup-safe helper')

    # Model Atlas house project must activate the Modeler route BEFORE the
    # renderer is opened. A second .open() is not needed.
    html=scoped(html,'function se226OpenBuilding(id,force=false){','const se226OriginalTemplate=',
        '  ModelAtelier.syncProject();ModelAtelier.open();',
        '  se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();',
        'five sheep house starters')
    html=scoped(html,'function se226OpenBuilding(id,force=false){','const se226OriginalTemplate=',
        "  panel?.classList.add('courier-studio');\n  if(edit){edit.hidden=false;edit.textContent='Edit model';edit.setAttribute('aria-pressed','true');}",
        "  panel?.classList.remove('courier-studio');\n  if(edit){edit.hidden=false;edit.textContent='Studio view';edit.setAttribute('aria-pressed','false');}",
        'house model editing tools visible')

    # v11.230 already attaches the rig before this statement. A workspace
    # change here opens the *fully rigged* wolf once, not an unrigged first copy.
    html=scoped(html,'const atelierOriginalWolfLoader=loadAnimalProject;','ModelAtelier.install();',
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();",
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();",
        'active Astra wolf model starter')

    # The earlier animal starter remains the active sheep implementation;
    # only the wolf is overridden by v11.88.
    html=scoped(html,'async function loadAnimalProject(species,force=false,rebuild=false){','const atelierAnimalTemplateBase=',
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();",
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();",
        'sheep model starter')

    # The original courier and blank model cards are independent of wolf-model.
    html=scoped(html,'function loadCourierProject(blank=false,force=false){','const courierPreviousTemplate=',
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();",
        "markSaved();document.getElementById('projectHub')?.classList.remove('show');se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();",
        'courier and blank model project')

    # Repair other explicit model starter choices using the same native owner.
    html=scoped(html,'function se212OpenHand(force=false){','const se212PreviousTemplate=',
        '  ModelAtelier.syncProject();ModelAtelier.open();',
        '  se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();',
        'floating glove model')
    html=scoped(html,'function loadModelAtelierStarter(force=false){','const modelAtelierPreviousTemplate=',
        "  ModelAtelier.syncProject();ModelAtelier.open();",
        "  se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();",
        'canonical model atelier starter')

    old=" source.engine='§wyrl§ Engine · Maker v11.231';source.version=11.231;"
    assert html.count(old)==2,('v11.232 source provenance count',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.232';source.version=11.232;")

    for a,b in [
       ('SWYRL_ENGINE_DEPLOY_MARKER: V11_231_SHEEP_HOUSE_CAMERA_FIT',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_232_MODEL_STARTER_WORKSPACE_ACTIVATION'),
       ('ENGINE · MAKER v11.231','ENGINE · MAKER v11.232'),
       ('v11.231 · full sheep house camera fit in Model Atelier',
        'v11.232 · model starter workspace activation'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.231'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.232'"),
       ('<title>§wyrl§ Engine · Maker v11.231</title>',
        '<title>§wyrl§ Engine · Maker v11.232</title>')
    ]:
        html=once(html,a,b,'v11.232 release identity')

    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    note,n=json.JSONDecoder().raw_decode(html[pos:])
    note.update(
      title='Model starter cards open Modeling instead of the empty Game Engine',
      date='2026-11-02',
      changes=[
        'Fix Game Engine remaining selected after opening any of the five Sheep Tag house models or the original Astra wolf model. The game viewport showed World Ground instead of the editable 3D model.',
        'Explicit model starter selection now uses the existing Modeling workspace tab/router, with no second model renderer, no reload, and correct modeler.html route.',
        'Preserve wolf rig initialization before the single first model render, and keep sheep house edit tools visible instead of inadvertently enabling studio-only mode.',
        'Apply the same explicit route fix to the independent Comet Courier, blank-model, sheep-model, floating glove and base Model Atelier starter cards.',
        'Game Engine remains the default site entry. Saved model geometry, Sheep Tag LAN/gameplay, player controller, materials, particles, other studios and VR controls are unchanged.',
        'Narrow Game-route-to-Modeling browser acceptance is required before deploy; physical Android/Quest approval remains the owner.'
      ])
    return html[:pos]+json.dumps(note,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
