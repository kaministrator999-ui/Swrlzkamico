// Articulated paper cutouts. Pose pivots, facial ink and silhouette thickness
// share the native story clock; the original atlas pixels remain immutable.
const RIG_SLOTS={torso:0,pelvis:1,head:2,cape:3,leftUpperArm:4,leftForearm:5,leftHand:6,staff:7,rightUpperArm:8,rightForearm:9,rightHand:10,quill:11,leftUpperLeg:12,leftLowerLeg:13,leftFoot:14,rightUpperLeg:15,rightLowerLeg:16,rightFoot:17,grimoire:18,magic:19};
// Character-specific artwork anchors: a skull cuff and a human glove do not share a grip.
const RIG_REST_ROWS={"kami":[["torso",null,0,0.35,0.02,1.8,2.02,0,-0.51,0],["pelvis","torso",0,-0.88,0.07,2,2.18,0,-0.79,0],["head","torso",0,0.52,0.21,1.8,1.75,0,0.7,0],["cape","torso",0,0.45,-0.2,2.55,3.08,0,-1.23,0],["leftUpperArm","torso",-0.54,0.16,0.09,0.86,1.16,0.075,-0.418,-0.16],["leftForearm","leftUpperArm",0.282,-0.764,0.035,0.73,1.03,0.108,-0.353,-1.3],["leftHand","leftForearm",0.245,-0.725,0.065,0.70,0.68,0.197,0.18,3.0307963267948965],["rightUpperArm","torso",0.69,0.25,0.1,0.82,1.17,0.014,-0.435,0.18],["rightForearm","rightUpperArm",-0.048,-0.878,0.035,0.6,1.03,-0.082,-0.35,0.7],["rightHand","rightForearm",-0.03,-0.713,0.075,0.72,0.62,0.237,0.166,-1.9],["leftUpperLeg","pelvis",-0.37,-0.16,-0.04,0.92,1.05,0,-0.43,0],["leftLowerLeg","leftUpperLeg",0,-0.83,0.025,0.51,0.98,0,-0.4,0],["leftFoot","leftLowerLeg",0,-0.81,0.035,0.54,0.416,-0.1,-0.12,0],["rightUpperLeg","pelvis",0.37,-0.16,-0.04,0.88,1.03,0,-0.42,0],["rightLowerLeg","rightUpperLeg",0,-0.82,0.025,0.53,0.98,0,-0.4,0],["rightFoot","rightLowerLeg",0,-0.81,0.035,0.48,0.403,0.08,-0.12,0],["staff","leftHand",0.291,0.264,-0.055,1.10,1.50,0,1.65,-1.5707963267948966],["quill","rightHand",0.419,0.263,0.08,0.46,1.2,0.16,0.5,0.82],["grimoire","leftHand",-0.25,0.25,0.06,2.05,1.65,-0.4,0.2,0.77]],"swyrlz":[["torso",null,0,0.35,0.02,1.75,1.99,0,-0.5,0],["pelvis","torso",0,-0.86,0.06,1.91,2.16,0,-0.77,0],["head","torso",0,0.32,0.2,2.5,2.35,0,0.7,0],["cape","torso",0,0.3,-0.18,2.37,2.85,0,-1.11,0],["leftUpperArm","torso",-0.65,0.2,0.075,0.78,1.06,0.234,-0.327,-0.62],["leftForearm","leftUpperArm",0.414,-0.648,0.03,0.79,0.98,-0.27,-0.333,0.8],["leftHand","leftForearm",-0.383,-0.635,0.06,0.76,0.56,-0.182,0.034,0.9],["rightUpperArm","torso",0.65,0.2,0.075,0.8,1.07,-0.022,-0.39,0.35],["rightForearm","rightUpperArm",-0.076,-0.724,0.03,0.78,1,0.261,-0.306,-0.35],["rightHand","rightForearm",0.387,-0.618,0.075,0.68,0.66,0.167,0.152,-1.7],["leftUpperLeg","pelvis",-0.34,-0.15,-0.035,0.89,1.01,0,-0.4,0],["leftLowerLeg","leftUpperLeg",0,-0.79,0.025,0.46,1,0,-0.41,0],["leftFoot","leftLowerLeg",0,-0.82,0.035,0.57,0.413,-0.13,-0.12,0],["rightUpperLeg","pelvis",0.34,-0.15,-0.035,0.84,1.01,0,-0.4,0],["rightLowerLeg","rightUpperLeg",0,-0.79,0.025,0.49,1,0,-0.41,0],["rightFoot","rightLowerLeg",0,-0.82,0.035,0.64,0.45,0.13,-0.12,0],["staff","leftHand",0.291,0.264,0.08,1.24,1.73,0,2.05,2.9],["quill","rightHand",0.419,0.263,0.08,0.46,1.2,0.04,0.5,0.82],["grimoire","leftHand",-0.306,0.084,0.06,1.73,1.67,-0.45,0.4,-1.23]]};
const RIG_REST_LAYOUTS=Object.freeze(Object.fromEntries(Object.entries(RIG_REST_ROWS).map(([c,rows])=>[c,Object.freeze(Object.fromEntries(rows.map(([id,parent,x,y,z,width,height,artX,artY,rotationZ])=>[id,Object.freeze({x,y,width,height,artX,artY,rotationZ})])))])));
function rigVisualSignature(cfg,character){return JSON.stringify([cfg.enabled,cfg.asset,cfg.thickness,cfg.depth,cfg.layout,character?socketModel().characters[character]:null]);}
function rigAtlasCells(texture,character){
  if(texture.userData.rigCells?.[character])return texture.userData.rigCells[character];
  const image=texture.image;if(!image?.width)return null;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;
  texture.userData.rigPixels=pixels;
  const bundledKami=character==='kami'&&rigModel().characters[character].asset==='assets/anime/kami-rig.png';
  const y0=bundledKami?75:0,height=bundledKami?1320:image.height,cells=[];
  for(let slot=0;slot<20;slot++){
    const l=Math.floor(slot%4*image.width/4),r=Math.floor((slot%4+1)*image.width/4),t=Math.floor(y0+Math.floor(slot/4)*height/5),b=Math.floor(y0+(Math.floor(slot/4)+1)*height/5);
    let x0=r,y1=b,x1=l,y2=t;
    for(let y=t;y<b;y++)for(let x=l;x<r;x++)if(pixels[(y*image.width+x)*4+3]>20){x0=Math.min(x0,x);x1=Math.max(x1,x+1);y1=Math.min(y1,y);y2=Math.max(y2,y+1);}
    if(x1<=x0){x0=l;x1=r;y1=t;y2=b;}
    x0=Math.max(l,x0-2);x1=Math.min(r,x1+2);y1=Math.max(t,y1-2);y2=Math.min(b,y2+2);
    // Keep the calf on its own cutout; the foot card owns the instep and sole.
    if((slot===14||slot===17)&&rigModel().characters[character].asset==='assets/anime/'+character+'-rig.png'){const trim=character==='kami'?(slot===14?.35:.38):(slot===14?.45:.40);y1+=Math.round((y2-y1)*trim);}
    const size=48,mask=[];
    for(let j=0;j<size;j++)for(let i=0;i<size;i++){
      const x=Math.min(x1-1,Math.floor(x0+(i+.5)*(x1-x0)/size)),y=Math.min(y2-1,Math.floor(y1+(j+.5)*(y2-y1)/size));
      mask.push(pixels[(y*image.width+x)*4+3]>40);
    }
    cells.push({x0,x1,y0:y1,y1:y2,width:image.width,height:image.height,mask,size});
  }
  texture.userData.rigCells??={};texture.userData.rigCells[character]=cells;return cells;
}
function rigGeometry(cell,w,h,thickness,segments=16){
  const plane=new THREE.PlaneGeometry(w,h,segments,segments),uv=plane.getAttribute('uv');
  if(cell)for(let i=0;i<uv.count;i++)uv.setXY(i,(cell.x0+uv.getX(i)*(cell.x1-cell.x0))/cell.width,1-(cell.y0+(1-uv.getY(i))*(cell.y1-cell.y0))/cell.height);
  uv.needsUpdate=true;
  const vertices=[],n=cell?.size||1,mask=cell?.mask||[true];
  const inside=(x,y)=>x>=0&&y>=0&&x<n&&y<n&&mask[y*n+x];
  const quad=(a,b)=>{const [x0,y0]=a,[x1,y1]=b,z=thickness/2;vertices.push(x0,y0,z,x1,y1,z,x1,y1,-z,x0,y0,z,x1,y1,-z,x0,y0,-z);};
  for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(inside(x,y)){
    const l=(x/n-.5)*w,r=((x+1)/n-.5)*w,t=(.5-y/n)*h,b=(.5-(y+1)/n)*h;
    if(!inside(x-1,y))quad([l,b],[l,t]);if(!inside(x+1,y))quad([r,t],[r,b]);
    if(!inside(x,y-1))quad([l,t],[r,t]);if(!inside(x,y+1))quad([r,b],[l,b]);
  }
  const edge=new THREE.BufferGeometry();edge.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));edge.computeVertexNormals();return {plane,edge};
}
function rigMakePart(texture,cell,width,height,thickness,id){
  const group=new THREE.Group(),geometry=rigGeometry(cell,width,height,thickness,id==='head'?64:16);
  const front=new THREE.Mesh(geometry.plane,new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide,transparent:true,alphaTest:.025,depthWrite:true,fog:false,toneMapped:false}));
  front.position.z=thickness/2;front.name=id+' · painted front';
  const back=new THREE.Mesh(geometry.plane.clone(),front.material.clone());back.position.z=-thickness/2;back.material.color.set('#8a643a');back.name=id+' · paper back';
  const edge=new THREE.Mesh(geometry.edge,new THREE.MeshBasicMaterial({color:'#b68a4f',side:THREE.DoubleSide,transparent:true,fog:false,toneMapped:false}));edge.name=id+' · cut paper edge';
  group.add(front,back,edge);group.userData.rigPart=id;group.userData.rigSize={width,height};group.userData.rigCell=cell;
  for(const mesh of [front,back,edge])mesh.userData.rigRestVertices=mesh.geometry.getAttribute('position').array.slice();
  return group;
}
// Surface relief leaves every attachment point in the paper's joint plane.
// Moving a keyed surface outwards must never translate its connected skeleton.
function rigPartRelief(part,amount,pins){
  if(!part||part.userData.rigRelief===amount)return;part.userData.rigRelief=amount;part.userData.rigReliefPins=pins;
  for(const mesh of part.children.filter(child=>child.userData.rigRestVertices)){
    const attribute=mesh.geometry.getAttribute('position'),rest=mesh.userData.rigRestVertices;
    for(let i=0;i<attribute.count;i++){
      const x=rest[i*3],y=rest[i*3+1],distance=Math.min(...pins.map(point=>Math.hypot(x-point.x,y-point.y)));
      const weight=Math.min(1,distance/.22)**2;
      attribute.setZ(i,rest[i*3+2]+amount*weight);
    }
    attribute.needsUpdate=true;mesh.geometry.computeBoundingBox();mesh.geometry.computeBoundingSphere();
  }
}
function rigPlaneSurfaceZ(mesh,x,y){
  const geometry=mesh.geometry,parameters=geometry.parameters;
  const nx=parameters.widthSegments||1,ny=parameters.heightSegments||1,attribute=geometry.getAttribute('position');
  const center=geometry.userData.rigPlaneCenter||[0,0];
  const u=THREE.MathUtils.clamp(((x-center[0])/parameters.width+.5)*nx,0,nx),v=THREE.MathUtils.clamp((.5-(y-center[1])/parameters.height)*ny,0,ny);
  const ix=Math.min(nx-1,Math.floor(u)),iy=Math.min(ny-1,Math.floor(v)),fu=u-ix,fv=v-iy;
  const a=iy*(nx+1)+ix,b=(iy+1)*(nx+1)+ix,c=b+1,d=a+1;
  const z=fu+fv<=1?attribute.getZ(a)*(1-fu-fv)+attribute.getZ(d)*fu+attribute.getZ(b)*fv:
    attribute.getZ(c)*(fu+fv-1)+attribute.getZ(b)*(1-fu)+attribute.getZ(d)*(1-fv);
  return mesh.position.z+z;
}
function rigSurfacePoint(part,x,y){
  const front=part.children.find(child=>child.name?.endsWith('painted front'));
  return new THREE.Vector3(x,y,rigPlaneSurfaceZ(front,x,y));
}
function rigSocketWorld(rig,id,point){
  const pivot=rig.joints[id],part=pivot.userData.part,attach=pivot.userData.rigSocketPart.attach,depth=rigModel().characters[rig.character].depth;
  return part?part.localToWorld(new THREE.Vector3(point.x,point.y,point.z*depth)):
    pivot.localToWorld(new THREE.Vector3(point.x-attach.x,point.y-attach.y,(point.z-attach.z)*depth));
}
function rigProjectedWorld(point){const p=point.clone().project(perspectiveCamera);return [(p.x+1)/2,(1-p.y)/2,p.z];}
function rigBuildSocketGuides(group){
  const rig=group.userData.rig;rig.guides=[];
  for(const [id,pivot] of Object.entries(rig.joints)){
    if(!pivot.userData.part)continue;
    const owner=pivot.userData.rigSocketPart;
    for(const [name,point] of [['attach',owner.attach],...Object.entries(owner.sockets)]){
      const marker=new THREE.Mesh(new THREE.SphereGeometry(name==='attach'?.04:.027,8,6),new THREE.MeshBasicMaterial({color:name==='attach'?'#77e8fc':'#ffd374',transparent:true,opacity:.95,depthTest:false,depthWrite:false,toneMapped:false}));
      marker.name=rig.character+' · '+id+' · '+name+' socket guide';marker.renderOrder=1000;
      marker.position.set(point.x-owner.attach.x,point.y-owner.attach.y,(point.z-owner.attach.z)*rigModel().characters[rig.character].depth);
      rig.guides.push({id,name,pivot,marker});
    }
  }
}
function rigUpdateSocketGuides(group){
  const rig=group.userData.rig;if(!rig?.guides)return;
  const shown=typeof socketEditorGuides==='function'&&socketEditorGuides(rig.character);
  for(const guide of rig.guides){if(shown){if(guide.marker.parent!==guide.pivot)guide.pivot.add(guide.marker);}else guide.marker.removeFromParent();}
}
function rigFaceRelief(face,amount,pins,part){
  if(face.relief===amount)return;face.relief=amount;
  const attribute=face.mesh.geometry.getAttribute('position'),rest=face.restVertices;
  for(let i=0;i<attribute.count;i++){
    const x=rest[i*3]+face.fit.x,y=rest[i*3+1]+face.fit.y;
    const front=part.children.find(child=>child.name?.endsWith('painted front'));
    attribute.setZ(i,rigSurfacePoint(part,x,y).z-front.position.z);
  }
  attribute.needsUpdate=true;face.mesh.geometry.computeBoundingBox();face.mesh.geometry.computeBoundingSphere();
}
// These footprints sit inside the blank skin on the bundled head cards. Kami's
// old placement crossed the chin into the neck; the skull has its own anatomy.
const RIG_FACE_FIT={kami:{x:-.10,y:-.165,width:.70,height:.45},swyrlz:{x:.065,y:-.635,width:.78,height:.67}};
function rigFaceSurface(character,layout,headPart){
  const canvas=document.createElement('canvas');canvas.width=256;canvas.height=192;
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const original=RIG_FACE_FIT[character],sx=layout.width/(character==='kami'?1.8:2.5),sy=layout.height/(character==='kami'?1.75:2.35);
  const fit={x:original.x*sx,y:original.y*sy,width:original.width*sx,height:original.height*sy};
  // Use the head's exact triangles. Cropped canvas UVs leave the rest of the
  // card transparent, while every facial fragment stays .02 above its skin.
  const geometry=headPart.children[0].geometry.clone(),positions=geometry.getAttribute('position'),uv=geometry.getAttribute('uv');
  for(let i=0;i<positions.count;i++){
    const x=positions.getX(i),y=positions.getY(i);
    positions.setXYZ(i,x-fit.x,y-fit.y,0);uv.setXY(i,(x-fit.x)/fit.width+.5,(y-fit.y)/fit.height+.5);
  }
  geometry.userData.rigPlaneCenter=[-fit.x,-fit.y];positions.needsUpdate=true;uv.needsUpdate=true;
  const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({map:texture,transparent:true,alphaTest:.01,depthWrite:true,side:THREE.DoubleSide,fog:false,toneMapped:false}));
  mesh.name=character+' · animated eyes brows and mouth';mesh.userData.rigFace=true;
  return {mesh,texture,canvas,fit,hash:null,applied:null,restVertices:mesh.geometry.getAttribute('position').array.slice(),relief:null};
}
function rigPaintFace(face,character,sample,time){
  const s={...sample},cue=storyBeat(time)?.cue||'';
  const speaking=s.speech&&(character==='kami'?/^KAMI\b/i:/^[§$]?WYRLZ\b/i).test(cue.trim());
  // Modest jaw motion keeps speech within the painted face and below the nose.
  if(speaking)s.mouth=Math.max(s.mouth,.12+.38*(.5+.5*Math.sin(time*31)));
  const hash=[s.expression,...Object.keys(RIG_FACE_BOUNDS).map(k=>Math.round(s[k]*50))].join(':');
  face.applied=s;if(face.hash===hash)return;face.hash=hash;
  const c=face.canvas.getContext('2d');c.clearRect(0,0,256,192);
  const skull=character==='swyrlz',happy=s.expression==='happy',sad=s.expression==='sad',determined=s.expression==='determined',surprised=s.expression==='surprised';
  const opening=Math.max(0,(1-s.blink)*(surprised?1.05:determined?.53:happy?.72:.86));
  c.lineCap='round';c.lineJoin='round';
  for(const side of [-1,1]){
    const x=128+side*44,y=67,ew=skull?29:28,eh=(skull?27:17)*opening;
    if(opening<.075){
      c.strokeStyle=skull?'#3b2418':'#583b2d';c.lineWidth=skull?4:3;
      c.beginPath();c.moveTo(x-ew,y-1);c.quadraticCurveTo(x,y+(happy?8:4),x+ew,y-1);c.stroke();
    }else if(skull){
      // Dark hollow sockets and warm embers belong to a skull, rather than
      // the human sclera and black pupils used on Kami's anime face.
      c.save();c.translate(x,y);c.rotate(side*(determined?-.10:.06));
      c.fillStyle='#281b14';c.strokeStyle='#755035';c.lineWidth=2.4;
      c.beginPath();c.ellipse(0,0,ew,eh,0,0,Math.PI*2);c.fill();c.stroke();
      c.clip();const gx=s.gazeX*9,gy=s.gazeY*7;
      const glow=c.createRadialGradient(gx,gy,1,gx,gy,12);glow.addColorStop(0,'#fff3b1');glow.addColorStop(.3,'#ffd66c');glow.addColorStop(.62,'#db8c27');glow.addColorStop(1,'rgba(166,86,18,0)');
      c.fillStyle=glow;c.beginPath();c.ellipse(gx,gy,12,Math.max(3,Math.min(13,eh*.7)),0,0,Math.PI*2);c.fill();
      c.restore();
    }else{
      // Tapered corners, one dark upper lash and a fine lower lid prevent the
      // full ellipse outlines from reading as round spectacles.
      const tilt=side*(determined?-3:sad?2:0),eyePath=()=>{
        c.beginPath();c.moveTo(x-ew,y+tilt);c.bezierCurveTo(x-ew*.42,y-eh,x+ew*.35,y-eh,x+ew,y-tilt);
        c.bezierCurveTo(x+ew*.4,y+eh*.55,x-ew*.4,y+eh*.62,x-ew,y+tilt);c.closePath();
      };
      eyePath();c.fillStyle='#f4dec8';c.fill();c.save();c.clip();
      const gx=x+s.gazeX*9,gy=y+s.gazeY*6;
      const iris=c.createLinearGradient(0,y-eh,0,y+eh);iris.addColorStop(0,'#6e451d');iris.addColorStop(.5,'#b17a31');iris.addColorStop(1,'#e1ad56');
      c.fillStyle=iris;c.beginPath();c.ellipse(gx,gy,10,Math.max(3,eh*.98),0,0,Math.PI*2);c.fill();
      c.fillStyle='#342318';c.beginPath();c.ellipse(gx,gy,3.7,Math.max(2,eh*.68),0,0,Math.PI*2);c.fill();
      c.fillStyle='#fff0ce';c.beginPath();c.ellipse(gx-3,gy-4,2.1,2.8,0,0,Math.PI*2);c.fill();c.restore();
      c.strokeStyle='#573a2a';c.lineWidth=3.3;c.beginPath();c.moveTo(x-ew,y+tilt);c.bezierCurveTo(x-ew*.42,y-eh,x+ew*.35,y-eh,x+ew,y-tilt);c.stroke();
      c.strokeStyle='#90684c';c.lineWidth=1.1;c.beginPath();c.moveTo(x-ew*.8,y+eh*.25);c.quadraticCurveTo(x,y+eh*.7,x+ew*.85,y+eh*.2);c.stroke();
      c.strokeStyle='#694c39';c.lineWidth=1.2;c.beginPath();c.moveTo(x-ew*.78,y-eh-4);c.quadraticCurveTo(x,y-eh-7,x+ew*.6,y-eh-4);c.stroke();
    }
    const browY=38-s.brow*6-(surprised?6:0),tilt=determined?-side*6:sad?side*6:0;
    c.strokeStyle=skull?'#8b633b':'#6f4d37';c.lineWidth=skull?2.2:2.7;c.beginPath();
    c.moveTo(x-ew*.8,browY-tilt);c.quadraticCurveTo(x,browY-3,x+ew*.76,browY+tilt);c.stroke();
  }
  if(skull){
    c.fillStyle='#39271b';c.beginPath();c.moveTo(127,102);c.quadraticCurveTo(121,107,119,116);c.quadraticCurveTo(125,115,128,118);c.quadraticCurveTo(131,114,137,115);c.lineTo(130,103);c.closePath();c.fill();
  }else{
    c.strokeStyle='#bd8a68';c.lineWidth=1.7;c.beginPath();c.moveTo(127,101);c.quadraticCurveTo(123,109,128,111);c.lineTo(132,110);c.stroke();
  }
  const smile=s.smile+(happy?.6:sad?-.4:0),mouthY=143;
  c.strokeStyle=skull?'#714b2f':'#945a43';c.lineWidth=skull?2.4:1.9;
  if(s.mouth>.06){
    const mouthWidth=skull?20:15+(surprised?2:0),mouthHeight=1.5+s.mouth*(skull?12:9);
    c.fillStyle=skull?'#332219':'#693c2c';c.beginPath();c.ellipse(128,mouthY,mouthWidth,mouthHeight,0,0,Math.PI*2);c.fill();c.stroke();
    if(skull){
      c.strokeStyle='#d5b583';c.lineWidth=2;for(let x=116;x<=140;x+=8){c.beginPath();c.moveTo(x,mouthY-mouthHeight+1);c.lineTo(x,mouthY-mouthHeight+4);c.moveTo(x,mouthY+mouthHeight-1);c.lineTo(x,mouthY+mouthHeight-3);c.stroke();}
    }else if(s.mouth>.24){
      c.fillStyle='#c59173';c.beginPath();c.ellipse(128,mouthY+mouthHeight*.55,8,Math.max(1,mouthHeight*.23),0,0,Math.PI*2);c.fill();
    }
  }else{
    c.beginPath();c.moveTo(skull?105:111,mouthY);c.quadraticCurveTo(128,mouthY+smile*(skull?10:7),skull?151:145,mouthY);c.stroke();
    if(skull){c.lineWidth=1.6;for(let x=112;x<=144;x+=8){c.beginPath();c.moveTo(x,mouthY-2);c.lineTo(x,mouthY+4);c.stroke();}}
  }
  face.texture.needsUpdate=true;
}
function rigBuildVisual(visual,character){
  const cfg=rigModel().characters[character],sockets=socketModel().characters[character],texture=storyTexture(cfg.asset),cells=rigAtlasCells(texture,character);
  const group=new THREE.Group();group.userData.storyVisual=visual;group.userData.popupHinge=true;
  const hinge=new THREE.Group();hinge.userData.storyCastHinge=true;hinge.position.y=-visual.height/2;group.add(hinge);
  const body=new THREE.Group(),factor=character==='swyrlz'?.53:1;body.scale.setScalar(factor);body.position.y=2.95*factor;hinge.add(body);
  const joints={},parts=[];
  for(const [id,parent,_x,_y,z] of RIG_REST_ROWS[character]){
    const fit=cfg.layout[id],{x,y,width:w,height:h,artX:mx,artY:my,rotationZ:rz}=fit;
    const socketPart=sockets.parts[id],attach=socketPart.attach,connection=sockets.connections[id];
    const rest=new THREE.Group();
    if(connection?.connected){const owner=sockets.parts[connection.parent],target=owner.sockets[connection.socket];
      rest.position.set(target.x-owner.attach.x,target.y-owner.attach.y,(target.z-owner.attach.z)*cfg.depth);
    }else rest.position.set(x,y,z*cfg.depth);
    rest.rotation.z=rz;rest.userData.rigBaseDepth=rest.position.z/cfg.depth;
    (parent?joints[parent]:body).add(rest);const pose=new THREE.Group();pose.name=character+' · '+id+' pivot';rest.add(pose);joints[id]=pose;pose.userData.rigParent=parent;
    pose.userData.rigSocketPart=socketPart;pose.userData.rigConnection=connection;
    const omit=character==='kami'?id==='grimoire':id==='staff'||id==='quill';
    if(!omit){const part=rigMakePart(texture,cells?.[RIG_SLOTS[id]],w,h,cfg.thickness,id);part.position.set(-attach.x,-attach.y,-attach.z*cfg.depth);pose.add(part);pose.userData.part=part;parts.push(part);}
  }
  if(character==='kami'){
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.045,.045,3.25,12),new THREE.MeshBasicMaterial({color:'#74502b',transparent:true,toneMapped:false}));
    shaft.position.set(0,-.625,0);shaft.name='Kami · socketed wooden staff shaft';joints.staff.add(shaft);joints.staff.userData.gripShaft=shaft;
    const ferrule=new THREE.Mesh(new THREE.CylinderGeometry(.067,.052,.15,12),new THREE.MeshBasicMaterial({color:'#cb9a42',transparent:true,toneMapped:false}));
    ferrule.position.set(0,.96,0);ferrule.name='Kami · staff head ferrule';joints.staff.add(ferrule);joints.staff.userData.gripFerrule=ferrule;
  }else{const magic=rigMakePart(texture,cells?.[19],.8,1.1,cfg.thickness,'magic');magic.position.set(-.4,1.05,.06);joints.grimoire.add(magic);parts.push(magic);}
  // Pin the neutral soles to the book hinge after fitting either body. Pose keys
  // can still lift a foot; changing one piece does not rescale the whole puppet.
  group.updateWorldMatrix(true,true);let sole=Infinity;
  for(const id of ['leftFoot','rightFoot']){const part=joints[id].userData.part;for(const p of rigInkPoints(part,body,1))sole=Math.min(sole,p[1]);}
  if(Number.isFinite(sole))body.position.y=-sole*factor;
  const face=rigFaceSurface(character,cfg.layout.head,joints.head.userData.part);face.mesh.position.set(face.fit.x,face.fit.y,cfg.thickness/2+.02);joints.head.userData.part.add(face.mesh);
  group.userData.rig={character,joints,parts,face,texture,signature:rigVisualSignature(cfg,character),cellsReady:!!cells,thickness:cfg.thickness,factor,body,sockets};
  rigBuildSocketGuides(group);
  rigAnimateCharacter(group,character,0);return group;
}
const rigOriginalPaperVisual=storyPaperVisual;
storyPaperVisual=function(value){
  const visual=storyCleanVisual(value),character=rigCharacterId(visual.layer);
  return character&&rigModel().characters[character].enabled?rigBuildVisual(visual,character):rigOriginalPaperVisual(visual);
};
function rigAnimateCharacter(group,character,time){
  const rig=group.userData.rig;if(!rig)return;
  const cfg=rigModel().characters[character];
  for(const [id,pivot] of Object.entries(rig.joints)){
    const key=rigSample(character,id,time);pivot.rotation.set(key.rotationX,key.rotationY,key.rotationZ);pivot.position.set(0,0,0);
    const pins=[pivot.userData.rigSocketPart.attach,...Object.values(pivot.userData.rigSocketPart.sockets)];
    if(id==='staff')pins.push({x:0,y:-cfg.layout.staff.height/2,z:0});
    rigPartRelief(pivot.userData.part,key.depth*cfg.depth,pins);
    if(id==='head')rigFaceRelief(rig.face,key.depth*cfg.depth,pins,pivot.userData.part);
  }
  rigPaintFace(rig.face,character,rigSample(character,'face',time),time);
  rigUpdateSocketGuides(group);
}
function rigDisposeChildren(group){
  for(const guide of group.userData.rig?.guides||[]){guide.marker.removeFromParent();guide.marker.geometry.dispose();guide.marker.material.dispose();}
  for(const child of [...group.children]){group.remove(child);child.traverse(o=>{o.geometry?.dispose();for(const m of Array.isArray(o.material)?o.material:o.material?[o.material]:[])m.dispose();if(o.userData.rigFace)o.material.map.dispose();});}
}
function rigRebuildActor(actor){
  const replacement=storyPaperVisual(actor.userData.storyVisual);rigDisposeChildren(actor);
  for(const child of [...replacement.children])actor.add(child);
  if(replacement.userData.rig)actor.userData.rig=replacement.userData.rig;else delete actor.userData.rig;
}
function rigRefreshNativeActors(){
  for(const character of RIG_CHARACTERS){const actor=storyBoundActor(character);if(actor)rigRebuildActor(actor);}
}
function rigRefreshStage(){
  if(!currentProject?.animeRigs)return;
  for(const character of RIG_CHARACTERS){
    const cfg=rigModel().characters[character],signature=rigVisualSignature(cfg,character);
    const cast=animeCine?.cast?.[character==='kami'?'kami':'wisp'];
    for(const actor of [storyBoundActor(character),cast].filter(Boolean)){
      if(actor.userData.rig?.signature!==signature&&(cfg.enabled||actor.userData.rig))rigRebuildActor(actor);
      if(actor.userData.rig&&!actor.userData.rig.cellsReady&&actor.userData.rig.texture.image?.width)rigRebuildActor(actor);
      rigAnimateCharacter(actor,character,animeCine?.elapsed||0);
    }
  }
  if(animeCine)storyRender();
}
function rigTextureLoaded(texture,source){
  if(currentProject?.animeRigs&&RIG_CHARACTERS.some(id=>rigModel().characters[id].asset===source))rigRefreshStage();
}
function rigFitCamera(c){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3();for(const actor of [c.cast.kami,c.cast.wisp])if(actor.visible)box.expandByObject(actor);
  if(box.isEmpty())return;
  const tangent=Math.tan(THREE.MathUtils.degToRad(perspectiveCamera.fov)*.5),aspect=perspectiveCamera.aspect||1;
  // Include off-center limbs and their frontmost surface, even in portrait.
  const target=storySample('camera',c.elapsed),halfWidth=Math.max(Math.abs(box.min.x-target.tx),Math.abs(box.max.x-target.tx)),halfHeight=Math.max(Math.abs(box.min.y-target.ty),Math.abs(box.max.y-target.ty));
  const z=Math.max(perspectiveCamera.position.z,box.max.z+halfWidth*1.15/(tangent*aspect),box.max.z+halfHeight*1.12/tangent,box.max.z+6.5);
  perspectiveCamera.position.z=z;perspectiveCamera.lookAt(target.tx,target.ty,target.tz);perspectiveCamera.updateMatrixWorld(true);
}
function rigFaceInkStatus(face){
  const w=face.canvas.width,h=face.canvas.height,pixels=face.canvas.getContext('2d').getImageData(0,0,w,h).data;
  let x0=w,y0=h,x1=0,y1=0,pixelCount=0;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(pixels[(y*w+x)*4+3]>8){pixelCount++;x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+1);y1=Math.max(y1,y+1);}
  const p=face.mesh.position,fit=face.fit;
  return {pixelCount,canvasInkBounds:pixelCount?{min:[x0,y0],max:[x1,y1]}:null,
    featureInkBounds:pixelCount?{min:[p.x+(x0/w-.5)*fit.width,p.y+(.5-y1/h)*fit.height,p.z],max:[p.x+(x1/w-.5)*fit.width,p.y+(.5-y0/h)*fit.height,p.z]}:null};
}
function rigFaceSurfaceStatus(rig){
  const face=rig.face,part=rig.joints.head.userData.part,front=part.children.find(child=>child.name?.endsWith('painted front'));
  const w=face.canvas.width,h=face.canvas.height,pixels=face.canvas.getContext('2d').getImageData(0,0,w,h).data,samples=[];
  let minFeatureClearance=Infinity,featureSurfaceSampleCount=0;
  for(let y=1;y<h;y+=3)for(let x=1;x<w;x+=3){
    const alpha=pixels[(y*w+x)*4+3];if(alpha<80)continue;
    const fx=((x+.5)/w-.5)*face.fit.width,fy=(.5-(y+.5)/h)*face.fit.height;
    const hx=fx+face.mesh.position.x,hy=fy+face.mesh.position.y;
    const headZ=rigPlaneSurfaceZ(front,hx,hy),faceZ=rigPlaneSurfaceZ(face.mesh,fx,fy),clearance=faceZ-headZ;
    featureSurfaceSampleCount++;minFeatureClearance=Math.min(minFeatureClearance,clearance);
    if(samples.length<80){const headWorld=part.localToWorld(new THREE.Vector3(hx,hy,headZ)),faceWorld=part.localToWorld(new THREE.Vector3(hx,hy,faceZ));
      samples.push({headLocal:[hx,hy,headZ],faceLocal:[hx,hy,faceZ],headWorld:headWorld.toArray(),faceWorld:faceWorld.toArray(),screen:rigProjectedWorld(faceWorld),alpha:alpha/255,clearance});}
  }
  return {minFeatureClearance:Number.isFinite(minFeatureClearance)?minFeatureClearance:null,featureSurfaceSampleCount,surfaceSamples:samples};
}
function rigInkPoints(part,actor,factor){
  const points=[],cell=part.userData.rigCell,size=cell?.size||1,mask=cell?.mask||[true],{width:w,height:h}=part.userData.rigSize,matrix=new THREE.Matrix4().copy(actor.matrixWorld).invert().multiply(part.matrixWorld);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++)if(mask[y*size+x]){const v=rigSurfacePoint(part,((x+.5)/size-.5)*w,(.5-(y+.5)/size)*h).applyMatrix4(matrix);points.push([v.x/factor,v.y/factor]);}
  return points;
}
function rigClosestInk(points,anchor){let distance=Infinity,point=null;for(const p of points){const d=Math.hypot(p[0]-anchor[0],p[1]-anchor[1]);if(d<distance){distance=d;point=p;}}return {distance,point};}
function rigAttachmentStatus(actor,rig){
  const factor=1,frame=rig.body,pieces={},ink={};
  for(const [id,pivot] of Object.entries(rig.joints))if(pivot.userData.part){
    const part=pivot.userData.part,points=rigInkPoints(part,frame,factor);ink[id]=points;
    const geometry=part.children[0].geometry;geometry.computeBoundingBox();const size=geometry.boundingBox.getSize(new THREE.Vector3());pieces[id]={width:size.x,height:size.y,artCenter:part.position.toArray(),restPosition:pivot.parent.position.toArray(),worldPosition:part.getWorldPosition(new THREE.Vector3()).toArray(),surfaceWorldPosition:part.localToWorld(rigSurfacePoint(part,0,0)).toArray(),relief:part.userData.rigRelief||0,surfaceDepthSpan:size.z,alphaBounds:{min:[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1]))],max:[Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))]}};
  }
  // The staff's painted skull is above the hand. Sample its actual cylinder,
  // whose wooden side surface passes through the glove's grip.
  const shaft=rig.joints.staff.userData.gripShaft;if(shaft){const matrix=new THREE.Matrix4().copy(frame.matrixWorld).invert().multiply(shaft.matrixWorld);for(let y=-1.625;y<=1.625;y+=.04)for(const x of [-.045,0,.045]){const v=new THREE.Vector3(x,y,0).applyMatrix4(matrix);ink.staff.push([v.x/factor,v.y/factor]);}}
  const attachments=[];
  for(const [id,pivot] of Object.entries(rig.joints)){
    const parent=pivot.userData.rigParent;if(!parent||!ink[id]||!ink[parent])continue;
    const v=frame.worldToLocal(pivot.getWorldPosition(new THREE.Vector3())),anchor=[v.x/factor,v.y/factor],a=rigClosestInk(ink[parent],anchor),b=rigClosestInk(ink[id],anchor);
    attachments.push({id,parent,child:id,anchor,parentPoint:a.point,childPoint:b.point,parentGap:a.distance,childGap:b.distance,gap:Math.max(a.distance,b.distance),limit:.20,visible:actor.visible});
  }
  return {pieces,attachments};
}
function rigSocketStatus(actor,rig){
  const sockets={},connections=[];
  for(const [id,pivot] of Object.entries(rig.joints)){
    const part=pivot.userData.rigSocketPart;
    sockets[id]={rendered:!!pivot.userData.part,attach:{local:{...part.attach},world:rigSocketWorld(rig,id,part.attach).toArray()},
      outgoing:Object.fromEntries(Object.entries(part.sockets).map(([name,point])=>[name,{local:{...point},world:rigSocketWorld(rig,id,point).toArray()}]))};
    const connection=pivot.userData.rigConnection;if(connection){
      const childAttach=rigSocketWorld(rig,id,part.attach),owner=rig.joints[connection.parent].userData.rigSocketPart;
      const parentSocket=rigSocketWorld(rig,connection.parent,owner.sockets[connection.socket]);
      connections.push({child:id,parent:connection.parent,socket:connection.socket,connected:connection.connected,rendered:!!pivot.userData.part,
        childAttachWorld:childAttach.toArray(),parentSocketWorld:parentSocket.toArray(),error:childAttach.distanceTo(parentSocket)});
    }
  }
  return {schema:SOCKET_SCHEMA,sockets,connections,guidesVisible:rig.guides.some(guide=>!!guide.marker.parent),staffGrip:rig.character==='kami'?rigStaffGripStatus(actor,rig):null};
}
function rigStaffGripStatus(actor,rig){
  const hand=rig.joints.leftHand.userData.part,staff=rig.joints.staff.userData.part,shaft=rig.joints.staff.userData.gripShaft;
  if(!hand||!staff||!shaft)return null;
  const cell=hand.userData.rigCell,pixels=rig.texture.userData.rigPixels,point=rig.joints.leftHand.userData.rigSocketPart.sockets.grip;
  const handSamples=[],size=cell?.size||0,{width:w,height:h}=hand.userData.rigSize;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    if(!cell.mask[y*size+x])continue;
    const px=Math.min(cell.x1-1,Math.floor(cell.x0+(x+.5)*(cell.x1-cell.x0)/size)),py=Math.min(cell.y1-1,Math.floor(cell.y0+(y+.5)*(cell.y1-cell.y0)/size)),i=(py*cell.width+px)*4;
    if(pixels[i+3]<235)continue;
    const ax=((x+.5)/size-.5)*w,ay=(.5-(y+.5)/size)*h,distance=Math.hypot(ax-point.x,ay-point.y);
    if(distance>.16)continue;
    const surface=rigSurfacePoint(hand,ax,ay),world=hand.localToWorld(surface.clone());
    handSamples.push({local:surface.toArray(),world:world.toArray(),screen:rigProjectedWorld(world),alpha:pixels[i+3]/255,rgb:[pixels[i],pixels[i+1],pixels[i+2]],gripDistance:distance});
  }
  handSamples.sort((a,b)=>a.gripDistance-b.gripDistance);
  const shaftBase=shaft.localToWorld(new THREE.Vector3(0,-1.625,0)),shaftTop=shaft.localToWorld(new THREE.Vector3(0,1.625,0));
  const shaftGrip=shaft.localToWorld(new THREE.Vector3(0,.625,0)),grip=rigSocketWorld(rig,'leftHand',point);
  const headBox=new THREE.Box3().setFromObject(staff),hsize=staff.userData.rigSize,stem=staff.localToWorld(rigSurfacePoint(staff,0,-hsize.height/2));
  const ferrule=rig.joints.staff.userData.gripFerrule,ferruleBox=new THREE.Box3().setFromObject(ferrule),scale=shaft.getWorldScale(new THREE.Vector3());
  const screen=rigProjectedWorld(grip),handFront=hand.localToWorld(rigSurfacePoint(hand,point.x,point.y));
  const cameraPosition=perspectiveCamera.getWorldPosition(new THREE.Vector3());
  return {paintedHand:hand.name||'leftHand',visible:actor.visible&&hand.visible,handSampleCount:handSamples.length,handFrontSamples:handSamples.slice(0,12),
    gripWorld:grip.toArray(),gripScreen:screen,shaftGripWorld:shaftGrip.toArray(),gripError:grip.distanceTo(shaftGrip),
    shaftBaseWorld:shaftBase.toArray(),shaftTopWorld:shaftTop.toArray(),shaftRadius:.045*Math.max(scale.x,scale.z),
    handFrontWorld:handFront.toArray(),fingerFrontClearance:cameraPosition.distanceTo(shaftGrip)-cameraPosition.distanceTo(handFront)-.045*Math.max(scale.x,scale.z),
    headStemWorld:stem.toArray(),headBounds:{min:headBox.min.toArray(),max:headBox.max.toArray()},ferruleBounds:{min:ferruleBox.min.toArray(),max:ferruleBox.max.toArray()},
    headStemToShaftTop:stem.distanceTo(shaftTop),shaftLength:shaftBase.distanceTo(shaftTop)};
}
function rigRenderStatus(character){
  if(!rigCharacterId(character))return null;
  const actor=animeCine?.cast?.[character==='kami'?'kami':'wisp']||storyBoundActor(character),rig=actor?.userData.rig;
  if(!rig)return {active:!!actor,rigged:false,partCount:0};
  actor.updateWorldMatrix(true,true);const box=new THREE.Box3().setFromObject(actor),joints={};let meshCount=0;actor.traverse(o=>{if(o.isMesh)meshCount++;});
  for(const [id,pivot] of Object.entries(rig.joints)){const part=pivot.userData.part;joints[id]={rotation:[pivot.rotation.x,pivot.rotation.y,pivot.rotation.z],position:pivot.parent.position.clone().add(pivot.position).toArray(),worldPosition:pivot.getWorldPosition(new THREE.Vector3()).toArray(),partWorldPosition:(part||pivot).getWorldPosition(new THREE.Vector3()).toArray(),surfaceWorldPosition:part?part.localToWorld(rigSurfacePoint(part,0,0)).toArray():null,artDepth:part?.userData.rigRelief||0};}
  return {active:!!animeCine,rigged:true,partCount:rig.parts.length,meshCount,thickness:rig.thickness,depthSpan:box.max.z-box.min.z,bounds:{min:box.min.toArray(),max:box.max.toArray()},joints,...rigAttachmentStatus(actor,rig),...rigSocketStatus(actor,rig),face:{...rig.face.applied,textureVersion:rig.face.texture.version,anchor:rig.face.mesh.position.toArray(),surfaceRelief:rig.face.relief,footprint:{width:rig.face.fit.width,height:rig.face.fit.height},...rigFaceInkStatus(rig.face),...rigFaceSurfaceStatus(rig)}};
}
window.SWYRL_ENGINE_RIG=Object.freeze({...window.SWYRL_ENGINE_RIG,renderStatus:rigRenderStatus});
window.SWYRL_ENGINE_SOCKETS=Object.freeze({...window.SWYRL_ENGINE_SOCKETS,renderStatus:character=>{
  if(!rigCharacterId(character))return null;
  const actor=animeCine?.cast?.[character==='kami'?'kami':'wisp']||storyBoundActor(character),rig=actor?.userData.rig;
  if(!rig)return {active:!!actor,rigged:false};actor.updateWorldMatrix(true,true);return {active:!!animeCine,rigged:true,...rigSocketStatus(actor,rig)};
}});
