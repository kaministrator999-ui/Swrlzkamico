/* v267: mobile repository inventory and source-fidelity contract.
 * No user account, production mutation or network call is required.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
function helper(name){
  const start=html.indexOf("const "+name+"=");
  assert(start>0,"Missing "+name);
  const end=html.indexOf("\n      };",start);
  assert(end>start,"Unterminated "+name);
  return html.slice(start,end+9);
}
const parse=vm.runInNewContext("(()=>{\n"+helper("splitVerifiedGitHubInventory")+
  "\nreturn splitVerifiedGitHubInventory;})()");
const sha="a".repeat(40),ctx={repo:"example/project",branch:"main",
  sourceSha:sha,directory:"",lastFile:"",kind:"directory"};
const report="## GitHub source report · example/project\n"+
  "Branch: main · commit "+sha+"\nDepth: structure\nScopes: /\n"+
  "Verified Git-tree inventory: 6 unique files\nSource contents inspected: 5/6\n"+
  "Complete Git-tree scope inventory; inspected files only.\n"+
  "### Source categories\n- Other: 5\n- Markdown: 1\n"+
  "### Inspected files\n- README.md (Documentation, 1 lines, Git blob abcd)\n"+
  "  - Opening comment: Example\n- write-action-tests/Testing.txt (Unknown/other source or resource, 1 lines, Git blob abcd)\n"+
  "Source inspection is static, not a behavioral or security audit.";
let result=parse(report,ctx);
assert(result,"Verified source report should produce inventory card");
assert.equal(result.kind,"analysis");
assert.equal(result.count,6);
assert.equal(result.inspected,5);
assert.deepEqual(Array.from(result.lines,x=>x.path),["README.md","write-action-tests/Testing.txt"]);
assert.equal(result.raw,report,"Expanded provenance must keep original text");
assert.equal(parse(report,{...ctx,sourceSha:"b".repeat(40)}),null,"No forged verified revision");
assert.equal(parse(report,null),null,"Without verified context remain prose");
const recursive="## GitHub recursive file inventory\nRepository: example/project\n"+
  "Branch: main\nRevision: "+sha+"\nScope: / (recursive)\n"+
  "Complete Git-tree file count: 2\n- README.md\n- write-action-tests/Testing.txt\n(All paths displayed.)";
result=parse(recursive,ctx);
assert(result,"Recursive file listing should be compact");
assert.equal(result.kind,"recursive");
assert.equal(result.count,2);
assert.equal(result.lines.length,2);
assert.equal(parse(recursive.replace("Revision: "+sha,"Revision: "+"b".repeat(40)),ctx),null);
assert.equal(parse(recursive.replace("README.md","../../token"),ctx),null,"Never form links to unsafe paths");
assert(html.includes('const inventory=splitVerifiedGitHubInventory(rawSource,verifiedContext);'),
  "Renderer must prefer verified compact inventory, not repeat a full source report");
assert(html.includes('if(inventory){appendGitHubInventoryCard(container,inventory);return;}'));
assert(html.includes("originalRenderedSources.set(container,rawSource)"),
  "Copy/export must retain original raw response");
assert(html.includes("inventory.raw"),"Expanded report must remain available");
assert(html.includes("rel=\"noopener noreferrer\""),"External GitHub links require isolation");
assert(html.includes(".github-inventory-item a{"),"Mobile file links need wrap-safe layout");
assert(html.includes("overflow-wrap:anywhere"),"Long file names must wrap");
console.log("v267 compact verified repository inventory, revision and mobile presentation PASS");
