/* Verifiable Chat-origin recovery-code UX + safe Google account picture. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../chat/§wyrlz/assets/forge-embed-v1.js',import.meta.url),'utf8');
new vm.Script(code);
const from=code.indexOf('  const showRecoveryCode = code => {');
const to=code.indexOf('  const error = message',from);
const u=code.indexOf('  const verifiedPicture = user => {');
const v=code.indexOf('  const revoke = reason',u);
assert(from>0&&to>from&&u>to&&v>u,'expected exact Chat-origin implementation sections');
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.attrs={};this.style={};this.textContent='';this.value='';this.listeners={};}
 setAttribute(k,v){this.attrs[k]=v}
 addEventListener(name,fn){this.listeners[name]=fn}
 append(...items){this.children.push(...items)}
 replaceChildren(...items){this.children=items}
 remove(){delete dom.nodes['swrlz-forge-recovery-note']}
 select(){this.selected=true}
 focus(){this.focused=true}
}
const dom={nodes:{},body:{appendChild(el){if(el.id)dom.nodes[el.id]=el}},createElement(tag){return new Element(tag)},getElementById(id){return this.nodes[id]||null}};
let clipboard='';
const ctx=vm.createContext({document:dom,window:{navigator:{clipboard:{writeText:async t=>{clipboard=t}}}},URL,embedded:true});
vm.runInContext(code.slice(from,to)+code.slice(u,v).replace('  const publicAccount = user => ({','  const publicAccount = user => ({'),ctx);
assert.equal(vm.runInContext('verifiedPicture({picture:"https://lh3.googleusercontent.com/a/a1"})',ctx),'https://lh3.googleusercontent.com/a/a1');
assert.equal(vm.runInContext('verifiedPicture({picture:"https://googleusercontent.com.attacker.com/steal"})',ctx),'');
assert.equal(vm.runInContext('verifiedPicture({picture:"javascript:alert(1)"})',ctx),'');
assert.equal(vm.runInContext('verifiedPicture({picture:"https://example.com/a.png"})',ctx),'');
assert.equal(vm.runInContext('publicAccount({displayName:"Test",picture:"https://lh3.googleusercontent.com/a/a1"}).user.picture',ctx),'https://lh3.googleusercontent.com/a/a1');
assert.equal(vm.runInContext('publicAccount({displayName:"Test",picture:"https://evil.example/a"}).user.picture',ctx),undefined);
vm.runInContext('showRecoveryCode("abcdef123456")',ctx);
const note=dom.nodes['swrlz-forge-recovery-note'];
assert(note,'note is visible in iframe');
assert(note.children.some(x=>x.tagName==='input'&&x.value==='abcdef123456'&&x.readOnly),'code is selectable before navigation');
const button=note.children.find(x=>x.tagName==='button');assert(button,'Copy code control exists');
await button.listeners.click();
assert.equal(clipboard,'abcdef123456','clipboard copy occurs from explicit user action');
assert(!code.includes('send("account.recoveryCode"'),'code never sent to §E parent');
vm.runInContext('showRecoveryCode("")',ctx);
assert.equal(dom.nodes['swrlz-forge-recovery-note'],undefined,'proof clears');
console.log(JSON.stringify({ok:true,suite:'forge-google-profile-and-preflight-code',checks:12}));
