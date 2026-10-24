"""Repair mobile layout viewport so text fields do not magnify the whole editor."""
import hashlib
import json
import re

def exactly(s,old,new):
    assert s.count(old)==1, (old[:80],s.count(old))
    return s.replace(old,new,1)

def apply(html):
    # Restrict changes to the real HTML <head>; older runtime templates may
    # contain viewport strings inside JavaScript that must remain unchanged.
    tag_re=r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>'
    end=re.search(r'</head\s*>',html,re.I)
    assert end, 'Cannot locate document head closing tag'
    dochead,tail=html[:end.start()],html[end.start():]
    existing=re.findall(tag_re,dochead,flags=re.I)
    print("SWRLZ_V1197_PREEXISTING_HEAD_VIEWPORT",len(existing),repr(existing),flush=True)
    print("SWRLZ_V1197_VIEWPORT_OTHER_TEMPLATES",
          len(re.findall(tag_re,tail,flags=re.I)),flush=True)
    # Deduplicate conflicting legacy directives and preserve browser pinch zoom.
    dochead=re.sub(tag_re,'',dochead,flags=re.I)
    match=re.search(r'<head(?:\s[^>]*)?>',dochead,re.I)
    assert match, 'Cannot find actual HTML document opening head'
    viewport='<meta name="viewport" content="width=device-width, initial-scale=1">'
    dochead=dochead[:match.end()]+'\n'+viewport+dochead[match.end():]
    html=dochead+tail
    assert len(re.findall(tag_re,html[:html.lower().find('</head>')],flags=re.I))==1
    from pathlib import Path
    mobile_js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_mobile_numpad_v11_97.js').read_text()
    assert html.count('const ModelAtelier=(()=>{')==1
    html=html.replace('const ModelAtelier=(()=>{',mobile_js+'\nconst ModelAtelier=(()=>{',1)
    assert html.count('ModelAtelier.install();')==1
    html=html.replace('ModelAtelier.install();','ModelAtelier.install();\nseMobileNumberPadInstall();',1)
    input_css=".se-mobile-numpad[hidden]{display:none!important}\n.se-mobile-numpad{position:fixed;inset:0;z-index:9000;color:#edf8ff;font:16px/1.35 system-ui,sans-serif}\n.se-mobile-numpad-shade{position:absolute;inset:0;background:rgba(4,10,24,.74)}\n.se-mobile-numpad-dialog{position:fixed;transform:translate(-50%,-50%);width:340px;overflow-y:auto;\n background:#1a2943;border:1px solid #78c5d3;border-radius:14px;box-shadow:0 14px 40px #000b;padding:12px}\n.se-mobile-numpad-dialog h3{font-size:17px;margin:0 0 8px}\n#seMobileNumValue{display:block;background:#101b31;color:#fff;border:1px solid #6887a6;\n border-radius:8px;padding:8px 10px;font:24px/1.35 ui-monospace,monospace;min-height:48px;overflow-wrap:anywhere}\n#seMobileNumHelp{margin:6px 0 10px;color:#c5d6e7;font-size:13px}\n.se-mobile-numpad-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px}\n.se-mobile-numpad-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:10px}\n.se-mobile-numpad button{background:#293e61;color:#f4ffff;border:1px solid #8aaac7;border-radius:9px;\n min-height:44px;font:600 18px/1.3 system-ui,sans-serif;touch-action:manipulation}\n.se-mobile-numpad-actions button{font-size:15px}\n.se-mobile-numpad button.se-mobile-numpad-apply{background:#166c73}\n.se-mobile-numpad button:disabled{opacity:.45}\n"
    html=html.replace('</head>','<style id="se-v1197-numpad-style">'+input_css+'</style>\n</head>',1)
    marker='SWYRL_ENGINE_DEPLOY_MARKER: V11_96_MOBILE_INPUT_ROUND_BLANK'
    html=exactly(html,marker,'SWYRL_ENGINE_DEPLOY_MARKER: V11_97_MOBILE_VIEWPORT_FOCUS')
    for old,new in [
        ('ENGINE · MAKER v11.96','ENGINE · MAKER v11.97'),
        ('v11.96 · mobile inputs and round blank model','v11.97 · device-width mobile model editor'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.96'","window.SWRLZ_FORGE_BUILD={version:'v11.97'"),
        ('<title>§wyrl§ Engine · Maker v11.96</title>','<title>§wyrl§ Engine · Maker v11.97</title>'),
    ]:html=exactly(html,old,new)
    prefix='const SE_RELEASE_NOTES='
    start=html.index(prefix)+len(prefix)
    notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Mobile device-width editor and focus usability',date='2026-10-23',changes=[
        'Normalize the actual document viewport and preserve the mobile edit layout.',
        'Tap a numeric field to use the in-editor number pad without triggering browser keyboard focus and auto magnification.',
        'Retain 16px mobile input fields, keyboard handling and user pinch-to-zoom accessibility.',
        'Preserve the true sphere blank starter, existing characters, model data and all prior assets.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    raw=html.encode('utf-8')
    print('SWRLZ_V1197_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
