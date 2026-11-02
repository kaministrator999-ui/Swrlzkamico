"""§E v11.205: Sheep Tag Play tactical view, menu cursor and Quest overlay.
Append-only, preserving XR tracked pose and editor source-of-truth.
"""
from pathlib import Path
import json
def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.205 source anchor',old[:130],count)
    return s.replace(old,new,1)
def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_play_menu_camera_polish_v11_205.js').read_text(encoding='utf8')
    # Reduce blurry Quest labels without recreating the textures on page switch.
    html=once(html,
      "const c=document.createElement('canvas');c.width=256;c.height=128;",
      "const c=document.createElement('canvas');c.width=384;c.height=192;")
    html=once(html,"g.scale(.5,.5);","g.scale(.75,.75);")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_204_SHEEP_VR_RAPID_GRID_WHEELS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_205_SHEEP_TACTICAL_MENU_POINTER_OVERLAY'),
      ('ENGINE · MAKER v11.204','ENGINE · MAKER v11.205'),
      ('v11.204 · Sheep Tag Quest rapid build grid and persistent skill selection',
       'v11.205 · Sheep Tag tactical view and immersive menu polish'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.204'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.205'"),
      ('<title>§wyrl§ Engine · Maker v11.204</title>',
       '<title>§wyrl§ Engine · Maker v11.205</title>'),
    ]: html=once(html,old,new)
    tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag Play tactical top-down view, menu hover and pointer, system overlay stability',
      date='2026-11-01',changes=[
        'The default Sheep Tag Play tactical camera is restored to a more overhead world perspective (~38 degrees down versus prior shallow ~16); built-in wrist VIEW page switches between TACTICAL and FORWARD without forcibly rotating the real WebXR headset.',
        'The existing 3.6-unit Sheep Tag house grid and forward controller ground placement remain independent of the camera height, so players can build close to the sheep while using a strategic view.',
        'Full wrist menus now use compact, cached and more legible 384x192 text label textures. Buttons brighten, grow slightly, and show a soft highlight backing when targeted. A fixed twelve-point glint ring and a soft halo use cached GPU geometry, no new frame loop.',
        'The controller reticle and beam visibly end at the actual menu button or backplate, not the game scene behind it. Both controllers keep their separate cyan and amber ray colors outside target focus.',
        'When WebXR visibilityState becomes visible-blurred/hidden because the Quest OS interface takes focus, freeze nonessential camera-reference translation, suppress cosmetic fog painting and block accidental held build/ability inputs until buttons are released. Network and game authority are not paused.',
        'The v11.204 rapid A/X radial selectors, Quest camera/capture tools, model editor controls, collision, fog authority, and all bundled scenes remain. Larger map graphics, spatial panels and full radial UX redesign are separately tracked.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
