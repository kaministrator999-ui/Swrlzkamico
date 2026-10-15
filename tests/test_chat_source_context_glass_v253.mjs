/* v253: verified-source card and readable mobile glass. Presentation only. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const page=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const css=page.split("</style>",1)[0];
const start=page.indexOf("      const splitGitHubSourcePreamble=value=>{");
const end=page.indexOf("      const renderAssistantContent=(",start);
assert.ok(start>0&&end>start,"source-card helpers in canonical Chat renderer");
const nodes=[];
const document={
  createElement(tag){
    const e={tag,children:[],attributes:{},listeners:{},textContent:"",className:"",
      append(...items){this.children.push(...items);},
      appendChild(item){this.children.push(item);return item;},
      setAttribute(key,value){this.attributes[key]=value;},
      addEventListener(event,fn){this.listeners[event]=fn;}
    };
    nodes.push(e);return e;
  }
};
const writes=[];
const clipboard={writeText:async value=>{writes.push(value)}};
const helpers=vm.runInNewContext(
  "(function(){"+page.slice(start,end)+"return {splitGitHubSourcePreamble,appendGitHubSourceCard};})()",
  {document,navigator:{clipboard}}
);
const commit="a".repeat(40),blob="b".repeat(40);
const sourcePath="kaministrator999-ui/Swrlzkamico/docs/engineering/§wyrlz_§tart.md";
const body="### Source-Grounded Analysis\n\n**Strengths**\n- Scoped source review.";
const raw="Verified source: "+sourcePath+"\n"+
  "Branch: main · commit "+commit+"\n"+
  "Blob SHA: "+blob+"\n"+
  "Coverage: bounded exact excerpts; unshown lines not verified.\n"+
  "GitHub access: read-only. No compiler or runtime tests executed.\n\n"+body;
const result=helpers.splitGitHubSourcePreamble(raw);
assert.ok(result,"real v251/v252 source preamble recognized");
assert.equal(result.repo,"kaministrator999-ui/Swrlzkamico","nested paths cannot contaminate repository identity");
assert.equal(result.file,"docs/engineering/§wyrlz_§tart.md");
assert.equal(result.body,body,"no loss of analysis body");
assert.equal(result.sourcePath,sourcePath);
for(const invalid of [
  "I think this is a verified source: "+raw,
  raw.replace("Blob SHA: "+blob,"Blob SHA: not-a-sha"),
  raw.replace("Coverage: bounded","Other: bounded"),
  "Verified source: owner/repo/file.md\nBranch: main · commit short\nBlob SHA: "+blob
])assert.equal(helpers.splitGitHubSourcePreamble(invalid),null,"unverified prose must not become a source card");
const container={children:[],appendChild(item){this.children.push(item);}};
helpers.appendGitHubSourceCard(container,result);
const card=container.children[0];
assert.equal(card.className,"github-source-card");
assert.equal(card.attributes["aria-label"],"GitHub source context");
const descendants=(n)=>[n,...(n.children||[]).flatMap(descendants)];
const all=descendants(card);
const findClass=v=>all.filter(n=>n.className===v);
assert.equal(findClass("github-source-filename")[0].textContent,result.file);
assert.equal(findClass("github-source-repo")[0].textContent,result.repo);
assert.equal(findClass("github-source-details")[0].open,undefined,"technical details collapsed by default");
assert.equal(findClass("github-source-row").length,5);
assert.equal(findClass("github-source-fact").length,2);
assert.ok(findClass("github-source-access")[0].textContent.includes("Read-only"));
const copyButtons=all.filter(n=>n.tag==="button");
assert.equal(copyButtons.length,3);
assert.ok(findClass("github-source-fact")[1].textContent.includes("Excerpts · partial"),"mobile coverage chip is compact");
const displayedValues=findClass("github-source-value").map(n=>n.children[0].textContent);
assert.equal(displayedValues[1],commit.slice(0,12)+"…"+commit.slice(-6),"full commit not visibly wrapped");
assert.equal(displayedValues[2],blob.slice(0,12)+"…"+blob.slice(-6),"full blob not visibly wrapped");
assert.equal(displayedValues[0],result.file,"source detail shows filename, not redundant repository path");
await copyButtons[1].listeners.click();
assert.deepEqual(writes,[commit],"copy exposes complete SHA without presenting 40 digits up front");
assert.equal(copyButtons[1].textContent,"Copied");
assert.ok(css.includes("rgba(2,13,26,.94)"),"assistant surface darker than v199 opacity .55");
assert.ok(css.indexOf("/* v253: readable deep-navy")>css.indexOf("/* v199: content-first"),"new color takes precedence");
assert.ok(css.includes(".assistant-body .github-source-card{"),"metadata visually separate from answer");
assert.ok(css.includes("body.a11y-reduced-transparency .assistant-body"),"accessibility override preserved");
assert.ok(page.includes("originalRenderedSources.set(container,rawSource)"),"raw response remains intact for copy/export");
assert.ok(page.includes("const source=sourceContext?sourceContext.body:rawSource"),"content only split when fully verified");
assert.ok(page.includes("if(sourceContext)appendGitHubSourceCard(container,sourceContext)"),"same renderer handles live and archive");
const inline=page.match(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/i);
assert.ok(inline,"inline script present");
new vm.Script(inline[1],{filename:"swrlz-chat-inline.js"});
console.log("v253 verified source context and darker mobile glass PASS");
