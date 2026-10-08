"""Episode 01 as a real selectable native editor starter with an in-editor screening room.

The canonical stage set stays independent from Embervault/Starforge.
The separate original canvas animation is a media asset, not a promise that
the §E runtime has a native character-keyframe animation pipeline.
"""
import json
from pathlib import Path


def once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError("Anime starter anchor mismatch: " + old[:120])
    return s.replace(old, new, 1)


SCREENING_CSS = r"""
<style id="animeStarterStyles">
.anime-screening-btn{position:fixed;bottom:16px;right:16px;z-index:80;padding:11px 15px;border:1px solid #9e86df;border-radius:11px;background:#19142e;color:#f1e8ff;font:700 13px system-ui;box-shadow:0 5px 22px #0008}
.anime-screening-btn[hidden]{display:none!important}
.anime-screening{position:fixed;inset:0;z-index:450;background:#030713ef;display:none;align-items:center;justify-content:center;padding:14px}
.anime-screening.open{display:flex}
.anime-screening-shell{width:min(1220px,100%);height:min(93vh,900px);display:flex;flex-direction:column;background:#07101e;border:1px solid #657fad;border-radius:15px;overflow:hidden;box-shadow:0 24px 90px #000e}
.anime-screening-head{padding:8px 13px;display:flex;align-items:center;gap:12px;background:#13213a;color:#e1eeff;font:700 13px system-ui}
.anime-screening-head strong{flex:1}
.anime-screening-head button{padding:7px 13px;border:1px solid #7894c4;border-radius:8px;background:#263752;color:white}
.anime-screening iframe{flex:1;width:100%;border:0;background:#080d18}
@media(max-width:640px){.anime-screening{padding:0}.anime-screening-shell{width:100%;height:100dvh;border-radius:0}.anime-screening-btn{bottom:10px;right:10px}}
</style>
"""


SCREENING_JS = r"""
// Project media screening is deliberately separate from in-world gameplay.
let animeScreeningReturnFocus=null;
function syncAnimeScreening(){
  const button=document.getElementById('animeScreeningBtn');
  if(button)button.hidden=currentProject?.canonicalId!=='ghosts-different-forms-ep01';
}
function closeAnimeScreening(){
  const panel=document.getElementById('animeScreening');
  if(!panel||!panel.classList.contains('open'))return;
  panel.classList.remove('open');
  // Unmount to stop animation, synthesized audio, and keyboard input.
  const frame=document.getElementById('animeEpisodeFrame');
  if(frame)frame.removeAttribute('src');
  const target=animeScreeningReturnFocus?.isConnected?animeScreeningReturnFocus:document.getElementById('animeScreeningBtn');
  animeScreeningReturnFocus=null;
  if(target)target.focus();
}
function openAnimeScreening(){
  if(currentProject?.canonicalId!=='ghosts-different-forms-ep01'){
    toast('Open Ghosts in Different Forms from Projects first.');return false;
  }
  const panel=document.getElementById('animeScreening'),frame=document.getElementById('animeEpisodeFrame');
  if(!panel||!frame)return false;
  animeScreeningReturnFocus=document.activeElement;
  if(document.pointerLockElement)document.exitPointerLock?.();
  panel.classList.add('open');
  // Relative asset is provided by the §E static Space packager.
  frame.src='episodes/ghosts-in-different-forms-ep01.html';
  document.getElementById('animeScreeningClose')?.focus();
  return true;
}
function installAnimeStarterUI(){
  if(document.getElementById('animeScreeningBtn'))return;
  const host=document.body,button=document.createElement('button'),panel=document.createElement('div');
  button.id='animeScreeningBtn';button.className='anime-screening-btn';
  button.type='button';button.textContent='▶ Watch Episode 01';button.hidden=true;
  button.addEventListener('click',openAnimeScreening);
  panel.id='animeScreening';panel.className='anime-screening';panel.setAttribute('role','dialog');
  panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','Anime Episode 01 screening');
  panel.innerHTML='<div class="anime-screening-shell"><div class="anime-screening-head"><strong>👻 Ghosts in Different Forms · Episode 01</strong><button type="button" id="animeScreeningClose">✕ Close screening</button></div><iframe id="animeEpisodeFrame" title="Ghosts in Different Forms animated episode" allow="fullscreen"></iframe></div>';
  panel.addEventListener('pointerdown',event=>{if(event.target===panel)closeAnimeScreening()});
  host.append(button,panel);
  document.getElementById('animeScreeningClose').addEventListener('click',closeAnimeScreening);
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&panel.classList.contains('open')){event.preventDefault();event.stopImmediatePropagation();closeAnimeScreening()}},true);
  // Also refresh when an imported scene changes the project header.
  const name=document.getElementById('currentProjectName');
  if(name)new MutationObserver(syncAnimeScreening).observe(name,{childList:true,characterData:true,subtree:true});
  syncAnimeScreening();
}
function loadCanonicalAnimeEpisode(){
  closeAnimeScreening();
  loadProject(structuredClone(CANONICAL_ANIME_EPISODE_PROJECT),{workspaceLocal:true});
  initializeHistory('Opened Ghosts in Different Forms anime starter');markSaved();
  syncAnimeScreening();
  editorLog('Anime Episode 01 starter · 8 stages · 8 workstations · 8 destinations · 1 guardian dragon','ok');
  toast('Ghosts in Different Forms · anime starter');
}
"""


