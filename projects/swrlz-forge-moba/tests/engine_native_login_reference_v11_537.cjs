'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync(process.argv[2],'utf8');
for(const token of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_537_ROBOTIC_HUMANOID_MANNEQUIN',
 'signIn:()=>se536PrepareLogin(),',
 'id="se536LoginProof"',
 'id="se536RecoveryCode"',
 'id="se536CopyCode"',
 'id="se536ContinueGoogle"',
 "rpc('account.signIn',{surface:'engine-startup'})",
 'se536Pair={pairId:result.pairId',
 "popupPair=se536Pair.pairId",
 'host.reference.import',
 'importFromChat:async offer=>',
 'await atelierRefUpload([new File([bytes],name,{type})])',
 'if(after!==before+1)',
 "SWYRL_ENGINE_REFERENCE?.importFromChat",
 "window.SWRLZ_FORGE_BUILD={version:'v11.537'"
])assert(html.includes(token),'Missing §E integration: '+token);
assert(!html.includes('signIn:()=>{openPanel();return signIn();},'),
 'Native startup must not open full integrated Chat for Google code');
assert(!html.includes('Copy the one-time code at the top of the secure §Chat panel'),
 'Old startup code instructions must not survive');
assert(html.includes("if(!ready||!se176AccountConnected||!isVisible())"),
 'Host reference import must require authenticated visible Chat');
assert(html.includes("if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')"),
 'Native reference import must be scoped to active Model Studio');
assert(html.includes('if(!((type===\'image/png\'&&png)'), 
 'Native reference importer must verify binary image magic');
assert(html.includes('new Uint8Array')||html.includes('Uint8Array'),'Typed image transport preserved');
console.log('SE536_NATIVE_GOOGLE_CODE_REFERENCE_PASS');
