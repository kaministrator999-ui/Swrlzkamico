"""§E v11.176: fix connected Google badge, hidden redundant login and live project picker."""
from pathlib import Path
import json

def once(html, old, new):
    count = html.count(old)
    if count != 1:
        raise AssertionError((old[:120], count))
    return html.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    script = (root / "runtime/chat_panel_account_project_v11_176.js").read_text(encoding="utf-8")
    html = once(html, "function mount(){\n  if(document.getElementById('seChatAccountPanel')",
                script + "\nfunction mount(){\n  if(document.getElementById('seChatAccountPanel')")
    html = once(html,
      "revoke('Account changed.');const user=payload.user;accountText.textContent=payload.authenticated&&user?'Connected · '+summaryName(user.name||user.email||'Google account'):'Google account not connected';",
      "revoke('Account changed.');se176AccountState(payload);")
    html = once(html,
      "setStatus(payload.authenticated?'Your Chat account is connected.':'Sign in to load your Chat history and save projects to your account.');return;",
      "setStatus(payload.authenticated?'Your Chat account is connected.':'Sign in to load your Chat history and save projects to your account.');if(payload.authenticated)void se176RefreshProjects();return;")
    html = once(html,
      "cloudRefs.clear();if(cloudList)cloudList.replaceChildren();",
      "cloudRefs.clear();se176AccountState({authenticated:false});")
    html = once(html,
      "const projectId=cloudList.value;if(!projectId){setStatus('Choose an account project first.',true);return;}",
      "const selectedProject=cloudList.value;const projectId=selectedProject.startsWith('cloud:')?selectedProject.slice(6):selectedProject;if(!selectedProject.startsWith('cloud:')){setStatus('Choose a Google-saved project first.',true);return;}")
    html = once(html,
      "cloudRefs.set(projectId,stored);setStatus('Saved to your account · revision '+stored.revision+'.');",
      "cloudRefs.set(projectId,stored);setStatus('Saved to your account · revision '+stored.revision+'.');void se176RefreshProjects();")
    html = once(html,
      "mount();se170Install();se175Install();",
      "mount();se170Install();se175Install();se176Install();")
    html = once(html,
      "function se175UpdateLabel(){\n if(!se175ProjectLabel)return;",
      "function se175UpdateLabel(){\n se176PaintPicker();if(!se175ProjectLabel)return;")
    html = once(html,
      "projectIds.set(currentProject,previousId);se175UpdateLabel();return result;",
      "projectIds.set(currentProject,previousId);se175UpdateLabel();se176PaintPicker();return result;")
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_175_CHAT_PROJECT_WORKFLOW","SWYRL_ENGINE_DEPLOY_MARKER: V11_176_CHAT_ACCOUNT_PROJECT_PICKER"),
      ("ENGINE · MAKER v11.175","ENGINE · MAKER v11.176"),
      ("v11.175 · Chat creates independent native projects","v11.176 · shared Google badge and active project picker"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.175'","window.SWRLZ_FORGE_BUILD={version:'v11.176'"),
      ("<title>§wyrl§ Engine · Maker v11.175</title>","<title>§wyrl§ Engine · Maker v11.176</title>"),
    ]: html = once(html, old, new)
    key="const SE_RELEASE_NOTES="
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Google account state and true project selection in embedded Chat',
      date='2026-10-30',
      changes=[
       'Hide Sign in with Google after verified Chat connection and show a Google badge beside the account name; sign-in returns on logout.',
       'The project selector always shows the actual active native project, even if nothing was saved to Google.',
       'My projects also refreshes local project copies and actual Google-saved cloud copies in distinct groups. Loading a local project uses the existing guarded native loader.',
       'Sign-in and sign-out clear stale cloud choices; account project listing is refreshed automatically. No credentials or account email cross the §E host boundary.',
       'If ChatGPT opens §E and the Google popup in different apps, use §E directly in Chrome; cross-browser login cannot reuse the opener connection.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
