// Prevent short-screen mobile Chat drawers from hiding chat rows below
// an expanded account card and pinned Versions footer.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const html=readFileSync(new URL("../chat/§wyrlz/index.html",import.meta.url),"utf8");
const style=html.split("<style>")[1]?.split("</style>")[0]||"";
assert.ok(style, "canonical clean-room Chat stylesheet exists");
const lastRule=(selector)=>{
  const escaped=selector.replace(/[.*+?^$\u007b\u007d()|[\]\\]/g,"\\$&");
  const re=new RegExp(escaped+"\\s*\\{([^}]*)\\}","g");
  let m,last="";
  while((m=re.exec(style))!==null)last=m[1];
  return last;
};
const menu=lastRule(".side-menu");
assert.match(menu,/height:\s*100dvh/);
assert.match(menu,/overflow-y:\s*auto/);
assert.match(menu,/overscroll-behavior-y:\s*contain/);
const rows=lastRule(".side-menu .thread-list");
assert.match(rows,/max-height:\s*none/);
assert.match(rows,/overflow:\s*visible/);
const panel=lastRule(".side-menu .thread-panel");
assert.match(panel,/flex:\s*0\s+0\s+auto/);
const footer=lastRule(".side-menu .version-box");
assert.match(footer,/margin-top:\s*12px/);
const positionThreads=html.indexOf('<section class="thread-panel"');
const positionVersion=html.indexOf('<div class="version-box collapsed"');
assert.ok(positionThreads>0 && positionVersion>positionThreads,
 "Version panel must occur AFTER all native chat rows, in same scrollport");
assert.match(html,/const newestFirst=orderNativeThreads\(chatThreads\)/,
 "Native threads are sorted newest-first independently of layout");
console.log("Mobile Chat: one scrollable drawer, no capped internal list, Versions after chats");
