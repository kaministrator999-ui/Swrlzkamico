"""§E v11.379 — correct false OS-blur recovery on slow visible Sheep Tag VR
frames and honor selected XR framebuffer preset at immersive entry.

Append-only controlled source patch. No second XR loop, headset pose modification,
changed simulation tick, network protocol or source-manifest checksum bypass.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_379_SHEEP_VR_VISIBLE_FRAME_CADENCE'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.379 source anchor',label,count,old[:130]))
    return html.replace(old,new,1)

def apply(html):
    addon=(ROOT/'runtime/sheep_vr_frame_cadence_v11_379.js').read_text(encoding='utf8')
    for token in ('se379PreviousOnFrame=se211OnFrame',
                  'se379PreviousFramebuffer=se191XRPrepareFramebuffer',
                  'se195OriginalFramebuffer()',
                  'SWYRL_ENGINE_SHEEP_VR_CADENCE_379'):
        if token not in addon:raise AssertionError(('v11.379 missing runtime symbol',token))
    for token in ('function se211OnFrame(){','function se238NativeMenuOpen(){',
                  'const se195OriginalFramebuffer=se191XRPrepareFramebuffer;',
                  'window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200=Object.freeze',
                  'window.SWYRL_ENGINE_QUEST_HEADTURN_239=Object.freeze'):
        if token not in html:raise AssertionError(('v11.379 missing prerequisite',token))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',addon+'\nwindow.SWRLZ_FORGE_BUILD=',
              'insert after existing XR, focus and joystick adapters')
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_378_STABLE_3D_BLOCKOUT',MARKER,'deploy marker'),
        ('ENGINE · MAKER v11.378','ENGINE · MAKER v11.379','header'),
        ('v11.378 · stable editable 3D blockout','v11.379 · Sheep Tag VR visible-frame stability','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.378'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.379'",'build identity'),
        ('<title>§wyrl§ Engine · Maker v11.378</title>',
         '<title>§wyrl§ Engine · Maker v11.379</title>','html title')
    ]:
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.378';source.version=11.378;"
    count=html.count(old)
    if count!=5:raise AssertionError(('v11.379 provenance count',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.379';source.version=11.379;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.378' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.378','changes':notes.get('changes',[])})
    notes.update(version='v11.379',date='2026-11-10',
        title='Sheep Tag VR: preserve camera and controller updates during visible frame hitches',
        changes=[
            'During immersive Sheep Tag, a 170–650ms browser/XR callback gap with both document and headset still explicitly visible no longer masquerades as a Quest OS-focus interruption and adds an artificial 300ms XR-input/camera pause.',
            'Actual XR visible-blurred/hidden, pending controller release, resume recovery and long >650ms callback-gap safeguards remain active. The game simulation, network authority, render loop and native HMD tracking are unchanged.',
            'Honor the selected graphics preset for Sheep Tag XR framebuffer resolution at VR session entry: Mobile Boost and Low use fewer pixels than High. Changing presets while immersed takes effect on the next VR entry; native headset refresh is unchanged.',
            'Expose separate diagnostics for ignored false OS-blur events and actual XR framebuffer scale without claiming real GPU frame time or proving complete Quest comfort at 25fps.',
            'Normal browser Sheep Tag, multiplayer, other projects, starter saves, sheep joystick mappings, wolf AI and editor workflows remain unchanged. Physical Quest 2 A/B acceptance pending.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
