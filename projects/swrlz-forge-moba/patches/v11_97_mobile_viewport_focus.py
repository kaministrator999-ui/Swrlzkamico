"""Repair mobile layout viewport so text fields do not magnify the whole editor."""
import hashlib
import json
import re

def exactly(s,old,new):
    assert s.count(old)==1, (old[:80],s.count(old))
    return s.replace(old,new,1)

def apply(html):
    before=re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',html,flags=re.I)
    print("SWRLZ_V1197_PREEXISTING_VIEWPORT",len(before),repr(before[:3]),flush=True)
    assert len(before)<=1, "Ambiguous viewport directives: fix explicitly"
    # Force true device-width layout; never disable pinch zoom or accessibility.
    viewport='<meta name="viewport" content="width=device-width, initial-scale=1">'
    if before:
        html=html.replace(before[0],viewport,1)
    else:
        match=re.search(r'<head(?:\s[^>]*)?>',html,re.I)
        assert match, "Cannot find real HTML document head"
        html=html[:match.end()]+'\n'+viewport+html[match.end():]
    assert len(re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',html,flags=re.I))==1
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
