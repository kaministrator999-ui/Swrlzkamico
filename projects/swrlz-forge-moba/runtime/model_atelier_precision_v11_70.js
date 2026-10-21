// §E v11.70: precision-controlled native transforms + compact viewport navigation.
// UI-only preferences are per-device and never saved into the model/project JSON.
const atelierPrecisionKey='swyrlz-atelier-transform-sensitivity-v1';
const atelierPrecisionMultipliers=[.125,.25,.5,.75,1,1.5,2,3,4];
let atelierPrecisionIndexes=(()=>{
 const base={move:4,rotate:4,scale:4};
 try{
  const v=JSON.parse(localStorage.getItem(atelierPrecisionKey)||'null');
  if(v&&typeof v==='object')
   for(const mode of Object.keys(base))
    if(Number.isInteger(v[mode])&&v[mode]>=0&&v[mode]<atelierPrecisionMultipliers.length)
     base[mode]=v[mode];
 }catch(_){}
 return base;
})();
function atelierMeshSensitivity(mode=atelierMeshMode){
 return atelierPrecisionMultipliers[atelierPrecisionIndexes[mode]??4]||1;
}
function atelierMeshPrecisionRefresh(){
 const root=atelierMeshStrip?.querySelector('[data-mesh-precision]');
 if(!root)return;
 const factor=atelierMeshSensitivity();
 const slider=root.querySelector('input[type=range]');
 const value=root.querySelector('[data-precision-value]');
 const caption=root.querySelector('[data-precision-mode]');
 if(slider&&document.activeElement!==slider)slider.value=String(atelierPrecisionIndexes[atelierMeshMode]??4);
 if(value)value.textContent=(factor===.125?'⅛':factor.toString())+'×';
 if(caption)caption.textContent={move:'Move distance',rotate:'Rotate speed',scale:'Scale speed'}[atelierMeshMode];
 root.setAttribute('aria-label',caption?.textContent+' sensitivity');
}
function atelierMeshPrecisionInstall(strip){
 if(strip.querySelector('[data-mesh-precision]'))return;
 const bar=document.createElement('div');
 bar.className='amq-precision';
 bar.dataset.meshPrecision='1';
 bar.innerHTML='<div class="amq-precision-label"><span data-precision-mode>Move distance</span><output data-precision-value>1×</output></div>'+
  '<div class="amq-precision-track"><span>Fine</span><input type="range" min="0" max="8" step="1" value="4" aria-label="Transform sensitivity: fine to fast"><span>Fast</span></div>';
 const modes=strip.querySelector('[data-axis="x"]')?.closest('.amq-line');
 if(modes)strip.insertBefore(bar,modes);else strip.append(bar);
 const slider=bar.querySelector('input');
 slider.addEventListener('input',()=>{
  atelierPrecisionIndexes[atelierMeshMode]=Number(slider.value);
  try{localStorage.setItem(atelierPrecisionKey,JSON.stringify(atelierPrecisionIndexes))}catch(_){}
  atelierMeshPrecisionRefresh();
 });
 slider.addEventListener('pointerdown',e=>e.stopPropagation());
 atelierMeshPrecisionRefresh();
}
function atelierViewportTopArrange(panel){
 const bar=panel.querySelector('#modelAtelierViewportModes');
 if(!bar||bar.dataset.arranged==='1')return;
 const byId=id=>bar.querySelector('#modelAtelier'+id);
 const group=(name,className)=>{
  const g=document.createElement('div');
  g.className='atelier-top-group '+className;
  g.setAttribute('aria-label',name);
  return g;
 };
 const primary=group('Render settings','atelier-top-render');
 const mode=byId('ViewportMode')?.closest('label');
 const scope=byId('ViewportScope')?.closest('label');
 if(!mode||!scope)return;
 primary.append(mode,scope);
 const cameraRow=group('Camera direction','atelier-top-camera');
 const presets=bar.querySelector('.atelier-view-presets');
 const center=byId('ViewportPanReset');
 if(presets)cameraRow.append(presets);
 if(center)cameraRow.append(center);
 const advanced=document.createElement('details');
 advanced.className='atelier-top-advanced';
 const heading=document.createElement('summary');
 heading.textContent='Display, wire & interior';
 advanced.append(heading);
 const toggles=group('Display options','atelier-top-display');
 for(const id of ['ViewportColors','ViewportTextures','ViewportWireContrast','ViewportWireTint']){
  const label=byId(id)?.closest('label');if(label)toggles.append(label);
 }
 advanced.append(toggles);
 const clipping=bar.querySelector('.atelier-clip-tools');
 if(clipping)advanced.append(clipping);
 const unused=Array.from(bar.children).filter(c=>c!==primary&&c!==cameraRow&&c!==advanced);
 // Preserve every unknown/extensible control: move the original DOM nodes,
 // never clone/rebind their listeners.
 bar.replaceChildren(primary,cameraRow,advanced,...unused);
 bar.dataset.arranged='1';
}
