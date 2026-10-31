"""§E v11.184: project preview cards and one saved-project startup default."""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.184 anchor',old[:150],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    boot=(root/'runtime/user_project_default_boot_v11_184.js').read_text(encoding='utf8')
    gallery=(root/'runtime/user_project_cards_v11_184.js').read_text(encoding='utf8')
    css=(root/'runtime/user_project_cards_v11_184.css').read_text(encoding='utf8')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se184SavedGallery">\n'+css+'\n</style>\n</head>',1)
    # Startup module shares the native single default-starter localStorage
    # key, keeping exactly one selection across starter and user projects.
    html=once(html,'function se128ReadDefault(){',boot+'\nfunction se128ReadDefault(){')
    html=once(html,
      " const requested=se128ReadDefault();\n window.se128StartupPending=true;",
      " if(window.SWYRL_ENGINE_SAVED_DEFAULT?.launch())return;\n const requested=se128ReadDefault();\n window.se128StartupPending=true;")
    html=once(html,
      "  label?.classList.toggle('se128-selected-default',input.checked);\n }\n}",
      "  label?.classList.toggle('se128-selected-default',input.checked);\n }\n window.SWYRL_ENGINE_SAVED_DEFAULT?.sync();\n}")

    # In-gallery helpers live in the existing account host closure, reusing
    # its auth / cloud RPC, native project loader and IndexedDB methods.
    html=once(html,'let se170Pane=null,',gallery+'\nlet se170Pane=null,')

    # Use real local scene data for small, persistent overview metadata.
    html=once(html,
      "return {id:projectId,name:summaryName(data.project.projectName),starterId:summaryName(data.project.sourceStarterId||data.project.template),updatedAt:new Date().toISOString(),data};",
      "return {id:projectId,name:summaryName(data.project.projectName),starterId:summaryName(data.project.sourceStarterId||data.project.template),updatedAt:new Date().toISOString(),preview:se184ExtractPreview(data),data};")

    # Local names are cheap IndexedDB metadata; view cards are built from
    # that metadata and do not clone complete scenes on library open.
    html=once(html,
      "const records=await se175Read();se175LocalList.replaceChildren();",
      "const records=await se175Read();se175LocalList.replaceChildren();se184RenderLocalProjects(records);")
    html=once(html,
      "document.getElementById('se170-tab-mine')?.addEventListener('click',se175RefreshLocal);",
      "document.getElementById('se170-tab-mine')?.addEventListener('click',se175RefreshLocal);\n se184InstallLocalGallery();")

    # Cloud list RPC continues to return metadata only; never download every
    # account project just to open a menu. A specific card's Preview scene
    # action can request its scene without altering the active editor.
    old_cloud="    for(const project of data.projects){\n      if(!bounded(project?.id,160))continue;\n      const card=document.createElement('article');card.className='se170-project-card';\n      const name=document.createElement('strong');name.textContent=summaryName(project.name)||'Untitled project';\n      const version=document.createElement('span');version.textContent='Revision '+(Number.isInteger(project.revision)?project.revision:'unknown');\n      const load=document.createElement('button');load.type='button';load.textContent='Load';load.setAttribute('aria-label','Load '+name.textContent);\n      load.onclick=async()=>{\n        if(cloudBusy)return;\n        load.disabled=true;se170Message('Loading '+name.textContent+'…');\n        try{const loaded=await loadCloud(project.id);\n          if(loaded){document.getElementById('projectHub')?.classList.remove('show');se170Message('Project loaded.');}\n          else se170Message('Project was not loaded; your previous workspace is preserved.');\n        }finally{load.disabled=false;}\n      };\n      card.append(name,version,load);se170Cards.append(card);\n    }"
    html=once(html,old_cloud,'    se184RenderCloudProjects(data.projects);')
    html=once(html,'function se170Invalidate(){\n  se183CloudCacheClear();',
      'function se170Invalidate(){\n  se184AccountReset();\n  se183CloudCacheClear();')
    html=once(html,'function se170AccountStatus(payload){\n  se170Invalidate();',
      'function se170AccountStatus(payload){\n  se170Invalidate();\n  se184LastAccountState=payload;\n  se184TryCloudDefault();')
    html=once(html,
      "ready=true;setStatus('Chat connected. Sign in to use your account.');if(se170Active==='mine')se170Refresh();",
      "ready=true;setStatus('Chat connected. Sign in to use your account.');se184TryCloudDefault();if(se170Active==='mine')se170Refresh();")

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_183_PROJECT_UI_LOADING','SWYRL_ENGINE_DEPLOY_MARKER: V11_184_SAVED_PROJECT_PREVIEWS_AND_DEFAULT'),
      ('ENGINE · MAKER v11.183','ENGINE · MAKER v11.184'),
      ('v11.183 · clear project controls and faster loading','v11.184 · saved project previews and startup default'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.183'","window.SWRLZ_FORGE_BUILD={version:'v11.184'"),
      ('<title>§wyrl§ Engine · Maker v11.183</title>','<title>§wyrl§ Engine · Maker v11.184</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Saved-project previews and one startup default across starters and your projects',
      date='2026-10-31',changes=[
       'My Projects now shows responsive preview cards for on-device and account projects with title, native open action and one Load this project by default checkbox.',
       'New local project snapshots save small scene-derived top-down overviews based on real actor positions. Older local saves and cloud cards have lightweight illustrations and on-demand scene preview; no bulk cloud downloads or second renderer.',
       'The existing starter default setting and saved-project defaults use one same-browser preference. Selecting any checkbox clears every other selected default; unchecked restores Dragon Den.',
       'On ordinary §E launches, a selected local saved project loads directly from IndexedDB. A selected account project is loaded only after verified Chat sign-in; an unavailable account safely falls back without silently replacing subsequent owner edits.',
       'Explicit ?project= URL links take precedence. Saved project scene data, workspace autosaves, account credentials, model tools, Sheep Tag LAN and WebXR remain unchanged.',
       'Owner Android and Quest project-gallery acceptance remains outstanding.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
