"""§E v11.294: clear inherited Prism Jester socket assemblies on Hooded Vanguard."""
import json
from pathlib import Path

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.294',label,n,old[:100]))
    return s.replace(old,new,1)

def apply(html):
    # Replacing the canonical starter parts leaves original Prism Jester's
    # assemblies.sockets[].partId and components[].group pointing to deleted
    # model parts. The real loadProject() assembly validator then throws
    # "Invalid named socket." before Model Atelier can activate.
    # The Vanguard is a self-contained *static* model, so discard only the
    # irrelevant inherited attachment graph; do not touch other starters.
    html=once(html,
      "model.parts=parts;model.meshGroups=[];\n  model.rigging=null;",
      "model.parts=parts;model.meshGroups=[];model.assemblies=null;\n  model.rigging=null;",
      'remove stale inherited named sockets when rebasing native model parts')
    old=" source.engine='§wyrl§ Engine · Maker v11.293';source.version=11.293;"
    if html.count(old)!=3:raise AssertionError(('v11.294 version refs',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.294';source.version=11.294;")
    for a,b in (
     ('SWYRL_ENGINE_DEPLOY_MARKER: V11_293_CHAT_CHARACTER_TOOLS',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_294_VANGUARD_SOCKET_LOAD_FIX'),
     ('ENGINE · MAKER v11.293','ENGINE · MAKER v11.294'),
     ('v11.293 · Chat native character tools and visible progress',
      'v11.294 · Hooded Vanguard model loads without inherited sockets'),
     ("window.SWRLZ_FORGE_BUILD={version:'v11.293'",
      "window.SWRLZ_FORGE_BUILD={version:'v11.294'"),
     ('<title>§wyrl§ Engine · Maker v11.293</title>',
      '<title>§wyrl§ Engine · Maker v11.294</title>')
    ):html=once(html,a,b,'build identification')
    token='const SE_RELEASE_NOTES='
    at=html.index(token)+len(token)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard native loader: remove stale inherited sockets',
      date='2026-11-06',changes=[
       'Fix real hosted Hooded Vanguard failure confirmed by targeted Chromium load: native 14-mesh model builds but loadProject rejects the old Prism Jester named sockets with Invalid named socket.',
       'On creation of the new Hooded Vanguard only, set model.assemblies to null after replacing model.parts. This prevents stale sockets and disconnected named assembly groups being validated against the new native mesh IDs.',
       'Keep coherent model parts, saved project schema, material textures, other model starters, current chat character tools, hand updates, XR and game behavior unchanged.',
       'Source assembly and exact release integrity are tested separately; successful Android and Quest visual acceptance remains for the owner.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+width:]
