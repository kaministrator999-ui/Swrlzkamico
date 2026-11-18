"""§E v11.505: action-triggered, opt-in editable prerequisites for modeling tools."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_505_ACTION_PREREQUISITES'
PREVIOUS_SHA256='99bf4e5ce75d65255ccabcee90af9dd0cd8f734e79dfe453c632dfa55e6a2941'
def once(src,old,new):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.505 unique insertion',old[:90],n))
    return src.replace(old,new,1)
def apply(html):
    assert hashlib.sha256(html.encode('utf8')).hexdigest()==PREVIOUS_SHA256,'v11.504 source changed'
    for token in (
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT',
      'SE503_UV_ISLAND_UI_START','SE481_TEXTURED_EDITABLE_COPY_START',
      'SE480_EDITABLE_ENTRY_START','SE474_PROGRESSIVE_MODEL_TOOLS_END',
      'function se503Refresh()','function se503Install()',
      'function ensurePanel()','  function ensurePanel(){',
      'const se481TexturedEditable=',
    ):assert token in html,('v11.505 missing inherited source',token)
    js=(ROOT/'runtime/model_action_prerequisites_v11_505.js').read_text('utf8')
    assert 'SE505_ACTION_PREREQUISITES_START' in js
    assert 'SE505_ACTION_PREREQUISITES_END' in js
    html=once(html,'  function ensurePanel(){',js+'\n  function ensurePanel(){')
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT',MARKER),
        ('ENGINE · MAKER v11.504','ENGINE · MAKER v11.505'),
        ('v11.504 · independent smooth textured witch hat starter',
         'v11.505 · confirmed editable prerequisites with automatic continuation'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.504'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.505'"),
        ('<title>§wyrl§ Engine · Maker v11.504</title>',
         '<title>§wyrl§ Engine · Maker v11.505</title>'),
    ):html=once(html,old,new)
    prior=" source.engine='§wyrl§ Engine · Maker v11.504';source.version=11.504;"
    assert html.count(prior)==5,('v11.505 project provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.505';source.version=11.505;")
    key='const SE_RELEASE_NOTES='
    index=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[index:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.504']
    notes['history'].insert(0,{'version':'v11.504','changes':notes.get('changes',[])})
    notes.update(version='v11.505',date='2026-11-17',
        title='Context-aware editable mesh prerequisites for UV and modeling tools',
        changes=[
         'One shared, confirm-before-changing preparation flow is callable by modeling tools that require editable indexed geometry.',
         'UV island Preview stays actionable for supported non-editable meshes: confirm conversion or preservation copy, then preview automatically.',
         'Topology family Vertex, Inset, Extrude and the manual topology modes offer the same conversion instead of requiring unrelated menu navigation.',
         'Native primitives use existing validated indexed conversion with native Undo; textured procedural meshes use existing UV-faithful editable working copies with the original recoverable.',
         'Existing editable copies are reused rather than duplicated, and successful conversions resume the exact action on the same project and selection.',
         'Cancel leaves the model unchanged; unsupported protected rigging, ambiguous multi-selection, and active previews retain explicit block reasons.',
         'No automatic face choice, mesh deletion, texture removal, project overwrite, or conversion without owner confirmation.'
        ])
    return html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[index+width:]
