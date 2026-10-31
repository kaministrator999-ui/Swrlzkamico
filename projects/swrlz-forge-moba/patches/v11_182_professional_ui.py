"""§E v11.182: editor UI visual-system polish and read-only collision geometry."""
from pathlib import Path
import json

def once(s, old, new):
    c=s.count(old)
    if c!=1:raise AssertionError((old[:150],c))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/engine_professional_ui_v11_182.css').read_text(encoding='utf-8')
    js=(root/'runtime/engine_professional_ui_v11_182.js').read_text(encoding='utf-8')
    html=once(html,'</head>','<style id="se182ProfessionalUI">\n'+css+'\n</style>\n</head>')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_181_IMMERSIVE_WEBXR_GATE','SWYRL_ENGINE_DEPLOY_MARKER: V11_182_PROFESSIONAL_UI'),
      ('ENGINE · MAKER v11.181','ENGINE · MAKER v11.182'),
      ('v11.181 · enter immersive VR from §E','v11.182 · professional editor layout and overlap audit'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.181'","window.SWRLZ_FORGE_BUILD={version:'v11.182'"),
      ('<title>§wyrl§ Engine · Maker v11.181</title>','<title>§wyrl§ Engine · Maker v11.182</title>'),
    ]:html=once(html,a,b)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Professional §E editor layout and responsive layer cleanup',
      date='2026-10-31',changes=[
       'Unify native toolbar, panel, inspector, cards, modal windows and VR controls using one restrained dark slate/teal design system with consistent focus indicators.',
       'Preserve the horizontally scrollable toolbar instead of floating extra controls over the scene; keep Projects and Play discoverable and protect Quest browser-sized hit targets.',
       'Contain Projects within the visual viewport, keep its header and close control reachable, and preserve its modal priority over Chat, inspector docks and Sheep Tag menus.',
       'Constrain game level controls, in-scene menus and responsive mobile drawers to their own viewports, respecting earlier mobile-tab collision fixes.',
       'Refine embedded Chat and VR Controller Studio presentation without changing their event handlers, auth or stored profiles.',
       'Expose a read-only SWYRL_ENGINE_LAYOUT.audit() geometry and collision receipt for mobile and desktop regression checks; no second renderer, hidden scene actions or gameplay behavior changes.',
       'Physical Quest 2 browser, Android portrait/landscape and live interaction remain owner acceptance steps.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
