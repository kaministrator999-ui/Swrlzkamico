"""§E v11.471 — display imported UV paint and explicit My Projects deletion."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE'
def once(s,old,new,label):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.471 source anchor',label,count,old[:120]))
    return s.replace(old,new,1)

def apply(html):
    required=[
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_470_UV_MODEL_SAVE',
      'async function se336ImportPaint(file)',
      'function se336RemovePaint()',
      'function se184ProjectCard(record,source)',
      'function se184SyncDefaultBoxes()',
      'async function se175Db()',
      'async function se175RefreshLocal()',
      'async function se170Refresh()',
      'SE469_UV_SHAPE_FIT_START',
      'function se470SavedCloudProjects(rows)'
    ]
    for token in required:
        if token not in html:raise AssertionError(('missing inherited feature',token))
    # Keep native material display separate from optional latitude-aware UV shaping.\n    # Fix the symptom in the actual owner material rather than the UV preview.
    # The new material map already exists in native v11.336; the user's
    # screenshot shows View · Solid, which intentionally hides authored paint.
    start=html.index('async function se336ImportPaint(file)')
    end=html.index('function se336RemovePaint()',start)
    part=html[start:end]
    part=once(part,
      """      signalEdited();
      select(id);
      se336SlideNotify();
      se356UVPreviewSchedule();
      status('Painted PNG applied""",
      """      signalEdited();
      select(id);
      se336SlideNotify();
      se356UVPreviewSchedule();
      // Imported artwork is only visible in the authored Material viewport.
      // Keep explicit modeling mode changes reversible and unrelated to Undo.
      const viewChanged=window.SWYRL_ENGINE_VIEW_READABILITY_455?.choose?.('shaded') ??
        window.SWYRL_ENGINE_MODEL_VIEW?.setMode?.('shaded');
      const shown=()=>modelRoot?.children?.find(m=>m.isMesh&&m.userData?.atelierId===id);
      if(part.uvPaintPNG&&!shown()?.material?.map)renderParts();
      const bound=!!shown()?.material?.map;
      if(viewChanged===false||!bound)
       status('Texture image imported, but the material viewport is not showing its map. Select View → Material or refresh the model display.',true);
      else status('Painted PNG applied""",
      'material viewport after import')
    html=html[:start]+part+html[end:]
    # Preserve native viewport mode selector semantics, but auto-select Material
    # for the specific import event, not when merely showing a UV guide.

    latitude=(ROOT/'runtime/uv_latitude_math_v11_471.js').read_text('utf8')
    fine=(ROOT/'runtime/uv_fine_fit_v11_471.js').read_text('utf8')
    html=once(html,'  function ensurePanel(){',
        latitude+'\n'+fine+'\n  function ensurePanel(){','shape-aware UV controls')
    js=(ROOT/'runtime/project_delete_confirm_v11_471.js').read_text('utf8')
    css=(ROOT/'runtime/project_delete_confirm_v11_471.css').read_text('utf8')
    for needle in ('SE471_PROJECT_DELETE_CONFIRM_START','function deleteLocal(record)',
                   'function deleteCloud(record)','showModal()','expectedRevision',
                   "rpc('cloud.delete'",'se175Db()','se184ProjectCard=function(record,source)'):
        assert needle in js,needle
    html=once(html,'function se184SyncDefaultBoxes(){',
                  js+'\nfunction se184SyncDefaultBoxes(){','account / local card deletion')
    assert html.index('</head>')<html.index('<body'),'missing html head'
    html=html.replace('</head>','<style id="se471ProjectDeleteStyles">\n'+css+
      '\n</style>\n</head>',1)

    # Keep the source receipt, retained older patches, native studios, game
    # scene and Chat-owned credentials unchanged.
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_470_UV_MODEL_SAVE',MARKER),
      ('ENGINE · MAKER v11.470','ENGINE · MAKER v11.471'),
      ('v11.470 · UV placement and explicit model saves','v11.471 · visible UV texture and project delete'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.470'","window.SWRLZ_FORGE_BUILD={version:'v11.471'"),
      ('<title>§wyrl§ Engine · Maker v11.470</title>',
       '<title>§wyrl§ Engine · Maker v11.471</title>')
    ]:html=once(html,old,new,'source version '+old[:30])
    prior=" source.engine='§wyrl§ Engine · Maker v11.470';source.version=11.470;"
    assert html.count(prior)==5,('model provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.471';source.version=11.471;")
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes['history']=[p for p in notes.get('history',[]) if p.get('version')!='v11.470']
    notes['history'].insert(0,{'version':'v11.470','changes':notes.get('changes',[])})
    notes.update(version='v11.471',date='2026-11-15',
      title='Painted UV map visible on import and project deletion confirmation',
      changes=[
       'Successful UV PNG import switches from Solid modeling display to authored Material display and checks for an actual bound mesh texture map.',
       'Latitude-aware correction adjusts spherical UV sampling by the flattened meridian geometry, with optional independent U/V fine tuning; all controls preserve geometry positions and painted PNG bytes.',
       'My Projects cards add Delete actions for saved local and account projects, with a native Cancel/Delete confirmation dialog and explicit data location.',
       'On-device deletion atomically removes IndexedDB project and metadata rows only after rechecking the project identity, and never the active project.',
       'Account deletion requests verify the current revision and require an authenticated Chat bridge acknowledgement before showing success. Unsupported account delete reports a failure rather than silently removing a card.',
       'Deleting a saved default clears that startup selection and refreshes the project lists. Existing unrelated local/account copies are preserved.',
       'Native geometry, UV controls, particle/editor workspaces, game projects, VR and account credentials remain otherwise unchanged.',
       'Automated source checks do not replace owner Android and Quest testing.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[pos+n:]
