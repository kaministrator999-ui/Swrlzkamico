/* v292: Keyboard interaction regression checks against the canonical Chat source.
 * No network, credentials, browser account state, or mutation.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const page=fs.readFileSync("chat/§wyrlz/index.html","utf8");
assert.ok(page.includes('<meta name="swrlz-chat-version" content="1.1.18">'));
assert.equal(fs.readFileSync("chat/§wyrlz/VERSION.txt","utf8").trim(),"1.1.18");

const composerMatch=page.match(/prompt\.addEventListener\("keydown",(e=>\{[\s\S]*?\n      \})\);/);
assert.ok(composerMatch,"Canonical composer keydown listener exists");
let sendCount=0, prevented=0;
const cameraEvents=[];
const settingsState={general:{enterToSend:true}};
const composerKeydown=vm.runInNewContext("("+composerMatch[1]+")",{
  settingsState,
  commitDraftFromPrompt:()=>sendCount++,
  uiCamera:(event,data)=>cameraEvents.push({event,data})
});
function keydown(options={}){
  const event={key:"Enter",shiftKey:false,ctrlKey:false,metaKey:false,isComposing:false,keyCode:13,
    preventDefault:()=>prevented++,...options};
  composerKeydown(event);
}
keydown({isComposing:true});
keydown({keyCode:229});
assert.equal(sendCount,0,"IME confirmation must not send");
assert.equal(prevented,0,"IME Enter must not block character confirmation");
assert.equal(cameraEvents.filter(x=>x.event==="composer-ime-enter-preserved").length,2,"IME preservation observable");
keydown({shiftKey:true});
assert.equal(sendCount,0,"Shift+Enter must remain a newline");
keydown();
assert.equal(sendCount,1,"regular Enter respects enabled enter-to-send");
assert.equal(prevented,1);
settingsState.general.enterToSend=false;
keydown();
assert.equal(sendCount,1,"plain Enter remains newline with enter-to-send disabled");
keydown({ctrlKey:true});
keydown({metaKey:true});
assert.equal(sendCount,3,"Ctrl/Meta+Enter remain deliberate send shortcuts");
assert.equal(prevented,3);
keydown({key:"a"});
assert.equal(sendCount,3,"ordinary typing does not send");

const escapeMatch=page.match(/document\.addEventListener\("keydown",(event=>\{\n        if\(event\.key!=="Escape"\|\|!document\.body\.classList\.contains\("menu-open"\)\)return;[\s\S]*?\n      \})\);/);
assert.ok(escapeMatch,"Side drawer has keyboard Escape handler");
let menuOpen=false, focusCount=0, dismissCount=0;
const drawerKeydown=vm.runInNewContext("("+escapeMatch[1]+")",{
  document:{body:{classList:{contains:name=>name==="menu-open"&&menuOpen}}},
  setMenu:value=>{menuOpen=value;dismissCount++;},
  menuButton:{focus:()=>focusCount++},
  uiCamera:(event,data)=>cameraEvents.push({event,data})
});
drawerKeydown({key:"Escape"});
assert.equal(dismissCount,0,"Closed drawer unchanged");
menuOpen=true;
drawerKeydown({key:"Enter"});
assert.equal(menuOpen,true,"Other keys do not dismiss");
drawerKeydown({key:"Escape"});
assert.equal(menuOpen,false,"Escape dismisses open drawer");
assert.equal(focusCount,1,"Focus returns to drawer opener");
assert.equal(cameraEvents.filter(x=>x.event==="menu-escape-dismiss").length,1);

const script=page.match(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/i);
assert.ok(script,"Inline application script exists");
new vm.Script(script[1],{filename:"swrlz-chat-inline.js"});
console.log("v292 Chat keyboard IME, shortcuts, Escape focus, and inline syntax PASS");
