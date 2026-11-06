/* SE293_SHARED_START */
// Typed, bounded mesh descriptions. This code is shared by host validation and
// the native Model Atelier receiver; neither receiver executes model programs.
function se293ShapeData(op){
  const has=k=>Object.hasOwn(op,k),num=(n,lo,hi)=>typeof n==='number'&&Number.isFinite(n)&&n>=lo&&n<=hi;
  const consecutive=a=>a.slice(1).every((p,i)=>Math.hypot(...p.map((n,j)=>n-a[i][j]))>1e-6);
  const detail=()=>{if(has('segments')&&(!Number.isInteger(op.segments)||!num(op.segments,8,64)))throw Error('INVALID_MESH_SEGMENTS');};
  if(op.kind==='loft'){
    if(!Array.isArray(op.path)||op.path.length<2||op.path.length>40||
      !op.path.every(p=>Array.isArray(p)&&p.length===3&&p.every(n=>num(n,-100,100)))||!consecutive(op.path)||
      !Array.isArray(op.radii)||op.radii.length!==op.path.length||!op.radii.every(n=>num(n,.00025,5)))throw Error('INVALID_LOFT_PROFILE');
    if(['profile','arcStart','arcLength'].some(has))throw Error('UNSUPPORTED_SHAPE_FIELD');
    detail();return {path:op.path.map(p=>[...p]),radii:[...op.radii],segments:op.segments??24};
  }
  if(op.kind==='lathe'){
    if(!Array.isArray(op.profile)||op.profile.length<2||op.profile.length>24||
      !op.profile.every(p=>Array.isArray(p)&&p.length===2&&num(p[0],0,5)&&num(p[1],-100,100))||
      !consecutive(op.profile)||!op.profile.some(p=>p[0]>0))throw Error('INVALID_LATHE_PROFILE');
    if(['path','radii'].some(has))throw Error('UNSUPPORTED_SHAPE_FIELD');
    if(has('arcStart')&&!num(op.arcStart,-Math.PI*2,Math.PI*2)||
      has('arcLength')&&!num(op.arcLength,.05,Math.PI*2))throw Error('INVALID_LATHE_ARC');
    detail();return {profile:op.profile.map(p=>[...p]),arcStart:op.arcStart??0,arcLength:op.arcLength??Math.PI*2,segments:op.segments??32};
  }
  if(['path','radii','profile','arcStart','arcLength','segments'].some(has))throw Error('UNSUPPORTED_SHAPE_FIELD');
  return {};
}
/* SE293_SHARED_END */

/* SE293_ATELIER_START */
function se293ChatNativePart(op){
  const shape=se293ShapeData(op);
  const p={id:'atelier-chat-'+crypto.randomUUID(),name:op.name||'New mesh',kind:op.kind,
    position:op.position||[0,2.6,.7],rotation:op.rotation||[0,0,0],scale:op.scale||[.3,.3,.3],
    color:op.color||'#88daff',material:op.material||'gloss',group:'Custom'};
  if(op.kind==='loft')Object.assign(p,shape);
  if(op.kind==='lathe'){
    const positions=[],uvs=[],indices=[],rows=[];
    for(let i=0;i<shape.profile.length;i++){
      const [radius,y]=shape.profile[i],row=[];
      if(radius===0){row.push(positions.length/3);positions.push(0,y,0);uvs.push(.5,i/(shape.profile.length-1));}
      else for(let j=0;j<=shape.segments;j++){
        const theta=shape.arcStart+shape.arcLength*j/shape.segments;
        row.push(positions.length/3);positions.push(radius*Math.sin(theta),y,radius*Math.cos(theta));
        uvs.push(j/shape.segments,i/(shape.profile.length-1));
      }
      rows.push(row);
    }
    for(let i=1;i<rows.length;i++){
      const a=rows[i-1],b=rows[i];
      if(a.length===1&&b.length===1)continue;
      for(let j=0;j<shape.segments;j++){
        if(a.length===1)indices.push(a[0],b[j],b[j+1]);
        else if(b.length===1)indices.push(a[j],b[0],a[j+1]);
        else indices.push(a[j],b[j],a[j+1],a[j+1],b[j],b[j+1]);
      }
    }
    // The radial shell faces outward for either overall profile direction.
    // A flat radius-only disk retains its original upward-facing winding.
    if(shape.profile.at(-1)[1]>shape.profile[0][1])for(let i=0;i<indices.length;i+=3){
      const next=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=next;
    }
    p.kind='topologyMesh';p.topologyMesh={positions,uvs,indices};
  }
  return p;
}
/* SE293_ATELIER_END */

/* SE293_HOST_START */
const se293MeshTools=Object.freeze({schema:'swrlz-forge-mesh-tools-v2',
  kinds:['sphere','box','cone','cylinder','loft','lathe'],maxOperations:64});
