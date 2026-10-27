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
// Include the production message renderer, not just its metadata helpers: the
// ordinary fenced-source path must actually call parseFenceInfo in Chromium.
const renderBegin=html.indexOf('      const splitGitHubSourcePreamble=');
const renderEnd=html.indexOf('      const setMessagePinned=',renderBegin);
const downloadBegin=html.indexOf('      const downloadTextFile=');
const safeUrlBegin=html.indexOf('      const safeHttpUrl=');
const safeUrlEnd=html.indexOf('      const evidenceRowsFromMessage=',safeUrlBegin);
assert(renderBegin>end&&renderEnd>renderBegin&&downloadBegin<begin&&safeUrlEnd>safeUrlBegin,'production renderer dependencies found');
const renderer=html.slice(safeUrlBegin,safeUrlEnd)+html.slice(downloadBegin,begin)+html.slice(renderBegin,renderEnd);
assert(html.includes('msg?.meta?.githubContext,projectArchiveContext(thread,msg)'),'persisted message passes its archive identity');
assert(html.includes('projectArchiveContext(thread,msg,artifact,artifact.currentRevision)'),'pin rail passes its displayed revision');
assert(html.includes('enhanceCodeArtifacts(container,archiveContext)'),'rendered files reach archive grouping');
const files=[
  {path:'index.html',language:'html',content:'<!doctype html>\n<title>Fixture</title>\n'},
  {path:'src/shape editor.js',language:'javascript',content:'export const label="cube §";\n'},
  {path:'styles/editor.css',language:'css',content:'#editor { color: green; }\n'},
];
const revisedFiles=files.map(file=>file.path==='src/shape editor.js'
  ?{...file,content:'export const label="sphere §";\n'}:file);
const makeZip=(revision,selectedFiles=files)=>execFileSync(process.env.SWRLZ_TEST_PYTHON||'python3',['-c',
  'import json,sys;from project_archive import build_project_archive;sys.stdout.buffer.write(build_project_archive(json.loads(sys.stdin.read()),artifact_id="artifact-a",revision='+revision+',source_hash="a"*64))'],
  {cwd:repo,input:JSON.stringify(selectedFiles),maxBuffer:40*1024*1024,env:{...process.env,PYTHONPATH:path.join(repo,'hf_space')}});
const metadataFiles=[
  {path:'index.html',language:'html',content:'\n<!-- index.html -->\r\n<!doctype html>\r\n'},
  {path:'styles.css',language:'css',content:'/* styles.css */\n#editor { color: green; }\n'},
  {path:'src/my editor.js',language:'javascript',content:'// "src/my editor.js"\nexport const ready=true;\n'},
  {path:'README.md',language:'markdown',content:'# README.md\n\nSource fixture.\n'},
];
const metadataMarkdown=metadataFiles.map(file=>'```'+file.language+'\n'+file.content+'```').join('\n\n');
const backendMetadata=JSON.parse(execFileSync(process.env.SWRLZ_TEST_PYTHON||'python3',['-c',
  'import json,sys;from project_archive import parse_project_files;print(json.dumps(parse_project_files(sys.stdin.read())))'],
  {cwd:repo,input:metadataMarkdown,env:{...process.env,PYTHONPATH:path.join(repo,'hf_space')}}));
