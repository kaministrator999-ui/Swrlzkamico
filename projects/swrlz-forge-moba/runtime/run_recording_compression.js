// Optional lossless browser-native gzip export/import for all Play-run modes.
// Old JSON/text/offline spectator formats retain their existing controls.
function stRunInstallCompressedUI() {
  const exportPlain=document.getElementById('stRunExportJson');
  const picker=document.getElementById('stRunFile');
  if(!exportPlain||!picker||document.getElementById('stRunExportGzip'))return;
  const button=document.createElement('button');
  button.id='stRunExportGzip';button.type='button';
  button.textContent='Export compressed (.json.gz)';
  button.title='Lossless gzip recording; decompress to obtain ordinary .swyrl-run.json';
  exportPlain.before(button);
  const feedback=()=>document.getElementById('stRunImportFeedback');
  const supported=typeof CompressionStream==='function'&&typeof DecompressionStream==='function';
  if(!supported){button.disabled=true;button.title='Compressed recordings require browser CompressionStream support';}
  const originalRefresh=stRunRefreshUI;
  stRunRefreshUI=function(...args){const result=originalRefresh(...args);button.disabled=!supported||exportPlain.disabled;return result;};
  button.disabled=!supported||exportPlain.disabled;
  // The legacy recorder also enables export buttons directly in stRunOpenRecord.
  // Observe that state so gzip becomes usable without requiring a HUD refresh.
  new MutationObserver(()=>{if(button.textContent!=='Compressing recording…')button.disabled=!supported||exportPlain.disabled;})
    .observe(exportPlain,{attributes:true,attributeFilter:['disabled']});
  button.addEventListener('click',async()=>{
    if(playing||simulating){feedback().textContent='Stop Play before exporting a recording.';return;}
    const run=stRunReviewState.record||stRunData();
    if(!run){feedback().textContent='No completed recording to export.';return;}
    if(!supported){feedback().textContent='Gzip compression is unsupported in this browser; use Export JSON.';return;}
    button.disabled=true;button.textContent='Compressing recording…';feedback().textContent='Compressing full recording without discarding frames or events…';
    try{
      const raw=new Blob([JSON.stringify(run)],{type:'application/json'});
      const zipped=await new Response(raw.stream().pipeThrough(new CompressionStream('gzip'))).blob();
      const name='play-run-'+String(run.id||run.startedAt||'run').replace(/[^a-z0-9_-]/gi,'-').slice(0,80)+'.swyrl-run.json.gz';
      stRunDownloadBlob(new Blob([zipped],{type:'application/gzip'}),name);
      const saved=(100*(1-zipped.size/Math.max(1,raw.size))).toFixed(1);
      feedback().textContent='Compressed recording downloaded: '+(zipped.size/1048576).toFixed(1)+' MiB ('+saved+'% smaller).';
    }catch(error){feedback().textContent='Compression failed; original recording is intact. '+error.message;}
    finally{button.textContent='Export compressed (.json.gz)';button.disabled=!supported||exportPlain.disabled;}
  });
  picker.setAttribute('accept','.json,.gz,.json.gz,application/json,application/gzip');
  picker.addEventListener('change',async event=>{
    const file=picker.files?.[0];
    if(!file||!(/\.gz$/i.test(file.name)||file.type==='application/gzip'))return;
    event.stopImmediatePropagation();
    try{
      if(typeof DecompressionStream!=='function')throw Error('This browser cannot decompress gzip recordings.');
      if(file.size>120*1048576)throw Error('Compressed recording exceeds the 120 MiB import limit.');
      const magic=new Uint8Array(await file.slice(0,2).arrayBuffer());
      if(magic[0]!==0x1f||magic[1]!==0x8b)throw Error('Not a valid gzip file.');
      const reader=file.stream().pipeThrough(new DecompressionStream('gzip')).getReader();
      const chunks=[];let bytes=0;
      while(true){
        const {done,value}=await reader.read();if(done)break;
        bytes+=value.byteLength;
        if(bytes>256*1048576){await reader.cancel();throw Error('Decompressed recording exceeds the 256 MiB safety limit.');}
        chunks.push(value);
      }
      const run=JSON.parse(await new Blob(chunks,{type:'application/json'}).text());
      const valid=stRunValidate(run);if(!valid.ok)throw Error(valid.reason);
      const result=stRunOpenRecord(run);if(!result.ok)throw Error(result.reason);
      feedback().textContent='Compressed recording opened successfully. Authored map unchanged.';
    }catch(error){feedback().textContent='Could not open compressed recording: '+error.message;}
    finally{picker.value='';}
  },true);
}
