"""§E v11.177: actual verified Google avatar and preflight code before mobile popup."""
from pathlib import Path
import json

def once(html,old,new):
    count=html.count(old)
    if count!=1:raise AssertionError((old[:150],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    source=(root/'runtime/chat_avatar_single_tab_v11_177.js').read_text(encoding='utf-8')
    original="""async function signIn(){
  if(!ready){setStatus('Chat is still connecting. Try sign-in when it is ready.',true);return;}
  popup=window.open('about:blank','seChatAccountConnect','popup,width=520,height=700');if(!popup){setStatus('Allow the account sign-in popup, then try again.',true);return;}
  try{const result=await rpc('account.signIn');const url=new URL(result.loginUrl,CHAT_ORIGIN);if(url.origin!==CHAT_ORIGIN||url.pathname!=='/forge/login'||!bounded(result.pairId,128)||url.searchParams.get('pairId')!==result.pairId)throw Error('INVALID_LOGIN_URL');popupPair=result.pairId;popup.location.href=url.href;setStatus('Complete Google sign-in and Connect in the account window.');}
  catch(error){popup.close();popup=null;popupPair=null;setStatus(error.message,true);}
}"""
    html=once(html,original,source)
    html=once(html,"if(mark)mark.hidden=!connected;",
      "if(mark){mark.hidden=!connected;se177ShowPicture(mark,connected?payload.user.picture:'');}if(connected)se177ResetPrepared();")
    # Keep v11.176's native active/local/cloud selector; only augment its
    # account avatar display and the existing sign-in button.
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_176_CHAT_ACCOUNT_PROJECT_PICKER","SWYRL_ENGINE_DEPLOY_MARKER: V11_177_GOOGLE_AVATAR_SINGLE_TAB"),
      ("ENGINE · MAKER v11.176","ENGINE · MAKER v11.177"),
      ("v11.176 · shared Google badge and active project picker","v11.177 · Google avatar and copy-code-before-login"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.176'","window.SWRLZ_FORGE_BUILD={version:'v11.177'"),
      ("<title>§wyrl§ Engine · Maker v11.176</title>","<title>§wyrl§ Engine · Maker v11.177</title>"),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Real Google profile photo and copy pairing code before opening sign-in',
      date='2026-10-30',
      changes=[
        'The verified Google profile photo replaces the generic G beside the connected account when available. Unknown images fall back to the G badge.',
        'Signing in from §E first prepares the Chat-origin one-time code, visible and copyable at the top of embedded Chat. Continue to Google is a separate user click.',
        'The account proof is never sent to §E, included in the URL or persisted. Google-origin session verification, PKCE single-use redemption and account isolation are preserved.',
        'Native active/local/cloud project selector and Sheep Tag scenes are unchanged. A browser that destroys the original §E tab may still interrupt in-memory pairing; use Chrome when needed.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
