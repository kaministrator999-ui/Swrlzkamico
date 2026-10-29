"""§E v11.171: fix native Projects vs Sheep Tag menu stacking priority."""
from pathlib import Path
import json

def once(html,old,new):
    count=html.count(old)
    if count!=1: raise AssertionError((old[:120],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/project_hub_layer_v11_171.css').read_text(encoding='utf-8')
    if '</head>' not in html: raise AssertionError('Document head missing')
    html=html.replace('</head>','<style id="se171-project-hub-layer">'+css+'</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_170_PROJECT_LIBRARY_TABS','SWYRL_ENGINE_DEPLOY_MARKER: V11_171_PROJECT_MODAL_PRIORITY'),
      ('ENGINE · MAKER v11.170','ENGINE · MAKER v11.171'),
      ('v11.170 · starter and account project tabs','v11.171 · project dialog layering'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.170'","window.SWRLZ_FORGE_BUILD={version:'v11.171'"),
      ('<title>§wyrl§ Engine · Maker v11.170</title>','<title>§wyrl§ Engine · Maker v11.171</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Projects dialog now appears above Sheep Tag menus',
      date='2026-10-29',changes=[
      'Projects is the active foreground dialog over Sheep Tag main/start menu and other engine viewport menus.',
      'Both existing Starter Projects and My Projects tabs, their buttons and all native account Save/Load behavior remain unchanged.',
      'Closing Projects restores the original Sheep Tag menu; attract scene, start/Play, LAN, gameplay and editor remain untouched.',
      'Narrow fixed-position stacking correction supports Android portrait/landscape, while the Chat side panel remains separate.',
      'Real Android and Quest visual/touch acceptance requires owner-device testing.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    return html
