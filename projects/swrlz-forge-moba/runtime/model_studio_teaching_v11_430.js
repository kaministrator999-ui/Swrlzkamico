/* SE430_MODEL_TEACHING_START */
// Shared teaching vocabulary and controlled diagrams. This module owns no
// editor geometry, history, camera, renderer, event loop or downloaded asset.
(function(){
 const rows=[
  ['primitive','Create geometry','Start with a simple shape, then edit its surfaces.','Object','Choose Cube, Sphere, Cylinder or Cone, then Add.','Build a bag body from a cube; use cylinders for handles.','available','cube'],
  ['select','Select geometry','Choose exactly the object or components you want to change.','Object / vertex / edge / face','Choose an editing mode, then tap the model. Multi adds to the selection.','Select a bag flap without moving the rest of the bag.','available','select'],
  ['move','Move','Slide the selection along an axis without changing its shape.','Any selection','Select geometry; choose X, Y or Z, then drag or nudge.','Position a pocket on the front of a bag.','available','move'],
  ['rotate','Rotate','Turn the selection around its editing pivot.','Any selection','Select geometry, choose Rotate and an axis.','Tilt a strap loop to match the side of a bag.','available','rotate'],
  ['scale','Scale','Make the selection larger or smaller along an axis.','Any selection','Select geometry, choose Scale and an axis.','Make the bottom of a pouch wider than its top.','available','scale'],
  ['convert','Make mesh editable','Bake the visible supported surface into ordinary native vertices and triangles.','One supported object','Select one object in its rest pose, then convert. Review any UV/refinement warning first.','Turn a primitive cube into a mesh whose faces can be inset or extruded.','available','cube'],
  ['inset','Inset','Create a smaller face region inside a selected surface, leaving a connected border.','Convex connected coplanar faces','Convert to editable topology, switch to Face, tap a face, then Select flat region.','Make the rim of a backpack opening or the border of a recessed panel.','available','inset'],
  ['extrude','Extrude','Extend selected faces outward or push them inward, creating connected sidewalls.','Convex connected coplanar faces','Select a flat face region. Positive depth comes out; negative depth goes in. Preview before applying.','Keep the inner faces selected after Inset, then push them inward to form a hollow container. Re-expanding the coplanar region also selects its rim.','available','extrude'],
  ['deleteFaces','Delete faces','Remove selected polygon surfaces to make an opening.','Faces','Select an editable face region. Preview shows the opening before Apply.','Open the mouth of a container or remove an unwanted surface.','available','delete'],
  ['solidify','Solidify','Give one complete convex planar open surface real thickness with an inner layer and boundary walls.','Open editable surface','Select the entire convex planar open mesh in its rest pose. Curved surfaces and partial patches are not supported by this Solidify operation.','Give a flat flap or strap enough thickness to read from the side.','available','solidify'],
  ['splitEdge','Split edge','Insert a real midpoint on the selected edge and reconnect its adjacent triangles.','One edge','Choose Edge mode and select one editable edge.','Add a control point before bending the outline of a strap.','available','split'],
  ['subdivide','Subdivide','Split triangle surfaces into smaller connected triangles. This adds density, not automatic rounding.','Editable mesh','Convert the object first. Keep within the native vertex/triangle budget.','Add vertices before sculpting or controlled deformation.','available','subdivide'],
  ['fillHole','Fill boundary','Close one supported simple boundary loop with connected faces.','Boundary edge or eligible open mesh','Choose an eligible simple boundary. Complex or ambiguous openings are rejected.','Cap the end of a tube or close a small unwanted opening.','available','fill'],
  ['repairNormals','Repair normals','Make neighboring faces agree about their orientation; outward direction is not guessed.','Editable mesh','Use the topology audit and review the repaired preview. This does not fix every geometric defect.','Fix dark or inside-out patches after editing a mesh.','available','normals'],
  ['sculpt','Sculpt','Use a brush to push, smooth, flatten or inflate a supported surface.','Supported surface','Choose Sculpt, an appropriate brush and a manageable geometry density.','Soften the body of a leather bag after shaping its main volume.','existing','sculpt'],
  ['group','Group','Keep separate objects together while retaining their editable shapes and materials.','Multiple objects','Add objects to a selection, then make an assembly using the existing group tools.','Move a bag body, flap and clasp together.','existing','group'],
  ['mirror','Mirror / symmetry','Reflect geometry across a chosen axis.','Object or components','Sculpt X symmetry is available. General object/component mirror remains incomplete in this checkpoint.','Make matching left and right details.','incomplete','mirror'],
  ['bevel','Bevel','Replace a sharp corner with a small connecting surface.','Edges / vertices','General edge and vertex bevel is not implemented in this checkpoint. The diagram explains the operation; there is no fake Apply action.','Round a hard box edge without sculpting the entire surface.','incomplete','bevel'],
  ['merge','Merge vertices','Join selected vertices into one shared point.','Vertices','A general vertex weld/merge tool is not implemented in this checkpoint. Object Join combines meshes but does not weld their seams.','Weld the ends of a continuous strap.','incomplete','merge'],
  ['bridge','Bridge loops','Connect two boundary loops with a band of faces.','Two compatible edge loops','General loop bridging is not implemented in this checkpoint.','Join two open ends of a handle.','incomplete','bridge'],
  ['loopCut','Edge loop','Add a continuous ring of edges through a surface.','Compatible edge loop topology','Dedicated quad edge-loop cutting and sliding remain incomplete. Triangle subdivision is available separately.','Add a controllable bend near the base of a handle.','incomplete','subdivide'],
  ['reference','Reference images','Align a local picture with the view you are modeling from.','Reference image','Open References and choose the appropriate view, scale, opacity and alignment.','Compare front and side silhouettes while shaping a bag.','existing','reference']
 ];
 const entries=Object.freeze(Object.fromEntries(rows.map(([id,name,explanation,selection,requires,use,status,icon])=>[id,Object.freeze({id,name,summary:explanation,explanation,selection,requires,use,status,icon,limitation:status==='incomplete'?requires:''})])));
 const paths={
  cube:['M6 9 16 4 26 9 16 14Z','M6 9v14l10 5 10-5V9','M16 14v14'],
  select:['M5 4v21l6-6 5 9 4-2-5-9 8-1Z'],
  move:['M16 3v26M3 16h26','m12 7 4-4 4 4M12 25l4 4 4-4M7 12l-4 4 4 4M25 12l4 4-4 4'],
  rotate:['M25 11a10 10 0 1 0 0 10','M25 4v8h-8','M16 11v5l4 3'],
  scale:['M5 27 27 5M5 18v9h9M18 5h9v9','M5 5h8v8H5ZM19 19h8v8h-8Z'],
  inset:['M4 8 16 3 28 8 16 14Z','M4 8v16l12 5 12-5V8M16 14v15','M9 8 16 5 23 8 16 11Z'],
  extrude:['M4 18 15 13 27 18 16 24Z','M4 18v9l12 4 11-5v-8','M9 11 16 8 23 11 16 15Z','M9 11v8M23 11v8M16 15v8','M16 7V1m-3 3 3-3 3 3'],
  solidify:['M4 10 20 4 29 10 13 17Z','M4 10v6l9 7 16-7v-6M13 17v6','M6 24v6m-3-3 3 3 3-3M23 23v-5m-3 3 3-3 3 3'],
  subdivide:['M5 6h22v22H5ZM5 17h22M16 6v22','M5 6 27 28M16 6 27 17M5 17 16 28'],
  merge:['M4 6h6v6H4ZM22 6h6v6h-6Z','M7 14 14 21M25 14 18 21','M14 17v4h-4M18 17v4h4','M13 25h6v6h-6Z'],
  bevel:['M5 27V9l6-5h16v23Z','M5 9h6V4M11 9l16 8M11 9v18'],
  mirror:['M16 2v28','M4 9h7v15H4ZM28 9h-7v15h7Z','M7 5h5m-3-3 3 3-3 3M25 5h-5m3-3-3 3 3 3'],
  sculpt:['M3 26c5-1 5-9 12-5s9-1 14-4','M14 12 22 4l6 6-8 8-6-6Z','m14 12-4 10 10-4M10 22l-4 2'],
  split:['M4 26 27 5','M14 16h5v5h-5Z','M3 23h6v6H3ZM24 2h6v6h-6Z'],
  fill:['M4 9 16 3 28 9v15l-12 5L4 24Z','M9 12 16 9l7 3v8l-7 4-7-4Z','M9 12 23 20M23 12 9 20'],
  normals:['M4 23 16 17 28 23 16 29Z','M9 20V5m-3 3 3-3 3 3M22 20V5m-3 3 3-3 3 3'],
  delete:['M5 9 16 4 27 9 16 14Z','M5 9v15l11 5 11-5V9M16 14v15','m11 7 10 5M21 7l-10 5'],
  group:['M2 7h11v11H2ZM19 14h11v11H19ZM8 21h8v8H8Z','M4 2h24M28 2v7M4 2v3'],
  bridge:['M3 7h7v19H3ZM22 7h7v19h-7Z','M10 7h12M10 13h12M10 20h12M10 26h12'],
  reference:['M4 5h24v22H4Z','M7 23 14 14l5 6 4-4 3 7','M22 10h1']
 };
 function get(id){return entries[id]||entries.select;}
 function iconSVG(id,size=24){const e=get(id),lines=paths[e.icon]||paths.cube;return '<svg class="se430-icon" viewBox="0 0 32 32" width="'+Math.max(12,Math.min(80,Number(size)||24))+'" height="'+Math.max(12,Math.min(80,Number(size)||24))+'" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+lines.map(d=>'<path d="'+d+'"/>').join('')+'</svg>';}
 function drawIcon(c,id,cx=16,cy=16,size=24,color='#b5ffe1'){
  if(!c)return;const e=get(id);c.save();c.translate(cx-size/2,cy-size/2);c.scale(size/32,size/32);c.strokeStyle=color;c.lineWidth=1.8;c.lineCap='round';c.lineJoin='round';
  if(typeof Path2D==='function')for(const d of paths[e.icon]||paths.cube)c.stroke(new Path2D(d));
  else{c.beginPath();c.moveTo(6,9);c.lineTo(16,4);c.lineTo(26,9);c.lineTo(26,23);c.lineTo(16,28);c.lineTo(6,23);c.closePath();c.stroke();}
  c.restore();
 }
 function polygon(c,points,fill,stroke='#8dabbc'){c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();if(fill){c.fillStyle=fill;c.fill();}c.strokeStyle=stroke;c.lineWidth=1.5;c.stroke();}
 function line(c,p,color='#b8ffe3'){c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=color;c.lineWidth=1.6;c.stroke();}
 function arrow(c,a,b){line(c,[a,b],'#f3d18f');const d=Math.atan2(b[1]-a[1],b[0]-a[0]);line(c,[[b[0]-5*Math.cos(d-.55),b[1]-5*Math.sin(d-.55)],b,[b[0]-5*Math.cos(d+.55),b[1]-5*Math.sin(d+.55)]],'#f3d18f');}
 function slab(c,x,y,w,h,d,highlight=true){
  polygon(c,[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],'#324457');
  polygon(c,[[x+w,y],[x+w+d,y-d*.6],[x+w+d,y+h-d*.6],[x+w,y+h]],'#263343');
  polygon(c,[[x,y],[x+d,y-d*.6],[x+w+d,y-d*.6],[x+w,y]],highlight?'#387d78':'#455a70',highlight?'#b5ffe1':'#8dabbc');
 }
 function diagram(c,id,p){
  const x=16,y=40,w=50,h=42,d=16;
  if(id==='solidify'){slab(c,x,y+12,w,Math.max(2,28*p),d,true);arrow(c,[85,58],[85,58+22*p]);return;}
  if(id==='merge'){for(const a of [-1,1]){const px=50+a*(25*(1-p));c.fillStyle='#b7ffe2';c.beginPath();c.arc(px,58,4,0,Math.PI*2);c.fill();}if(p<.9){arrow(c,[22,76],[43,76]);arrow(c,[78,76],[57,76]);}return;}
  if(id==='mirror'){line(c,[[50,15],[50,100]],'#8e96b5');polygon(c,[[20,42],[41,31],[41,87],[20,73]],'#587d8b');if(p>0){c.globalAlpha=.25+.75*p;polygon(c,[[80,42],[59,31],[59,87],[80,73]],'#387d78','#b5ffe1');c.globalAlpha=1;}return;}
  if(id==='bevel'){const q=13*p;polygon(c,[[x+q,y],[x+w-q,y],[x+w,y+q],[x+w,y+h-q],[x+w-q,y+h],[x+q,y+h],[x,y+h-q],[x,y+q]],'#456073','#b5ffe1');if(p>.05){line(c,[[x+q,y],[x+q,y+h]],'#f3d18f');line(c,[[x+w-q,y],[x+w-q,y+h]],'#f3d18f');}return;}
  if(id==='sculpt'){c.beginPath();c.moveTo(12,82);c.bezierCurveTo(35,82,32,82-34*p,51,82-34*p);c.bezierCurveTo(70,82-34*p,65,82,90,82);c.strokeStyle='#b5ffe1';c.lineWidth=2;c.stroke();c.beginPath();c.arc(51,52,15,0,Math.PI*2);c.strokeStyle='#f3d18f';c.stroke();return;}
  if(id==='move'||id==='rotate'||id==='scale'){c.save();c.translate(id==='move'?p*17:0,id==='move'?-p*9:0);if(id==='rotate'){c.translate(50,58);c.rotate(p*.6);c.translate(-50,-58);}if(id==='scale'){c.translate(50,58);c.scale(1+p*.3,1+p*.3);c.translate(-50,-58);}slab(c,x,y,w,h,d);c.restore();return;}
  slab(c,x,y,w,h,d,id!=='deleteFaces');
  if(id==='extrude'){
   const shift=27*p,top=[[x,y-shift],[x+d,y-d*.6-shift],[x+w+d,y-d*.6-shift],[x+w,y-shift]];
   polygon(c,[[x,y],[x+w,y],[x+w,y-shift],[x,y-shift]],'#387d78','#b5ffe1');
   polygon(c,[[x+w,y],[x+w+d,y-d*.6],[x+w+d,y-d*.6-shift],[x+w,y-shift]],'#286962','#b5ffe1');polygon(c,top,'#529b8c','#c0ffe8');if(p>.05)arrow(c,[87,y+6],[87,y-shift]);
  }else if(id==='inset'){
   const q=12*p,top=[[x+q,y-1],[x+d+q,y-d*.6+q*.4],[x+w+d-q,y-d*.6+q*.4],[x+w-q,y-1]];if(p>.01)polygon(c,top,'#68bca5','#e8ffdd');
  }else if(['subdivide','splitEdge','loopCut'].includes(id)){
   if(p>.15){line(c,[[x+w*.5,y],[x+w*.5,y+h]]);line(c,[[x,y+h*.5],[x+w,y+h*.5]]);}if(p>.55){line(c,[[x,y],[x+w,y+h]]);line(c,[[x+w*.5,y],[x+w,y+h*.5]]);line(c,[[x,y+h*.5],[x+w*.5,y+h]]);}
  }else if(id==='deleteFaces'||id==='fillHole'){
   const alpha=id==='deleteFaces'?p:1-p;c.globalAlpha=alpha;polygon(c,[[x+8,y+8],[x+w-8,y+8],[x+w-8,y+h-8],[x+8,y+h-8]],'#10202c','#f3d18f');c.globalAlpha=1;
  }else if(id==='repairNormals'){
   arrow(c,[32,40],[32,20]);arrow(c,[59,40],[59,40+(p<.5?18:-20)]);
  }
 }
 function drawDemo(c,id,t=0,width=320,height=150){
  if(!c)return;const e=get(id),w=Math.max(180,Number(width)||320),h=Math.max(100,Number(height)||150);c.save();c.clearRect(0,0,w,h);c.fillStyle='#101b2a';c.fillRect(0,0,w,h);
  const cycle=Number.isFinite(t)?(.5-.5*Math.cos((t%3)/3*Math.PI*2)):.5;
  for(let i=0;i<3;i++){
   const cell=w/3,scale=Math.min((cell-10)/100,(h-32)/112);c.save();c.translate(i*cell+(cell-100*scale)/2,8);c.scale(scale,scale);diagram(c,e.id,i===0?0:i===2?1:cycle);c.restore();
   c.fillStyle=i===1?'#b5ffe1':'#b9c8d8';c.textAlign='center';c.textBaseline='bottom';c.font='600 '+Math.max(10,Math.min(12,w/28))+'px system-ui,sans-serif';c.fillText(['Before','During','After'][i],i*cell+cell/2,h-7);
  }
  c.restore();
 }
 window.SWYRL_MODEL_TEACHING=Object.freeze({get,list:()=>Object.values(entries),iconSVG,drawIcon,drawDemo});
})();
/* SE430_MODEL_TEACHING_END */
