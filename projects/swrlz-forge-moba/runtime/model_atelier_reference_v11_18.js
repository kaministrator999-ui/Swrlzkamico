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
