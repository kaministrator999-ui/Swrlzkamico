// Real Chromium DOM/download boundary with synthetic source fixtures. No model-quality claim.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const html=fs.readFileSync(path.join(repo,'chat/§wyrlz/index.html'),'utf8');
const begin=html.indexOf('      const parseFenceInfo=');
const end=html.indexOf('      // Presentation-only: route unlabelled fenced songs',begin);
assert(begin>0&&end>begin,'production archive helpers found');
const helper=html.slice(begin,end);
assert(html.includes('msg?.meta?.githubContext,projectArchiveContext(thread,msg)'),'persisted message passes its archive identity');
assert(html.includes('projectArchiveContext(thread,msg,artifact,artifact.currentRevision)'),'pin rail passes its displayed revision');
assert(html.includes('enhanceCodeArtifacts(container,archiveContext)'),'rendered files reach archive grouping');
const files=[
  {path:'index.html',language:'html',content:'<!doctype html>\n<title>Fixture</title>\n'},
  {path:'src/shape editor.js',language:'javascript',content:'export const label="cube §";\n'},
  {path:'styles/editor.css',language:'css',content:'#editor { color: green; }\n'},
];
const makeZip=revision=>execFileSync(process.env.SWRLZ_TEST_PYTHON||'python3',['-c',
  'import json,sys;from project_archive import build_project_archive;sys.stdout.buffer.write(build_project_archive(json.loads(sys.stdin.read()),artifact_id="artifact-a",revision='+revision+',source_hash="a"*64))'],
  {cwd:repo,input:JSON.stringify(files),env:{...process.env,PYTHONPATH:path.join(repo,'hf_space')}});
