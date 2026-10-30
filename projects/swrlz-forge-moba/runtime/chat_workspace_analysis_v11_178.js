// §E v11.178: bounded, read-only inspection of the actual open editor workspace.
function se178EnrichContext(ctx){
  const rows=Array.isArray(ctx.workspace==='model-atelier'?ctx.meshes:ctx.actors)
    ? (ctx.workspace==='model-atelier'?ctx.meshes:ctx.actors):[];
  // The existing native snapshot selects at most 48 visible data records.
  // Full scenes are NOT copied into Chat; do not call sample concerns "bugs".
  const currentBytes=new TextEncoder().encode(JSON.stringify(ctx)).length;
  if(currentBytes>29000)return;
  const names=new Map(),types=new Map(),places=new Map(),findings=[];
  for(const row of rows){
    if(!row||typeof row!=='object')continue;
    const name=String(row.name||'').slice(0,100).trim();
    if(name)names.set(name,(names.get(name)||0)+1);
    const kind=String(row.type||row.kind||'unknown').slice(0,60);
    types.set(kind,(types.get(kind)||0)+1);
    if(Array.isArray(row.position)&&row.position.length===3&&row.position.every(Number.isFinite)){
      // Position equality is a *review hint*; layered objects can be intentional.
      const key=row.position.map(n=>Number(n).toFixed(3)).join(',');
      const group=places.get(key)||[];group.push(name||String(row.id||'unnamed').slice(0,80));places.set(key,group);
    }
  }
  for(const [name,count] of names){
    if(count>1&&findings.length<6)
      findings.push({code:'duplicate-name',detail:count+' inspected objects share the name '+name+'; confirm their identities in the Outliner.'});
  }
  for(const [position,group] of places){
    if(group.length>1&&findings.length<8)
      findings.push({code:'shared-position',detail:group.length+' inspected objects share a position ('+position+'); check whether their overlap is intentional.'});
  }
  ctx.workspaceAudit={
    sampled:rows.length,
    types:[...types.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,10).map(([name,count])=>({name,count})),
    findings,
  };
}
function se178AnalyzeWorkspace(){
  if(!ready||!isVisible()){setStatus('Open and connect § Chat before analyzing the editor.',true);return;}
  if(!se176AccountConnected){setStatus('Connect the Chat account first to analyze the current §E workspace.',true);return;}
  try{
    const ctx=context();
    if(!ctx.projectId||!ctx.project?.name)throw Error('PROJECT_NOT_READY');
    // The Chat-origin composer performs its own fresh snapshot request and
    // server-side owner/lease check. We send no scene strings as instructions.
    send('host.analyze',{});
    setStatus('Analyze request sent for '+summaryName(ctx.project.name)+'. Chat will inspect the current project; no changes will be made. If a draft is open, finish it and try again.');
  }catch(error){setStatus('Workspace analysis unavailable: '+summaryName(error.message),true);}
}
function se178Install(){
  const nearby=document.getElementById('seChatRefresh');
  if(!nearby||document.getElementById('se178Analyze'))return;
  const button=document.createElement('button');
  button.id='se178Analyze';button.type='button';button.textContent='Analyze workspace';
  button.title='Read-only analysis of the open project, level, selected object and bounded scene metadata';
  button.setAttribute('aria-label','Analyze currently open §E workspace in §wyrlz Chat');
  button.addEventListener('click',se178AnalyzeWorkspace);
  nearby.after(button);
}