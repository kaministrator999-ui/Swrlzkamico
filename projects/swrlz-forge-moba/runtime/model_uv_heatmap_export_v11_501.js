// SE501_UV_HEATMAP_EXPORT_START
// Read-only UV distortion and texture-registration diagnostics in the native UV editor.
const se501UV = (() => {
  let busy = false;
  let opacity = 0.46;
  let centered = true;
  let resolution = 2048;
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const selected = () => se336SelectedMesh();
  function anchor(target) {
    if (!target) return null;
    const marker = se366Marker(target.part);
    const pin = se356UVPin?.id === target.part.id ? se356UVPin : null;
    if (!pin && !marker) return null;
    const u = clamp(pin ? pin.u : marker.centerUV[0], 0, 1);
    const v = clamp(pin ? pin.v : marker.centerUV[1], 0, 1);
    const same = !!marker && Math.hypot(u - marker.centerUV[0], v - marker.centerUV[1]) < 0.0001;
    return {u, v, angleDeg: same ? marker.angleDeg : 0,
      scale: same ? marker.scale : 1, source: pin ? 'picked UV point' : 'saved UV center'};
  }
  function paintSnapshot(target) {
    const p = target.part;
    return JSON.stringify([p.uvPaintPNG, p.uvPaintOffset, p.uvPaintRepeat, p.uvArtMarker,
      se356UVPin?.id === p.id ? [se356UVPin.u, se356UVPin.v] : null]);
  }
  function surfaceLayer(canvas, report) {
    const ctx = canvas.getContext('2d');
    if (!ctx) throw Error('UV diagnostic canvas unavailable.');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const size = canvas.width;
    for (const face of report.faces) {
      const [u0, v0, u1, v1, u2, v2] = face.uv;
      ctx.fillStyle = face.ratio < 1.25 ? '#2ed5b8' :
        face.ratio < 1.75 ? '#d4da55' : face.ratio < 3 ? '#f49846' : '#ed5067';
      ctx.beginPath();
      ctx.moveTo(u0 * size, (1 - v0) * size);
      ctx.lineTo(u1 * size, (1 - v1) * size);
      ctx.lineTo(u2 * size, (1 - v2) * size);
      ctx.closePath(); ctx.fill();
    }
  }
  function canvas(size) {
    const node = document.createElement('canvas');
    node.width = node.height = size;
    return node;
  }
  function drawCenter(ctx, size, a) {
    if (!a) return;
    const x = a.u * size, y = (1 - a.v) * size;
    const r = Math.max(9, size * 0.012);
    ctx.save();
    ctx.lineWidth = Math.max(2, size / 512);
    ctx.strokeStyle = '#101525';
    ctx.beginPath(); ctx.arc(x,y,r + 2,0,Math.PI*2); ctx.stroke();
    ctx.strokeStyle = '#fff4c2';
    ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - r * 1.7,y); ctx.lineTo(x + r * 1.7,y);
    ctx.moveTo(x,y - r * 1.7); ctx.lineTo(x,y + r * 1.7); ctx.stroke();
    ctx.restore();
  }
  function transformCentered(image, size, a) {
    if (!a || !centered) return image;
    const result = canvas(size), ctx = result.getContext('2d');
    if (!ctx) throw Error('Centered UV canvas unavailable.');
    ctx.fillStyle = '#142334'; ctx.fillRect(0,0,size,size);
    ctx.translate(size/2,size/2);
    ctx.rotate(a.angleDeg * Math.PI / 180);
    ctx.scale(a.scale,a.scale);
    ctx.translate(-a.u * size, -(1-a.v) * size);
    ctx.drawImage(image,0,0);
    return result;
  }
  function drawLegend(ctx,size,report,kind,a) {
    const font=Math.max(13,Math.round(size/75));
    const pad=Math.max(12,Math.round(size/85));
    const h=font*3.1, w=Math.min(size-2*pad,font*31);
    ctx.save(); ctx.fillStyle='rgba(8,19,31,.86)';ctx.fillRect(pad,pad,w,h);
    ctx.fillStyle='#eefaff'; ctx.font=`600 ${font}px sans-serif`;
    ctx.fillText(kind==='overlay'?'TEXTURE + UV STRETCH':'UV SURFACE STRETCH',pad+font*.5,pad+font*1.12);
    ctx.font=`${Math.round(font*.75)}px sans-serif`;
    ctx.fillText(`low  •  moderate  •  high  |  ${report.sampled}/${report.triangles} triangles`,pad+font*.5,pad+font*2.12);
    const cy=pad+font*2.44, sw=Math.max(12,Math.floor(w/10));
    ['#2ed5b8','#d4da55','#f49846','#ed5067'].forEach((color,i)=>{
      ctx.fillStyle=color;ctx.fillRect(pad+font*.5+i*sw,cy,sw-1,Math.max(3,font*.27));
    });
    if (a) {
      ctx.fillStyle='rgba(8,19,31,.83)';ctx.fillRect(pad,size-pad-font*1.7,w,font*1.7);
      ctx.fillStyle='#fff4c2';ctx.font=`${Math.round(font*.75)}px sans-serif`;
      ctx.fillText(`Center U ${a.u.toFixed(4)}  V ${a.v.toFixed(4)}  •  ${a.source}`,pad+font*.4,size-pad-font*.68);
    }
    ctx.restore();
  }
  function compose(target, size, report, kind, image, a, includeLegend) {
    const base=canvas(size),ctx=base.getContext('2d');
    if (!ctx) throw Error('UV canvas unavailable.');
    ctx.fillStyle='#142334';ctx.fillRect(0,0,size,size);
    if (kind==='overlay') {
      if (!image) throw Error('A painted texture is required for combined UV export.');
      se356UVPaintImage(ctx,image,target.part,size);
    }
    const heat=canvas(size);
    surfaceLayer(heat,report);
    ctx.globalAlpha=kind==='overlay'?opacity:1;
    ctx.drawImage(heat,0,0);
    ctx.globalAlpha=1;
    const guide=canvas(size);
    se336UVLayout(target.mesh,guide);
    ctx.globalAlpha=kind==='overlay'?.92:.48;
    ctx.drawImage(guide,0,0);
    ctx.globalAlpha=1;
    drawCenter(ctx,size,a);
    const result=transformCentered(base,size,a);
    if (includeLegend) drawLegend(result.getContext('2d'),size,report,kind,a);
    return result;
  }
  function measure(target, full) {
    target.mesh.updateWorldMatrix(true,false);
    return se469Math.measure(target.mesh.geometry,target.mesh.matrixWorld,full?40000:6000);
  }
  function refresh() {
    const root=document.getElementById('se501UVDiagnostics');
    if (!root) return;
    const target=selected(),a=anchor(target);
    for (const button of root.querySelectorAll('[data-se501-export]')) {
      button.disabled=busy||!target||(button.dataset.se501Export==='overlay'&&!target.part.uvPaintPNG);
    }
    root.querySelector('#se501UVCenter').textContent=a?
      `UV center: U ${a.u.toFixed(4)}, V ${a.v.toFixed(4)} (${a.source})`:
      'No UV center selected; export uses the native 0–1 UV layout.';
    root.querySelector('#se501UVUseCenter').disabled=!a||busy;
    root.querySelector('#se501UVUseCenter').checked=centered&&!!a;
    root.querySelector('#se501UVOpaqueLabel').textContent=Math.round(opacity*100)+'%';
  }
  async function imageFor(target) {
    if (!target.part.uvPaintPNG) throw Error('This mesh has no painted texture yet.');
    const img = new Image();
    await new Promise((resolve,reject)=>{
      img.onload=resolve;
      img.onerror=()=>reject(Error('Unable to decode the saved painted texture.'));
      img.src=target.part.uvPaintPNG;
    });
    return img;
  }
  async function exportPNG(kind) {
    if (busy) return;
    const target=selected();
    if (!target) {status('Select a model mesh first.',true);return;}
    busy=true;refresh();
    const before=paintSnapshot(target), mesh=target.mesh;
    try {
      const image=kind==='overlay'?await imageFor(target):null;
      const current=selected();
      if (!current||current.part!==target.part||current.mesh!==mesh||paintSnapshot(current)!==before)
        throw Error('UV selection or texture settings changed. Export again.');
      const a=anchor(target),report=measure(target,true);
      const result=compose(target,resolution,report,kind,image,a,true);
      const blob=await new Promise((resolve,reject)=>result.toBlob(b=>b?resolve(b):reject(Error('Unable to encode UV PNG.')),'image/png'));
      if (selected()?.part!==target.part || paintSnapshot(target)!==before)
        throw Error('UV selection changed during export. Export again.');
      const url=URL.createObjectURL(blob);
      const link=document.createElement('a');
      const suffix=kind==='overlay'?'TEXTURE-STRETCH':'STRETCH-HEATMAP';
      link.href=url;
      link.download=(target.part.name+'-uv-'+suffix+'-'+resolution+'.png').replace(/[^a-z0-9_.-]+/gi,'-').slice(0,95);
      document.body.append(link);link.click();link.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1500);
      status('Exported '+suffix+' ('+report.sampled+'/'+report.triangles+' sampled UV triangles). Center and current UV mapping shown; source texture and mesh unchanged.');
    } catch(error) {status('UV diagnostic export: '+error.message,true);}
    finally {busy=false;refresh();}
  }
  function preview() {
    if (!se356UVPopupVisible()) return;
    const root=se356UVPreviewRoot(),cv=root?.querySelector('#se356UVCanvas');
    const info=root?.querySelector('#se356UVInfo'),target=selected();
    if (!cv||!info||!target) return;
    try {
      const img=se356UVLoadImage(target.part);
      if (!img) {info.textContent=target.part.uvPaintPNG?'Loading current mapped texture…':'Import a painted texture to compare with the UV heatmap.';return;}
      const report=measure(target,false),a=anchor(target);
      const result=compose(target,cv.width,report,'overlay',img,a,false);
      const ctx=cv.getContext('2d');ctx.clearRect(0,0,cv.width,cv.height);ctx.drawImage(result,0,0);
      info.textContent=target.part.name+' · current texture / stretch overlay · '+report.sampled+'/'+report.triangles+' sampled UV triangles'+(centered&&a?' · center framed':'');
      refresh();
    } catch(error) {info.textContent='UV texture diagnostic: '+error.message;}
  }
  function install() {
    const root=se356UVPreviewRoot();
    if (!root||root.querySelector('#se501UVDiagnostics')) return;
    const mode=root.querySelector('.se356-uv-preview-modes');
    if (mode) {
      const button=document.createElement('button');button.type='button';
      button.dataset.se356Mode='texture-stretch';button.setAttribute('aria-pressed','false');
      button.textContent='Texture + stretch';mode.append(button);
    }
    const block=document.createElement('section');block.id='se501UVDiagnostics';
    block.innerHTML='<strong>UV heatmap diagnostics · PNG exports</strong>'+
      '<p>Compare the existing image to the real UV wireframe and measured mesh stretching. Heat colors show distortion, not automatically detected painting errors.</p>'+
      '<p id="se501UVCenter" role="status"></p>'+
      '<label><input type="checkbox" id="se501UVUseCenter" checked> Frame selected UV center in preview and exports (using saved marker rotation/scale when applicable)</label>'+
      '<label>Heat overlay opacity <input type="range" id="se501UVOpaque" min="0" max="100" value="46" step="1"> <span id="se501UVOpaqueLabel">46%</span></label>'+
      '<label>PNG size <select id="se501UVResolution"><option value="1024">1024 px</option><option value="2048" selected>2048 px</option><option value="4096">4096 px</option></select></label>'+
      '<div class="se501-uv-actions"><button type="button" data-se501-export="heat">Export stretch heatmap</button>'+
      '<button type="button" data-se501-export="overlay">Export texture + heatmap</button></div>'+
      '<p>The export preserves the image’s current UV Slide and UV repeat/shape-fit settings. No UVs, textures, geometry or markers are modified. Overlapping islands and painting offsets require manual inspection.</p>';
    root.append(block);
    block.querySelector('#se501UVUseCenter').addEventListener('change',e=>{
      centered=!!e.target.checked;se356UVPreviewSchedule();refresh();
    });
    block.querySelector('#se501UVOpaque').addEventListener('input',e=>{
      opacity=Number(e.target.value)/100;se356UVPreviewSchedule();refresh();
    });
    block.querySelector('#se501UVResolution').addEventListener('change',e=>{resolution=Number(e.target.value);});
    for (const button of block.querySelectorAll('[data-se501-export]'))
      button.addEventListener('click',()=>void exportPNG(button.dataset.se501Export));
    refresh();
  }
  return Object.freeze({install,preview,refresh,exportPNG,anchor,compose,measure});
})();
const se501OriginalUVRender=se356UVRender;
se356UVRender=function() {
  if(se356UVMode==='texture-stretch')return se501UV.preview();
  return se501OriginalUVRender.apply(this,arguments);
};
const se501OriginalInstallPreview=se356UVInstallPreview;
se356UVInstallPreview=function() {
  const result=se501OriginalInstallPreview.apply(this,arguments);
  se501UV.install();return result;
};
const se501OriginalRefreshInspector=refreshInspector;
refreshInspector=function() {
  const result=se501OriginalRefreshInspector.apply(this,arguments);
  se501UV.refresh();return result;
};
const se501OriginalUVResolve=se356UVResolve;
se356UVResolve=function() {
  const result=se501OriginalUVResolve.apply(this,arguments);
  se501UV.refresh();return result;
};
const se501OriginalSaveMarker=se366SaveMarker;
se366SaveMarker=function() {
  const result=se501OriginalSaveMarker.apply(this,arguments);
  se501UV.refresh();return result;
};
window.SWYRLZ_E_UV_HEATMAP_EXPORT_501=Object.freeze({
  state:()=>({available:!!se336SelectedMesh(),anchor:se501UV.anchor(se336SelectedMesh())})
});
// SE501_UV_HEATMAP_EXPORT_END
