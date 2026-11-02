"""§E v11.226: five independent sheep-faction houses as native Model Atelier starters.
Preserve current Sheep Tag gameplay/building rules, saved projects and unrelated tabs.
"""
from pathlib import Path
import json


def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.226 sheep building anchor',old[:140],count))
    return html.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/sheep_building_model_starters_v11_226.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')

    cards=[
      ('sheep-free-shelter','🛖','Free Sheep Shelter','OPEN LEAN-TO · FREE',
       'Open-sided timber shelter, slate-blue sloped roof, clean hay bedding and lantern.'),
      ('sheep-thatched-hut','🐑','Thatched Starter Hut','STARTER HUT · FREE',
       'Compact straw cottage with sheep fleece crest, ram-horn roof trim and wooden door.'),
      ('sheep-cottage','🏡','Cozy Sheep Cottage','COTTAGE · BASIC',
       'Warm plaster and timber cottage with straw gable, chimney, amber windows and flowers.'),
      ('sheep-barn','🏚️','Flock Barn','BARN · BASIC',
       'Red timber barn, blue roof, hay bales, true entrance opening and loft window.'),
      ('sheep-ram-house','🏠','Ram House','SHEEP HOUSE · BASIC',
       'Wool-crest thatched house with a barnlike open doorway and side awning.'),
    ]
    html_cards=''.join(
      '<button class="project-card den se226-house-card" data-project-template="'+key+'">'
      '<span class="project-icon">'+icon+'</span><strong>'+name+'</strong>'
      '<span class="template-tag">'+tag+'</span>'
      '<p>'+description+'</p>'
      '<span class="hint den-glow">Open editable 3D building model</span></button>'
      for key,icon,name,tag,description in cards
    )
    html=once(html,
      '<button class="project-card den" data-project-template="floating-hand-glove">',
      html_cards+'<button class="project-card den" data-project-template="floating-hand-glove">')

    # Native project router, per-device saved default and template new-copy
    # discovery already use data-project-template. Only intercept our deep links.
    html=once(html,
      'function se128LaunchStartupProject(){',
      """function se128LaunchStartupProject(){
 const se226Requested=new URLSearchParams(location.search).get('project');
 if(se226BuildingIds.has(se226Requested)){
  se226OpenBuilding(se226Requested,true);
  window.se128StartupPending=false;
  return;
 }""")

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_225_MATERIAL_TEXTURE_STUDIO_TABS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_226_SHEEP_BUILDING_MODEL_STARTERS'),
      ('ENGINE · MAKER v11.225','ENGINE · MAKER v11.226'),
      ('v11.225 · Material Texture Studio and four workspace tabs',
       'v11.226 · five sheep-faction building model starters'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.225'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.226'"),
      ('<title>§wyrl§ Engine · Maker v11.225</title>',
       '<title>§wyrl§ Engine · Maker v11.226</title>'),
    ]:
        html=once(html,old,new)

    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
      title='Sheep Tag faction: five independent native house model starters',
      date='2026-11-02',
      changes=[
        'Projects now offers five independent 3D model starters: Free Sheep Shelter, Thatched Starter Hut, Cozy Sheep Cottage, Flock Barn and Ram House.',
        'Each starter is a separate native Model Atelier project with original editable indexed mesh walls, roof pitches, frames, doors, windows, wood and stone materials, and themed decorative details.',
        'Free Shelter is an open lean-to with straw bedding. The Hut has a thatched roof and ram ornament. Cottage adds amber windows, flowers and chimney. Barn uses red timber and blue roofing; Ram House adds a porch.',
        'Starter scenes can be opened from Project cards, chosen as a per-browser startup default, or opened with modeler.html?project=<starter-id>. Existing Model Atelier save, group edit, native view, and export remain the data owners.',
        'This is model asset authoring only. It does not silently replace Sheep Tag building gameplay meshes, resources, placement, collision or LAN authority; reuse in active matches is a separate reviewed integration.',
        'No additional renderer, external image download, AI model change or Quest controller override. Existing game starters and saved user models remain intact; hands-on device acceptance is pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
