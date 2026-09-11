(()=>{"use strict";
if(window.__swrlzResponsePolishInstalled)return;
window.__swrlzResponsePolishInstalled=true;

const NAME_RE=/^\s*[§S]?wyrlz\s*[.!:;,-]*\s*$/i;
const FALLBACK_LEAD='Here’s a quick code example:';

function isNameOnly(node){return node&&NAME_RE.test(String(node.textContent||''))}
function removeStandaloneName(root){
  if(!root)return;
  const candidates=[...root.querySelectorAll(':scope > p,:scope > div')];
  for(const node of candidates){if(isNameOnly(node)&&!node.matches('.swrlz-code-artifact-title,.swrlz-code-notes-title'))node.remove()}
}
function ensureLead(artifact){
  if(!artifact)return;
  const head=artifact.querySelector(':scope > .swrlz-code-artifact-head');
  let lead=artifact.querySelector(':scope > .swrlz-code-artifact-lead');
  if(lead&&isNameOnly(lead)){lead.replaceChildren();lead.textContent=FALLBACK_LEAD}
  if(!lead){lead=document.createElement('div');lead.className='swrlz-code-artifact-lead swrlz-presentational-lead';lead.textContent=FALLBACK_LEAD;const workspace=artifact.querySelector(':scope > .swrlz-code-workspace');if(workspace)artifact.insertBefore(lead,workspace);else if(head)head.after(lead);else artifact.prepend(lead)}
  removeStandaloneName(lead);
  if(!String(lead.textContent||'').trim())lead.textContent=FALLBACK_LEAD;
}
function looksLikeClosing(node,notes){
  if(!node||node.tagName!=='P')return false;
  const text=String(node.textContent||'').trim();if(!text||text.length>240)return false;
  const blocks=[...notes.children].filter(el=>!el.classList.contains('swrlz-code-notes-title')&&!el.hidden);
  if(blocks.length<2)return false;
  return /(?:let me know|if you(?:'d| would)? like|if you want|feel free|happy to|that gives|this gives|you can build|you can expand|from here|next step)/i.test(text)||blocks.length>=3;
}
function moveClosing(artifact){
  const notes=artifact?.querySelector(':scope > .swrlz-code-artifact-notes');if(!notes)return;
  const last=[...notes.children].filter(el=>!el.classList.contains('swrlz-code-notes-title')&&!el.hidden).at(-1);if(!looksLikeClosing(last,notes))return;
  let close=artifact.nextElementSibling;if(!close||!close.classList.contains('swrlz-code-artifact-close')){close=document.createElement('div');close.className='swrlz-code-artifact-close';artifact.after(close)}
  close.replaceChildren(last.cloneNode(true));last.remove();
}
function polishBubble(bubble){
  if(!bubble)return;
  removeStandaloneName(bubble);
  const artifact=bubble.querySelector(':scope > .swrlz-code-artifact');
  if(artifact){ensureLead(artifact);removeStandaloneName(artifact);moveClosing(artifact)}
  const live=bubble.querySelector(':scope > .swrlz-live-code-artifact');
  if(live){ensureLead(live);removeStandaloneName(live);moveClosing(live)}
}
function scan(root=document){root.querySelectorAll?.('.message.assistant .bubble').forEach(polishBubble)}
function install(){
  scan();
  const target=document.querySelector('.messages')||document.querySelector('.message-stack')||document.body;
  const observer=new MutationObserver(records=>{for(const record of records){const node=record.target?.nodeType===1?record.target:record.target?.parentElement;const bubble=node?.closest?.('.message.assistant .bubble');if(bubble)polishBubble(bubble);for(const added of record.addedNodes||[]){if(added.nodeType!==1)continue;const b=added.matches?.('.message.assistant .bubble')?added:added.querySelector?.('.message.assistant .bubble');if(b)polishBubble(b)}}});
  observer.observe(target,{childList:true,subtree:true,characterData:true});window.__swrlzResponsePolishObserver=observer;
}
const style=document.createElement('style');style.textContent=`
.swrlz-code-artifact-close{margin:12px 2px 0;line-height:1.65;color:var(--text)}
.swrlz-code-artifact-close p{margin:0}
.swrlz-presentational-lead{line-height:1.65}
`;document.head.appendChild(style);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();