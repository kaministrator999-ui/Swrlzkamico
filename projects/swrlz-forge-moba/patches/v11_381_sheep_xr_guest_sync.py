"""§E v11.381 — Quest guest world snapshots and controller bridge to phone host.

Append-only fix: authoritative host physics untouched. Existing WebXR frame
and v11.156 guest browser RAF remain the only visual scheduling owners.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_381_XR_GUEST_HOST_SYNC'

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.381',label,n,old[:100]))
    return s.replace(old,new,1)

def apply(html):
    script=(ROOT/'runtime/sheep_xr_guest_sync_v11_381.js').read_text(encoding='utf8')
    for need in ('se381OriginalXRFrame=se193XRFrame',
                 'se381OriginalGuestFrameOnce=se156GuestFrameOnce',
                 'se381OriginalGuestControls=se152GuestControls',
                 'SWYRL_ENGINE_SHEEP_XR_GUEST_381'):
        if need not in script:raise AssertionError(('v11.381 missing bridge',need))
    for need in ('function se156GuestFrameOnce(){',
                 'function se199StickIntent(){',
                 'function se193XRFrame(){',
                 'SWYRL_ENGINE_SHEEP_VR_LAN_268',
                 'SWYRL_ENGINE_ADVANCED_GRAPHICS_380'):
        if need not in html:raise AssertionError(('v11.381 missing prerequisite',need))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=','late XR/LAN bridge')
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_380_ADVANCED_GRAPHICS_PERFORMANCE_TABS',MARKER,'deploy marker'),
        ('ENGINE · MAKER v11.380','ENGINE · MAKER v11.381','header'),
        ('v11.380 · advanced graphics and Quest performance','v11.381 · Quest guest multiplayer movement','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.380'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.381'",'runtime build'),
        ('<title>§wyrl§ Engine · Maker v11.380</title>',
         '<title>§wyrl§ Engine · Maker v11.381</title>','HTML title')
    ]:html=once(html,old,new,label)
    provenance=" source.engine='§wyrl§ Engine · Maker v11.380';source.version=11.38;"
    # JavaScript parses 11.380 as the numeric value 11.38. Preserve the
    # actual token form from current authored sources when promoting it.
    if html.count(provenance)!=5:
        provenance=" source.engine='§wyrl§ Engine · Maker v11.380';source.version=11.380;"
    if html.count(provenance)!=5:raise AssertionError(('v11.381 provenance',html.count(provenance)))
    html=html.replace(provenance,
        " source.engine='§wyrl§ Engine · Maker v11.381';source.version=11.381;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.380' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.380','changes':notes.get('changes',[])})
    notes.update(version='v11.381',date='2026-11-10',
        title='Meta Quest multiplayer guest: restore sheep motion and controller input',
        changes=[
            'Immersive Sheep Tag guest devices now run the existing host-authoritative sheep visual interpolation on the existing WebXR frame callback, avoiding reliance on regular browser RAF during Quest presentation.',
            'Only when joining as a WebXR guest, relay the actual left-controller thumbstick through existing sequenced guest-stick-v2 WebRTC messages to the phone/PC host, instead of repeatedly sending idle touch-joystick intent.',
            'Guest movements remain bounded to the host native collision/physics simulation, and host snapshots still own sheep position, rotation, animations, buildings and resources.',
            'Preserve browser-only guest animation and touch joystick when not immersed, including Quest browser hosting and phone joining.',
            'Do not create another renderer, simulation ticker, polling loop or networking channel; keep original VR controller orientation, Quest graphics presets and project saves.',
            'Expose distinct guest XR frame, applied snapshot, joystick TX and stop/neutral diagnostics for device A/B tests. Real Quest 3S / phone-host acceptance pending.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
