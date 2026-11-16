import assert from 'node:assert/strict';
import fs from 'node:fs';
const html=fs.readFileSync(process.argv[2],'utf8');
const required=[
 'SE468_STANDALONE_STUDIO_ASSETS_START',
 'function se468ParticleMode()',
 'if(se468ParticleMode())return se468ParticleModel();',
 'if(se468ParticleMode()){',
 'localStorage.setItem(se468ParticleDraftKey,JSON.stringify(validated));',
 'loadStandaloneModel(data){',
 'scratch=structuredClone(data);preferScratch=true;',
 "if(!window.SWYRL_ENGINE_WORKSPACES?.loadStandaloneModel?.(structuredClone(record.data)))",
 'if(!window.SWYRL_ENGINE_PARTICLES?.import?.(structuredClone(record.data)))',
 "if(!connected||!api()?.save)throw Error('Connect your Google account",
 "window.SWYRL_ENGINE_ACCOUNT_ASSETS=Object.freeze({",
 "window.dispatchEvent(new CustomEvent('swrlz:account-assets'",
 "const dock=type==='modeler'?document.querySelector('#modelAtelierPanel .atelier-inspector')",
 'function envelope(record){',
 'function decode(doc,type){'
];
for(const item of required)assert(html.includes(item),'Missing standalone isolation: '+item);
const mutate=html.slice(html.indexOf('function se223Mutate('),html.indexOf('function se223Create(',html.indexOf('function se223Mutate(')));
assert(mutate.includes('if(se468ParticleMode()){'),'Particle standalone mode must be checked before game transactions');
assert(mutate.indexOf('if(se468ParticleMode()){')<mutate.indexOf('beginTransaction(label)'),'No transaction in standalone mode');
const load=html.slice(html.indexOf('loadStandaloneModel(data){'),html.indexOf('  draftEdited,onNativeLoad,newBlankModel,',html.indexOf('loadStandaloneModel(data){')));
assert(!load.includes('loadProject('),'Model standalone load cannot replace active game project');
const library=html.slice(html.indexOf('/* SE468_STANDALONE_STUDIO_ASSETS_START */'),html.indexOf('/* SE468_STANDALONE_STUDIO_ASSETS_END */'));
assert(!library.includes('loadProject('),'Asset library must not import into game project');
assert(!library.includes('currentProject.particleStudio='),'Asset library cannot mutate game particle metadata');
console.log('SE468_ASSET_ISOLATION_PASS: standalone model, particle draft, account bridge and no implicit game import');
