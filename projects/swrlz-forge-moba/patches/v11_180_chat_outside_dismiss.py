"""§E v11.180: click/tap outside the Chat side panel slides it closed."""
from pathlib import Path
import json

def once(text,old,new):
    count=text.count(old)
    if count!=1:
        raise AssertionError((old[:120],count))
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/chat_outside_dismiss_v11_180.js').read_text(encoding='utf-8')
    css=(root/'runtime/chat_outside_dismiss_v11_180.css').read_text(encoding='utf-8')
    original=(
      "function openPanel(){open=true;panel.hidden=false;document.getElementById('seChatToggle').setAttribute('aria-expanded','true');document.getElementById('seChatClose').focus();if(!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';if(port)send('host.visibility',{visible:true});}\n"
      "function closePanel(){revoke();open=false;panel.hidden=true;document.getElementById('seChatToggle').setAttribute('aria-expanded','false');document.getElementById('seChatToggle').focus();}"
    )
    html=once(html,original,js)
    html=once(html,
      "panel.addEventListener('keydown',event=>{if(event.key==='Escape'",
      "se180InstallDismiss();\n  panel.addEventListener('keydown',event=>{if(event.key==='Escape'")
    assert '</head>' in html
    html=html.replace('</head>','<style id="seChatOutsideDismissV11180">\n'+css+'\n</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_179_VR_CONTROLLER_STUDIO','SWYRL_ENGINE_DEPLOY_MARKER: V11_180_CHAT_OUTSIDE_DISMISS'),
      ('ENGINE · MAKER v11.179','ENGINE · MAKER v11.180'),
      ('v11.179 · Quest controller profiles and diagnostics','v11.180 · Chat dismisses on outside selection'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.179'","window.SWRLZ_FORGE_BUILD={version:'v11.180'"),
      ('<title>§wyrl§ Engine · Maker v11.179</title>','<title>§wyrl§ Engine · Maker v11.180</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Chat slides away when you choose another part of §E',
      date='2026-10-31',
      changes=[
        'A primary click or tap on the editor outside the embedded Chat panel dismisses Chat, sliding the existing panel to the screen edge; the outside interaction is never intercepted.',
        'Clicks within Chat or on its own toggle do not trigger outside dismissal. The existing toggle, close button and Escape remain available.',
        'The same iframe stays mounted, retaining unsent text and conversation state. Closing revokes the temporary editor editing permission as before.',
        'Outside taps preserve focus on the selected editor control instead of forcing focus onto the Chat toggle. Reduced-motion users receive immediate closure.',
        'No changes to Game Editor, Model Atelier, Sheep Tag, VR Controller Studio, account authorization or native project storage.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
