"""§E v11.541 — restore futuristic humanoid card to Starter Models category.

The v11.540 copy changed its template-tag to 'ONE UV BODY...' which lacks
the classifier's 'starter model' phrase. The stable mannequin template ID
also was absent from se285's native modelIds set, so the existing sorter
reparented its card under Starter Games. Change the live classifier and
semantic badge together. Do not replace project UI, saved projects or meshes.
"""
import json

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_540_HUMANOID_FIVE_DIGIT'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_541_HUMANOID_STARTER_CATEGORY'

def once(html, before, after, label):
    n=html.count(before)
    if n!=1:
        raise AssertionError(('se541',label,n,before[:140]))
    return html.replace(before,after,1)

def apply(html):
    # This is the actual v11.285 Projects → Starter Games/Models classifier
    # that moves original DOM card nodes after the editor initializes.
    html=once(html,
       " const modelIds=new Set([\n  'plain-hand-base'",
       " const modelIds=new Set([\n  'robotic-humanoid-mannequin',\n  'plain-hand-base'",
       'native starter-model category')
    # Keep the category self-describing so tag-based fallbacks and any future
    # independent classifying view also recognize this as a model starter.
    html=once(html,
       '<span class="template-tag">ONE UV BODY · FIVE FINGERS PER HAND</span>',
       '<span class="template-tag">STARTER MODEL · ONE UV BODY · FIVE FINGERS PER HAND</span>',
       'visible mannequin classification')
    # The existing immersive VR index has the correct canonical ID but
    # still calls the starter by its pre-upgrade v11.537 name.
    html=once(html,
       "'robotic-humanoid-mannequin':['Robotic Humanoid Mannequin','model-atelier','model-atelier']",
       "'robotic-humanoid-mannequin':['Futuristic Humanoid · Detailed Hands','model-atelier','model-atelier']",
       'immersive starter name')
    for before,after in (
       (OLD,MARKER),
       ('ENGINE · MAKER v11.540','ENGINE · MAKER v11.541'),
       ('v11.540 · anatomical humanoid with five-digit hands',
        'v11.541 · restored mannequin Starter Models category'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.540'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.541'"),
       ('<title>§wyrl§ Engine · Maker v11.540</title>',
        '<title>§wyrl§ Engine · Maker v11.541</title>')
    ):
        html=once(html,before,after,'release identity')
    previous=" source.engine='§wyrl§ Engine · Maker v11.540';source.version=11.540;"
    assert html.count(previous)==5,('source provenance',html.count(previous))
    html=html.replace(previous,
       " source.engine='§wyrl§ Engine · Maker v11.541';source.version=11.541;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[entry for entry in notes['history']
                      if entry.get('version')!='v11.540']
    notes['history'].insert(0,{'version':'v11.540','changes':notes['changes']})
    notes.update(
      version='v11.541',date='2026-11-22',
      title='Restore the Futuristic Humanoid to Starter Models',
      changes=[
        'Fixed the missing Futuristic Humanoid starter: its v11.540 card had lost the Starter Model label and was absent from the Projects classifier model ID registry, allowing it to be sorted into Starter Games.',
        'Register the stable robotic-humanoid-mannequin template ID as a model starter and restore the category label, without changing project data, the native card, click handlers or other categories.',
        'Show the updated Futuristic Humanoid · Detailed Hands name in the immersive project library while retaining its original canonical ID.',
        'Preserve the v11.540 one-piece hand-detail geometry, UV material atlas, user saves, account ownership, Quest tooling and v11.539 immersive sculpt repairs.',
        'Add regression assertions for the actual runtime sorter; owner device menu verification remains outstanding.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
