"""§E v11.185: glitch/wisp startup and collapsible Model Atelier settings."""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.185 anchor mismatch',old[:120],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_wisp_boot_atelier_v11_185.js').read_text(encoding='utf8')
    css=(root/'runtime/engine_wisp_boot_atelier_v11_185.css').read_text(encoding='utf8')
    html=html.replace('</head>','<style id="se185WispBootAtelier">\n'+css+'\n</style>\n</head>',1)
    # Earlier stable boot gate owns visibility; decorate only, never change its readiness.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    # Call after the native grouped toolbar is assembled. No tool DOM nodes are cloned.
    html=once(html,' seAtelierTopBarArrange(panel);',' seAtelierTopBarArrange(panel);\n se185InstallAtelierToggle(panel);')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_184_SAVED_PROJECT_PREVIEWS_AND_DEFAULT','SWYRL_ENGINE_DEPLOY_MARKER: V11_185_WISP_GLITCH_BOOT_ATELIER_COLLAPSE'),
      ('ENGINE · MAKER v11.184','ENGINE · MAKER v11.185'),
      ('v11.184 · saved project previews and startup default','v11.185 · glitch-wisp startup and collapsible modeling settings'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.184'","window.SWRLZ_FORGE_BUILD={version:'v11.185'"),
      ('<title>§wyrl§ Engine · Maker v11.184</title>','<title>§wyrl§ Engine · Maker v11.185</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Glitch/wisp startup and collapsible Model Atelier top settings',
       date='2026-10-31',changes=[
       'Replace the plain legacy startup cover with a lightweight particle-fragment §E sigil, cyan-violet wisps, glowing rings and honest initialization phases; no extra 3D scene, media or dependency.',
       'Preserve the existing ready-state gate and watchdog so slow saved-project restores stay covered and initialization cannot trap the user.',
       'Model Atelier top render, target, camera, display and reference settings can collapse into a compact Settings toggle, leaving Save, Export, Close, viewport and bottom tool rail available.',
       'Remember expanded/collapsed preference on this browser; mobile defaults collapsed, desktop expanded; native controls and their event handlers are retained.',
       'Honor reduced-motion accessibility, including static startup presentation and accessible status; project data and engine functionality remain unchanged.',
       'Physical Android and Quest acceptance remains with the owner.'
       ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\\\\\/')+html[pos+count:]
