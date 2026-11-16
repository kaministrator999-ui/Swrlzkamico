"""§E v11.476: first-paint Google account gateway and safe session restoration.
Append-only native wiring. Google auth stays in the existing Chat origin;
scene mutations and saved-project validation stay with native engine handlers.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_476_ACCOUNT_FIRST_WORKSPACE'
def once(html,old,new):
    n=html.count(old)
    assert n==1,('se476 source anchor drift',old[:110],n)
    return html.replace(old,new,1)
def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_475_PROGRESSIVE_RAIL_VISIBILITY' in html
    runtime=lambda file:(ROOT/'runtime'/file).read_text('utf8')
    js=runtime('engine_account_start_v11_476.js')
    css=runtime('engine_account_start_v11_476.css')
    bridge=runtime('engine_account_bridge_v11_476.js')
    camera=runtime('engine_resume_camera_v11_476.js')
    assert 'SE476_ENGINE_ACCOUNT_START_START' in js
    # The original Chat host already handles popup binding, session identity,
    # local IndexedDB records, cloud versions and dirty/recovery guards.
    html=once(html,"function mount(){\n  if(document.getElementById('seChatAccountPanel')",
       bridge+"\nfunction mount(){\n  if(document.getElementById('seChatAccountPanel')")
    html=once(html,"se175LocalMessage('Loaded '+wanted.name+'.');",
       "se175LocalMessage('Loaded '+wanted.name+'.');window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('local',wanted.id);")
    html=once(html,
       "cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');",
       "cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('cloud',result.project.id);")
    # Emit only a verified boolean account state; no identity or Google token
    # crosses from the Chat origin. This is after the existing account verifier.
    html=once(html,"revoke('Account changed.');se176AccountState(payload);",
      "revoke('Account changed.');se176AccountState(payload);"+
      "window.dispatchEvent(new CustomEvent('swrlz:account-assets',{detail:{authenticated:payload?.authenticated===true&&!!payload?.user}}));")
    html=once(html,"cloudRefs.clear();se176AccountState({authenticated:false});se170Invalidate();",
      "cloudRefs.clear();se176AccountState({authenticated:false});se170Invalidate();"+
      "window.dispatchEvent(new CustomEvent('swrlz:account-assets',{detail:{authenticated:false}}));")
    # Native camera binding is intentionally scoped to ModelAtelier.
    html=once(html,'/* SE430_MODEL_STUDIO_CAMERA_END */',
       '/* SE430_MODEL_STUDIO_CAMERA_END */\n'+camera)
    html=once(html,'/* SE475_PROGRESSIVE_RAIL_VISIBILITY_END */',
       '/* SE475_PROGRESSIVE_RAIL_VISIBILITY_END */\n'+js)
    assert '</head>' in html
    html=html.replace('</head>','<style id="se476AccountStartStyles">\n'+css+'\n</style>\n</head>',1)
    # First paint is covered; the native scene initializes beneath the gateway
    # so existing performance, project and VR boot contracts are not rewritten.
    gate="""<section id="se476StartupGate" aria-label="§wyrl§ Engine account and project startup">
 <div id="se476StartupCard">
  <h1>§wyrl§ Engine</h1><p class="se476-lead">Connect your Google account, synchronize your projects, and restore your workspace before entering the editor.</p>
  <section id="se476SignalLost" class="se476-signal-lost" role="region" aria-label="§C connection unavailable" hidden>
    <div class="se476-signal-art" aria-hidden="true">
      <div class="se476-signal-rings"></div>
      <span class="se476-signal-glyph" data-glitch="§C">§C</span>
      <span class="se476-signal-static"></span>
    </div>
    <p class="se476-signal-code">§C:// CONNECTION_UNAVAILABLE</p>
    <h2 class="se476-signal-title" data-glitch="SIGNAL LOST">SIGNAL LOST</h2>
    <p class="se476-signal-detail">The Chat Space cannot be reached right now. Your saved on-device projects are still available, and none have been deleted.</p>
    <button id="se476RetryConnection" type="button">↻ Reconnect to §C</button>
  </section>
  <div class="se476-group" aria-label="Account sign in">
   <strong class="se476-section-title">Account</strong>
   <span id="se476AccountLabel">Checking Google account…</span>
   <button id="se476SignIn" type="button" class="se476-primary">Sign in with Google</button>
  </div>
  <div class="se476-group" aria-label="Choose saved project">
   <label class="se476-section-title" for="se476Projects">Projects</label>
   <select id="se476Projects"><option value="">Continue current workspace</option></select>
   <label class="se476-check"><input type="checkbox" id="se476Remember"> Automatically load the selected project next time</label>
   <p class="se476-note">When no project is marked automatic, §E restores the last successfully opened saved project and studio. Unsaved work remains subject to the existing Save controls.</p>
  </div>
  <div class="se476-actions">
   <button id="se476Open" type="button" class="se476-primary">Open workspace</button>
   <button id="se476ContinueLocal" type="button">Continue with local projects</button>
  </div>
  <div id="se476StartupStatus" role="status" aria-live="polite">Checking existing account session…</div>
 </div>
</section>"""
    head_end=html.index('</head>')+len('</head>')
    match=re.search(r'<body(?:\s[^>]*)?>',html[head_end:],flags=re.I)
    if match:
        absolute=head_end+match.end()
    else:
        absolute=-1
    assert match,('se476 original body tag not found')
    html=html[:absolute]+'\n'+gate+html[absolute:]
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_475_PROGRESSIVE_RAIL_VISIBILITY',MARKER),
      ('ENGINE · MAKER v11.475','ENGINE · MAKER v11.476'),
      ('v11.475 · visible mobile tool flyouts','v11.476 · Google-first project restoration'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.475'","window.SWRLZ_FORGE_BUILD={version:'v11.476'"),
      ('<title>§wyrl§ Engine · Maker v11.475</title>','<title>§wyrl§ Engine · Maker v11.476</title>')
    ]:html=once(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.475';source.version=11.475;"
    assert html.count(old)==5,('se476 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.476';source.version=11.476;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.475']
    notes['history'].insert(0,{'version':'v11.475','changes':notes.get('changes',[])})
    notes.update(version='v11.476',date='2026-11-16',
      title='Google-first startup and last-workspace restore',
      changes=[
        'New first-paint Google sign-in and project selection gateway appears before the editor is exposed; existing §Chat OAuth verifies the account, with no duplicate credentials or token storage.',
        'Account/cloud project list loads before opening an authenticated saved project. Existing local projects work offline; a §Chat outage does not trap the user.',
        'An explicitly checked default project wins. Without a checked default, the last successfully loaded saved project is restored where available, including its last studio, model camera orbit/position, and existing locally persisted settings.',
        'Cloud and on-device projects use original native revision/dirty/recovery guards. No project bytes or Google credentials are stored in localStorage.',
        'Existing engine game/Model/Particle/Material routing, renderer, VR and Undo remain authoritative. Physical Moto/Quest acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
