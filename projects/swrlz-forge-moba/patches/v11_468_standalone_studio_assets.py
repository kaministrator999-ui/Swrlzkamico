"""§E v11.468: standalone Model and Particle asset persistence without game-scene mutation."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(s,a,b):
 n=s.count(a)
 assert n==1,('v11.468 source anchor',a[:140],n)
 return s.replace(a,b,1)
def apply(html):
 js=(ROOT/'runtime/studio_standalone_assets_v11_468.js').read_text('utf8')
 # Modeler standalone loader writes only the existing native scratch model.
 # It does not call loadProject or modify the game project.
 html=once(html,
  "  scratchModel,usingScratch,isScratchModel:data=>data===scratch,",
  """  scratchModel,usingScratch,isScratchModel:data=>data===scratch,
  loadStandaloneModel(data){
   if(!data||data.schema!=='swyrl-model-atelier-v1'||!validDraft(data))return false;
   if(active!=='modeler')return false;
   scratch=structuredClone(data);preferScratch=true;draftChanged=true;flushDraft();
   ModelAtelier.close();ModelAtelier.syncProject();ModelAtelier.open();renderTabs();
   return true;
  },""")
 # Particle Studio must not touch the active game project while its studio is
 # open. The existing validation and renderer continue to operate on an
 # isolated scratch emitter document, not an actor or game-scene extension.
 html=once(html,
  "function se223Data(create=false){\n if(!currentProject||typeof currentProject!=='object')return null;",
  """const se468ParticleDraftKey='swrlz.engine.particle-draft.v1';
 let se468ParticleDraft=null;
 function se468ParticleMode(){return window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles';}
 function se468ParticleModel(){
  if(se468ParticleDraft)return se468ParticleDraft;
  let data={schema:SE223_SCHEMA,emitters:[]};
  try{
   const saved=JSON.parse(localStorage.getItem(se468ParticleDraftKey)||'null');
   if(saved)data=se223ValidateModel(saved);
  }catch(error){console.warn('§E particle draft restore',error);}
  se468ParticleDraft=data;return data;
 }
 function se223Data(create=false){
 if(se468ParticleMode())return se468ParticleModel();
 if(!currentProject||typeof currentProject!=='object')return null;""")
 html=once(html,
  """  beginTransaction(label);
  currentProject.particleStudio=validated;
  commitTransaction(label);""",
  """  if(se468ParticleMode()){
   // Standalone authoring: no project transaction or game scene mutation.
   localStorage.setItem(se468ParticleDraftKey,JSON.stringify(validated));
   se468ParticleDraft=validated;
  }else{
   beginTransaction(label);
   currentProject.particleStudio=validated;
   commitTransaction(label);
  }""")
 # Native particle API's import and export operate on the active studio
 # data. Explicit game-project import remains a future separate action.
 html=once(html,
  " schema:SE223_SCHEMA,presets:()=>Object.keys(SE223_PRESETS),",
  " schema:SE223_SCHEMA,presets:()=>Object.keys(SE223_PRESETS),\n export:()=>structuredClone(se223Data()),")
 # Existing account handshake is the only authenticated boundary.
 # Expose restricted save/list/load methods, not arbitrary RPC or credentials.
 html=once(html,
  "function validEnvelope(value){",
  """window.SWYRL_ENGINE_ACCOUNT_ASSETS=Object.freeze({
  list:()=>rpc('cloud.list'),
  save:(bytes,name)=>{
   if(!(bytes instanceof ArrayBuffer)||bytes.byteLength>8*1024*1024||typeof name!=='string'||!name.startsWith('§E Asset · '))return Promise.reject(Error('INVALID_ASSET_SAVE'));
   return rpc('cloud.save',{bytes,name,expectedRevision:0},[bytes]);
  },
  load:projectId=>typeof projectId==='string'&&/^[a-zA-Z0-9_-]{1,128}$/.test(projectId)?rpc('cloud.load',{projectId}):Promise.reject(Error('INVALID_ASSET_ID'))
 });
 function validEnvelope(value){""")
 html=once(html,
  "  if(type==='account.status'){",
  """  if(type==='account.status'){
    window.dispatchEvent(new CustomEvent('swrlz:account-assets',{detail:{authenticated:payload.authenticated===true,user:payload.user||null}}));""")
 html=once(html,
  "    revoke('Chat session changed.');\n  }\n}",
  """    if(type==='account.logout'||payload.reason==='account-changed')
      window.dispatchEvent(new CustomEvent('swrlz:account-assets',{detail:{authenticated:false,user:null}}));
    revoke('Chat session changed.');
  }
}""")
 html=once(html,'/* SE467_QUEST_BROWSER_INPUT_END */',
  '/* SE467_QUEST_BROWSER_INPUT_END */\n'+js)
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_467_QUEST_EDITOR_INPUT','SWYRL_ENGINE_DEPLOY_MARKER: V11_468_STANDALONE_STUDIO_ASSETS')
 html=once(html,'ENGINE · MAKER v11.467','ENGINE · MAKER v11.468')
 html=once(html,'v11.467 · Quest editor input and Extrude controls','v11.468 · standalone model and particle assets')
 html=once(html,"window.SWRLZ_FORGE_BUILD={version:'v11.467'","window.SWRLZ_FORGE_BUILD={version:'v11.468'")
 html=once(html,'<title>§wyrl§ Engine · Maker v11.467</title>','<title>§wyrl§ Engine · Maker v11.468</title>')
 prior=" source.engine='§wyrl§ Engine · Maker v11.467';source.version=11.467;"
 assert html.count(prior)==5,html.count(prior)
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.468';source.version=11.468;")
 key='const SE_RELEASE_NOTES=';i=html.index(key)+len(key)
 notes,length=json.JSONDecoder().raw_decode(html[i:])
 notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.467']
 notes['history'].insert(0,{'version':'v11.467','changes':notes.get('changes',[])})
 notes.update(version='v11.468',date='2026-11-15',
  title='Independent Model and Particle asset libraries',
  changes=[
   'Standalone Model Studio loads account or local assets into its native draft without replacing the Game Studio project.',
   'Standalone Particle Studio validates and saves emitter definitions separately; editing effects does not write to the active game project.',
   'Asset library provides local save/load, authenticated Google-account save/load, account list and explicit selection. No automatic asset import into games.',
   'Existing cloud authentication and versioned project protocol are reused; no new tokens or Google Drive permissions.',
   'Game project save/load and existing model/particle runtime remain unchanged outside their authoring workspace.',
   'Physical Quest 2 and Moto device acceptance remains pending.'
  ])
 return html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[i+length:]