assert.deepEqual(backendMetadata,metadataFiles,'backend comment metadata retains all filenames and exact contents');
// A deterministic, non-executable text payload produces a realZIP above the old8MiB limit.
let fixtureSeed=0x9e3779b9;
const largeFiles=Array.from({length:24},(_,index)=>{
  const bytes=Buffer.alloc(393216);
  for(let i=0;i<bytes.length;i++){fixtureSeed^=fixtureSeed<<13;fixtureSeed^=fixtureSeed>>>17;fixtureSeed^=fixtureSeed<<5;bytes[i]=fixtureSeed&255;}
  return {path:'fixtures/source-'+index+'.txt',language:'text',content:bytes.toString('base64')};
});
const zip1=makeZip(1),zip2=makeZip(2,revisedFiles),singleZip2=makeZip(2,[revisedFiles[0]]),zip3=makeZip(3,backendMetadata),largeZip=makeZip(4,largeFiles);
assert(largeZip.length>8*1024*1024&&largeZip.length<40*1024*1024,'real bounded textZIP exercises the expanded download cap');
const requests=[],ownershipCookies=[];let mode='valid';
const server=http.createServer((req,res)=>{
  if(req.url==='/'){
    res.setHeader('Content-Type','text/html');
    res.setHeader('Set-Cookie','swrlz_hf_sid=synthetic-owner; HttpOnly; SameSite=Lax; Path=/');
    res.end('<!doctype html><meta charset="utf-8"><style>body{margin:0;max-width:100vw}.code-artifact{max-width:100vw}.code-block{max-width:100%;max-height:240px;overflow:auto}.code-block code{display:block;white-space:pre}.code-tabs{display:flex;max-width:100%;overflow:auto}</style><main id="fixture" data-message-id="m1"></main><script>const codeArtifactState=new Map(),codeViewState=new Map(),lyricViewCollapsed=new Map();const originalRenderedSources=new WeakMap();'+helper+renderer+
      ';window.archiveTest={parseFenceInfo,sourceFileFences,sourceFileMarkdown,projectArchiveContext,enhanceCodeArtifacts,renderAssistantContent,originalSource:node=>originalRenderedSources.get(node)};</script>');return;
  }
  if(req.url.startsWith('/api/lalm_station/artifacts/')){
    requests.push(req.url);
    ownershipCookies.push(req.headers.cookie||'');
    if(mode==='deny'){res.statusCode=404;res.end('Missing project');return;}
    if(mode==='wrong-type'){res.setHeader('Content-Type','application/json');res.end('{"error":"not an archive"}');return;}
    const revision=Number(new URL(req.url,'http://fixture').searchParams.get('revision')||1);
    const bytes=mode==='single-source'?singleZip2:revision===4?largeZip:revision===3?zip3:revision===2?zip2:zip1;
    if(mode==='oversize-header')res.setHeader('Content-Length',String(40*1024*1024+1));
    res.setHeader('Content-Type','application/zip');
    res.setHeader('Content-Disposition',mode==='unsafe-name'?'attachment; filename="../../outside.zip"':'attachment; filename="editor-project-r'+revision+'.zip"');
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
      path:window.archiveTest.parseFenceInfo(fence.header,fence.content).file,content:fence.content,
    }));
  },nestedFiles);
  assert.deepEqual(roundtrip,nestedFiles.map(({path,content})=>({path,content})),'nested README fences and inline JS markers preserve whole files');
  const metadataRoundtrip=await page.evaluate(markdown=>window.archiveTest.sourceFileFences(markdown).map(fence=>({
    path:window.archiveTest.parseFenceInfo(fence.header,fence.content).file,content:fence.content,
  })),metadataMarkdown);
  assert.deepEqual(metadataRoundtrip,metadataFiles.map(({path,content})=>({path,content})),'browser metadata exactly matches backend filenames without editing comments');
  const rendered=await page.evaluate(({markdown,files})=>{
    const target=document.querySelector('#fixture');
    const owner=window.archiveTest.projectArchiveContext({id:'thread-a'},{id:'m1'},
      {id:'artifact-a',currentRevision:3,files,revisions:[{revision:3,files}]},3);
    window.archiveTest.renderAssistantContent(target,markdown,'m1','',null,owner);
    return {names:[...target.querySelectorAll('.code-tab')].map(node=>node.textContent),
      contents:[...target.querySelectorAll('.code-block code')].map(node=>node.textContent),
      original:window.archiveTest.originalSource(target),
      downloads:target.querySelectorAll('.download-all-code').length};
  },{markdown:metadataMarkdown,files:metadataFiles});
  assert.deepEqual(rendered.names,metadataFiles.map(file=>file.path),'actual message renderer produces filename tabs from HTML/CSS/JS/Markdown source fences');
  assert.deepEqual(rendered.contents,metadataFiles.map(file=>file.content.replace(/\n$/,'')),'actual message renderer retains source comments and body text with its existing terminal display-newline convention');
  assert.equal(rendered.original,metadataMarkdown,'full original response stays available for copying and persistence');
  assert.equal(rendered.downloads,1,'actual rendered persisted project receives one owned ZIP action');
  const unfinished=await page.evaluate(()=>{
    const target=document.querySelector('#fixture');
    const source='```html\n<!-- index.html -->\n<script>window.renderedCodeExecuted=true;</script>\n';
    window.archiveTest.renderAssistantContent(target,source,'stream');
    return {file:target.querySelector('.code-block')?.dataset.file,
      provisional:target.querySelector('.code-block')?.classList.contains('provisional'),
      content:target.querySelector('code')?.textContent,executed:window.renderedCodeExecuted===true};
  });
  assert.deepEqual(unfinished,{file:'index.html',provisional:true,
    content:'<!-- index.html -->\n<script>window.renderedCodeExecuted=true;</script>',executed:false},
    'actual streamed unfinished fence renders as inert source without a temporal-dead-zone failure');
  const metadataSafety=await page.evaluate(()=>[
    window.archiveTest.parseFenceInfo('javascript file=canonical.js','// ../untrusted.js\nconst ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// ../untrusted.js\nconst ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// https://example.org/editor.js\nconst ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// An explanation of editor.js\nconst ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','const ready=true;\n// later.js').file,
    window.archiveTest.parseFenceInfo('markdown','# README.md\nText.').file,
    window.archiveTest.parseFenceInfo('javascript','\ufeff// editor.js\nexport const ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','\u0085// editor.js\nexport const ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// foo\u0085.js\nexport const ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// licenſe\nexport const ready=true;').file,
    window.archiveTest.parseFenceInfo('python','#!/usr/bin/python3.12\nprint(1)').file,
    window.archiveTest.parseFenceInfo('javascript','// .ſvn/editor.js\nexport const ready=true;').file,
    window.archiveTest.parseFenceInfo('javascript','// ſWRLZ_PROJECT_MANIFEﬅ.json\nexport const ready=true;').file,
  ]);
  assert.deepEqual(metadataSafety,['canonical.js','','','','','README.md','editor.js','editor.js','','','','',''],'explicit authority, unsafe metadata, URLs, prose and later comments remain conservative');
  const metadataWhitespace=['\u0009','\u000a','\u000b','\u000c','\u000d','\u001c','\u001d','\u001e','\u001f',' ','\u0085','\u00a0','\u1680',...Array.from({length:11},(_,i)=>String.fromCodePoint(0x2000+i)),'\u2028','\u2029','\u202f','\u205f','\u3000','\ufeff'];
  const parityCases=metadataWhitespace.flatMap(space=>[
    {language:'javascript',content:space+'// editor.js\nconst ready=true;'},
    {language:'javascript',content:'// a'+space+'.js\nconst ready=true;'},
    {language:'javascript',content:'// "a'+space+'.js"\nconst ready=true;'},
  ]);
  const expectedNames=JSON.parse(execFileSync(process.env.SWRLZ_TEST_PYTHON||'python3',['-c',
    'import json,sys;from project_archive import leading_file_metadata,validate_project_files,ProjectArchiveError\nrows=[]\nfor item in json.loads(sys.stdin.read()):\n name=leading_file_metadata(item["content"],item["language"])\n try:\n  if name is not None:validate_project_files([{"path":name,"content":""}])\n except ProjectArchiveError:name=None\n rows.append(name or "")\nprint(json.dumps(rows))'],
    {cwd:repo,input:JSON.stringify(parityCases),env:{...process.env,PYTHONPATH:path.join(repo,'hf_space')}}));
  const browserNames=await page.evaluate(cases=>cases.map(item=>window.archiveTest.parseFenceInfo(item.language,item.content).file),parityCases);
  assert.deepEqual(browserNames,expectedNames,'metadata whitespace and quoted-path decisions match between actualPython and browserJavaScript');
  const mount=async(revision,unsaved=false,separated=false,selectedFiles=files)=>page.evaluate(({files,revision,unsaved,separated})=>{
    const target=document.querySelector('#fixture');target.replaceChildren();
    for(const [index,file] of files.entries()){
      if(separated&&index){const prose=document.createElement('p');prose.className='message-text';prose.textContent='Explanation before file '+(index+1);target.appendChild(prose);}
      const key=['file','path','filename'][index];
      const info=window.archiveTest.parseFenceInfo(file.language+' '+key+'="'+file.path+'" project="editor project"');
      const block=document.createElement('section');block.className='code-block';block.dataset.file=info.file;block.dataset.project=info.project;
      const code=document.createElement('code');code.textContent=file.content;block.appendChild(code);target.appendChild(block);
    }
    const currentRevision=Math.max(2,revision||1);
    const record={id:'artifact-a',sourceMessageId:'m1',currentRevision,files,revisions:[{revision:1,files},{revision:2,files},...(currentRevision>2?[{revision:currentRevision,files}]:[])]};
    const message={id:'m1',meta:{codeArtifactId:'artifact-a',artifactRevision:1}};
    const thread={id:'thread-a',codeArtifacts:[record]};
    const owner=unsaved?null:window.archiveTest.projectArchiveContext(thread,message,record,revision);
    window.archiveTest.enhanceCodeArtifacts(target,owner);
    // Changing the source metadata/navigation after rendering cannot retarget its button.
    thread.id='thread-b';record.id='artifact-b';record.currentRevision=99;message.meta.artifactRevision=99;
  },{files:selectedFiles,revision,unsaved,separated});
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

  // A committed edit is normally persisted as prose plus revision metadata.
  // Rendering it must expose the new whole-projectZIP without replaying files,
  // while the original source message continues to download its own r1.
  await page.evaluate(({files,revisedFiles})=>{
    const target=document.querySelector('#fixture');target.replaceChildren();
    const record={id:'artifact-a',sourceMessageId:'m1',currentRevision:2,files:revisedFiles,
      revisions:[{revision:1,files},{revision:2,files:revisedFiles}]};
    const thread={id:'thread-a',codeArtifacts:[record]};
    const original={id:'m1',meta:{codeArtifactId:'artifact-a',artifactRevision:1}};
    const updated={id:'m2',meta:{updatedCodeArtifactId:'artifact-a',artifactRevision:2}};
    for(const [name,message,text] of [
      ['original',original,files.map(window.archiveTest.sourceFileMarkdown).join('\n\n')],
      ['updated',updated,'Updated the shape label; the other project files are preserved.'],
    ]){
      const body=document.createElement('article');body.dataset.testMessage=name;target.appendChild(body);
      window.archiveTest.renderAssistantContent(body,text,message.id,'',null,
        window.archiveTest.projectArchiveContext(thread,message));
    }
    // Existing controls are immutable even if navigation or later revisions
    // alter the objects from which their saved context was captured.
    thread.id='another-thread';record.id='another-artifact';record.currentRevision=9;
    updated.meta.artifactRevision=9;record.files=[];
  },{files,revisedFiles});
  const originalMessage=page.locator('[data-test-message="original"]');
  const updatedMessage=page.locator('[data-test-message="updated"]');
  assert.equal(await updatedMessage.locator('.project-archive-card').count(),1);
  assert.match(await updatedMessage.locator('.project-archive-summary').textContent(),/Saved project · revision 2 · 3 files/);
  assert.equal(await updatedMessage.locator('.code-block').count(),0,'a prose-only revision does not reprint unchanged project sources');
  const [updatedDownload]=await Promise.all([page.waitForEvent('download'),updatedMessage.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const updatedFile=path.join(temp,'updated-project.zip');await updatedDownload.saveAs(updatedFile);
  assert.deepEqual(fs.readFileSync(updatedFile),zip2,'new revision delivers the changed file plus preserved whole-project source bytes');
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=2');
  const [historicalDownload]=await Promise.all([page.waitForEvent('download'),originalMessage.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const historicalFile=path.join(temp,'historical-project.zip');await historicalDownload.saveAs(historicalFile);
  assert.deepEqual(fs.readFileSync(historicalFile),zip1,'the older message remains a byte-exact revision1 download');
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=1');
  mode='deny';const beforeRevisionDenial=downloads;
  await updatedMessage.getByRole('button',{name:'Download ZIP',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('[data-test-message="updated"] .code-download-status').textContent.includes('unavailable'));
  assert.equal(downloads,beforeRevisionDenial,'a missing/foreign revision response cannot become a ZIP download');
  assert.equal(await updatedMessage.getByRole('button',{name:'Download ZIP',exact:true}).isEnabled(),true);
  mode='valid';
  const [retriedRevisionDownload]=await Promise.all([page.waitForEvent('download'),updatedMessage.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const retriedRevisionFile=path.join(temp,'retried-updated-project.zip');await retriedRevisionDownload.saveAs(retriedRevisionFile);
  assert.deepEqual(fs.readFileSync(retriedRevisionFile),zip2,'a failed revision download remains retryable with its original identity');

  await page.evaluate(file=>{
    const target=document.querySelector('#fixture');
    const record={id:'artifact-a',currentRevision:2,files:[file],revisions:[{revision:2,files:[file]}]};
    const thread={id:'thread-a',codeArtifacts:[record]};
    const message={id:'single-edit',meta:{codeArtifactId:'artifact-a',artifactRevision:2}};
    window.archiveTest.renderAssistantContent(target,'Updated the page.',message.id,'',null,
      window.archiveTest.projectArchiveContext(thread,message));
  },revisedFiles[0]);
  assert.match(await page.locator('.project-archive-summary').textContent(),/revision 2 · 1 file$/);
  mode='single-source';
  const [singleDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const singleFile=path.join(temp,'single-file-project.zip');await singleDownload.saveAs(singleFile);
  assert.deepEqual(fs.readFileSync(singleFile),singleZip2,'a saved single-file revision also has an actual sourceZIP');
  mode='valid';
  const missingRevision=await page.evaluate(()=>{
    const target=document.querySelector('#fixture');
    const record={id:'artifact-a',sourceMessageId:'m1',currentRevision:2,files:[{}],revisions:[{revision:2,files:[{}]}]};
    const thread={id:'thread-a',codeArtifacts:[record]};
    const message={id:'m1',meta:{codeArtifactId:'artifact-a',artifactRevision:1}};
    const missing=window.archiveTest.projectArchiveContext(thread,message);
    const foreign=window.archiveTest.projectArchiveContext(thread,message,{...record,id:'another-artifact'},2);
    window.archiveTest.renderAssistantContent(target,'A saved response without its old source snapshot.',message.id,'',null,missing);
    return {missing,foreign,downloads:target.querySelectorAll('.download-all-code').length};
  });
  assert.deepEqual(missingRevision,{missing:null,foreign:null,downloads:0},'missing historical source and mismatched artifact metadata never fabricate a revision link');
  const compactLargeRevision=await page.evaluate(()=>{
    const target=document.querySelector('#fixture');
    const files=Array.from({length:2000},(_,i)=>({path:'src/File'+i+'.kt',language:'kotlin',content:'class File'+i+'\n'}));
    const record={id:'artifact-a',currentRevision:2,files,revisions:[{revision:2,files}]};
    const message={id:'large-edit',meta:{codeArtifactId:'artifact-a',artifactRevision:2}};
    const owner=window.archiveTest.projectArchiveContext({id:'thread-a',codeArtifacts:[record]},message);
    window.archiveTest.renderAssistantContent(target,'Updated one project file.',message.id,'',null,owner);
    return {label:target.querySelector('.project-archive-summary').textContent,nodes:target.querySelectorAll('*').length,
      sourceBlocks:target.querySelectorAll('.code-block').length};
  });
  assert.match(compactLargeRevision.label,/revision 2 · 2[,.]?000 files/);
  assert.equal(compactLargeRevision.sourceBlocks,0);
  assert(compactLargeRevision.nodes<12,'large saved-project revisions render a compact download card instead of thousands of files');

  await page.evaluate(({markdown,files})=>{
    const target=document.querySelector('#fixture');target.replaceChildren();
    for(const fence of window.archiveTest.sourceFileFences(markdown)){
      const info=window.archiveTest.parseFenceInfo(fence.header,fence.content);
      const block=document.createElement('section');block.className='code-block';block.dataset.file=info.file;block.dataset.project=info.project;
      const code=document.createElement('code');code.textContent=fence.content;block.appendChild(code);target.appendChild(block);
    }
    const record={id:'artifact-a',sourceMessageId:'m1',currentRevision:3,files,revisions:[{revision:3,files}]};
    const owner=window.archiveTest.projectArchiveContext({id:'thread-a'},{id:'m1'},record,3);
    window.archiveTest.enhanceCodeArtifacts(target,owner);
  },{markdown:metadataMarkdown,files:metadataFiles});
  assert.deepEqual(await page.locator('.code-tab').allTextContents(),metadataFiles.map(file=>file.path),'leading filename comments produce real file tabs');
  assert.deepEqual(await page.locator('.code-block code').allTextContents(),metadataFiles.map(file=>file.content),'metadata extraction never rewrites code');
  const [metadataDownload]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP',exact:true}).click()]);
  const metadataFile=path.join(temp,'metadata.zip');await metadataDownload.saveAs(metadataFile);assert.deepEqual(fs.readFileSync(metadataFile),zip3);
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=3');

  await mount(4,false,false,largeFiles);
  const [largeDownload]=await Promise.all([page.waitForEvent('download',{timeout:15000}),page.getByRole('button',{name:'Download ZIP',exact:true}).click({timeout:15000})]).catch(async error=>{console.error('Large archive diagnostic',JSON.stringify({zipBytes:largeZip.length,status:await page.locator('.code-download-status').textContent(),requests:requests.slice(-2)}));throw error;});
  const largeFile=path.join(temp,'large.zip');await largeDownload.saveAs(largeFile);assert.deepEqual(fs.readFileSync(largeFile),largeZip,'realZIP above8MiB downloads unchanged within40MiB bound');
  assert.equal(requests.at(-1),'/api/lalm_station/artifacts/thread-a/artifact-a/download?revision=4');
  mode='oversize-header';const beforeOversize=downloads;
  await page.getByRole('button',{name:'Download ZIP',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.code-download-status').textContent.includes('unavailable'));
  assert.equal(downloads,beforeOversize,'40MiB+1 declared size cannot create a download');
  assert.equal(await page.getByRole('button',{name:'Download ZIP',exact:true}).isEnabled(),true);
  mode='valid';

  const priorCalls=requests.length;await mount(0,true);
  assert.equal(await page.getByRole('button',{name:'Saving project…',exact:true}).isDisabled(),true);
  assert.equal(requests.length,priorCalls,'unsaved streamed files do not fabricate archive endpoints');
  const invalid=await page.evaluate(()=>window.archiveTest.projectArchiveContext({id:'t',codeArtifacts:[]},{id:'missing'}));
  assert.equal(invalid,null);
  await context.close();
  console.log('Project ZIP browser download PASS: production fenced-source renderer, inert streaming fences, real bytes, prose-only revised-project cards, single-file and2000-file revision metadata, immutable historical downloads, leading filename metadata, nested files, >8MiB boundedZIP ('+largeZip.length+' bytes),40MiB oversize guard, displayed revisions, captured ownership, errors, safe filenames and streaming guard');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));fs.rmSync(temp,{recursive:true,force:true});}
