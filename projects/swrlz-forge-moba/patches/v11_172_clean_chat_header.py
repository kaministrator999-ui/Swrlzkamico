"""§E v11.172: remove redundant 'Open Chat' link from embedded Chat header."""
import json

def once(html,old,new):
    n=html.count(old)
    if n!=1:raise AssertionError((old[:120],n))
    return html.replace(old,new,1)

def apply(html):
    # Only remove the external link in the existing embedded Chat panel header.
    # Keep the launcher, Close button, authenticated sign-in, account-project
    # controls and the separate My Projects sign-in action unchanged.
    html=once(html,
      '<strong>§wyrlz Chat</strong><a href="https://kamiloki-swyrlz.hf.space" target="_blank" rel="noopener">Open Chat</a><button type="button" id="seChatClose"',
      '<strong>§wyrlz Chat</strong><button type="button" id="seChatClose"')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_171_PROJECT_MODAL_PRIORITY','SWYRL_ENGINE_DEPLOY_MARKER: V11_172_CLEAN_CHAT_HEADER'),
      ('ENGINE · MAKER v11.171','ENGINE · MAKER v11.172'),
      ('v11.171 · project dialog layering','v11.172 · cleaner Chat side panel'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.171'","window.SWRLZ_FORGE_BUILD={version:'v11.172'"),
      ('<title>§wyrl§ Engine · Maker v11.171</title>','<title>§wyrl§ Engine · Maker v11.172</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Simplified embedded Chat side-panel header',
      date='2026-10-29',changes=[
      'Remove redundant external Open Chat link from the embedded §wyrlz Chat header; retain the title and Close button.',
      'Keep the standalone Chat link available elsewhere, without promoting it inside a panel that already displays Chat.',
      'Google sign-in, same-account history and project Save/Load, My Projects sign-in, editor permissions and Chat transport are unchanged.',
      'Keep v11.171 foreground Projects dialog fix, original Sheep Tag menu, Quest controls, engine source/assets and model behavior unchanged.'
      ])
    html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
    return html
