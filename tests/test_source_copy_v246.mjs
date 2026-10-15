/* v246: copy exact persisted response, not custom guide DOM decoration. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const start=html.indexOf("      const addCopyButton = node => {");
const end=html.indexOf("      const widgetsFromMessage=msg=>{",start);
assert(start>0&&end>start,"Copy integration located in canonical Chat source");
const snippet=html.slice(start,end);
assert(/originalRenderedSources\.set\(container,(?:source|rawSource)\)/.test(html),"Raw source collected at render time before any display-only formatting");
assert(snippet.includes("originalRenderedSources.get(body)"),"Copy must prefer source");
const actual="## §E engine guide · GitHub Stage 1 (read only)\n@GitHub files projects/swrlz-forge-moba";
const decorated="Forge engine guide • READ ONLY • Insert • Full original answer and restrictions • "+actual;
class Element {constructor(){this.children=[];this.textContent="";}append(node){this.children.push(node);}appendChild(node){this.children.push(node);}}
const document={createElement:()=>new Element()};
let copied=null;
const navigator={clipboard:{writeText:async value=>{copied=value;}}};
const context={document,navigator,setTimeout:()=>{},WeakMap};
vm.runInNewContext(
  "const originalRenderedSources = new WeakMap();\n"+snippet+
  "\nfunction attach(node,body,raw){if(raw!==undefined)originalRenderedSources.set(body,raw);addCopyButton(node);}\nthis.attach=attach;",
  context
);
const body={textContent:decorated};
const node={querySelector:selector=>selector===".assistant-body"?body:null,children:[],appendChild(element){this.children.push(element);},append(element){this.children.push(element);}};
context.attach(node,body,actual);
assert.equal(node.children.length,1);
const button=node.children[0].children[0];
await button.onclick();
assert.equal(copied,actual);
assert.equal(button.textContent,"Copied");
const oldBody={textContent:"Legacy response text"};
const oldNode={querySelector:()=>oldBody,children:[],appendChild(x){this.children.push(x);},append(x){this.children.push(x);}};
context.attach(oldNode,oldBody,undefined);
await oldNode.children[0].children[0].onclick();
assert.equal(copied,"Legacy response text","Legacy copy fallback remains available");
console.log("v246 Copy response: original-source fidelity and backwards-compatible fallback PASS");
