import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../runtime/chat_avatar_single_tab_v11_177.js',import.meta.url),'utf8');
new vm.Script(code);
let opens=[],rpcCalls=0,popupPair='',popup=null,seenStatus=[];
const button={textContent:'Sign in with Google',disabled:false};
const document={getElementById:k=>k==='seChatSignIn'?button:null,createElement(tag){return {tagName:tag,style:{},setAttribute(){},append(){},onerror:null}}};
const ctx=vm.createContext({URL,Date,document,window:{open:(url,name,opts)=>{opens.push({url,name,opts});return {closed:false}}},ready:true,popupPair,popup,
 CHAT_ORIGIN:'https://kamiloki-swyrlz.hf.space',
 bounded:(v,max)=>typeof v==='string'&&v.length>0&&v.length<=max,
 rpc:async(type)=>{assert.equal(type,'account.signIn');rpcCalls++;return {pairId:'a'.repeat(32),loginUrl:'/forge/login?pairId='+'a'.repeat(32)};},
 setStatus:(v)=>seenStatus.push(v),summaryName:String});
vm.runInContext(code,ctx);
await vm.runInContext('signIn()',ctx);
assert.equal(opens.length,0,'preflight must not open or replace page before code can be copied');
assert.equal(rpcCalls,1);
assert.equal(button.textContent,'Continue to Google');
assert(seenStatus.some(s=>s.includes('copy the one-time code')));
await vm.runInContext('signIn()',ctx);
assert.equal(opens.length,1,'navigation only on explicit second gesture');
assert.equal(opens[0].url,'https://kamiloki-swyrlz.hf.space/forge/login?pairId='+'a'.repeat(32));
assert.equal(rpcCalls,1,'second gesture retains original PKCE pair');
assert(!opens[0].url.includes('recoveryCode'),'proof never in URL');
const mk={children:[],textContent:'G',replaceChildren(){this.children=[];this.textContent=''},append(i){this.children.push(i)},contains(i){return this.children.includes(i)}};
vm.runInContext('se177ShowPicture',ctx)(mk,'https://lh3.googleusercontent.com/a/profile');
assert.equal(mk.children.length,1);
assert.equal(mk.children[0].referrerPolicy,'no-referrer');
assert.equal(mk.children[0].src,'https://lh3.googleusercontent.com/a/profile');
vm.runInContext('se177ShowPicture',ctx)(mk,'https://googleusercontent.com.attacker.example/photo');
assert.equal(mk.textContent,'G','untrusted profile URL falls back to G');
vm.runInContext('se177ResetPrepared()',ctx);
assert.equal(button.textContent,'Sign in with Google');
assert.equal(vm.runInContext('se177Prepared',ctx),null);
console.log(JSON.stringify({ok:true,suite:'forge-v11-177-avatar-single-tab',checks:14}));
