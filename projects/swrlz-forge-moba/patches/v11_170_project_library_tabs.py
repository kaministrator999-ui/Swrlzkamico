"""§E v11.170: account-backed project library tab without a second store."""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    if count!=1: raise AssertionError((old[:100],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/project_hub_my_projects_v11_170.js').read_text(encoding='utf-8')
    css=(root/'runtime/project_hub_my_projects_v11_170.css').read_text(encoding='utf-8')
    html=once(html,'</head>','<style id="se170-project-library">'+css+'</style>\n</head>')
    html=once(html,'function mount(){\n  if(document.getElementById(\'seChatAccountPanel\')||disposed)return;',js+'\nfunction mount(){\n  if(document.getElementById(\'seChatAccountPanel\')||disposed)return;')
    html=once(html,'async function loadCloud(){','async function loadCloud(requestedId){')
    html=once(html,'const projectId=cloudList.value;if(!projectId)','const projectId=typeof requestedId===\'string\'?requestedId:cloudList.value;if(!projectId)')
    html=once(html,"cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');",
        "cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');return true;")
    html=once(html,"setStatus(payload.authenticated?'Your Chat account is connected.':'Sign in to load your Chat history and save projects to your account.');return;",
        "setStatus(payload.authenticated?'Your Chat account is connected.':'Sign in to load your Chat history and save projects to your account.');se170AccountStatus(payload);return;")
    html=once(html,"cloudRefs.clear();if(cloudList)cloudList.replaceChildren();",
        "cloudRefs.clear();if(cloudList)cloudList.replaceChildren();se170Invalidate();")
    html=once(html,"ready=true;setStatus('Chat connected. Sign in to use your account.');",
        "ready=true;setStatus('Chat connected. Sign in to use your account.');if(se170Active==='mine')se170Refresh();")
    html=once(html,"if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(mount);",
        "if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(()=>{mount();se170Install();});")
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_169_CHAT_ACCOUNT_PANEL','SWYRL_ENGINE_DEPLOY_MARKER: V11_170_PROJECT_LIBRARY_TABS'),
        ('ENGINE · MAKER v11.169','ENGINE · MAKER v11.170'),
        ('v11.169 · shared Chat account and native editor assistance','v11.170 · starter and account project tabs'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.169'","window.SWRLZ_FORGE_BUILD={version:'v11.170'"),
        ('<title>§wyrl§ Engine · Maker v11.169</title>','<title>§wyrl§ Engine · Maker v11.170</title>'),
    ]: html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Starter Projects and My Projects in the native library',date='2026-10-29',changes=[
        'The existing Projects dialog now has Starter Projects and My Projects tabs, with large touch- and Quest-friendly controls.',
        'My Projects lists saved projects belonging to the connected Chat account with their stored revisions and a Load action.',
        'Project loading reuses the existing authenticated cloud RPC, full native importer, recovery snapshot and unsaved-changes confirmation.',
        'Starter cards, default-starter checkboxes, local file Save/Load and all native starter behavior stay unchanged.',
        'Switching account clears the displayed library; no duplicate storage, credentials or general AI editing permissions were added.',
        'Cloud account login, storage and owner-device acceptance still require real user testing.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    return html
