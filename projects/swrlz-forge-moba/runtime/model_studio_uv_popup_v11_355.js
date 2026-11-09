/* §E v11.355 — independent Model Studio UV editor window.
   Reparent native UV widgets (do not clone/rewrite their listeners or UV data). */
(function se355UVEditor(){
  'use strict';
  let panel=null,popup=null,button=null,scheduled=false,drag=null;
  // Fit the UV window inside the actual 3D work area, *below* responsive
  // viewport controls. Do not guess header height or overlap the left tree.
  function safeBounds(){
    const model=panel?.getBoundingClientRect(),scene=q('.atelier-scene',panel)?.getBoundingClientRect();
    const header=q('.atelier-head',panel)?.getBoundingClientRect();
    const tabs=q('.se187-model-tabs',panel)?.getBoundingClientRect();
    const toolbar=q('#se320ModelTransform',panel);
    const transform=toolbar&&!toolbar.hidden?toolbar.getBoundingClientRect():null;
    const left=Math.max(6,(scene?.left??model?.left??0)+6);
    const right=Math.min(innerWidth-6,(scene?.right??model?.right??innerWidth)-6);
    const top=Math.max(6,(scene?.top??0)+6,(header?.bottom??0)+6,
      (tabs?.bottom??0)+6,(transform?.bottom??0)+8);
    const bottom=Math.min(innerHeight-6,(model?.bottom??innerHeight)-6);
    return {left,right,top:Math.min(top,bottom-116),bottom};
  }
  function fitWindow(reset=false){
    if(!popup||popup.hidden)return;
    const b=safeBounds(),width=Math.max(120,Math.min(480,b.right-b.left));
    const height=Math.max(116,Math.min(Math.round(innerHeight*.72),b.bottom-b.top));
    popup.style.width=width+'px';popup.style.height=height+'px';
    popup.style.maxWidth=width+'px';popup.style.maxHeight=height+'px';
    const rect=popup.getBoundingClientRect();
    const preferred=b.right-width;
    const x=reset?preferred:rect.left;
    const y=reset?b.top:rect.top;
    popup.style.left=Math.max(b.left,Math.min(x,b.right-width))+'px';
    popup.style.top=Math.max(b.top,Math.min(y,b.bottom-height))+'px';
    popup.style.right='auto';popup.style.bottom='auto';
  }
  const q=(selector,root=document)=>root?.querySelector(selector);
  function slideApi(){return window.SWYRLZ_E_MODEL_UV_SLIDE;}
  function isOpen(){return !!popup&&!popup.hidden;}
  function selectedState(){return slideApi()?.state?.()||{available:false,enabled:false,offset:[0,0]};}
  function refresh(){
    if(!panel||!popup)return;
    const selected=selectedState();
    const name=q('#se355UVSelection',popup);
    if(name)name.textContent=selected.available?
      'Selected textured mesh · U '+selected.offset[0].toFixed(3)+' · V '+selected.offset[1].toFixed(3):
      'Select a painted mesh to adjust its texture.';
    for(const element of popup.querySelectorAll('[data-se355-slide]')){
      element.disabled=!selected.available;
      if(element.dataset.se355Slide==='toggle'){
        element.setAttribute('aria-pressed',String(!!selected.enabled));
        element.textContent=selected.enabled?'✓ UV Slide ON':'⇄ UV Slide';
      }
    }
    if(button) {
      button.setAttribute('aria-expanded',String(isOpen()));
      button.classList.toggle('se355-uv-active',isOpen());
      button.classList.toggle('se355-uv-sliding',!!selected.enabled);
      button.title=selected.enabled?'UV Slide active · Open the UV Editor':'Open the separate UV Editor';
    }
  }
  function setOpen(open){
    if(!popup)return;
    popup.hidden=!open;
    if(open)fitWindow(true);
    if(!open&&selectedState().enabled)slideApi()?.toggle?.();
    refresh();
    if(open){
      const atlas=q('#se345UVAtlas',popup);
      if(atlas&&q('#se355UVWhole',popup)?.getAttribute('aria-pressed')==='true')atlas.open=true;
      q('#se355UVClose',popup)?.focus({preventScroll:true});
    }else button?.focus({preventScroll:true});
  }
  function activateSection(which){
    if(!popup)return;
    const atlas=q('#se345UVAtlas',popup);
    const area=q('.se355-uv-scroll',popup);
    for(const nav of popup.querySelectorAll('[data-se355-section]'))
      nav.setAttribute('aria-pressed',String(nav.dataset.se355Section===which));
    if(which==='whole'&&atlas){
      atlas.open=true;
      atlas.scrollIntoView({block:'start',behavior:'auto'});
    }else if(area)area.scrollTop=0;
  }
  function createPopup(root){
    const el=document.createElement('section');
    el.id='se355UVPopup';
    el.className='se355-uv-popup';
    el.hidden=true;
    el.setAttribute('role','dialog');
    el.setAttribute('aria-modal','false');
    el.setAttribute('aria-labelledby','se355UVTitle');
    el.innerHTML=
      '<div class="se355-uv-titlebar" id="se355UVHandle">'+
        '<strong id="se355UVTitle">🎨 UV Editor</strong>'+
        '<span class="se355-uv-grip" aria-hidden="true">⠿ Move</span>'+
        '<button type="button" id="se355UVClose" aria-label="Close UV Editor">✕ Close</button></div>'+
      '<nav class="se355-uv-nav" aria-label="UV workflows">'+
        '<button type="button" data-se355-section="single" aria-pressed="true">Selected mesh</button>'+
        '<button type="button" id="se355UVWhole" data-se355-section="whole" aria-pressed="false">Whole model atlas</button></nav>'+
      '<div class="se355-uv-scroll">'+
        '<section class="se355-uv-slide" aria-label="Position painted texture">'+
          '<strong>Texture placement on model</strong>'+
          '<p id="se355UVSelection">Select a painted mesh to adjust its texture.</p>'+
          '<div class="se355-uv-slide-buttons">'+
            '<button type="button" data-se355-slide="toggle" aria-pressed="false" title="Drag over the mesh to shift the painted texture">⇄ UV Slide</button>'+
            '<button type="button" data-se355-slide="left" title="Nudge U negative">U−</button>'+
            '<button type="button" data-se355-slide="right" title="Nudge U positive">U+</button>'+
            '<button type="button" data-se355-slide="down" title="Nudge V negative">V−</button>'+
            '<button type="button" data-se355-slide="up" title="Nudge V positive">V+</button>'+
            '<button type="button" data-se355-slide="reset" title="Reset the painted texture position">Reset UV</button>'+
          '</div>'+
          '<p class="se355-uv-hint">Enable UV Slide, then drag directly over the selected mesh in the 3D viewport. Mesh geometry stays in place; Undo/Redo remains in the viewport transform bar.</p>'+
        '</section>'+
        '<div id="se355UVNativeHost"></div>'+
      '</div>';
    root.append(el);
    el.addEventListener('pointerdown',event=>event.stopPropagation());
    el.addEventListener('keydown',event=>{
      // Model Studio uses Escape to close the entire editor. Inside this window
      // Escape closes the UV editor ONLY.
      if(event.key==='Escape'){
        event.preventDefault();
        event.stopImmediatePropagation();
        setOpen(false);
      }
    },true);
    q('#se355UVClose',el).addEventListener('click',()=>setOpen(false));
    el.addEventListener('click',event=>{
      const control=event.target.closest('[data-se355-slide],[data-se355-section]');
      if(!control||control.disabled)return;
      if(control.dataset.se355Section){activateSection(control.dataset.se355Section);return;}
      const api=slideApi();
      if(control.dataset.se355Slide==='toggle')api?.toggle?.();
      else api?.nudge?.(control.dataset.se355Slide);
      refresh();
    });
    const handle=q('#se355UVHandle',el);
    handle.addEventListener('pointerdown',event=>{
      if(event.button!==0||event.target.closest('button'))return;
      const rect=el.getBoundingClientRect();
      drag={id:event.pointerId,x:event.clientX,y:event.clientY,
        left:rect.left,top:rect.top};
      try{handle.setPointerCapture(event.pointerId);}catch(_){}
      event.preventDefault();event.stopPropagation();
    });
    handle.addEventListener('pointermove',event=>{
      if(!drag||drag.id!==event.pointerId)return;
      const nextLeft=drag.left+event.clientX-drag.x;
      const nextTop=drag.top+event.clientY-drag.y;
      const b=safeBounds();
      el.style.left=Math.max(b.left,Math.min(nextLeft,b.right-el.offsetWidth))+'px';
      el.style.top=Math.max(b.top,Math.min(nextTop,b.bottom-el.offsetHeight))+'px';
      el.style.right='auto';el.style.bottom='auto';
      event.preventDefault();event.stopPropagation();
    });
    const end=event=>{
      if(!drag||drag.id!==event.pointerId)return;
      drag=null;
      try{handle.releasePointerCapture(event.pointerId);}catch(_){}
    };
    handle.addEventListener('pointerup',end);
    handle.addEventListener('pointercancel',end);
    return el;
  }
  function mount(){
    const next=q('#modelAtelierPanel');
    if(!next)return;
    if(next!==panel){panel=next;popup=null;button=null;}
    const header=q('.atelier-head',panel);
    if(!header)return;
    button=q('#se355UVEditorOpen',panel);
    if(!button){
      button=document.createElement('button');
      button.type='button';
      button.id='se355UVEditorOpen';
      button.textContent='🎨 UV Editor';
      button.setAttribute('aria-controls','se355UVPopup');
      button.setAttribute('aria-haspopup','dialog');
      button.setAttribute('aria-expanded','false');
      const projects=q('#se320ModelProjects',header);
      if(projects)projects.after(button);
      else header.insertBefore(button,header.firstChild);
      button.addEventListener('click',()=>setOpen(!isOpen()));
      panel.addEventListener('swrlz:uv-slide-change',refresh);
      panel.addEventListener('change',event=>{
        if(event.target?.id==='modelAtelierParts')queueMicrotask(refresh);
      },true);
    }
    popup=q('#se355UVPopup',panel)||createPopup(panel);
    const host=q('#se355UVNativeHost',popup);
    if(isOpen())fitWindow(false);
    const single=q('#modelAtelierUVLayout',panel);
    // Keep the original UV export/import and whole-model atlas as one unit.
    if(single&&single.parentElement!==host)host.append(single);
    // Earlier indexed-topology UV repair is separate from the guide widget.
    const repair=q('#modelAtelierUVTools',panel);
    if(repair&&repair.parentElement!==host)host.append(repair);
    // The old selected-mesh toolbar UV row is superseded by the popup, not duplicated.
    q('#se320ModelTransform .se320-transform-uv',panel)?.remove();
    refresh();
  }
  function schedule(){
    if(scheduled)return;
    scheduled=true;
    queueMicrotask(()=>{scheduled=false;mount();});
  }
  function install(){
    mount();
    // Model Studio and UV atlas mount lazily; only react when DOM nodes change.
    new MutationObserver(records=>{
      if(records.some(record=>[...record.addedNodes].some(node=>node.nodeType===1)))schedule();
    }).observe(document.body,{subtree:true,childList:true});
    window.addEventListener('resize',()=>fitWindow(false));
    if(typeof ResizeObserver!=='undefined'){
      const host=q('#modelAtelierPanel');
      if(host)new ResizeObserver(()=>fitWindow(false)).observe(host);
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
  else queueMicrotask(install);
  window.SWYRLZ_E_UV_POPUP=Object.freeze({
    open:()=>{mount();setOpen(true);},close:()=>setOpen(false),
    state:()=>({open:isOpen(),hasNativeUV:!!q('#modelAtelierUVLayout',popup),
      hasAtlas:!!q('#se345UVAtlas',popup),
      hasTopButton:!!button})
  });
})();