let se293BatchTail=Promise.resolve();
function applyBatch(payload){
  // A second generation cannot interleave with a partly painted first batch.
  // Its own frozen preconditions are checked again when its turn begins.
  const result=se293BatchTail.then(()=>se293ApplyBatch(payload));
  se293BatchTail=result.catch(()=>{});return result;
}
const se293Paint=()=>new Promise(resolve=>setTimeout(resolve,100));
async function se293ApplyBatch(payload){
  if(!lease||!isVisible()||payload.leaseId!==lease.leaseId||seenBatches.has(payload.batchId))return;
  const active=lease;seenBatches.add(payload.batchId);if(seenBatches.size>256)seenBatches.delete(seenBatches.values().next().value);
  clearTimeout(heartbeatTimer);heartbeatTimer=null;
  let taken,results=[],lastRenew=Date.now();
  const startedAt=Date.now();let deadline=startedAt+25000;
  const progress=(op,result,total)=>{
    const name=summaryName(result.name||op.name||op.op);
    setStatus((result.ok?'Applied ':'Paused ')+results.length+'/'+total+' · '+name,!result.ok);
    if(port)try{send('host.progress',{batchId:payload.batchId,generationId:payload.generationId,
      completed:results.length,total,op:op.op,name,ok:result.ok,...(result.code?{code:result.code}:{})});}catch{}
  };
  try{
    taken=await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/take',{leaseId:active.leaseId},active);
    if(Object.hasOwn(taken,'applicationWindowMs')){
      if(!Number.isInteger(taken.applicationWindowMs)||taken.applicationWindowMs<1000||taken.applicationWindowMs>25000)throw Error('INVALID_BATCH_WINDOW');
      deadline=startedAt+taken.applicationWindowMs-1000;
    }else if(taken.operations?.length>16)throw Error('MISSING_BATCH_WINDOW');
    const before=context(),binding=taken.preconditions;
    if(!isVisible()||lease!==active||!binding||binding.leaseId!==active.leaseId||binding.threadId!==active.threadId||binding.projectId!==before.projectId||binding.generationId!==payload.generationId||JSON.stringify(binding.context)!==JSON.stringify(before))throw Error('STALE_NATIVE_PRECONDITIONS');
    if(!Array.isArray(taken.operations)||!taken.operations.length||taken.operations.length>MAX_BATCH)throw Error('INVALID_BATCH');
    if(taken.operations.length>1&&taken.operations.some(op=>op?.op==='editor.undo'||op?.op==='editor.redo'||op?.op?.startsWith('material.')||op?.op?.startsWith('particle.')||op?.op?.startsWith('rig.')))throw Error('HISTORY_OR_STUDIO_REQUIRES_SEPARATE_BATCH');
    if(taken.operations.some(op=>op?.op==='project.create')&&taken.operations.length!==1)throw Error('PROJECT_CREATE_REQUIRES_SEPARATE_BATCH');
    for(const op of taken.operations)validateOperation(op,before);
    let expected=before,failed=false;
    for(const op of taken.operations){
      if(failed){const result={op:op.op,ok:false,code:'PREVIOUS_OPERATION_FAILED'};results.push(result);progress(op,result,taken.operations.length);continue;}
      let result;
      try{
        let now=context();
        if(Date.now()>=deadline)throw Error('EDITOR_BATCH_DEADLINE');
        if(!isVisible()||lease!==active||now.projectId!==before.projectId||now.workspace!==before.workspace||now.mode!=='edit')throw Error('EDITOR_DETACHED');
        if(JSON.stringify(now)!==JSON.stringify(expected))throw Error('EDITOR_CHANGED_DURING_BATCH');
        if(Date.now()-lastRenew>=4000){
          await hostRequest('heartbeat',{leaseId:active.leaseId,visible:true,hostId,channelId,
            threadId:active.threadId,projectId:active.projectId,context:now},active);
          lastRenew=Date.now();now=context();
          if(!isVisible()||lease!==active||JSON.stringify(now)!==JSON.stringify(expected))throw Error('EDITOR_CHANGED_DURING_BATCH');
          if(Date.now()>=deadline)throw Error('EDITOR_BATCH_DEADLINE');
        }
        result={op:op.op,ok:true,...(op.op==='project.create'?await se175Create(op,active,before):execute(op))};expected=context();
      }catch(error){failed=true;if(result?.ok!==true)result={op:op.op,ok:false,code:summaryName(error.message)};}
      results.push(result);progress(op,result,taken.operations.length);
      if(!failed)await se293Paint();
    }
    await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/finish',{leaseId:active.leaseId,receiptNonce:taken.receiptNonce,results,context:context()},active);
    if(!failed&&taken.operations[0]?.op==='project.create'){
      revoke('New project opened. Reconnect on your next message.');
      setStatus('Created '+summaryName(currentProject.projectName||currentProject.name)+' · saved on this device. Chat will inspect it on your next message.');
    }else setStatus(failed?'Some editor actions could not finish. See Chat for the receipts.':'Native editor changes applied. Undo is available.',failed);
    se175UpdateLabel();
  }catch(error){
    // Retain successful native receipts if transport fails after a partial edit.
    // A revoked lease may reject the final request; that is never native undo.
    if(taken?.receiptNonce&&Array.isArray(taken.operations))try{
      const pending=taken.operations.slice(results.length).map(op=>({op:op.op,ok:false,code:summaryName(error.message)}));
      await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/finish',{leaseId:active.leaseId,
        receiptNonce:taken.receiptNonce,results:[...results,...pending],context:context()},active);
    }catch{}
    setStatus('Editor actions paused: '+summaryName(error.message),true);
  }finally{if(lease===active&&isVisible())heartbeatTimer=setTimeout(heartbeat,5000);}
}
/* SE293_HOST_END */
