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
const sortEntries=sandbox.window.SwrlzGitHubExplorerV223?.sortDirectoryEntries;
assert.equal(typeof sortEntries,"function","Pure directory-first sorter must be testable");
assert.equal(sandbox.window.SwrlzGitHubExplorerV223.version,"225");
const entries=[
  {type:"file",path:"docs/Z.py",name:"Z.py",sizeBytes:50},
  {type:"dir",path:"docs/Alpha",name:"Alpha",sizeBytes:20,fileCount:5},
  {type:"file",path:"docs/A.py",name:"A.py",sizeBytes:100},
  {type:"dir",path:"docs/Zulu",name:"Zulu",sizeBytes:10,fileCount:1}
];
const original=JSON.stringify(entries);
const dates=new Map([
  ["docs/Z.py","2026-10-12T20:00:00Z"],
  ["docs/A.py","2026-10-12T19:00:00Z"],
  ["docs/Alpha","2026-10-10T20:00:00Z"],
  ["docs/Zulu","2026-10-11T20:00:00Z"]
]);
const expected={
  "name":["Alpha","Zulu","A.py","Z.py"],
  "name-desc":["Zulu","Alpha","Z.py","A.py"],
  "type":["Alpha","Zulu","A.py","Z.py"],
  "size":["Alpha","Zulu","A.py","Z.py"],
  "files":["Alpha","Zulu","A.py","Z.py"],
  "modified":["Zulu","Alpha","Z.py","A.py"]
};
for(const [mode,names] of Object.entries(expected)){
  assert.deepEqual(Array.from(sortEntries(entries,mode,dates),x=>x.name),names,
    mode+" sorts inside directories and files, never files ahead of directories");
}
assert.equal(JSON.stringify(entries),original,"Sorter must not mutate canonical source order");
assert.deepEqual(Array.from(sortEntries(entries.filter(x=>x.type==="file"),"size",dates),x=>x.name),
  ["A.py","Z.py"],"Files-only filter keeps existing sort semantics");
assert.deepEqual(Array.from(sortEntries(entries.filter(x=>x.type==="dir"),"name-desc",dates),x=>x.name),
  ["Zulu","Alpha"],"Folders-only filter keeps existing sort semantics");
const missing=[
  {type:"file",path:"largest-file",name:"largest-file",sizeBytes:900000,fileCount:300},
  {type:"dir",path:"unknown-folder",name:"unknown-folder"}
];
for(const mode of Object.keys(expected)){
  assert.equal(sortEntries(missing,mode,new Map())[0].type,"dir",
    mode+" must keep unknown-metadata folder ahead of any file");
}
console.log("v225 GitHub explorer folders-first sorting: all six modes, missing metadata, filters and immutability PASS");
console.log("v224 GitHub directory response parsing: root, nested, Unicode, truncation and invalid paths PASS");
