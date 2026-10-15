/* Offline v245: genuine DOM behavior using a minimal inert DOM harness. */
import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
const require=createRequire(import.meta.url);
const guides=require("../chat/§wyrlz/assets/source-guides-v245.js");
class FakeNode {
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.dataset={};this.className="";this.textContent="";this.handlers={};}
  append(...nodes){this.children.push(...nodes);}
  appendChild(node){this.children.push(node);return node;}
  setAttribute(name,value){this.attributes[name]=String(value);}
  addEventListener(name,listener){this.handlers[name]=listener;}
}
globalThis.document={createElement:tag=>new FakeNode(tag)};
const walk=(node,filter)=>[...(filter(node)?[node]:[]),...node.children.flatMap(child=>walk(child,filter))];
const inputs=[
  ["workflow","## GitHub workflow guide · source-only\nBrowse verified workflow files with @GitHub files .github/workflows, then inspect a named workflow with @GitHub read file .github/workflows/NAME.yml. A workflow file is not a workflow-run receipt; executions and all mutations remain locked in Stage 1."],
  ["engine","## §E engine guide · GitHub Stage 1 (read only)\nBrowse the real Forge source with @GitHub files projects/swrlz-forge-moba and @GitHub read file §tart_§E.md. Engine-specific status and deployment are not enabled in this Stage 1."],
  ["engine-pack","## §E atomic starter-pack guide · GitHub Stage 1 (read only)\nBrowse @GitHub files projects/swrlz-forge-moba/starter-packs or read its named file via @GitHub read file PATH. Engine-pack draft and verify-tool execution are not enabled."]
];
for(const [kind,original] of inputs){
  const parsed=guides.classify(original);
  assert.equal(parsed?.kind,kind);
  assert.equal(parsed?.contract,"swrlz-source-guide-v1");
  assert.equal(parsed?.commands.length,2);
  const container=new FakeNode("div");
  let inserted="";
  assert.equal(guides.render(container,original,{preparePrompt:x=>{inserted=x;}}),true);
  assert.equal(container.children.length,1);
  const card=container.children[0];
  assert.equal(card.dataset.guideKind,kind);
  const buttons=walk(card,node=>node.tagName==="button");
  assert.equal(buttons.length,2);
  await buttons[0].handlers.click();
  assert.equal(inserted,parsed.commands[0].value,"Read command only fills composer");
  assert.equal(buttons[1].textContent,"Copy","Unresolved PATH/NAME never automatically inserted");
  const raw=walk(card,node=>node.tagName==="pre")[0];
  assert.equal(raw.textContent,original,"Original raw answer kept verbatim");
  assert.equal(walk(card,node=>node.tagName==="details").length,1,"Full answer remains discoverable");
  assert.equal(walk(card,node=>node.tagName==="script").length,0);
}
for(const text of ["Some other model paragraph","## GitHub workflow guide · source-only\nNo commands here","Prior sentence\n## GitHub workflow guide · source-only\n@GitHub files .github/workflows"]){
  assert.equal(guides.classify(text),null,"Do not invent widgets for arbitrary text");
}
const markup=fs.readFileSync("chat/§wyrlz/index.html","utf8");
assert(markup.includes("source-guides-v245.js?v=245"));
assert(markup.includes("appendRepositoryExplorer(value)||appendSourceGuide(value)"));
assert(markup.includes('.station-activity[data-active="false"] .station-activity-sub{display:none}'));
assert(markup.includes('details.open=expandedActivityTraces.has(requestId)'));
const pack=fs.readFileSync("scripts/prepare_hf_space.py","utf8");
assert(pack.includes('"chat/§wyrlz/assets/source-guides-v245.js"'));
console.log("v245 guides: three exact classifications, safe command prefill, evidence fidelity, staging and activity disclosure PASS");
