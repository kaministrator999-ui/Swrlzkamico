/* v224: reproduce GitHub directory output exactly; no DOM or login required. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source=fs.readFileSync("chat/§wyrlz/assets/github-explorer-v223.js","utf8");
const sandbox={
  window:{},
  document:{
    createElement(){return {textContent:"",className:""};},
    head:{appendChild(){}}
  },
  console
};
vm.runInNewContext(source,sandbox,{filename:"github-explorer-v223.js",timeout:3000});
const parse=sandbox.window.SwrlzGitHubExplorerV223?.parseDirectoryResponse;
assert.equal(typeof parse,"function","Pure listing parser must be testable");

function check(value, expectedPath, names, partial=false){
  const data=parse(value);
  assert.ok(data,"Valid GitHub output should render as an explorer: "+value.slice(0,80));
  assert.equal(data.path,expectedPath);
  assert.deepEqual(Array.from(data.entries,x=>x.path),names);
  assert.equal(data.incomplete,partial);
}
check("## GitHub directory: /\n- dir docs\n- file README.md","",["docs","README.md"]);
check("## GitHub directory: docs\n- dir docs/engineering\n- file docs/start.md","docs",
      ["docs/engineering","docs/start.md"]);
check("## GitHub directory: docs/engineering\n- file docs/engineering/spec.md",
      "docs/engineering",["docs/engineering/spec.md"]);
check("## GitHub directory: hf_space\n- file hf_space/station.py\n- file hf_space/github_connection.py",
      "hf_space",["hf_space/station.py","hf_space/github_connection.py"]);
check("## GitHub directory: /\n- dir docs\n- file §wyrlz_§tart.md\n(First 60 entries.)",
      "",["docs","§wyrlz_§tart.md"],true);
assert.equal(parse("## GitHub directory: docs/../private\n- file docs/secret"),null);
assert.equal(parse("## GitHub directory: /../../private\n- file docs/secret"),null);
assert.equal(parse("## GitHub directory: docs\n- file <script>alert(1)</script>"),null);
assert.equal(parse("## GitHub directory: docs\n- nonsensical anything"),null);
assert.equal(parse("Unrelated model text"),null);
console.log("v224 GitHub directory response parsing: root, nested, Unicode, truncation and invalid paths PASS");
