/* SE521_PERSISTENT_EDIT_JOURNAL_START
 * Native Model Atelier document-scoped, lab-aware, append-only edit history.
 * The journal is part of each saved modelAtelier document. No global history
 * stack may reach across project identities. No undo event is itself undoable.
 */
const se521Journal=(()=>{
 'use strict';
 const LABS=['model','rig','animate','texture'];
 const absent=()=>({__se521Absent:true});
 const isAbsent=v=>!!v&&typeof v==='object'&&v.__se521Absent===true&&Object.keys(v).length===1;
 const copy=v=>v===undefined?absent():structuredClone(v);
 const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const safe=k=>typeof k==='number'||typeof k==='string'&&!['__proto__','prototype','constructor'].includes(k);
 let active=null,mirror=null,applying=false,nextLabel='',lastError='';
 function authored(m){
  return {parts:structuredClone(m?.parts||[]),
   rigging:m?.rigging===undefined?absent():structuredClone(m.rigging)};
 }
 function journal(m){
  if(!m)return null;
  const j=m.editJournal;
  if(!j||j.schema!=='swyrl-edit-journal-v1'||!Array.isArray(j.events))
   m.editJournal={schema:'swyrl-edit-journal-v1',events:[]};
  return m.editJournal;
 }
 function bind(){
  const m=model();
  if(!m){active=null;mirror=null;return null;}
  if(m!==active){active=m;mirror=authored(m);applying=false;nextLabel='';lastError='';}
  journal(m);return m;
 }
 function changes(a,b,path=[],out=[]){
  if(equal(a,b))return out;
  if(!Array.isArray(a)||!Array.isArray(b)){
   if(a&&b&&typeof a==='object'&&typeof b==='object'&&!isAbsent(a)&&!isAbsent(b)&&
      !Array.isArray(a)&&!Array.isArray(b)){
    const keys=new Set([...Object.keys(a),...Object.keys(b)]);
    for(const k of keys)if(safe(k))changes(a[k],b[k],path.concat(k),out);
    return out;
   }
   out.push({path,before:copy(a),after:copy(b)});return out;
  }
  if(path.length===1&&path[0]==='parts'){
   const left=new Map(a.map((p,i)=>[p.id,{p,i}])),right=new Map(b.map((p,i)=>[p.id,{p,i}]));
   for(const id of new Set([...left.keys(),...right.keys()])){
    const old=left.get(id),now=right.get(id);
    if(!old||!now){out.push({path:['parts',id],before:copy(old?.p),after:copy(now?.p),
     beforeIndex:old?.i??-1,afterIndex:now?.i??-1});continue;}
    changes(old.p,now.p,['parts',id],out);
   }
   return out;
  }
  if(a.length!==b.length){out.push({path,before:copy(a),after:copy(b)});return out;}
  for(let i=0;i<a.length;i++)changes(a[i],b[i],path.concat(i),out);
  return out;
 }
 function read(doc,path){
  if(!Array.isArray(path)||!path.length||path.some(k=>!safe(k)))return absent();
  let node=doc,index=0;
  if(path[0]==='parts'){
   if(path.length<2)return absent();
   node=doc.parts.find(x=>x?.id===path[1]);index=2;
  }
  else if(path[0]==='rigging'){node=doc.rigging;index=1;}
  else return absent();
  for(;index<path.length;index++){
   if(node===undefined||node===null||isAbsent(node))return absent();
   node=node[path[index]];
  }
  return copy(node);
 }
 function write(doc,c,value,reverse){
  const path=c.path;
  if(!Array.isArray(path)||path.length<1||path.some(k=>!safe(k)))throw Error('Unsafe history field');
  if(path[0]==='parts'){
   if(path.length<2||typeof path[1]!=='string')throw Error('Invalid history part');
   let idx=doc.parts.findIndex(p=>p?.id===path[1]);
   if(path.length===2){
    if(idx>=0)doc.parts.splice(idx,1);
    if(!isAbsent(value)){
     const index=reverse?c.beforeIndex:c.afterIndex;
     doc.parts.splice(Math.max(0,Math.min(doc.parts.length,Number.isInteger(index)?index:doc.parts.length)),0,copy(value));
    }
    return;
   }
   if(idx<0)throw Error('Part required for history');
   let parent=doc.parts[idx];
   for(let i=2;i<path.length-1;i++){parent=parent[path[i]];if(parent==null)throw Error('History path missing');}
   const k=path.at(-1);
   if(isAbsent(value)){if(Array.isArray(parent))throw Error('Array removal not supported');delete parent[k];}
   else parent[k]=copy(value);
   return;
  }
  if(path[0]!=='rigging')throw Error('History field outside authoring document');
  if(path.length===1){if(isAbsent(value))delete doc.rigging;else doc.rigging=copy(value);return;}
  let parent=doc.rigging;
  if(!parent||isAbsent(parent))throw Error('Rigging path missing');
  for(let i=1;i<path.length-1;i++){parent=parent[path[i]];if(parent==null)throw Error('Rigging path missing');}
  const k=path.at(-1);
  if(isAbsent(value)){if(Array.isArray(parent))throw Error('Array removal not supported');delete parent[k];}
  else parent[k]=copy(value);
 }
 function inferLab(diff,hint){
  if(LABS.includes(hint))return hint;
  if(typeof se340XR!=='undefined'&&se340XR?.session&&LABS.includes(se340XR.se521Lab))
   return se340XR.se521Lab;
  const desktop=window.SWYRL_ENGINE_MINI_STUDIOS_496?.mode?.();
  if(desktop==='rig')return 'rig';
  if(desktop==='animate')return 'animate';
  if(desktop==='texture')return 'texture';
  if(diff.every(d=>d.path[0]==='rigging')){
   if(diff.some(d=>['timeline','clips','activeClip','duration','loop'].includes(d.path[1])))return 'animate';
   return 'rig';
  }
  if(diff.every(d=>d.path[0]==='parts'&&
   ['uvPaintPNG','uvMap','uv','material','color','texture','textureAtlas','uvTransform'].some(k=>d.path.includes(k))))
   return 'texture';
  if(diff.some(d=>d.path[0]==='rigging'))return 'rig';
  return 'model';
 }
 function labelFor(lab,diff){
  const field=diff[0]?.path?.slice(2).join('.')||diff[0]?.path?.join('.')||'';
  return ({model:'Model edit',rig:'Rig edit',animate:'Animation edit',texture:'Texture/material edit'})[lab]+
   (field?' · '+field.slice(0,80):'');
 }
 function record(hint='',label=''){
  const m=bind();if(!m||applying)return {changed:false};
  const current=authored(m),diff=changes(mirror,current);
  if(!diff.length)return {changed:false};
  const lab=inferLab(diff,hint),j=journal(m),seq=j.events.length+1;
  j.events.push({seq,time:new Date().toISOString(),type:'edit',lab,
   label:String(label||nextLabel||labelFor(lab,diff)).slice(0,160),changes:diff});
  nextLabel='';mirror=current;lastError='';
  return {changed:true,seq,lab,count:diff.length};
 }
 function stacks(lab){
  const m=bind();if(!m)return {undo:[],redo:[]};
  const stack=[],redo=[],edits=new Map();
  for(const ev of journal(m).events){
   if(ev?.lab!==lab)continue;
   if(ev.type==='edit'){edits.set(ev.seq,ev);stack.push(ev.seq);redo.length=0;}
   else if(ev.type==='undo'&&stack.at(-1)===ev.target){redo.push(stack.pop());}
   else if(ev.type==='redo'&&redo.at(-1)===ev.target){stack.push(redo.pop());}
  }
  return {undo:stack,redo,edits};
 }
 function labNow(){
  if(typeof se340XR!=='undefined'&&se340XR?.session&&LABS.includes(se340XR.se521Lab))return se340XR.se521Lab;
  const v=window.SWYRL_ENGINE_MINI_STUDIOS_496?.mode?.();
  return LABS.includes(v)?v:'model';
 }
 function depths(lab=labNow()){
  const {undo,redo}=stacks(lab);
  return {canUndo:!!undo.length,canRedo:!!redo.length,undoDepth:undo.length,redoDepth:redo.length,lab};
 }
 function step(backward,lab=labNow()){
  const m=bind();
  if(!m)return {ok:false,changed:false,error:'No active model'};
  if(applying)return {ok:false,changed:false,error:'History operation in progress'};
  record();
  const j=journal(m),state=stacks(lab);
  const id=(backward?state.undo:state.redo).at(-1),target=state.edits.get(id);
  if(!target)return {ok:true,changed:false,reason:'No '+(backward?'undo':'redo')+' step in '+lab+' lab'};
  const current=authored(m),ordered=backward?[...target.changes].reverse():target.changes;
  for(const c of ordered){
   const expected=backward?c.after:c.before;
   if(!equal(read(current,c.path),expected)){
    lastError='History conflict: a later edit depends on '+target.label;
    return {ok:false,changed:false,error:lastError};
   }
  }
  const draft=authored(m);
  try{for(const c of ordered)write(draft,c,backward?c.before:c.after,backward);}
  catch(e){lastError='History cannot be applied: '+String(e?.message||e);
   return {ok:false,changed:false,error:lastError};}
  applying=true;
  try{
   m.parts=draft.parts;
   if(isAbsent(draft.rigging))delete m.rigging;else m.rigging=draft.rigging;
   selection=null;
   renderParts();
   if(typeof se220RigBind==='function')se220RigBind();
   if(typeof se220RigRefresh==='function')se220RigRefresh();
   const type=backward?'undo':'redo';
   j.events.push({seq:j.events.length+1,time:new Date().toISOString(),type,lab,
    target:target.seq,label:(backward?'Undid ':'Redid ')+target.label});
   mirror=authored(m);lastError='';
   if(typeof markDirty==='function')markDirty();
   if(typeof refreshList==='function')refreshList();
   if(typeof refreshInspector==='function')refreshInspector();
   return {ok:true,changed:true,lab,target:target.seq,type};
  }catch(e){lastError='History refresh error: '+String(e?.message||e);
   return {ok:false,changed:false,error:lastError};
  }finally{applying=false;}
 }
 function resetPreview(){bind();return depths();}
 function inspect(){
  const m=bind(),j=journal(m);return {projectId:currentProject?.instanceId||null,
   totalEvents:j?.events.length||0,lab:labNow(),...depths(),lastError};
 }
 return Object.freeze({bind,record,step,depths,inspect,resetPreview,
  before:()=>{bind();},touched:record,setLabel:s=>{nextLabel=String(s||'').slice(0,160)},
  getEvents:()=>journal(bind())?.events?.map(e=>({seq:e.seq,time:e.time,type:e.type,lab:e.lab,
   label:e.label,target:e.target}))||[]});
})();
window.SWYRL_ENGINE_EDIT_JOURNAL_521=se521Journal;
/* SE521_PERSISTENT_EDIT_JOURNAL_END */