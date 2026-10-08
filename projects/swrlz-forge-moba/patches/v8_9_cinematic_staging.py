"""v8.9: Keep pop-up book/scenery below and behind the character action.

The v8.8 phone screenshots exposed opaque foreground-book/desk cutouts
blocking the wizards and huge pages folding across the cinematic camera.
The edit must be in the governed engine source, not just a storyboard image.
"""
def once(s,old,new):
    if s.count(old)!=1:
        raise RuntimeError("v8.9 staging anchor missing/ambiguous: "+old[:110])
    return s.replace(old,new,1)

EXTRA=r"""
// Narrow, low-height foreground ink: never fill the middle of the shot with
// a solid rectangle. Pop-up backdrops and characters retain their own plates.
function popLowStageTrim(c,w,h){
  c.clearRect(0,0,w,h);
  const top=h*.79;
  const wood=c.createLinearGradient(0,top,0,h);
  wood.addColorStop(0,'#8d633d');wood.addColorStop(.25,'#30202b');
  wood.addColorStop(1,'#251a29');
  c.fillStyle=wood;c.fillRect(0,top+13,w,h-top-13);
  c.strokeStyle='#ce9961';c.lineWidth=7;c.beginPath();
  c.moveTo(0,top+13);c.lineTo(w,top+13);c.stroke();
  c.strokeStyle='#edc18677';c.lineWidth=2;
  for(let i=0;i<4;i++){c.beginPath();c.moveTo(0,top+30+i*27);c.lineTo(w,top+30+i*27);c.stroke()}
  // Low corner accents, not another tall panel in the characters' foreground.
  c.fillStyle='#b28051';c.fillRect(18,top-14,34,31);
  c.fillRect(w-52,top-14,34,31);
  c.strokeStyle='#dfb477';c.lineWidth=4;
  c.beginPath();c.arc(91,top+37,20,0,Math.PI*2);
  c.arc(w-91,top+37,20,0,Math.PI*2);c.stroke();
}
function animePopupStageSafety(c){
  if(!c)return null;
  scene.updateMatrixWorld(true);
  const front=c.layers.foreground;
  const trim=front.children.find(item=>item.userData.popupHinge);
  const ink=trim?.children.find(item=>item.isSprite);
  const book=front.children.find(item=>item.userData.animePopupBook);
  const bookPos=new THREE.Vector3(),inkPos=new THREE.Vector3(),
    kamiPos=new THREE.Vector3(),swyrlzPos=new THREE.Vector3(),
    cathedralPos=new THREE.Vector3();
  book?.getWorldPosition(bookPos);ink?.getWorldPosition(inkPos);
  c.cast.kami.getWorldPosition(kamiPos);
  c.cast.wisp.getWorldPosition(swyrlzPos);
  c.layers.midground.children[0]?.getWorldPosition(cathedralPos);
  const kamiSprite=c.cast.kami.children.find(o=>o.isSprite);
  const kamiBottom=kamiPos.y-(kamiSprite?.scale.y||0)*c.cast.kami.scale.y*.5;
  // Painted pixels start at 79% canvas height, not at the clear sprite top.
  const frontInkTop=inkPos.y+ink.scale.y*.5-ink.scale.y*.79;
  const bookTop=bookPos.y+.25;
  return {bookY:bookPos.y,bookTopY:bookTop,foregroundInkTopY:frontInkTop,
    kamiBottomY:kamiBottom,characterZ:kamiPos.z,swyrlzZ:swyrlzPos.z,
    cathedralZ:cathedralPos.z,
    cameraFrontGap:perspectiveCamera.position.z-
      Math.max(bookPos.z,inkPos.z)};
}
"""
def apply(html):
    s=html
    # More expressive than just changing z: remove opaque desk-scene occluder,
    # keep an unobtrusive visible rim which remains an editable depth layer.
    s=once(s,'function animeCreateCelLayers(){',EXTRA+'\nfunction animeCreateCelLayers(){')
    s=once(s,"plate('foreground',popDeskArt,3.4,[11.5,8],2.8);",
        "plate('foreground',popLowStageTrim,1.5,[10.5,2.3],1.0);")
    # The original pen-and-ink scenes are unchanged; the actual foreground
    # artwork is now restricted to the bottom of its cutout.
    s=once(s,"['background',1.9],['atmosphere',1.9],['midground',1.9],['effects',1.9],['foreground',1.9]",
        "['background',1.9],['atmosphere',1.9],['midground',1.9],['effects',1.9],['foreground',0.7]")
    s=once(s,"book.position.set(delta*.73,1.9-1.3*(1-t0),3.2);",
        """// Book lives on the lower stage; never intersect a character's face.
    // Its depth is behind the actors even when the camera dollies.
    book.position.set(delta*.18,.15-.22*(1-t0),-1.85);""")
    s=once(s,"book.scale.set(1,.1+.9*t0,1);",
        "book.scale.set(.9,.33+.67*t0,.9);")
    # Effects are glows behind the characters, not opaque stage cards in front.
    s=once(s,"plate('effects',(c,w,h)=>{c.clearRect(0,0,w,h);",
        "plate('effects',(c,w,h)=>{c.clearRect(0,0,w,h);")
    s=once(s,"},1,[15,11],4.7);","},-2.6,[15,11],4.7);")
    # Clamp big plane geometry behind BOTH actors, preserving editable negative
    # depth values. An FX plane may be moved closer but still stays behind.
    s=once(s,"hinge.position.set(0,-1.3+progress*1.3,setting.depth+(index%2)*1.6);",
        """const unclamped=setting.depth+(index%2)*1.6;
      const depth=(id==='background'||id==='atmosphere'||id==='midground'||id==='effects')
        ?Math.min(unclamped,Math.min(cfg.kami.depth,cfg.swyrlz.depth)-1.25)
        :Math.min(unclamped,2.0);
      hinge.position.set(0,-1.3+progress*1.3,depth);""")
    # For existing v8.8 projects whose Director saved an overly-near foreground
    # value, render safely but preserve user setting for backward compatibility.
    s=once(s,"  popUpStatus:()=>{const c=animeCine;if(!c)return null;",
      "  popUpStatus:()=>{const c=animeCine;if(!c)return null;")
    s=once(s,"      sceneZ:{background:animePopConfig().layers.background.depth,midground:animePopConfig().layers.midground.depth,foreground:animePopConfig().layers.foreground.depth}};}",
        """      sceneZ:{background:animePopConfig().layers.background.depth,midground:animePopConfig().layers.midground.depth,foreground:animePopConfig().layers.foreground.depth},
      stageSafety:animePopupStageSafety(c)};}""")
    s=once(s,'V8_8_POPUP_STORYBOOK_DIRECTOR','V8_9_CINEMATIC_STAGING_SAFE')
    s=s.replace('Maker v8.8','Maker v8.9').replace('MAKER v8.8','MAKER v8.9')
    s=s.replace("version:'v8.8'","version:'v8.9'").replace('version:8.8','version:8.9')
    s=s.replace('§E v8.8 Tools','§E v8.9 Tools')
    s=s.replace('v8.8 · POP-UP STORYBOOK DIRECTOR','v8.9 · SAFE CINEMATIC POP-UP STAGING')
    s=s.replace('§wyrl§ Engine v8.8 · animated 3D pop-up storybook cinema',
                '§wyrl§ Engine v8.9 · camera-safe 3D pop-up storybook cinema')
    return s
