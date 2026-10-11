// The first native Chat user message is durably committed by Station before
// the 202 ACK, not when slow model inference eventually completes.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
const html=readFileSync(new URL("../chat/§wyrlz/index.html",import.meta.url),"utf8");
const begin=html.indexOf("      const promoteAcceptedNativeThread = ");
const end=html.indexOf("      const renderThreads = ",begin);
assert.ok(begin>=0&&end>begin,"Expected pure promotion helper");
const context={};
vm.runInNewContext(html.slice(begin,end).replace("const promoteAcceptedNativeThread = ","globalThis.promoteAcceptedNativeThread = "),context);
const promote=context.promoteAcceptedNativeThread;
const older=[{id:"prior",title:"Existing chat"}],newChat={id:"first-sent",title:"My first question",messages:[{id:"m1",role:"user",text:"test",meta:{localPending:true}}]};
assert.deepEqual(Array.from(promote(older,newChat,"req1","req1"),x=>x.id),["prior","first-sent"],
 "First user message appears in the list on acknowledged durable save");
assert.deepEqual(Array.from(promote(older,newChat,"wrong","req1"),x=>x.id),["prior"],
 "Never show an unaccepted draft as saved");
assert.deepEqual(Array.from(promote(older,null,"req1","req1"),x=>x.id),["prior"]);
const once=promote(older,newChat,"req1","req1");
assert.equal(promote(once,newChat,"req1","req1"),once,
 "Retried ACK must not duplicate a chat");
assert.equal(older.length,1,"No mutation of original account snapshot");
const ack=html.indexOf("sendAcknowledged=true;");
const promoted=html.indexOf("chatThreads=promoteAcceptedNativeThread",ack);
const stream=html.indexOf("const streamResponse=await fetch",ack);
assert.ok(ack>0&&promoted>ack&&stream>promoted,
 "Promotion happens after verified send ACK and before inference stream consumption");
assert.ok(html.includes("void syncStation(true);"),"Reconcile the durable server snapshot independently");
assert.ok(html.includes("if(!sendAcknowledged){prompt.value=text;"),"Unaccepted sends still retain their drafts");
console.log("Native Chat first-message ACK promotion before inference and no phantom/duplicate threads verified");
