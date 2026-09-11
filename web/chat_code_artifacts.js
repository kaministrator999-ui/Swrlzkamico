(()=>{"use strict";
if(window.__swrlzCodeArtifactsInstalled)return;
window.__swrlzCodeArtifactsInstalled=true;

const EXT_BY_LANG={cpp:'cpp',cxx:'cpp','c++':'cpp',c:'c',h:'h',hpp:'hpp',html:'html',xml:'xml',css:'css',javascript:'js',js:'js',typescript:'ts',ts:'ts',jsx:'jsx',tsx:'tsx',python:'py',py:'py',java:'java',kotlin:'kt',kt:'kt',json:'json',yaml:'yaml',yml:'yml',markdown:'md',md:'md',bash:'sh',shell:'sh',sh:'sh',powershell:'ps1',sql:'sql',go:'go',rust:'rs',rs:'rs',swift:'swift',ruby:'rb',rb:'rb',php:'php'};
const DEFAULT_NAME_BY_LANG={cpp:'main.cpp',cxx:'main.cpp','c++':'main.cpp',c:'main.c',h:'main.h',hpp:'main.hpp',html:'index.html',css:'styles.css',javascript:'script.js',js:'script.js',typescript:'app.ts',ts:'app.ts',jsx:'App.jsx',tsx:'App.tsx',python:'main.py',py:'main.py',java:'Main.java',kotlin:'Main.kt',kt:'Main.kt',json:'data.json',yaml:'config.yaml',yml:'config.yml',markdown:'README.md',md:'README.md',bash:'script.sh',shell:'script.sh',sh:'script.sh',powershell:'script.ps1',sql:'query.sql',go:'main.go',rust:'main.rs',rs:'main.rs',swift:'main.swift',ruby:'main.rb',rb:'main.rb',php:'index.php'};
const FILE_RE=/\b([A-Za-z0-9_.-]+\.(?:h|hpp|c|cc|cpp|cxx|html?|css|mjs|cjs|js|jsx|ts|tsx|py|java|kt|kts|json|xml|ya?ml|md|sh|ps1|sql|go|rs|swift|rb|php))\b/i;

function make(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;if(text!=null)el.textContent=text;return el}
function languageOf(pre){const code=pre.querySelector('code');const cls=[...(code?.classList||[]),...(pre.classList||[])];for(const value of cls){const m=String(value).match(/^(?:language-|lang-)(.+)$/i);if(m)return m[1].toLowerCase()}return String(code?.dataset?.language||pre.dataset?.language||'text').toLowerCase()}
function inferredName(pre,lang,index,used){let node=pre.previousElementSibling;for(let depth=0;node&&depth<2;depth++,node=node.previousElementSibling){const hit=String(node.textContent||'').match(FILE_RE);if(hit){let n=hit[1];if(!used.has(n)){used.add(n);return n}}}
  const base=DEFAULT_NAME_BY_LANG[lang]||`code.${EXT_BY_LANG[lang]||'txt'}`;if(!used.has(base)){used.add(base);return base}
  const dot=base.lastIndexOf('.'),stem=dot>=0?base.slice(0,dot):base,ext=dot>=0?base.slice(dot):'';let n=`${stem}-${index+1}${ext}`,x=index+1;while(used.has(n)){x++;n=`${stem}-${x}${ext}`}used.add(n);return n}
function copyText(text,button){const done=()=>{const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,900)};if(navigator.clipboard?.writeText){navigator.clipboard.writeText(text).then(done).catch(()=>fallback())}else fallback();function fallback(){const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch(_){}ta.remove()}}
function download(name,text,type='text/plain;charset=utf-8'){const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function bundleName(){return `swrlz-code-${new Date().toISOString().replace(/[:.]/g,'-')}.json`}
function filePayload(files){return {format:'swrlz-code-artifact-v1',capturedAt:new Date().toISOString(),files:files.map(f=>({name:f.name,language:f.lang,content:f.text}))}}

function decorateBubble(bubble){
  if(!bubble||bubble.dataset.swrlzCodeArtifact==='true')return;
  const pres=[...bubble.querySelectorAll('pre')].filter(pre=>!pre.closest('.swrlz-code-artifact'));
  if(!pres.length)return;
  bubble.dataset.swrlzCodeArtifact='true';
  const originals=[...bubble.childNodes];const firstPre=pres[0];
  const used=new Set();const files=pres.map((pre,index)=>{const lang=languageOf(pre),name=inferredName(pre,lang,index,used);return {name,lang,text:String(pre.querySelector('code')?.textContent??pre.textContent??''),pre:pre.cloneNode(true)}});

  const outer=make('section','swrlz-code-artifact');outer.dataset.fileCount=String(files.length);
  const head=make('div','swrlz-code-artifact-head');
  const titleWrap=make('div','swrlz-code-artifact-title');const title=make('strong','',files.length>1?'Code project':'Code artifact');const meta=make('span','',files.length>1?`${files.length} files`:`${files[0].name} · ${files[0].lang}`);titleWrap.append(title,meta);
  const headActions=make('div','swrlz-code-artifact-actions');
  const copyAll=make('button','','Copy all');copyAll.type='button';copyAll.addEventListener('click',()=>copyText(files.map(f=>`// ${f.name}\n${f.text}`).join('\n\n'),copyAll));
  const exportAll=make('button','','Export all');exportAll.type='button';exportAll.addEventListener('click',()=>download(bundleName(),JSON.stringify(filePayload(files),null,2),'application/json;charset=utf-8'));
  headActions.append(copyAll,exportAll);head.append(titleWrap,headActions);outer.appendChild(head);

  const lead=make('div','swrlz-code-artifact-lead');let before=true;for(const node of originals){if(node===firstPre||((node.nodeType===1)&&node.contains?.(firstPre)))before=false;if(before)lead.appendChild(node.cloneNode(true))}if(lead.textContent.trim())outer.appendChild(lead);

  const workspace=make('div','swrlz-code-workspace');const tabs=make('div','swrlz-code-tabs');tabs.setAttribute('role','tablist');const stage=make('div','swrlz-code-stage');let active=0;
  const paneEls=[];const tabEls=[];
  files.forEach((file,index)=>{
    const tab=make('button','swrlz-code-tab',file.name);tab.type='button';tab.setAttribute('role','tab');tab.setAttribute('aria-selected',index===0?'true':'false');tab.dataset.index=String(index);tabs.appendChild(tab);tabEls.push(tab);
    const pane=make('section','swrlz-code-pane');pane.dataset.index=String(index);pane.hidden=index!==0;
    const toolbar=make('div','swrlz-code-pane-tools');const label=make('span','',`${file.lang} · ${file.name}`);const copy=make('button','','Copy');copy.type='button';copy.addEventListener('click',()=>copyText(file.text,copy));const save=make('button','','Download');save.type='button';save.addEventListener('click',()=>download(file.name,file.text));toolbar.append(label,copy,save);
    const codeShell=make('div','swrlz-code-inner');codeShell.appendChild(file.pre);pane.append(toolbar,codeShell);stage.appendChild(pane);paneEls.push(pane);
    tab.addEventListener('click',()=>{active=index;tabEls.forEach((t,i)=>t.setAttribute('aria-selected',i===active?'true':'false'));paneEls.forEach((p,i)=>p.hidden=i!==active);meta.textContent=files.length>1?`${files.length} files · ${files[active].name}`:`${files[active].name} · ${files[active].lang}`});
  });
  if(files.length===1)tabs.classList.add('single');workspace.append(tabs,stage);outer.appendChild(workspace);

  const notes=make('div','swrlz-code-artifact-notes');const notesHead=make('div','swrlz-code-notes-title','Details');notes.appendChild(notesHead);let seenFirst=false;
  for(const node of originals){const isPre=node===firstPre||((node.nodeType===1)&&node.contains?.(firstPre));if(isPre){seenFirst=true;continue}if(!seenFirst)continue;const clone=node.cloneNode(true);if(clone.nodeType===1){clone.querySelectorAll?.('pre').forEach(x=>x.remove());if(!String(clone.textContent||'').trim()&&!clone.querySelector?.('img,table,ul,ol,blockquote'))continue}if(clone.nodeType===3&&!String(clone.textContent||'').trim())continue;notes.appendChild(clone)}
  if(notes.children.length>1)outer.appendChild(notes);
  bubble.replaceChildren(outer);
}

function scan(root=document){root.querySelectorAll?.('.message.assistant .bubble').forEach(decorateBubble)}
function install(){scan();const target=document.querySelector('.messages')||document.querySelector('.message-stack')||document.body;const observer=new MutationObserver(records=>{for(const record of records){for(const node of record.addedNodes){if(node.nodeType!==1)continue;if(node.matches?.('.message.assistant .bubble'))decorateBubble(node);else scan(node)}}});observer.observe(target,{childList:true,subtree:true});window.__swrlzCodeArtifactObserver=observer}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
