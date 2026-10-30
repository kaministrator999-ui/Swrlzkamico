"""§E v11.178: active workspace analysis from verified read-only native context."""
from pathlib import Path
import json

def once(html,old,new):
    n=html.count(old)
    if n!=1:raise AssertionError((old[:140],n))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    script=(root/'runtime/chat_workspace_analysis_v11_178.js').read_text(encoding='utf-8')
    html=once(html,"function context(){",script+"\nfunction context(){")
    html=once(html,"se175UpdateLabel();if(new TextEncoder().encode(JSON.stringify(value)).length>32768)",
      "se178EnrichContext(value);se175UpdateLabel();if(new TextEncoder().encode(JSON.stringify(value)).length>32768)")
    html=once(html,"mount();se170Install();se175Install();se176Install();",
      "mount();se170Install();se175Install();se176Install();se178Install();")
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_177_GOOGLE_AVATAR_SINGLE_TAB","SWYRL_ENGINE_DEPLOY_MARKER: V11_178_WORKSPACE_ANALYSIS"),
      ("ENGINE · MAKER v11.177","ENGINE · MAKER v11.178"),
      ("v11.177 · Google avatar and copy-code-before-login","v11.178 · read-only active workspace analysis"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.177'","window.SWRLZ_FORGE_BUILD={version:'v11.178'"),
      ("<title>§wyrl§ Engine · Maker v11.177</title>","<title>§wyrl§ Engine · Maker v11.178</title>"),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='§wyrlz Chat inspects the active §E project and workspace',
      date='2026-10-30',
      changes=[
        'Analyze workspace asks connected Chat for a read-only inspection of the actual open project, active level, workspace, selection, edit mode and bounded visible object metadata.',
        'The snapshot includes bounded type counts, duplicate-name and shared-position review hints from current native actor/mesh records. Findings are not visual confirmations or automatic fixes.',
        'Chat refreshes the native context through the existing authenticated lease before replying; scene and selected object edits still require explicit separate requests.',
        'The existing local/cloud project picker, verified Google avatar and mobile sign-in flow are preserved.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
