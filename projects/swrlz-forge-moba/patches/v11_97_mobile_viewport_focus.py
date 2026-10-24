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
        'Use the actual phone viewport width for Model Atelier, so the editing dock and tool rail use the responsive mobile layout instead of shrinking a desktop canvas.',
        'Retain 16px mobile input fields, keyboard handling and user pinch-to-zoom accessibility.',
        'Preserve the true sphere blank starter, existing characters, model data and all prior assets.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    raw=html.encode('utf-8')
    print('SWRLZ_V1197_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
