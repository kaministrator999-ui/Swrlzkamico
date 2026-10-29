"""§E: canonical Chat side panel, shared account and typed native edit bridge."""
from pathlib import Path
import json

def once(html, old, new):
    if html.count(old) != 1:
        raise AssertionError((old[:100], html.count(old)))
    return html.replace(old, new, 1)

def apply(html):
    source = (Path(__file__).resolve().parents[1] / 'runtime/chat_account_panel_v1.js').read_text(encoding='utf-8')
    start = source.index('/* ATELIER_BRIDGE_START */')
    end = source.index('/* ATELIER_BRIDGE_END */') + len('/* ATELIER_BRIDGE_END */')
    bridge = source[start:end]
    host = source[end:]
    html = once(html, '  return Object.freeze({presentationStatus:atelierGirlPresentationV1193,',
                bridge + '\n  return Object.freeze({chatAction:seChatAtelierApply,presentationStatus:atelierGirlPresentationV1193,')
    anchor = 'installPerformanceSettings();applyPerformanceSettings();se128LaunchStartupProject();'
    html = once(html, anchor, host + '\n' + anchor)
    # User-supplied literal actor labels are data, including angle brackets.
    # Preserve exact stored text and use textContent in the mobile inspector.
    html = once(html, "<b>'+selected.name+'</b>", '<b id="seChatMobileActorLabel"></b>')
    html = once(html, "</div></div>';d.querySelector('#miMulti').onclick=", "</div></div>';d.querySelector('#seChatMobileActorLabel').textContent=selected.name;d.querySelector('#miMulti').onclick=")
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_168_QUEST_BROWSER_PANEL','SWYRL_ENGINE_DEPLOY_MARKER: V11_169_CHAT_ACCOUNT_PANEL'),
        ('ENGINE · MAKER v11.168','ENGINE · MAKER v11.169'),
        ('v11.168 · Quest Browser comfort and device profiling','v11.169 · shared Chat account and native editor assistance'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.168'","window.SWRLZ_FORGE_BUILD={version:'v11.169'"),
        ('<title>§wyrl§ Engine · Maker v11.168</title>','<title>§wyrl§ Engine · Maker v11.169</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Your Chat, Google account projects and native editor assistance',date='2026-10-29',changes=[
        'Open the full §wyrlz Chat in the §E side panel, or continue in the standalone Chat page.',
        'Connect your existing Google Chat account in a first-party sign-in window to load the same history and explicitly saved settings.',
        'Save and load complete native projects through separate encrypted account storage; local editing and downloads remain available.',
        'Ask Chat to inspect the active workspace or make supported native mesh and scene edits. Actions need the open visible editor and actual native receipts; close the panel to pause access.',
        'Native Undo/Redo remains available. Unsupported requests, stale selections and partial failures are reported truthfully; no model scripts execute in the editor.',
        'Keep Quest Browser controls and existing game, project, level and LAN behavior. Real Google account and owner-device acceptance are separate from controlled tests.',
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    return html
