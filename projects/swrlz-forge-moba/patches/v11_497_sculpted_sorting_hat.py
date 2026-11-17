"""§E v11.497 — register a second, one-piece sculpted Sorting Hat starter.
Append-only: original Sorting Hat project is unchanged; no separate renderer.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT'

def once(html,old,new,label):
    count=html.count(old)
    assert count==1,('se497',label,count,old[:100])
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_496_MODEL_MINI_STUDIOS' in html
    script=(ROOT/'runtime/sorting_hat_sculpted_v11_497.js').read_text('utf8')
    assert 'SE497_SCULPTED_SORTING_HAT_END' in script
    assert 'se497DeformHat' in script
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
              script+'\nwindow.SWRLZ_FORGE_BUILD=','second starter native loader')
    card=(
      '<button class="project-card den" data-project-template="sorting-hat-sculpted">'
      '<span class="project-icon">🎩</span>'
      '<strong>The Sorting Hat · Sculpted</strong>'
      '<span class="template-tag">STARTER MODEL · SINGLE MESH · SCULPTED</span>'
      '<p>An alternate expressive fabric hat. One sealed, editable mesh with '
      'deformed cloth folds, integrated face, softly bent peak and asymmetric brim. '
      'Original Sorting Hat remains unchanged.</p>'
      '<span class="hint den-glow">Open in Model Studio</span>'
      '</button>'
    )
    html=once(html,'<button class="project-card den" data-project-template="sorting-hat">',
              card+'<button class="project-card den" data-project-template="sorting-hat">',
              'independent starter card')
    html=once(html,'function se128LaunchStartupProject(){',
       """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='sorting-hat-sculpted'){
  window.se128StartupPending=true;
  queueMicrotask(()=>Promise.resolve(se497OpenSculptedHat(true))
   .catch(error=>console.error('Sculpted Sorting Hat startup',error))
   .finally(()=>{window.se128StartupPending=false;}));
  return;
 }
""",'deep link')
    for old,new,label in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_496_MODEL_MINI_STUDIOS',MARKER,'marker'),
      ('ENGINE · MAKER v11.496','ENGINE · MAKER v11.497','headline title'),
      ('v11.496 · Model, Rigging and Animation mini-studios',
       'v11.497 · a second sculpted Sorting Hat starter','release heading'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.496'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.497'",'version'),
      ('<title>§wyrl§ Engine · Maker v11.496</title>',
       '<title>§wyrl§ Engine · Maker v11.497</title>','browser title')
    ):html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.496';source.version=11.496;"
    count=html.count(old)
    assert count==5,('provenance',count)
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.497';source.version=11.497;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.496']
    notes['history'].insert(0,{'version':'v11.496','changes':notes.get('changes',[])})
    notes.update(version='v11.497',date='2026-11-17',
      title='Second Sorting Hat — one fully deformed cloth surface',
      changes=[
       'Added a second Sorting Hat starter card and a distinct project canonical ID; never overwrites the original hat or an account project.',
       'Built this alternate via direct vertex deformations of the same native closed cloth topology: layered wrinkle folds, gently side-bent tip, integrated eye/brow/mouth relief, and irregular flared brim.',
       'Preserves a single editable topologyMesh, matching original vertex index/UV/face topology and existing woven texture; no separate objects, reference-image cutouts or new renderer.',
       'Loads in the existing Model Studio with source mesh and native rig/animation tools. Phone and Quest visual acceptance remains owner testing.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
