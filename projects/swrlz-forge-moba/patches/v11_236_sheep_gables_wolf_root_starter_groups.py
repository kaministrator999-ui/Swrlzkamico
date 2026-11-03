"""§E v11.236 — complete sheep house gables, correct wolf face weights and
preview root stabilization, organize existing starter project cards.

Append-only assembler patch: no changes to old source snapshots or saved user
projects. All behaviors use native Model Atelier geometry, rig and project hub.
"""
import json


def once(s, old, new, why):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.236',why,count,old[:160]))
    return s.replace(old,new,1)


def apply(html):
    gable=r""" function se236GableInfill(w,depth,eave,rise){
  // A genuinely closed triangle prism above each rectangular end wall.
  // Previously all four enclosed sheep houses had an open front/rear attic.
  const half=w/2,thickness=.14;
  for(const side of [-1,1]){
   const outer=side*(depth/2+.048),inner=outer-side*thickness;
   const positions=[
    -half,eave,outer,half,eave,outer,0,eave+rise,outer,
    -half,eave,inner,half,eave,inner,0,eave+rise,inner
   ];
   const faces=side>0
    ? [0,1,2,3,5,4,0,3,4,0,4,1,1,4,5,1,5,2,2,5,3,2,3,0]
    : [0,2,1,3,4,5,0,4,3,0,1,4,1,5,4,1,2,5,2,3,5,2,0,3];
   part('Gable · '+(side>0?'front':'rear')+' enclosed attic','topologyMesh',
    d.wall,'matte','Walls / gables',{
     topologyMesh:{positions,indices:faces,uvs:[0,0,1,0,.5,1,0,0,1,0,.5,1]}
    });
  }
 }
"""
    html=once(html," function roofGable(width,depth,eaveY,rise,thatch){",
              gable+" function roofGable(width,depth,eaveY,rise,thatch){",
              "insert native triangular end wall solid builder")
    html=once(html,
       "  roofGable(w+.45,depth,tall+.30,d.type==='hut'?1.65:1.70,d.type!=='barn');\n  doors(depth,d.type==='barn',open);",
       """  roofGable(w+.45,depth,tall+.30,d.type==='hut'?1.65:1.70,d.type!=='barn');
  se236GableInfill(w+.12,depth,tall+.25,d.type==='hut'?1.65:1.70);
  // Real interior floor visible through the intentionally open barn/ram door.
  box('Interior · timber floor',0,.325,0,w-.26,.15,depth-.25,d.trim,'Interior / floor');
  doors(depth,d.type==='barn',open);""",
       "close hut/cottage/barn/ram front and back gables with an editable floor")

    # The v11.234 face weights explicitly classified eyes and ears but the
    # separately modelled nose, nostrils, smile, muzzle and cheek ruff inherited
    # torso/neck weights, making details lag or detach as the head rotated.
    html=once(html,
       """ }else if(part?.wolf224Joint==='head'||region==='face'||region==='muzzle'||
           named.includes('eye')||named.includes('ear ·')){""",
       """ }else if(part?.wolf224Joint==='head'||region==='face'||region==='muzzle'||
           /^(?:nose|nostril|face|eye|ear|ruff · cheek|muzzle|snout|whisker|lip|brow|chin|fang|tooth|teeth)(?:\b| ·)/.test(named)||
           /(?:^|[-_])(?:nose|nostril|muzzle|snout|whisker|cheek|brow|lip)(?:[-_]|$)/.test(pId)){""",
       "bind separate nose and facial detail parts rigidly to skull")

    # Preview-only root stabilization. No changes to authored keyframes, clip
    # schemas or world/gameplay motion. The existing root bone starts at [0,0,0],
    # so the only root translation here is the procedural body-bob height.
    html=once(html,
       """ const root=se224WolfBones.wolf_root,base=rig.bones[0].rest;
 root.position.set(base[0],base[1]+bob,base[2]);
 root.updateMatrixWorld(true);se224WolfSkeleton.update();atelierHDDirty=true;""",
       """ const root=se224WolfBones.wolf_root,base=rig.bones[0].rest;
 const clipName=document.getElementById('modelAtelierWolfClip')?.value||'';
 const locomotion=['walk','run','stalk'].includes(clipName);
 const inPlace=locomotion&&(document.getElementById('se236WolfInPlace')?.checked!==false);
 const steady=locomotion&&(document.getElementById('se236WolfSteady')?.checked!==false);
 if(steady&&se224WolfBones.wolf_spine)se224WolfBones.wolf_spine.rotation.x*=.18;
 root.position.set(base[0],base[1]+(inPlace?0:bob),base[2]);
 root.updateMatrixWorld(true);se224WolfSkeleton.update();atelierHDDirty=true;""",
       "keep wolf root stationary and reduce torso pitch in optional preview mode")

    stabilizer=r""" const se236WolfPreviewOptions=document.createElement('div');
 se236WolfPreviewOptions.id='se236WolfPreviewOptions';
 se236WolfPreviewOptions.innerHTML=
  '<label><input type="checkbox" id="se236WolfInPlace" checked> In place · lock root height</label>'+
  '<label><input type="checkbox" id="se236WolfSteady" checked> Steady torso · reduce walk/run rocking</label>'+
  '<small>Preview only. Disable either to inspect authored movement; animation keys are unchanged. Foot planting/IK is a separate feature.</small>';
 ui.querySelector('#modelAtelierWolfSaveKey')?.after(se236WolfPreviewOptions);
 se236WolfPreviewOptions.addEventListener('change',()=>{
  if(!se224WolfIsModel())return;
  const clip=model().wolfAnimations?.clips?.find(c=>c.name===clipSelect.value);
  const sample=se224WolfSampleClip(clip,se224WolfPreview.elapsed);
  if(sample)se224WolfApplyPose(sample.rotations,sample.bodyBob);
 });
"""
    html=once(html," const sliderUpdate=()=>{",stabilizer+" const sliderUpdate=()=>{",
              "add reversible root-lock and torso-steady options inside native Motion panel")

    tabs=r"""function se236InstallStarterGroups(){
 const pane=document.getElementById('se170-pane-starter');
 const games=pane?.querySelector('.project-grid');
 if(!games||pane.querySelector('#se236StarterGroups'))return;
 const original=[...games.children];
 const models=document.createElement('div');
 models.className=games.className+' se236-starter-grid';
 models.id='se236StarterModels';models.hidden=true;
 games.classList.add('se236-starter-grid');games.id='se236StarterGames';
 games.after(models);
 const isModel=id=>
  /^(?:sheep-(?:free-shelter|thatched-hut|cottage|barn|ram-house)|(?:sheep|wolf)-model|comet-courier|blank-model|floating-hand-glove)$/.test(id)||
  /(?:^|[-_])(?:model|atelier|sculpt|ferret|glove|character|festival)(?:$|[-_])/.test(id);
 for(const child of original){
  const card=child.matches?.('button[data-project-template]')?child:child.querySelector?.('button[data-project-template]');
  if(card&&isModel(card.dataset.projectTemplate))models.append(child);
 }
 const tabs=document.createElement('div');tabs.id='se236StarterGroups';
 tabs.className='se236-starter-tabs';tabs.setAttribute('role','tablist');
 tabs.setAttribute('aria-label','Starter project types');
 const items=[['games','Starter Games',games],['models','Starter Models',models]];
 const choose=which=>{
  for(const [id,,panel] of items){
   const selected=id===which;
   panel.hidden=!selected;
   const button=tabs.querySelector('#se236StarterTab-'+id);
   button.setAttribute('aria-selected',String(selected));
   button.tabIndex=selected?0:-1;
  }
 };
 for(const [id,label,panel] of items){
  panel.setAttribute('role','tabpanel');
  const button=document.createElement('button');
  button.type='button';button.id='se236StarterTab-'+id;
  button.textContent=label;button.setAttribute('role','tab');
  button.setAttribute('aria-controls',panel.id);
  panel.setAttribute('aria-labelledby',button.id);
  button.onclick=()=>choose(id);
  button.addEventListener('keydown',event=>{
   if(event.key!=='ArrowLeft'&&event.key!=='ArrowRight')return;
   event.preventDefault();const next=id==='games'?'models':'games';
   choose(next);tabs.querySelector('#se236StarterTab-'+next)?.focus();
  });
  tabs.append(button);
 }
 games.before(tabs);choose('games');
}
"""
    html=once(html,"function se170Install(){",tabs+"function se170Install(){",
              "install separate games and models sections within Starter Projects")
    html=once(html,"  se170Select('starter');\n}",
              "  se170Select('starter');se236InstallStarterGroups();\n}",
              "activate Starter Games by default without replacing My Projects")
    styles=r"""
<style id="se236StarterCategories">
#projectHub .se236-starter-tabs{
 display:flex;gap:8px;padding:12px 14px 4px;align-items:center;flex-wrap:wrap
}
#projectHub .se236-starter-tabs button{
 flex:1 1 150px;min-height:43px;padding:9px;border-radius:9px;
 border:1px solid #536e91;background:#192b42;color:#d5e9fa;
 font:650 13px system-ui,sans-serif;cursor:pointer
}
#projectHub .se236-starter-tabs button[aria-selected=true]{
 border-color:#80dfda;background:#19565b;color:#fff
}
#projectHub .se236-starter-tabs button:focus-visible{
 outline:3px solid #aaf8ef;outline-offset:2px
}
#projectHub .se236-starter-grid[hidden]{display:none!important}
#modelAtelierPanel #se236WolfPreviewOptions{
 display:grid;gap:7px;padding:9px;border:1px solid #416481;
 background:#142a3c;border-radius:8px;margin:6px 0;color:#deecfa
}
#modelAtelierPanel #se236WolfPreviewOptions label{
 display:flex;flex-direction:row;align-items:center;gap:8px;
 font:600 12px/1.3 system-ui,sans-serif
}
#modelAtelierPanel #se236WolfPreviewOptions input{
 width:19px;height:19px;flex:0 0 auto
}
#modelAtelierPanel #se236WolfPreviewOptions small{
 color:#aac5d7;font:11px/1.4 system-ui,sans-serif
}
</style>
"""
    if '</head>' not in html:
        raise AssertionError('No outer document head for category styling')
    html=html.replace('</head>',styles+'</head>',1)

    old=" source.engine='§wyrl§ Engine · Maker v11.235';source.version=11.235;"
    if html.count(old)!=2:
        raise AssertionError(('v11.236 source provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.236';source.version=11.236;")
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_235_WOLF_MOTION_PANEL_VISIBILITY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_236_SHEEP_GABLES_WOLF_ROOT_STARTER_GROUPS'),
      ('ENGINE · MAKER v11.235','ENGINE · MAKER v11.236'),
      ('v11.235 · accessible Astra wolf Motion controls',
       'v11.236 · sheep gables, wolf root preview, starter categories'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.235'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.236'"),
      ('<title>§wyrl§ Engine · Maker v11.235</title>',
       '<title>§wyrl§ Engine · Maker v11.236</title>')
    ]:
        html=once(html,a,b,'release identity')

    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
      title='Sheep houses complete, wolf root preview, organized starter games/models',
      date='2026-11-02',
      changes=[
        'Complete four Sheep Tag enclosed house starters with real editable solid front and rear gable triangles and an interior timber floor. Open shelter intentionally remains an open lean-to.',
        'Bind Astra wolf nose, nostrils, cheek ruff, lip/smile and other separately authored facial detail meshes to the head so they do not lag behind the animated skull.',
        'Wolf Motion now offers optional In place (root height locked) and Steady torso (reduced gait rocking) toggles, enabled by default for walk/run/stalk. These only change preview, not original animation keyframes or Sheep Tag locomotion.',
        'Projects → Starter Projects now contains Starter Games and Starter Models sub-tabs, keeping the existing My Projects library and every original project card/default checkbox functional.',
        'No new 3D renderer, physics changes, model storage migration, world controller changes, or alterations to other studios. Verify appearance and comfort with the owner’s real phone/Quest.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
