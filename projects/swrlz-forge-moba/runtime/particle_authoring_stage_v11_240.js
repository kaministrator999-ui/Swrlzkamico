// §E v11.240 — isolated Particle Studio authoring chamber on the EXISTING WebGL renderer.
// Render-layer isolation, not a separate renderer, new scene import, or editor actor.
// Current project emitters remain native; saved world position/attachment is unchanged.
(function(){
  const LAYER=25;
  const state={active:false,scene:null,camera:null,project:null,saved:null,root:null,
    entries:0,exits:0,lastError:''};
  const chamberColor=0x162239;
  function layer(object){object.layers.set(LAYER);return object;}
  function buildStage(target){
    const root=new THREE.Group();root.name='Particle Studio authoring chamber (editor-only)';
    root.userData.se240EditorOnly=true;
    const floor=layer(new THREE.Mesh(new THREE.PlaneGeometry(32,32),
      new THREE.MeshBasicMaterial({color:chamberColor,side:THREE.DoubleSide})));
    floor.name='VFX test floor';floor.rotation.x=-Math.PI/2;floor.position.y=-.07;
    const grid=layer(new THREE.GridHelper(24,24,0x497e97,0x30425c));
    grid.position.y=-.06;grid.name='VFX grid';
    const marker=layer(new THREE.Mesh(new THREE.RingGeometry(.54,.58,48),
      new THREE.MeshBasicMaterial({color:0x5dcee3,transparent:true,opacity:.9,side:THREE.DoubleSide})));
    marker.rotation.x=-Math.PI/2;marker.position.y=-.045;
    marker.name='Emitter center reference';
    const cross=layer(new THREE.AxesHelper(.7));cross.position.y=.02;
    const backdrop=layer(new THREE.Mesh(new THREE.SphereGeometry(80,20,12),
      new THREE.MeshBasicMaterial({color:0x0b1527,side:THREE.BackSide,fog:false})));
    backdrop.name='VFX dark background';
    for(const child of [backdrop,floor,grid,marker,cross])root.add(child);
    target.add(root);
    return root;
  }
  function status(message,error=false){
    const note=document.getElementById('se225ViewNote');
    if(note){note.textContent=message;note.dataset.error=String(error);}
  }
  function open(){
    if(state.active)return true;
    if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='particles')return false;
    if(!scene||!camera||!renderer||playing||simulating||renderer.xr?.isPresenting){
      status('Particle test chamber needs Edit mode outside immersive VR. Stop Play and reopen Particle Studio.',true);
      return false;
    }
    try{
      state.scene=scene;state.camera=camera;state.project=currentProject;
      state.saved={position:camera.position.clone(),quaternion:camera.quaternion.clone(),
        mask:camera.layers.mask};
      state.root=buildStage(scene);
      state.active=true;state.entries++;
      se223State.preview=true;
      se223Reset();
      status('Isolated 3D test chamber · only the selected emitter is shown here. Its saved Sheep Tag position and actor attachment are untouched.');
      return true;
    }catch(error){
      state.lastError=String(error?.message||error).slice(0,160);
      close();
      status('Could not enter the particle test chamber; normal scene preview remains available.',true);
      return false;
    }
  }
  function close(){
    if(!state.active&&!state.root)return;
    state.active=false;
    if(state.camera===camera&&state.saved){
      camera.position.copy(state.saved.position);
      camera.quaternion.copy(state.saved.quaternion);
      camera.layers.mask=state.saved.mask;
      camera.updateMatrixWorld(true);
    }
    if(state.root){
      state.root.traverse(object=>{
        object.geometry?.dispose?.();
        if(Array.isArray(object.material))object.material.forEach(m=>m.dispose?.());
        else object.material?.dispose?.();
      });
      state.root.removeFromParent();
    }
    state.root=null;state.saved=null;state.scene=null;state.camera=null;state.project=null;
    state.exits++;
    se223Reset();
  }
  function frame(){
    if(!state.active)return false;
    if(scene!==state.scene||camera!==state.camera||
       currentProject!==state.project||
       window.SWYRL_ENGINE_STUDIOS?.active?.()!=='particles'||
       playing||simulating||renderer.xr?.isPresenting){
      close();return false;
    }
    // Reassert after engine camera controls; restore its exact previous pose on exit.
    camera.position.set(6.2,4.4,8.2);
    camera.lookAt(0,1.35,0);
    camera.layers.set(LAYER);
    camera.updateMatrixWorld(true);
    return true;
  }
  window.addEventListener('pagehide',close);
  window.SWYRL_ENGINE_PARTICLE_STAGE_240=Object.freeze({
    open,close,active:()=>state.active,frame,
    inspect:()=>({active:state.active,entries:state.entries,exits:state.exits,
      rendererCount:1,layer:LAYER,project:state.project?.name||null,
      lastError:state.lastError})
  });
})();
