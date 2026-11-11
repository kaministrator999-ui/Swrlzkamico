"""§E v11.391 — a reliable left-controller Y entry to Sheep Tag tools.

Meta Quest Browser reserves the real left Menu system button. The exposed
left Y face button is used instead; no application can bind the reserved key.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_391_SHEEP_QUEST_Y_TOOLS_RADIAL'
def one(src,old,new,label):
    count=src.count(old)
    if count!=1:raise AssertionError(('v11.391',label,count,old[:120]))
    return src.replace(old,new,1)
def apply(html):
    script=(ROOT/'runtime/sheep_vr_y_tools_radial_v11_391.js').read_text('utf8')
    for anchor in ('se391PriorButtonEdges=se193XRButtonEdges',
                   'se193.held.set(left.index,held)',
                   'SWYRL_ENGINE_SHEEP_VR_Y_MENU_391'):
        assert anchor in script,anchor
    for anchor in ('function se193XRButtonEdges(){',
                   'function se195SetVisible(value){',
                   'SWYRL_ENGINE_SHEEP_XR_GUEST_381',
                   'SE390_MODEL_VR_FLUENT_UI'):
        assert anchor in html,anchor
    html=one(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=','late XR radial')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_390_MODEL_VR_FLUENT_HOTKEYS',MARKER),
        ('ENGINE · MAKER v11.390','ENGINE · MAKER v11.391'),
        ('v11.390 · fluent Grab, selection and creation shortcuts',
         'v11.391 · Quest Sheep Tag Y quick tools radial'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.390'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.391'"),
        ('<title>§wyrl§ Engine · Maker v11.390</title>',
         '<title>§wyrl§ Engine · Maker v11.391</title>')
    ]:html=one(html,before,after,before)
    prior=" source.engine='§wyrl§ Engine · Maker v11.390';source.version=11.390;"
    assert html.count(prior)==5,('provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.391';source.version=11.391;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.390' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.390','changes':notes.get('changes',[])})
    notes.update(version='v11.391',date='2026-11-10',
        title='One-press Y shortcut for Sheep Tag immersive VR tools',
        changes=[
            'Quest Browser reserves the physical left Menu button. Press exposed left Y once to open or close the existing Sheep Tag tools radial; the main page exposes FOLLOW and FREE camera commands.',
            'Consume the former left-Y follow/recenter edge only during immersive Sheep Tag gameplay. Keep right B camera-free shortcut, X skills, A building selection and L3 Nerd Stats intact.',
            'A held Y never repeats; Meta system overlay, photo mode and non-game VR use no custom Y action. No additional renderer, game timer, network packet or project mutation.',
            'Real Quest hardware acceptance remains pending; this mapping does not claim to intercept the Quest system Menu button.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+length:]
