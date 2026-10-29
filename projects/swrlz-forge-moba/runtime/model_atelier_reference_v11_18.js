// Saved native finish controls for the supplied portrait and hair-wrap close-up.
function atelierReferenceIrisPalette(p){
 return [new THREE.Color('#32243d'),new THREE.Color(p.irisPigments?.lower||'#f4b956'),new THREE.Color(p.irisPigments?.upper||'#ad4c6b')];
}
function atelierReferenceCrown(p){
 const g=atelierDetailSphere(p),a=g.attributes.position,c=g.attributes.color;
 for(let i=0;i<a.count;i++){
  const x=a.getX(i),y=a.getY(i),z=a.getZ(i),angle=Math.atan2(z,x),flow=angle*42+y*7;
  const ridge=Math.cos(flow),r=1+.005*p.hdFinish.relief*ridge*Math.sqrt(Math.max(0,1-y*y));
  a.setXYZ(i,x*r,y,z*r);if(c){const shade=.92+.07*ridge;c.setXYZ(i,c.getX(i)*shade,c.getY(i)*shade,c.getZ(i)*shade);}
 }
 g.computeVertexNormals();g.computeBoundingSphere();return g;
}
function atelierReferenceKnot(p){
 const along=p.meshDensity?.u||96,around=p.meshDensity?.v||64;
 const ring=new THREE.TorusGeometry(.73,.285,around,along),positions=[],colors=[],indices=[],uv=[];
 const base=new THREE.Color(p.color);
 const append=g=>{const a=g.attributes.position,n=positions.length/3,t=g.attributes.uv;
  for(let i=0;i<a.count;i++){const x=a.getX(i),y=a.getY(i),z=a.getZ(i)*.72;
   positions.push(x,y,z);uv.push(t?.getX(i)||0,t?.getY(i)||0);
   const weave=Math.cos(Math.atan2(y,x)*45+z*28)*Math.cos(z*42-x*7),col=base.clone().multiplyScalar(.90+.06*weave);colors.push(col.r,col.g,col.b);
  }for(let i=0;i<g.index.count;i++)indices.push(n+g.index.getX(i));g.dispose();};
 append(ring);
 // Two thin folded ends emerge from the lower knot; pointed cloth, not solid horns.
 for(const side of [-1,1]){
  const tail={path:[[side*.48,-.48,.05],[side*1.12,-.67,.07],[side*1.85,-.64,.04],[side*2.1,-.58,0]],radii:[.20,.22,.10,.003],meshDensity:{u:Math.max(6,Math.round(along/2)),v:Math.max(4,Math.round(around/2))},hdFinish:{style:'hair',relief:p.hdFinish.relief},color:p.color};
  append(atelierHDSweep(tail));
 }
 return atelierHDMesh(positions,colors,indices,uv);
}
function atelierReferenceFinishRefresh(){
 const p=partById(selection),deck=$m('IrisPigments');if(!deck)return;deck.hidden=p?.hdFinish?.style!=='iris';
 if(p){$m('IrisUpper').value=p.irisPigments?.upper||'#ad4c6b';$m('IrisLower').value=p.irisPigments?.lower||'#f4b956';}
}
function atelierReferenceFinishInstall(){
 $m('IrisApply').addEventListener('click',()=>{
  const p=partById(selection);if(p?.hdFinish?.style!=='iris')return;
  const next={...p,irisPigments:{upper:$m('IrisUpper').value,lower:$m('IrisLower').value}};
  if(!checkPart(next)){status('Iris pigments rejected: choose two valid colors.',true);return;}
  checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Iris colors saved. Undo and model JSON retain the pigments.');
 });
}

// Anatomical lower-leg contour: the front is +depth and the calf is -depth.
// Compact support leaves the thigh, knee ring and ankle attachment untouched.
function atelierReferenceLegContour(p,center,frame,s,c){
 const a=p.legAnatomy;if(!a)return new THREE.Vector3();
 const ankle=p.path[5][1],knee=(p.path[2][1]+p.path[3][1])/2,u=(center.y-ankle)/(knee-ankle);
 if(!Number.isFinite(u)||u<=0||u>=1)return new THREE.Vector3();
 const bell=v=>v<=0||v>=1?0:729/16*v**4*(1-v)**2;
 const bulk=bell(u),medial=-Math.sign(p.path[0][0])*c;
 // The medial head descends slightly lower than the lateral head.
 const heads=bell(u+medial*.055)*THREE.MathUtils.smoothstep(u,0,.15)*THREE.MathUtils.smoothstep(1-u,0,.15),back=Math.max(0,-s),front=Math.max(0,s);
 return frame.depth.clone().multiplyScalar(-a.calfFullness*heads*back**2-a.shinTaper*bulk*front**2)
  .addScaledVector(frame.right,c*a.calfFullness*.30*heads);
}
function atelierReferenceLegRefresh(){
 const p=partById(selection),deck=$m('LegAnatomy');if(!deck)return;
 deck.hidden=!(p?.kind==='loft'&&p.surfaceStyle==='anatomy-smooth'&&p.path?.length===6&&p.hdFinish?.style==='skin');
 if(!deck.hidden){$m('CalfFullness').value=p.legAnatomy?.calfFullness??0;$m('ShinTaper').value=p.legAnatomy?.shinTaper??0;}
}
function atelierReferenceLegInstall(){
 $m('LegApply').addEventListener('click',()=>{
  const p=partById(selection);if(!p)return;
  const next={...p,legAnatomy:{calfFullness:Number($m('CalfFullness').value),shinTaper:Number($m('ShinTaper').value)}};
  if(!checkPart(next)){status('Leg contour rejected: select a six-knot skin leg and use valid calf and shin values.',true);return;}
  checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Calf and shin contours saved. Undo and model JSON retain the anatomy.');
 });
}
