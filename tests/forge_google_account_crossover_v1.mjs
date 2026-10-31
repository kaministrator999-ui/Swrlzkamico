/* Controlled §E/Chat Google crossover contract. No Google credentials or network. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { webcrypto } from 'node:crypto';

const root=new URL('../',import.meta.url);
const broker=fs.readFileSync(new URL('chat/§wyrlz/assets/forge-embed-v1.js',root),'utf8');
const html=fs.readFileSync(new URL('chat/§wyrlz/index.html',root),'utf8');
assert.match(html,/accountRefreshSerial/,'older anonymous account refreshes must not overwrite a successful login');
assert.match(html,/serial!==accountRefreshSerial/);
const ORIGIN='https://kamiloki-swyrlz.hf.space',PARENT='https://kamiloki-swrlz-forge-moba.static.hf.space';
const HOST='h'.repeat(32),CHANNEL='c'.repeat(32),PAIR='a'.repeat(32),TOKEN='sfe1_'+'x'.repeat(43);
const alice={id:'google:alice',displayName:'Alice'};
const sent=[],emitted=[],requests=[],events={};
let valid=true,verifyUser=alice,cloudListRequests=0;
const reply=(status,body)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});
const nativeFetch=async(input,options={})=>{
 const url=new URL(input,ORIGIN),auth=new Headers(options.headers).get('Authorization');
 requests.push({url:url.href,path:url.pathname,auth,credentials:options.credentials});
 if(url.pathname==='/api/forge/embed/pair')return reply(200,{pairId:PAIR,loginUrl:'/forge/login?pairId='+PAIR,expiresAt:Date.now()/1000+60,recoveryCode:'b'.repeat(12)});
 if(url.pathname==='/api/forge/embed/pair/'+PAIR)return reply(200,{approved:true});
 if(url.pathname==='/api/forge/embed/pair/exchange')return reply(200,{token:TOKEN,expiresAt:Date.now()/1000+3600,user:alice,parentOrigin:PARENT,hostId:HOST,channelId:CHANNEL});
 if(url.pathname==='/api/account/me')return valid?reply(200,{user:verifyUser,durable:true,profile:{version:1}}):reply(401,{detail:'FORGE_PARENT_LOGIN_REVOKED'});
 if(url.pathname==='/api/forge/projects'){cloudListRequests++;await new Promise(r=>setTimeout(r,40));return reply(200,{projects:[]});}
 if(url.pathname==='/api/github/status')return reply(401,{detail:'GITHUB_NOT_LINKED'});
 if(url.pathname==='/api/lalm_station/forbidden')return reply(401,{detail:'STATION_PERMISSION_REQUIRED'});
 if(url.pathname==='/api/forge/embed/logout')return reply(200,{ok:true});
 return reply(200,{ok:true});
};
const host={postMessage(){}};const location={href:ORIGIN+'/?forgeEmbed=1',origin:ORIGIN,search:'?forgeEmbed=1'};
const window={parent:host,fetch:nativeFetch,addEventListener:(name,cb)=>{events[name]=cb;},dispatchEvent:e=>emitted.push(e.type)};
const document={documentElement:{classList:{add(){}}},visibilityState:'visible',addEventListener(){}};
const CustomEvent=class{constructor(type,{detail}){this.type=type;this.detail=detail;}};
vm.runInNewContext(broker,{window,document,location,crypto:webcrypto,URL,URLSearchParams,Headers,Request,Response,Blob,TextEncoder,CustomEvent,setTimeout,clearTimeout,btoa:s=>Buffer.from(s,'binary').toString('base64'),console});
const port={postMessage:m=>sent.push(m),start(){},onmessage:null};
const envelope=(type,requestId='r1')=>({protocol:'swrlz-forge-chat-v1',hostId:HOST,channelId:CHANNEL,type,requestId,payload:{}});
events.message({source:host,origin:PARENT,data:envelope('host.hello')});
events.message({source:host,origin:PARENT,data:envelope('host.connect'),ports:[port]});
assert.equal(sent.at(-1).type,'account.status');
assert.equal(sent.at(-1).payload.authenticated,false);
window.SwrlzForgeEmbedV1.notifyAccount(alice);
assert.equal(sent.filter(m=>m.type==='account.status'&&m.payload.authenticated).length,0,
  'first-party Google profile must never masquerade as an authorized embedded §e session');
await port.onmessage({data:envelope('account.signIn')});
await new Promise(resolve=>setTimeout(resolve,1350));
assert(sent.some(m=>m.type==='account.status'&&m.payload.authenticated===true),'§E received verified signed-in status');
assert(emitted.includes('swrlz-forge-account-changed'),'embedded Chat received its own login-change event');
assert.equal(sent.filter(m=>m.type==='account.status'&&m.payload.authenticated).length,1,
  'verified login publishes one account status');
window.SwrlzForgeEmbedV1.notifyAccount(alice);
window.SwrlzForgeEmbedV1.notifyAccount({id:'google:bob',displayName:'Bob'});
assert.equal(sent.filter(m=>m.type==='account.status'&&m.payload.authenticated).length,1,
  'UI refresh and foreign identity must not cause duplicate or forged connected notices');
await Promise.all([
 port.onmessage({data:envelope('cloud.list','list-a')}),
 port.onmessage({data:envelope('cloud.list','list-b')})
]);
assert.equal(cloudListRequests,1,'simultaneous automatic project-list refreshes share one server fetch');
const listings=sent.filter(m=>m.type==='rpc.result'&&['list-a','list-b'].includes(m.requestId));
assert.equal(listings.length,2);
assert(listings.every(m=>m.payload.ok===true&&Array.isArray(m.payload.result.projects)),
  'both callers get a verified cloud list, not a misleading busy error');
assert(requests.some(r=>r.path==='/api/account/me'&&r.auth==='Bearer '+TOKEN&&r.credentials==='omit'),'Chat /me verified by scoped credential');
await window.fetch('/api/github/status');
await window.fetch('/api/lalm_station/forbidden');
assert.equal(sent.filter(m=>m.type==='account.status').at(-1).payload.authenticated,true,'unrelated HTTP 401 must not revoke Google connection');
assert.equal((await window.fetch('/api/account/me')).status,200,'normal Chat account still authenticated');
await window.fetch('https://other.example/api/account/me');
assert.equal(requests.at(-1).auth,null,'Google credential never sent to other origins');
valid=false;
assert.equal((await window.fetch('/api/account/me')).status,401,'real Chat session revocation recognized');
assert.equal(sent.filter(m=>m.type==='account.status').at(-1).payload.authenticated,false,'revoked session clears shared UI');
const before=requests.length;
assert.equal((await window.fetch('/api/account/me')).status,401,'expired/revoked token denied');
assert.equal(requests.length,before,'invalid session does not reach network again');
console.log(JSON.stringify({ok:true,suite:'forge-google-account-crossover',checks:18}));
