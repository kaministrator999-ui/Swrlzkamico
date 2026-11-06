"""§E v11.285 — independent Starter Models grouping and compact foreground Projects picker.
Append-only repair of the generated v11.284 runtime. No project data migration.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(("v11.285",label,count,old[:100]))
    return html.replace(old,new,1)

def apply(html):
    # v11.284 calls se236InstallStarterGroups from outside the private
    # Chat-host IIFE. Remove that invalid cross-scope wrapper.
    old='''const se284PriorGroups=se236InstallStarterGroups;
se236InstallStarterGroups=function(){
 const result=se284PriorGroups.apply(this,arguments);
 se284SortStarterCards();
 return result;
};
'''
    html=once(html,old,
       "// v11.285: categories are reconciled by the independent native hub.\n",
       "remove cross-scope starter-group access")
    css=(ROOT/"runtime/project_hub_compact_v11_285.css").read_text("utf8")
    js=(ROOT/"runtime/project_hub_compact_v11_285.js").read_text("utf8")
    assert "</head>" in html
    html=html.replace("</head>",
       '<style id="se285ProjectHubCompact">\n'+css+'\n</style>\n</head>',1)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
       js+"\nwindow.SWRLZ_FORGE_BUILD=",
       "repair native grouping after DOM initialization")
    old_version=" source.engine='§wyrl§ Engine · Maker v11.284';source.version=11.284;"
    assert html.count(old_version)==3,("v11.285 provenance count",html.count(old_version))
    html=html.replace(old_version,
       " source.engine='§wyrl§ Engine · Maker v11.285';source.version=11.285;")
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_284_PLAIN_HAND_MODEL_CATEGORIES",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_285_COMPACT_PROJECT_CATEGORIES"),
      ("ENGINE · MAKER v11.284","ENGINE · MAKER v11.285"),
      ("v11.284 · plain anatomy hand and corrected starter models tabs",
       "v11.285 · compact mobile project library and native starter tabs"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.284'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.285'"),
      ("<title>§wyrl§ Engine · Maker v11.284</title>",
       "<title>§wyrl§ Engine · Maker v11.285</title>")
    ]:
        html=once(html,old,new,"version identity")
    token="const SE_RELEASE_NOTES="
    pos=html.index(token)+len(token)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title="Compact Projects menu with reliable Starter Models sorting",
      date="2026-11-05",changes=[
       "Keep every editable model starter in Projects → Starter Projects → Starter Models; playable game starters stay in Starter Games.",
       "Fix the cross-scope helper call that made previous grouping unreliable. Native project tabs no longer depend on Chat account host mounting.",
       "Reparent existing native card nodes without duplicating event handlers, changing default checkboxes, or modifying user projects.",
       "Make the project picker compact and vertically scrollable on Android and touch/desktop-mode browsers, with shorter cards and accessible category tabs.",
       "Move the active dialog out of editor stacking contexts so the right inspector/sidebar cannot cover it.",
       "Owner phone/Quest visual acceptance remains pending."
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[pos+n:]