const zip1=makeZip(1),zip2=makeZip(2);
const requests=[],ownershipCookies=[];let mode='valid';
const server=http.createServer((req,res)=>{
  if(req.url==='/'){
    res.setHeader('Content-Type','text/html');
    res.setHeader('Set-Cookie','swrlz_hf_sid=synthetic-owner; HttpOnly; SameSite=Lax; Path=/');
    res.end('<!doctype html><meta charset="utf-8"><main id="fixture" data-message-id="m1"></main><script>const codeArtifactState=new Map();'+helper+
      ';window.archiveTest={parseFenceInfo,sourceFileFences,sourceFileMarkdown,projectArchiveContext,enhanceCodeArtifacts};</script>');return;
  }
  if(req.url.startsWith('/api/lalm_station/artifacts/')){
    requests.push(req.url);
    ownershipCookies.push(req.headers.cookie||'');
    if(mode==='deny'){res.statusCode=404;res.end('Missing project');return;}
    if(mode==='wrong-type'){res.setHeader('Content-Type','application/json');res.end('{"error":"not an archive"}');return;}
    const bytes=req.url.endsWith('revision=2')?zip2:zip1;
    res.setHeader('Content-Type','application/zip');
    res.setHeader('Content-Disposition',mode==='unsafe-name'?'attachment; filename="../../outside.zip"':'attachment; filename="editor-project-r1.zip"');
    res.setHeader('Cache-Control','private, no-store');res.end(bytes);return;
  }
  res.statusCode=404;res.end();
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'/opt/codex/cua_node/lib/node_modules/playwright/index.mjs');
const executablePath=process.env.CHROMIUM_PATH||(fs.existsSync('/usr/lib/chromium/chromium')?'/usr/lib/chromium/chromium':undefined);
const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'swrlz-project-download-'));
try{
  const context=await browser.newContext({acceptDownloads:true});const page=await context.newPage();page.setDefaultTimeout(5000);
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  const nestedFiles=[
    {path:'README.md',language:'markdown',content:'# Project\n\n```sh\npython -m http.server\n```\n'},
    {path:'src/my editor.js',language:'javascript',content:'export const marker="```";\nexport const complete=true;\n'},
    {path:'src/tick`name.js',language:'javascript',content:'export const value=true;\n'},
  ];
  const roundtrip=await page.evaluate(files=>{
    const markdown=files.map(window.archiveTest.sourceFileMarkdown).join('\n\n');
    return window.archiveTest.sourceFileFences(markdown).map(fence=>({
      path:window.archiveTest.parseFenceInfo(fence.header).file,content:fence.content,
    }));
  },nestedFiles);
  assert.deepEqual(roundtrip,nestedFiles.map(({path,content})=>({path,content})),'nested README fences and inline JS markers preserve whole files');
  const mount=async(revision,unsaved=false,separated=false)=>page.evaluate(({files,revision,unsaved,separated})=>{
    const target=document.querySelector('#fixture');target.replaceChildren();
    for(const [index,file] of files.entries()){
      if(separated&&index){const prose=document.createElement('p');prose.className='message-text';prose.textContent='Explanation before file '+(index+1);target.appendChild(prose);}
      const key=['file','path','filename'][index];
      const info=window.archiveTest.parseFenceInfo(file.language+' '+key+'="'+file.path+'" project="editor project"');
      const block=document.createElement('section');block.className='code-block';block.dataset.file=info.file;block.dataset.project=info.project;
      const code=document.createElement('code');code.textContent=file.content;block.appendChild(code);target.appendChild(block);
    }
    const record={id:'artifact-a',sourceMessageId:'m1',currentRevision:2,files,revisions:[{revision:1,files},{revision:2,files}]};
    const message={id:'m1',meta:{codeArtifactId:'artifact-a',artifactRevision:1}};
    const thread={id:'thread-a',codeArtifacts:[record]};
    const owner=unsaved?null:window.archiveTest.projectArchiveContext(thread,message,record,revision);
    window.archiveTest.enhanceCodeArtifacts(target,owner);
    // Changing the source metadata/navigation after rendering cannot retarget its button.
    thread.id='thread-b';record.id='artifact-b';record.currentRevision=99;message.meta.artifactRevision=99;
  },{files,revision,unsaved,separated});
  await mount(0); // original message r1 even though current artifact has advanced to r2
  assert.equal(await page.locator('.code-tab').count(),3);
  await page.getByRole('tab',{name:'src/shape editor.js',exact:true}).click();
  assert.equal(await page.locator('.code-block:not([hidden]) code').textContent(),files[1].content);
  let downloads=0;page.on('download',()=>downloads++);
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const first=path.join(temp,'first.zip');await download.saveAs(first);
  assert.equal(download.suggestedFilename(),'editor-project-r1.zip');assert.deepEqual(fs.readFileSync(first),zip1);
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=1');
  assert(ownershipCookies.at(-1).includes('swrlz_hf_sid=synthetic-owner'),'browser sends the existing same-origin session cookie');
  await page.waitForFunction(()=>document.querySelector('.code-download-status').textContent==='ZIP downloaded');

  await mount(2);const [pinDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const pinned=path.join(temp,'pinned.zip');await pinDownload.saveAs(pinned);assert.deepEqual(fs.readFileSync(pinned),zip2);
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=2');

  mode='deny';const before=downloads;
  await page.getByRole('button',{name:'Download ZIP',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.code-download-status').textContent.includes('unavailable'));
  assert.equal(downloads,before,'denied ownership/project request cannot create a download');
  assert.equal(await page.getByRole('button',{name:'Download ZIP',exact:true}).isEnabled(),true,'failure leaves retry available');

  mode='wrong-type';await page.getByRole('button',{name:'Download ZIP',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.code-download-status').textContent.includes('unavailable'));
  assert.equal(downloads,before,'a successful JSON/error response cannot become a fake ZIP');

  mode='unsafe-name';await mount(0);
  const [safeDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  assert.equal(safeDownload.suggestedFilename(),'swrlz-project-r1.zip','path-shaped response filename uses safe fallback');
  await safeDownload.cancel();

  mode='valid';await mount(0,false,true);
  assert.equal(await page.locator('.code-artifact').count(),0,'prose-separated files stay in their original flow');
  assert.equal(await page.locator('.project-archive-tools').count(),1,'one project toolbar remains available without grouped tabs');
  assert.deepEqual(await page.locator('.message-text').allTextContents(),['Explanation before file 2','Explanation before file 3']);
  assert.deepEqual(await page.locator('.code-block code').allTextContents(),files.map(file=>file.content),'download enhancement does not rewrite files');
  const [separatedDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const separatedFile=path.join(temp,'separated.zip');await separatedDownload.saveAs(separatedFile);assert.deepEqual(fs.readFileSync(separatedFile),zip1);
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=1');

  const revisionCounts=await page.evaluate(()=>{
    const record={id:'a',currentRevision:2,files:[{},{},{}],revisions:[{revision:1,files:[{}]},{revision:2,files:[{},{},{}]}]};
    const thread={id:'t'},message={id:'m',meta:{artifactRevision:1}};
    return [window.archiveTest.projectArchiveContext(thread,message,record).fileCount,
      window.archiveTest.projectArchiveContext(thread,message,record,2).fileCount,
      window.archiveTest.parseFenceInfo('javascript path="src/shape editor.js" group="editor project"')];
  });
  assert.deepEqual(revisionCounts,[1,3,{language:'javascript',file:'src/shape editor.js',project:'editor project'}]);

  const priorCalls=requests.length;await mount(0,true);
  assert.equal(await page.getByRole('button',{name:'Saving project…',exact:true}).isDisabled(),true);
  assert.equal(requests.length,priorCalls,'unsaved streamed files do not fabricate archive endpoints');
  const invalid=await page.evaluate(()=>window.archiveTest.projectArchiveContext({id:'t',codeArtifacts:[]},{id:'missing'}));
  assert.equal(invalid,null);
  await context.close();
  console.log('Project ZIP browser download PASS: real bytes, nested files, displayed revisions, captured ownership, errors, safe filenames and streaming guard');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));fs.rmSync(temp,{recursive:true,force:true});}
