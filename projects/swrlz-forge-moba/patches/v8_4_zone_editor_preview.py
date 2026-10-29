"""Transient editor previews and world-space camera framing for travel zones."""


def _once(source, before, after):
    if source.count(before) != 1:
        raise RuntimeError("Zone preview anchor must occur once: " + before[:100])
    return source.replace(before, after, 1)


JS = r'''
const ZONE_PREVIEW_PREF_KEY='swyrl.engine.zonePreview.v1';
const zonePreviewGroup=new THREE.Group();zonePreviewGroup.name='Editor destination previews';zonePreviewGroup.userData.editorOnly=true;zonePreviewGroup.userData.helper=true;scene.add(zonePreviewGroup);
let zonePreviewEnabled=false;
try{zonePreviewEnabled=localStorage.getItem(ZONE_PREVIEW_PREF_KEY)==='true'}catch{}
function clearZonePreviews(){
  const geometries=new Set(),materials=new Set();
  for(const marker of [...zonePreviewGroup.children]){marker.traverse(node=>{if(node.geometry)geometries.add(node.geometry);for(const material of (Array.isArray(node.material)?node.material:[node.material]))if(material)materials.add(material)});zonePreviewGroup.remove(marker)}
  for(const geometry of geometries)geometry.dispose();for(const material of materials)material.dispose();
}
function syncZonePreviewUI(){
  zonePreviewGroup.visible=zonePreviewEnabled&&!playing&&!simulating;
  const toggle=$('zoneEditorPreview');if(toggle)toggle.checked=zonePreviewEnabled;
  const frame=$('zoneEditorFrame');if(frame)frame.disabled=playing||simulating||!listTeleportZones().some(zone=>zone.id===$('zoneEditorSelect')?.value);
}
function rebuildZonePreviews(){
  clearZonePreviews();
  if(zonePreviewEnabled)for(const zone of listTeleportZones()){
    const marker=new THREE.Group();marker.name=zone.name;marker.userData.zoneId=zone.id;marker.userData.zoneYaw=zone.yaw;marker.position.fromArray(zone.position);marker.position.y+=.025;
    const material=new THREE.MeshBasicMaterial({color:zone.accent,transparent:true,opacity:.85,side:THREE.DoubleSide,depthWrite:false,fog:false});
    const ring=new THREE.Mesh(new THREE.RingGeometry(.48,.56,48),material);ring.rotation.x=-Math.PI/2;marker.add(ring);
    const heading=new THREE.Group();heading.rotation.y=-zone.yaw;
    const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,-.16),new THREE.Vector3(0,0,-1.04)]),new THREE.LineBasicMaterial({color:zone.accent,transparent:true,opacity:.95,depthWrite:false,fog:false}));heading.add(line);
    const shape=new THREE.Shape();shape.moveTo(-.18,.87);shape.lineTo(.18,.87);shape.lineTo(0,1.25);shape.closePath();const head=new THREE.Mesh(new THREE.ShapeGeometry(shape),material);head.rotation.x=-Math.PI/2;heading.add(head);marker.add(heading);
    // Previews are never actors, support surfaces, blockers, or pick targets.
    marker.traverse(node=>{node.userData.editorOnly=true;node.userData.helper=true;node.raycast=()=>{};node.castShadow=false;node.receiveShadow=false});zonePreviewGroup.add(marker);
  }
  syncZonePreviewUI();
}
function configureZonePreview(enabled){
  zonePreviewEnabled=!!enabled;try{localStorage.setItem(ZONE_PREVIEW_PREF_KEY,String(zonePreviewEnabled))}catch{}
  rebuildZonePreviews();return inspectZonePreview();
}
function inspectZonePreview(){
  return {enabled:zonePreviewEnabled,visible:zonePreviewGroup.visible,markerCount:zonePreviewGroup.children.length,selectedZoneId:$('zoneEditorSelect')?.value||null,markers:zonePreviewGroup.children.map(marker=>({id:marker.userData.zoneId,name:marker.name,position:marker.position.toArray(),yaw:marker.userData.zoneYaw}))};
}
function frameTeleportZone(id){
  if(playing||simulating)return {ok:false,error:'Return to the editor to frame a destination.'};
  const zone=listTeleportZones().find(zone=>zone.id===id);if(!zone)return {ok:false,error:'Choose a saved destination to frame.'};
  const target=new THREE.Vector3(...zone.position),delta=camera.position.clone().sub(orbit.target);
  if(editorCameraView==='perspective'){if(delta.lengthSq()<.0001)delta.set(7,6,9);delta.setLength(THREE.MathUtils.clamp(delta.length(),6,12))}
  // Orthographic views translate their existing axes, distance, and zoom intact.
  orbit.target.copy(target);camera.position.copy(target.clone().add(delta));camera.lookAt(target);orbit.update();
  $('zoneEditorFeedback').textContent='Framed '+zone.name+' · ring marks feet position; arrow marks arrival heading.';
  return {ok:true,zoneId:zone.id,position:zone.position.slice()};
}
'''


def apply(html):
    s = html.replace('</head>', '<style>.zone-preview-toggle{display:flex;gap:7px;align-items:center;margin:4px 0 10px;font-size:12px}.zone-editor .zone-preview-toggle input{width:auto;flex:0 0 auto}</style>\n</head>', 1)
    s = _once(s, 'installTeleportTools();\n', JS + '\ninstallTeleportTools();\n')
    s = _once(s, 'function setSessionButtons(){\n', 'function setSessionButtons(){\n  syncZonePreviewUI();\n')
    s = _once(s, '  closeTeleportMenu(false);\n  editorLayers=[];', '  closeTeleportMenu(false);\n  clearZonePreviews();\n  editorLayers=[];')
    s = _once(s, "function renderTeleportEditor(preferredId){\n", "function renderTeleportEditor(preferredId){\n  rebuildZonePreviews();\n")
    s = _once(s, "$('zoneEditorDelete').disabled=!zone;$('zoneEditorFeedback').textContent='';", "$('zoneEditorDelete').disabled=!zone;$('zoneEditorFeedback').textContent='';syncZonePreviewUI();")
    s = _once(s, '<div class="field"><label for="zoneEditorSelect">Destination</label>', '<label class="zone-preview-toggle"><input id="zoneEditorPreview" type="checkbox"> Show destination markers</label><div class="row"><button id="zoneEditorFrame" type="button">Frame Destination</button></div><div class="field"><label for="zoneEditorSelect">Destination</label>')
    s = _once(s, "  $('zoneEditorSelect').onchange=", "  $('zoneEditorPreview').onchange=()=>configureZonePreview($('zoneEditorPreview').checked);$('zoneEditorFrame').onclick=()=>frameTeleportZone($('zoneEditorSelect').value);\n  $('zoneEditorSelect').onchange=")
    s = _once(s, '  upsertTeleportZone:(zone)=>upsertTeleportZone(zone),', '  configureZonePreview:(enabled)=>configureZonePreview(enabled),\n  inspectZonePreview:()=>inspectZonePreview(),\n  frameTeleportZone:(id)=>frameTeleportZone(id),\n  upsertTeleportZone:(zone)=>upsertTeleportZone(zone),')
    return s
