"""§E v11.173: actual modal stacking-context escape and ordered editor layers."""
from pathlib import Path
import json

def once(html, old, new):
    n=html.count(old)
    if n!=1:raise AssertionError((old[:130],n))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/editor_layer_priority_v11_173.css').read_text(encoding='utf-8')
    js=(root/'runtime/editor_layer_priority_v11_173.js').read_text(encoding='utf-8')
    if '</head>' not in html:raise AssertionError('Document head missing')
    html=html.replace('</head>','<style id="se173-editor-layer-priority">'+css+'</style>\n</head>',1)
    anchor='installPerformanceSettings();applyPerformanceSettings();se128LaunchStartupProject();'
    html=once(html,anchor,js+'\n'+anchor)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_172_CLEAN_CHAT_HEADER',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_173_DIALOG_LAYER_PRIORITY'),
      ('ENGINE · MAKER v11.172','ENGINE · MAKER v11.173'),
      ('v11.172 · cleaner Chat side panel','v11.173 · corrected editor dialog stacking'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.172'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.173'"),
      ('<title>§wyrl§ Engine · Maker v11.172</title>',
       '<title>§wyrl§ Engine · Maker v11.173</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Correct dialog and editor panel priority',
      date='2026-10-29',changes=[
        'Projects is now above the right Details and left Outliner panels, Chat, and viewport/game menus when opened.',
        'Preserve native Projects Starter/My Projects tabs, startup checkboxes, Save/Load, and account ownership by moving the original dialog to document.body.',
        'Layer priority is viewport, editor side panels, Chat, then modal dialogs; no camera, gameplay, LAN, account or Chat backend changes.',
        'Closing the dialog returns to the existing editor; Android and Quest physical touch acceptance remains pending.'
      ])
    html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
    return html
