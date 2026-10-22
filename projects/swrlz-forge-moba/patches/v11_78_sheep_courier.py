"""Use Astra's complete textured native model for every Sheep Tag wolf."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    # Factory executes only after all module constants have been initialized;
    # it builds from the same immutable saved source as the separate model card.
    factory=(root/'runtime/sheep_courier_v11_78.js').read_text()
    html=once(html,'  function refreshList(){',factory+'\n  function refreshList(){')
    html=once(html,'return Object.freeze({validateAssemblies:',
              'return Object.freeze({createCourierHunter:atelierCourierHunter,validateAssemblies:')
    html=once(html,'function stMakeVisual(type){',
              "function stMakeVisual(type){\n  if(type==='st-wolf')return ModelAtelier.createCourierHunter();")
    inspect=(root/'runtime/sheep_courier_inspect_v11_78.js').read_text()
    html=once(html,'function stRenderStatus(id=null){',inspect+'\nfunction stRenderStatus(id=null){')
    html=once(html,"return {id:entity.id,kind:entity.captured?'wisp':entity.kind,visible:walkingObjectVisible(object)",
              "return {...stCourierVisualStatus(object),id:entity.id,kind:entity.captured?'wisp':entity.kind,visible:walkingObjectVisible(object)")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_77_COMET_COURIER_MODEL_PROJECT','SWYRL_ENGINE_DEPLOY_MARKER: V11_78_SHEEP_TAG_COURIER'),
      ('ENGINE · MAKER v11.77','ENGINE · MAKER v11.78'),
      ('v11.77 · textured model projects','v11.78 · Astra in Sheep Tag'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.77'","window.SWRLZ_FORGE_BUILD={version:'v11.78'"),
      ('<title>§wyrl§ Engine · Maker v11.77</title>','<title>§wyrl§ Engine · Maker v11.78</title>')
    ):html=once(html,old,new)
    return html
