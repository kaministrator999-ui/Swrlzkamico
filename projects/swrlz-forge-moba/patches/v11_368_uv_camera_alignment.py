"""§E v11.368 · preserve v11.367 stone hands; expose verified camera-relative UV auto-alignment."""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_368_UV_CAMERA_ALIGNMENT'

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.368',label,n,old[:120]))
    return s.replace(old,new,1)

def apply(html):
    for term in [
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_367_PROPER_STONE_HAND_ANATOMY',
        'SWYRL_ENGINE_STONE_HAND_ANATOMY_367',
        'se367CliffField',
        'se367AnatomicalRockScene',
        'function se366AutoAlignCamera()',
        'function se366AngleFromView(pa,pb,pc,ta,tb,tc,screenRight,screenUp)',
        'function se366CaptureSlide()',
        'Auto center + upright from view',
        'Capture corrected UV Slide position',
        'function se366ImportAuthored(file)',
        'window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze',
    ]:
        if term not in html:raise AssertionError(('v11.368 missing previous feature',term))
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_367_PROPER_STONE_HAND_ANATOMY',MARKER,'deploy marker'),
        ('ENGINE · MAKER v11.367','ENGINE · MAKER v11.368','visible header'),
        ('v11.367 · distinct anatomical Cliff and full-rock hands',
         'v11.368 · auto-align visible UV front and up','subtitle'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.367'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.368'",'build'),
        ('<title>§wyrl§ Engine · Maker v11.367</title>',
         '<title>§wyrl§ Engine · Maker v11.368</title>','title')
    ]:
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.367';source.version=11.367;"
    if html.count(old)!=5:raise AssertionError(('v11.368 model provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.368';source.version=11.368;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.367' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.367','changes':notes.get('changes',[])})
    notes.update(version='v11.368',date='2026-11-08',
      title='Model UV marker auto-center from visible side, camera-up and captured Slide',
      changes=[
        'Within Model Studio UV Editor, Auto center + upright from view raycasts the selected mesh toward its center, identifies its actual visible UV triangle and calculates artwork-up using its world-transformed tangent directions and the current camera axes.',
        'Rotated meshes—including a hand viewed palm-up or a sphere whose UV front falls one-quarter across the image—can get a centered, upright authoring guide without moving mesh geometry or manually moving UVs.',
        'Capture corrected UV Slide position records an existing hand-adjusted texture offset as a reusable marker; for a centered illustration and +0.2494 U Slide, the matching mesh marker sits at about U=0.2506.',
        'These features operate on the optional UV marker, not ordinary image import. Semantic palm/front can only be confirmed from the chosen view or model metadata, not guessed from arbitrary triangulation.',
        'Exact inverse marker artwork import, authored UVs, original UV Slide, per-mesh JSON persistence, current stone-hand starters, model and game editors and VR controllers are preserved.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