def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/ghosts-in-different-forms-ep01.swyrl.json').read_text(encoding='utf-8'))
    actors=scene['scene']['actors']
    stations=scene['project']['workspaces']['stations']
    assert len(actors)==62 and len({a['id'] for a in actors})==62
    assert len(stations)==8 and len(scene['project']['teleportZones'])==8
    assert len(scene['editor']['layers'])==3 and sum(a['type']=='dragon' for a in actors)==1
    assert all(len(station.get('files',[]))>=2 for station in stations.values())
    assert scene['project']['canonicalId']=='ghosts-different-forms-ep01'
    scene['engine']='§wyrl§ Engine · Maker v8.5'
    scene['version']=8.5
    encoded=json.dumps(scene,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')
    assert '<script type="module">' in html, "The JS module entrypoint changed"
    s=html.replace('<script type="module">',SCREENING_CSS+'<script type="module">',1)
    anchor='function createProjectFromTemplate(template,force=false){'
    s=once(s,anchor,'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n'+SCREENING_JS+'\n'+anchor)
    old="if(template==='moba')buildMobaProject();else if(template==='default')buildDefaultProject();else if(template==='starforge-observatory')loadCanonicalStarforge();else loadCanonicalGlitchDen();"
    new="if(template==='moba')buildMobaProject();else if(template==='default')buildDefaultProject();else if(template==='starforge-observatory')loadCanonicalStarforge();else if(template==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else loadCanonicalGlitchDen();"
    s=once(s,old,new)
    card_end='<span class="hint den-glow">Open Starforge Observatory</span></button></div>'
    card='<span class="hint den-glow">Open Starforge Observatory</span></button><button class="project-card den" data-project-template="anime-ghosts-ep01"><span class="project-icon">🎬</span><strong>Ghosts in Different Forms</strong><span class="template-tag">ANIME STUDIO STARTER</span><p>Eight explorable scene stages, dialogue and direction workstations, a guardian dragon, and an integrated animated screening.</p><span class="hint den-glow">Open Anime Studio · Episode 01</span></button></div>'
    s=once(s,card_end,card)
    boot="if(new URLSearchParams(location.search).get('project')==='starforge-observatory')loadCanonicalStarforge();else loadCanonicalGlitchDen();"
    new_boot="if(new URLSearchParams(location.search).get('project')==='starforge-observatory')loadCanonicalStarforge();else if(new URLSearchParams(location.search).get('project')==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else loadCanonicalGlitchDen();installAnimeStarterUI();"
    s=once(s,boot,new_boot)
    s=once(s,"  buildStarforgeObservatory:()=>{loadCanonicalStarforge();return true;},","  buildStarforgeObservatory:()=>{loadCanonicalStarforge();return true;},\n  buildAnimeEpisode:()=>{loadCanonicalAnimeEpisode();return true;},\n  openAnimeScreening:()=>openAnimeScreening(),")
    s=once(s,'V8_4_WAYFINDING_ZONE_PREVIEW','V8_5_ANIME_STUDIO_STARTER')
    s=s.replace('Maker v8.4','Maker v8.5').replace('MAKER v8.4','MAKER v8.5')
    s=s.replace("version:'v8.4'","version:'v8.5'").replace('version:8.4','version:8.5')
    s=s.replace("version:'swyrl-engine-agent-v6.4'","version:'swyrl-engine-agent-v6.5'")
    s=s.replace('§E v8.4 Tools','§E v8.5 Tools')
    s=s.replace('v8.4 · WAYFINDING & ZONE PREVIEW','v8.5 · ANIME STUDIO STARTER')
    s=s.replace('§wyrl§ Engine v8.4 · both project workspaces ready','§wyrl§ Engine v8.5 · anime studio starter ready')
    return s

# CI probe: release deployment observation is PR-only and leaves source unchanged.
