/* §wyrlz Chat rich-widget viewer v284.
 * Client/Mask display only. Consumes trusted, bounded swrlz-widget-v1 metadata.
 * No eval, HTML injection, external CDN, network, or arbitrary mesh/file execution.
 */
(function(root){
  "use strict";
  const CONTRACT="swrlz-widget-v1";
  const KINDS=new Set(["comparison","math-graph","model-3d"]);
  const numeric=v=>typeof v==="number"&&Number.isFinite(v);
  const limit=(v,lo,hi)=>Math.min(hi,Math.max(lo,v));
  const label=(v,n=110)=>String(v===undefined||v===null?"":v).slice(0,n);
  const sane=(v,d,lo,hi)=>numeric(v)?limit(v,lo,hi):d;
  function normalize(widget){
    if(!widget||widget.contract!==CONTRACT||!KINDS.has(widget.kind)||widget.version!==1)return null;
    const data=widget.data;
    if(!data||typeof data!=="object"||Array.isArray(data))return null;
    const common={contract:CONTRACT,kind:widget.kind,version:1,title:label(widget.title||widget.kind),provider:label(widget.provider||"§wyrlz",70)};
    if(widget.kind==="comparison"){
      if(!Array.isArray(data.items)||!Array.isArray(data.metrics))return null;
      const metrics=data.metrics.slice(0,6).filter(x=>x&&typeof x==="object"&&/^[a-zA-Z][a-zA-Z0-9_-]{0,30}$/.test(String(x.key||"")))
        .map(x=>({key:String(x.key),label:label(x.label||x.key,60),unit:label(x.unit||"",12),higherIsBetter:x.higherIsBetter===true?true:x.higherIsBetter===false?false:null}));
      const items=data.items.slice(0,4).filter(x=>x&&typeof x==="object").map(x=>{
        const values={};
        for(const m of metrics)if(x.values&&Object.prototype.hasOwnProperty.call(x.values,m.key)){
          const v=x.values[m.key];if(numeric(v))values[m.key]=limit(v,-1e9,1e9);
          else if(typeof v==="string")values[m.key]=label(v,45);
        }
        return {name:label(x.name||"Option",65),values};
      });
      if(items.length<2||metrics.length<1)return null;
      return {...common,data:{items,metrics,note:label(data.note||"",240)}};
    }
    if(widget.kind==="math-graph"){
      if(!Array.isArray(data.series))return null;
      const series=data.series.slice(0,5).filter(x=>x&&typeof x==="object").map(x=>{
        if(x.type==="polynomial"&&Array.isArray(x.coefficients)&&x.coefficients.length>0&&x.coefficients.length<=4&&x.coefficients.every(numeric))
          return {type:"polynomial",coefficients:x.coefficients.map(v=>limit(v,-1e5,1e5)),label:label(x.label||"",75)};
        if(x.type==="sine"&&["amplitude","frequency","phase","offset"].every(k=>numeric(x[k])))
          return {type:"sine",amplitude:limit(x.amplitude,-1e5,1e5),frequency:limit(x.frequency,-1e3,1e3),phase:limit(x.phase,-1e3,1e3),offset:limit(x.offset,-1e5,1e5),label:label(x.label||"",75)};
        return null;
      }).filter(Boolean);
      if(!series.length)return null;
      const domain=Array.isArray(data.domain)&&data.domain.length===2&&data.domain.every(numeric)&&data.domain[1]>data.domain[0]
        ?[limit(data.domain[0],-1e4,1e4),limit(data.domain[1],-1e4,1e4)]:[-10,10];
      if(domain[1]-domain[0]<0.001) return null;
      const range=Array.isArray(data.range)&&data.range.length===2&&data.range.every(numeric)&&data.range[1]>data.range[0]
        ?[limit(data.range[0],-1e6,1e6),limit(data.range[1],-1e6,1e6)]:[-10,10];
      if(range[1]-range[0]<0.001)return null;
      return {...common,data:{series,domain,range,note:label(data.note||"",240)}};
    }
    if(!["cube","sphere","torus","pyramid"].includes(data.shape))return null;
    return {...common,data:{shape:data.shape,caption:label(data.caption||"",200),yaw:sane(data.yaw,0,-Math.PI*4,Math.PI*4),pitch:sane(data.pitch,0.30,-Math.PI/2,Math.PI/2)}};
  }
  const fmt=n=>numeric(n)?Number(n.toPrecision(4)).toString():"—";
  function evaluate(series,x){
    if(!numeric(x)||!series)return NaN;
    if(series.type==="polynomial"){
      let y=0;
      for(let i=series.coefficients.length-1;i>=0;i--)y=y*x+series.coefficients[i];
      return Number.isFinite(y)?y:NaN;
    }
    if(series.type==="sine"){
      const y=series.offset+series.amplitude*Math.sin(series.frequency*x+series.phase);
      return Number.isFinite(y)?y:NaN;
    }
    return NaN;
  }
  function equation(s){
    if(s.label)return s.label;
    if(s.type==="sine")return "y = "+fmt(s.offset)+" + "+fmt(s.amplitude)+" sin("+fmt(s.frequency)+"x + "+fmt(s.phase)+")";
    const powers=["","x","x²","x³"];
    const terms=s.coefficients.map((value,i)=>({value,i})).filter(t=>t.value!==0).reverse();
    if(!terms.length)return "y = 0";
    let t="y = ";
    for(let j=0;j<terms.length;j++){
      const {value,i}=terms[j],mag=Math.abs(value),val=i&&mag===1?"":fmt(mag);
      t+=(j?(value<0?" − ":" + "):(value<0?"−":""))+val+powers[i];
    }
    return t;
  }
  function make(tag,cls,content){
    const el=document.createElement(tag);
    if(cls)el.className=cls;
    if(content!==undefined)el.textContent=String(content);
    return el;
  }
  function button(text,action,aria){
    const b=make("button","rich-widget-btn",text);b.type="button";b.setAttribute("aria-label",aria||text);b.addEventListener("click",action);return b;
  }
  function canvasView(card,aria){
    const wrap=make("div","rich-widget-viewport");
    const canvas=make("canvas","rich-widget-canvas");
    canvas.width=720;canvas.height=375;canvas.tabIndex=0;
    canvas.setAttribute("role","img");canvas.setAttribute("aria-label",aria);
    wrap.appendChild(canvas);card.appendChild(wrap);
    return canvas;
  }
  function comparison(card,w){
    const {items,metrics,note}=w.data;
    const region=make("div","rich-compare-region");region.setAttribute("role","region");region.setAttribute("aria-label","Comparison metrics");
    const table=make("table","rich-compare-table");
    const thead=make("thead");const header=make("tr");
    header.appendChild(make("th","rich-compare-metric","Metric"));
    for(const item of items){const th=make("th","rich-compare-name",item.name);th.scope="col";header.appendChild(th);}
    thead.appendChild(header);table.appendChild(thead);
    const tbody=make("tbody");
    for(const metric of metrics){
      const tr=make("tr");
      const th=make("th","",metric.label+(metric.unit?" ("+metric.unit+")":""));th.scope="row";tr.appendChild(th);
      const values=items.map(i=>i.values[metric.key]),nums=values.filter(numeric);
      const max=Math.max(0,...nums);
      const winner=(metric.higherIsBetter===null||!nums.length)?null:
        metric.higherIsBetter?Math.max(...nums):Math.min(...nums);
      for(const value of values){
        const td=make("td","rich-compare-value");
        if(value===undefined){td.textContent="—";}
        else {
          const span=make("span","",numeric(value)?fmt(value):value);
          if(numeric(value)&&winner!==null&&value===winner){span.className="rich-compare-leading";span.setAttribute("aria-label",span.textContent+" — best in row");}
          td.appendChild(span);
          if(numeric(value)&&max>0&&value>=0){
            const track=make("div","rich-compare-bar");track.setAttribute("aria-hidden","true");
            const fill=make("div","rich-compare-bar-fill");fill.style.width=fmt(value/max*100)+"%";
            track.appendChild(fill);td.appendChild(track);
          }
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);region.appendChild(table);card.appendChild(region);
    if(note)card.appendChild(make("p","rich-widget-note",note));
    return true;
  }
  const COLORS=["#54dafa","#d298ff","#ffcf85","#81eead","#ff9ba9"];
  function grid(ctx,w,h){
    ctx.clearRect(0,0,w,h);ctx.fillStyle="#071a2b";ctx.fillRect(0,0,w,h);
    ctx.strokeStyle="rgba(180,222,250,.12)";ctx.lineWidth=1;
    for(let i=1;i<10;i++){ctx.beginPath();ctx.moveTo(w*i/10,0);ctx.lineTo(w*i/10,h);ctx.stroke();}
    for(let i=1;i<6;i++){ctx.beginPath();ctx.moveTo(0,h*i/6);ctx.lineTo(w,h*i/6);ctx.stroke();}
  }
  function graph(card,w){
    const note=make("div","rich-equation-list");
    w.data.series.forEach((s,i)=>{const p=make("div","rich-equation",equation(s));p.style.borderColor=COLORS[i];note.appendChild(p);});
    card.appendChild(note);
    const canvas=canvasView(card,"Function graph; pan with pointer or arrow keys; zoom with plus or minus buttons");
    const controls=make("div","rich-widget-controls");
    const readout=make("span","rich-widget-readout");
    let {domain,range}=w.data;domain=domain.slice();range=range.slice();
    const original={domain:domain.slice(),range:range.slice()};
    function draw(){
      const ctx=canvas.getContext&&canvas.getContext("2d");if(!ctx)return;
      const width=canvas.width,height=canvas.height;
      grid(ctx,width,height);
      const xpos=x=>(x-domain[0])/(domain[1]-domain[0])*width;
      const ypos=y=>height-(y-range[0])/(range[1]-range[0])*height;
      ctx.strokeStyle="rgba(235,251,255,.65)";ctx.lineWidth=1.2;
      if(domain[0]<=0&&domain[1]>=0){ctx.beginPath();ctx.moveTo(xpos(0),0);ctx.lineTo(xpos(0),height);ctx.stroke();}
      if(range[0]<=0&&range[1]>=0){ctx.beginPath();ctx.moveTo(0,ypos(0));ctx.lineTo(width,ypos(0));ctx.stroke();}
      w.data.series.forEach((s,i)=>{
        ctx.strokeStyle=COLORS[i];ctx.lineWidth=2.4;ctx.beginPath();let active=false;
        for(let p=0;p<=720;p++){
          const x=domain[0]+(domain[1]-domain[0])*p/720, y=evaluate(s,x);
          const py=ypos(y);
          if(!Number.isFinite(y)||py< -height*3||py>height*4){active=false;continue;}
          if(!active)ctx.moveTo(p,py);else ctx.lineTo(p,py);
          active=true;
        }
        ctx.stroke();
      });
      readout.textContent="x: "+fmt(domain[0])+" … "+fmt(domain[1])+" · y: "+fmt(range[0])+" … "+fmt(range[1]);
    }
    function zoom(factor){
      for(const dim of [domain,range]){
        const mid=(dim[0]+dim[1])/2,half=(dim[1]-dim[0])*factor/2;
        dim[0]=mid-half;dim[1]=mid+half;
      }
      draw();
    }
    controls.append(button("−",()=>zoom(1.25),"Zoom out"),button("+",()=>zoom(0.8),"Zoom in"),button("Reset",()=>{
      domain=original.domain.slice();range=original.range.slice();draw();
    }),readout);
    card.appendChild(controls);
    let drag=null;
    canvas.addEventListener("pointerdown",ev=>{drag={x:ev.clientX,y:ev.clientY};canvas.setPointerCapture?.(ev.pointerId);});
    canvas.addEventListener("pointermove",ev=>{if(!drag)return;const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;
      const dx=(ev.clientX-drag.x)/rect.width*(domain[1]-domain[0]),dy=(ev.clientY-drag.y)/rect.height*(range[1]-range[0]);
      domain=domain.map(v=>v-dx);range=range.map(v=>v+dy);
      drag={x:ev.clientX,y:ev.clientY};draw();
    });
    const stop=()=>{drag=null;};canvas.addEventListener("pointerup",stop);canvas.addEventListener("pointercancel",stop);
    canvas.addEventListener("keydown",ev=>{const dx=(domain[1]-domain[0])*.08,dy=(range[1]-range[0])*.08;
      if(ev.key==="+"||ev.key==="=")zoom(.8);
      else if(ev.key==="-")zoom(1.25);
      else if(ev.key==="ArrowRight")domain=domain.map(v=>v+dx);
      else if(ev.key==="ArrowLeft")domain=domain.map(v=>v-dx);
      else if(ev.key==="ArrowUp")range=range.map(v=>v+dy);
      else if(ev.key==="ArrowDown")range=range.map(v=>v-dy);
      else return;ev.preventDefault();draw();
    });
    if(w.data.note)card.appendChild(make("p","rich-widget-note",w.data.note));
    draw();return true;
  }
  function mesh(shape){
    const vertices=[],edges=[];
    const add=(x,y,z)=>vertices.push([x,y,z])-1;
    const edge=(a,b)=>edges.push([a,b]);
    if(shape==="cube"||shape==="pyramid"){
      if(shape==="cube"){
        for(let x of [-1,1])for(let y of [-1,1])for(let z of [-1,1])add(x,y,z);
        for(let a=0;a<8;a++)for(let b=a+1;b<8;b++)if([a^b].some(v=>v===1||v===2||v===4))edge(a,b);
      }else{
        const a=[add(-1,-1,-1),add(1,-1,-1),add(1,-1,1),add(-1,-1,1)],top=add(0,1.4,0);
        for(let i=0;i<4;i++){edge(a[i],a[(i+1)%4]);edge(a[i],top);}
      }
    }else{
      const rings=shape==="sphere"?13:16,steps=24;
      for(let i=0;i<rings;i++){
        const phi=shape==="sphere"?(Math.PI*i/(rings-1)):(2*Math.PI*i/rings);
        for(let j=0;j<steps;j++){
          const theta=2*Math.PI*j/steps;
          if(shape==="sphere")add(Math.sin(phi)*Math.cos(theta),Math.cos(phi),Math.sin(phi)*Math.sin(theta));
          else add((1+.36*Math.cos(theta))*Math.cos(phi),.36*Math.sin(theta),(1+.36*Math.cos(theta))*Math.sin(phi));
        }
      }
      for(let i=0;i<rings;i++)for(let j=0;j<steps;j++){
        const a=i*steps+j;edge(a,i*steps+(j+1)%steps);
        if(shape==="torus"||i<rings-1)edge(a,((i+1)%rings)*steps+j);
      }
    }
    return {vertices,edges};
  }
  function project(point,yaw,pitch,zoom=1){
    const [x,y,z]=point,c=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
    const x1=x*c-z*s,z1=x*s+z*c,y1=y*cp-z1*sp,z2=y*sp+z1*cp;
    const p=3.8/(5+z2);return [x1*p*zoom,y1*p*zoom];
  }
  function model(card,w){
    const canvas=canvasView(card,w.data.shape+" rotatable 3D wireframe; drag to rotate; arrow keys also rotate");
    const control=make("div","rich-widget-controls"),readout=make("span","rich-widget-readout");
    let yaw=w.data.yaw,pitch=w.data.pitch,zoom=1;const geometry=mesh(w.data.shape);
    function draw(){
      const ctx=canvas.getContext&&canvas.getContext("2d");if(!ctx)return;
      grid(ctx,canvas.width,canvas.height);
      const xy=geometry.vertices.map(p=>project(p,yaw,pitch,zoom));
      ctx.strokeStyle="#5fe5ff";ctx.lineWidth=1.4;
      ctx.beginPath();
      for(const [a,b] of geometry.edges){
        ctx.moveTo(canvas.width/2+xy[a][0]*canvas.height*.38,canvas.height/2-xy[a][1]*canvas.height*.38);
        ctx.lineTo(canvas.width/2+xy[b][0]*canvas.height*.38,canvas.height/2-xy[b][1]*canvas.height*.38);
      }
      ctx.stroke();
      readout.textContent=w.data.shape+" · "+fmt(yaw)+" rad";
    }
    control.append(button("−",()=>{zoom=limit(zoom*.8,.45,2.5);draw();},"Zoom out"),button("+",()=>{zoom=limit(zoom*1.25,.45,2.5);draw();},"Zoom in"),button("Reset",()=>{yaw=w.data.yaw;pitch=w.data.pitch;zoom=1;draw();}),readout);card.appendChild(control);
    let last=null;
    canvas.addEventListener("pointerdown",ev=>{last={x:ev.clientX,y:ev.clientY};canvas.setPointerCapture?.(ev.pointerId);});
    canvas.addEventListener("pointermove",ev=>{if(!last)return;const dx=ev.clientX-last.x,dy=ev.clientY-last.y;
      yaw+=dx*.01;pitch=limit(pitch+dy*.01,-1.55,1.55);last={x:ev.clientX,y:ev.clientY};draw();
    });
    canvas.addEventListener("pointerup",()=>{last=null;});canvas.addEventListener("pointercancel",()=>{last=null;});
    canvas.addEventListener("keydown",ev=>{
      if(ev.key==="ArrowLeft")yaw-=.15;else if(ev.key==="ArrowRight")yaw+=.15;
      else if(ev.key==="ArrowUp")pitch=limit(pitch-.15,-1.55,1.55);
      else if(ev.key==="ArrowDown")pitch=limit(pitch+.15,-1.55,1.55);
      else return;ev.preventDefault();draw();
    });
    if(w.data.caption)card.appendChild(make("p","rich-widget-note",w.data.caption));
    draw();return true;
  }
  function render(card,raw){
    const w=normalize(raw);if(!w||!card||typeof card.appendChild!=="function")return false;
    try{
      if(w.kind==="comparison")return comparison(card,w);
      if(w.kind==="math-graph")return graph(card,w);
      if(w.kind==="model-3d")return model(card,w);
    }catch(err){
      card.appendChild(make("p","rich-widget-note","This widget could not be displayed."));
      return false;
    }
    return false;
  }
  const api=Object.freeze({normalize,evaluate,equation,mesh,project,render});
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.SwrlzRichWidgetsV284=api;
})(typeof window!=="undefined"?window:null);
