// Curated Sheep Tag map tools. All saved pieces are native editor actors;
// brush and route helpers are detached from native actor/project serialization.
const ST_CREATOR_SCHEMA = 'swyrl-sheep-tag-map-v1';
const ST_CREATOR_TYPES = Object.freeze([
  'st-sheep','st-wolf','st-farm','st-income','st-fort','st-pen','st-tree','st-rock',
  'st-pond','st-shop','st-meadow','st-thorn','st-wall','st-ramp','st-totem',
  'st-road','st-grass','st-earth','st-zone'
]);
const ST_CREATOR_RULE_KEYS = new Set([
  'duration','headstart','bounds','startGold','role','preset','buildSnap',
  'sheepSpeed','wolfSpeed','wolfDamage','attackInterval','farmHp','incomeHp','fortHp',
  'sheepRadius','wolfRadius','houseLimit','fogMode','sheepVision','wolfVision',
  'rescueProtection','rescueHold','thorns','totems','elevated','split','events',
  'thornChance','thornDuration','thornCooldown','scentInterval','densityRadius',
  'totemRadius','fadeSeconds','revealSeconds','totemLimit','totemCooldown',
  'wallCost','rampCost','wallHp','rampHp','wallHeight','wolvesUseRamps','splitUnlock',
  'progressionSeconds','rescueXp','splitCooldown','splitLifetime','eventInterval',
  'eventWarning','eventDuration','eventPool','seed','permittedStructures'
]);
const stCreator = {
  open:false, tool:'st-grass', cells:1, rotation:0, snap:3, pointer:null,
  lastStamp:null, strokeCount:0, helper:null, paths:null, routeFrom:null,
  selection:[], orbitEnabled:true, returnAfterPlay:false, installed:false
};

function stCreatorAvailable() {
  return currentProject?.kind === 'sheep-tag' && !playing && !simulating && !stSession;
}
function stCreatorMessage(message) {
  const output = $('stCreatorFeedback'); if (output) output.textContent = String(message);
}
function stCreatorDisposeGraphic(object) {
  if (!object) return;
  object.parent?.remove(object);
  const geometries = new Set(), materials = new Set(), textures = new Set();
  object.traverse(child => {
    if (child.geometry) geometries.add(child.geometry);
    for (const material of child.material ? (Array.isArray(child.material) ? child.material : [child.material]) : []) {
      materials.add(material);
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    }
  });
  for (const texture of textures) texture.dispose();
  for (const geometry of geometries) geometry.dispose();
  for (const material of materials) material.dispose();
}
function stCreatorClearPaths() {
  stCreatorDisposeGraphic(stCreator.paths); stCreator.paths = null; stCreator.routeFrom = null;
}
function stCreatorClearHelpers() {
  stCreatorDisposeGraphic(stCreator.helper); stCreator.helper = null; stCreatorClearPaths();
}
function stCreatorRestoreSelection(ids = stCreator.selection) {
  const existing = ids.map(id => actors.find(actor => actor.userData.id === id)).filter(Boolean);
  multiSelected = existing; selectActor(existing[0] || null);
  if (existing.length > 1) multiSelected = existing;
  if (stCreator.open && stCreator.tool !== 'select') {
    transform.detach(); if (selectionBox) selectionBox.visible = false;
  }
}
function stCreatorRefresh() {
  const available = stCreatorAvailable();
  $('stCreatorLauncher')?.classList.toggle('hidden', !available);
  if (!available && stCreator.open) stCreatorClose(true);
  const count = $('stCreatorCount');
  if (count) {
    const native = actors.filter(actor => ST_CREATOR_TYPES.includes(actor.userData.actorType));
    count.textContent = native.length + ' map pieces · ' + native.filter(actor => actor.userData.actorType === 'st-sheep').length +
      ' sheep · ' + native.filter(actor => actor.userData.actorType === 'st-wolf').length + ' wolves';
  }
}
function stCreatorUpdateInteraction() {
  if (!stCreator.open) return;
  const navigating = stCreator.tool === 'select';
  orbit.enabled = navigating && stCreator.orbitEnabled;
  if (!navigating) {
    stCreator.selection = [...new Set((multiSelected.length ? multiSelected : selected ? [selected] : []).map(actor => actor.userData.id))];
    transform.detach(); if (selectionBox) selectionBox.visible = false;
  }
  else stCreatorRestoreSelection();
  $('viewport').style.cursor = navigating ? '' : 'crosshair';
  const footprint = ['st-wall','st-ramp'].includes(stCreator.tool) ? '2.4 × 6 m, raised routes' :
    stCreator.tool === 'st-zone' ? (6 * stCreator.cells) + ' × ' + (6 * stCreator.cells) + ' m, walkable but building prohibited' :
    ['st-grass','st-earth','st-road','forest','erase'].includes(stCreator.tool) ? (3 * stCreator.cells) + ' × ' + (3 * stCreator.cells) + ' m brush' :
    'one native map piece';
  $('stCreatorHint').textContent = navigating ?
    'Use native selection, Move, Rotate and Scale. Choose a brush to return to painting.' :
    stCreator.tool === 'route' ? 'Tap the start, then the destination. Green is sheep; coral is wolf.' :
    stCreator.tool === 'erase' ? 'Tap or drag to remove map pieces. Undo restores the last brush mark.' :
    footprint + '. Tap or drag to place. Pan / select restores native camera controls.';
}
function stCreatorOpen() {
  if (!stCreatorAvailable()) return {ok:false,reason:'Stop a Sheep Tag match before editing its map.'};
  if (!stCreator.installed) stInstallCreator();
  if (!stCreator.open) {
    stCreator.selection = [...new Set((multiSelected.length ? multiSelected : selected ? [selected] : []).map(actor => actor.userData.id))];
    stCreator.orbitEnabled = orbit.enabled; stCreator.open = true;
  }
  stUiCloseRules(); $('stCreatorPanel').hidden = false;
  $('stCreatorMapName').value = currentProject.name;
  stCreatorSyncRules(); stCreatorRefresh(); stCreatorUpdateInteraction();
  $('stCreatorClose').focus();
  stCreatorMessage('Make a map with native pieces, compare routes, then Playtest. Stop returns here.');
  return {ok:true};
}
function stCreatorClose(restore = true) {
  if (!stCreator.open) return;
  if (stCreator.tool === 'select') stCreator.selection = [...new Set((multiSelected.length ? multiSelected : selected ? [selected] : []).map(actor => actor.userData.id))];
  stCreator.open = false; stCreator.pointer = null;
  $('stCreatorPanel').hidden = true; $('viewport').style.cursor = '';
  stCreatorClearHelpers();
  if (restore) {orbit.enabled = stCreator.orbitEnabled; stCreatorRestoreSelection();}
}
function stCreatorBeforePlay() {
  stCreator.returnAfterPlay = stCreator.open;
  stCreatorClose(true); stCreatorRefresh(); $('stCreatorLauncher')?.classList.add('hidden');
}
function stCreatorAfterStop() {
  stCreatorRefresh();
  if (stCreator.returnAfterPlay && stCreatorAvailable()) {stCreator.returnAfterPlay = false; stCreatorOpen();}
}

// Suppress only nested agent commits, then record one native history entry.
// This gives a multi-piece brush one Undo and keeps native Save/Load authoritative.
function stCreatorTransaction(label, mutation) {
  if (!stCreatorAvailable()) return {ok:false,reason:'Stop the match before editing the map.'};
  if (historyLock || transactionBefore) return {ok:false,reason:'Finish the current editor edit first.'};
  const ids = [...new Set((multiSelected.length ? multiSelected : selected ? [selected] : []).map(actor => actor.userData.id))];
  const before = captureProject(); beginTransaction(label); let result;
  historyLock = true;
  try {result = mutation();}
  catch (error) {
    loadProject(JSON.parse(before), {preserveHistory:true}); transactionBefore = null;
    return {ok:false,reason:String(error?.message || 'This map edit could not be applied.')};
  }
  finally {historyLock = false;}
  rebuildHierarchy(); renderLayerPanel(); refreshDebug(); stCreatorRestoreSelection(ids);
  commitTransaction(label); stCreatorRefresh(); stCreatorClearPaths();
  return result ?? {ok:true};
}
function stCreatorLayerFor(type) {
  const name = ['st-grass','st-earth','st-road','st-meadow'].includes(type) ? 'Creator · Terrain' :
    ['st-sheep','st-wolf'].includes(type) ? 'Creator · Spawns' :
    ['st-pen','st-shop','st-zone'].includes(type) ? 'Creator · Landmarks & zones' :
    ['st-farm','st-income','st-fort','st-wall','st-ramp','st-totem'].includes(type) ? 'Creator · Structures' : 'Creator · Woodland';
  const layer = editorLayers.find(item => item.name === name && item.visible !== false);
  return layer?.id || window.SWYRL_ENGINE_AGENT.createLayer(name)?.id;
}
function stCreatorRemoveActor(actor) {
  removeActorRecursive(actor); stCreatorDisposeGraphic(actor);
}
function stCreatorPoint(payload) {
  const x = Number(payload?.x), z = Number(payload?.z), bounds = stRules().bounds;
  if (!Number.isFinite(x) || !Number.isFinite(z) || Math.abs(x) > bounds || Math.abs(z) > bounds) return null;
  const snap = Math.max(.15, Math.min(6, Number(payload?.snap) || stCreator.snap));
  return {x:Math.round(x / snap) * snap,z:Math.round(z / snap) * snap};
}
// Normalize native world transforms without mutating actors or starting a match.
// The same physical preflight guards native Play and portable creator maps.
function stCreatorNativePreflightPieces() {
  return actors.filter(actor => ST_CREATOR_TYPES.includes(actor.userData.actorType)).map(actor => {
    actor.updateWorldMatrix(true,false);
    const position = new THREE.Vector3(), scale = new THREE.Vector3(), rotation = new THREE.Quaternion();
    actor.getWorldPosition(position); actor.getWorldScale(scale); actor.getWorldQuaternion(rotation);
    const yaw = new THREE.Euler().setFromQuaternion(rotation,'YXZ').y;
    return {id:actor.userData.id,type:actor.userData.actorType,name:actor.name,
      position:position.toArray(),rotation:[0,yaw,0],scale:scale.toArray(),
      active:actor.userData.baked !== false && walkingObjectVisible(actor)};
  });
}
function stCreatorPaint(payload = {}) {
  if (!stCreatorAvailable()) return {ok:false,reason:'Stop the match before painting.'};
  const tool = payload.type || stCreator.tool;
  const type = tool === 'forest' ? 'st-tree' : tool;
  if (!ST_CREATOR_TYPES.includes(type) || type === 'st-meadow') return {ok:false,reason:'Choose a Sheep Tag map piece.'};
  const point = stCreatorPoint(payload);
  if (!point) return {ok:false,reason:'Place pieces inside the map boundary.'};
  const cells = Math.min(3, Math.max(1, Math.round(Number(payload.cells) || stCreator.cells)));
  const angle = Number.isFinite(Number(payload.rotation)) ? Number(payload.rotation) : stCreator.rotation;
  const terrain = ['st-grass','st-earth','st-road'].includes(type), multi = terrain || tool === 'forest';
  const coordinates = [];
  if (multi) {
    for (let row = 0; row < cells; row++) for (let col = 0; col < cells; col++) {
      const dx = (col - (cells - 1) / 2) * 3, dz = (row - (cells - 1) / 2) * 3;
      coordinates.push([point.x + Math.cos(angle) * dx + Math.sin(angle) * dz,
        point.z - Math.sin(angle) * dx + Math.cos(angle) * dz]);
    }
  } else coordinates.push([point.x,point.z]);
  const bounds = stRules().bounds;
  if (coordinates.some(([x,z]) => Math.abs(x) > bounds - (terrain ? 1.5 : 0) || Math.abs(z) > bounds - (terrain ? 1.5 : 0)))
    return {ok:false,reason:'The whole brush must fit inside the map boundary.'};
  if (['st-wall','st-ramp','st-zone','st-pen'].includes(type)) {
    const halfX = type === 'st-zone' ? cells * 3 : type === 'st-pen' ? 5 : 1.2, halfZ = type === 'st-zone' ? cells * 3 : type === 'st-pen' ? 5 : 3;
    const extentX = Math.abs(Math.cos(angle)) * halfX + Math.abs(Math.sin(angle)) * halfZ;
    const extentZ = Math.abs(Math.sin(angle)) * halfX + Math.abs(Math.cos(angle)) * halfZ;
    if (Math.abs(point.x) + extentX > bounds || Math.abs(point.z) + extentZ > bounds)
      return {ok:false,reason:'The whole structure, spirit pen or no-build zone must fit inside the map boundary.'};
  }
  if (actors.filter(actor => ST_CREATOR_TYPES.includes(actor.userData.actorType)).length + coordinates.length > 1500)
    return {ok:false,reason:'This map has reached its 1,500-piece limit.'};
  if (type === 'st-sheep' && actors.filter(actor => actor.userData.actorType === type).length >= 24)
    return {ok:false,reason:'Use at most 24 sheep spawns.'};
  if (type === 'st-wolf' && actors.filter(actor => actor.userData.actorType === type).length >= 8)
    return {ok:false,reason:'Use at most eight wolf spawns.'};
  if (['st-sheep','st-wolf'].includes(type) && actors.some(actor => ['st-sheep','st-wolf'].includes(actor.userData.actorType) &&
      worldPos(actor).distanceTo(new THREE.Vector3(point.x,0,point.z)) < 1.5))
    return {ok:false,reason:'Leave space between creature spawns.'};
  if (['st-sheep','st-wolf','st-pen','st-tree','st-rock','st-pond','st-shop','st-farm','st-income','st-fort','st-wall','st-ramp','st-totem'].includes(type)) {
    const pieces = stCreatorNativePreflightPieces().filter(piece => type !== 'st-pen' || piece.type !== 'st-pen');
    for (const [index,[x,z]] of coordinates.entries()) pieces.push({id:'creator-preview-' + index,type,
      name:type === 'st-sheep' ? 'New sheep spawn' : type === 'st-wolf' ? 'New wolf spawn' : type === 'st-pen' ? 'New spirit pen' : 'New ' + type.slice(3),
      position:[x,0,z],rotation:[0,angle,0],scale:[1,1,1],active:true});
    const checked = stAuthoredMapPreflight({rules:stRules(),pieces,requireRoster:false});
    if (!checked.ok) return checked;
  }
  return stCreatorTransaction('Paint ' + (tool === 'forest' ? 'forest' : type.slice(3)), () => {
    const layer = stCreatorLayerFor(type), created = [];
    if (type === 'st-pen') for (const actor of [...actors]) if (actor.userData.actorType === type) stCreatorRemoveActor(actor);
    for (const [x,z] of coordinates) {
      if (terrain) for (const actor of [...actors]) {
        if (['st-grass','st-earth','st-road'].includes(actor.userData.actorType) &&
            Math.hypot(actor.position.x - x, actor.position.z - z) < .2) stCreatorRemoveActor(actor);
      }
      const number = actors.filter(actor => actor.userData.actorType === type).length + 1;
      const id = window.SWYRL_ENGINE_AGENT.spawn(type, {position:[x,0,z],
        name:(type === 'st-sheep' ? 'Sheep spawn ' : type === 'st-wolf' ? 'Wolf spawn ' : type.slice(3) + ' ') + number,
        folder:'Sheep Tag/Creator'});
      if (!id) throw new Error('This map piece could not be created.');
      const scale = type === 'st-zone' ? [cells,1,cells] : [1,1,1];
      window.SWYRL_ENGINE_AGENT.setTransform(id, {rotation:[0,angle,0],scale});
      window.SWYRL_ENGINE_AGENT.assignActorsToLayer([id],layer,{replace:true});
      const actor = actors.find(item => item.userData.id === id);
      actor.userData.baked = true; applyGhostVisual(actor); created.push(id);
    }
    return {ok:true,ids:created,count:created.length};
  });
}
function stCreatorErase(payload = {}) {
  const point = stCreatorPoint(payload);
  if (!point) return {ok:false,reason:'Choose a point inside the map.'};
  const cells = Math.min(3, Math.max(1, Math.round(Number(payload.cells) || stCreator.cells))), half = cells * 1.5;
  const removing = actors.filter(actor => ST_CREATOR_TYPES.includes(actor.userData.actorType) && actor.userData.actorType !== 'st-meadow' &&
    Math.abs(worldPos(actor).x - point.x) <= half && Math.abs(worldPos(actor).z - point.z) <= half);
  if (!removing.length) return {ok:false,reason:'No map pieces in this brush.'};
  return stCreatorTransaction('Erase ' + removing.length + ' map pieces', () => {
    for (const actor of removing) stCreatorRemoveActor(actor);
    return {ok:true,count:removing.length};
  });
}
function stCreatorOutline(point) {
  stCreatorDisposeGraphic(stCreator.helper); stCreator.helper = null;
  if (!point || stCreator.tool === 'select') return;
  const type = stCreator.tool, cells = stCreator.cells;
  let halfX = 1.5 * cells, halfZ = halfX;
  if (type === 'st-wall' || type === 'st-ramp') {halfX = 1.2; halfZ = 3;}
  if (type === 'st-zone') {halfX = halfZ = 3 * cells;}
  if (type === 'st-pen') {halfX = halfZ = 5;}
  if (['st-sheep','st-wolf','st-tree','st-rock','st-thorn'].includes(type)) {halfX = halfZ = type === 'st-wolf' ? .68 : type === 'st-sheep' ? .27 : 1.7;}
  const angle = stCreator.rotation;
  const extentX = Math.abs(Math.cos(angle)) * halfX + Math.abs(Math.sin(angle)) * halfZ;
  const extentZ = Math.abs(Math.sin(angle)) * halfX + Math.abs(Math.cos(angle)) * halfZ;
  const valid = Math.abs(point.x) + extentX <= stRules().bounds && Math.abs(point.z) + extentZ <= stRules().bounds;
  const vertices = [[-halfX,-halfZ],[halfX,-halfZ],[halfX,halfZ],[-halfX,halfZ]].map(([x,z]) =>
    new THREE.Vector3(point.x + Math.cos(angle)*x + Math.sin(angle)*z,.14,point.z - Math.sin(angle)*x + Math.cos(angle)*z));
  const line = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(vertices),
    new THREE.LineBasicMaterial({color:type === 'erase' || !valid ? 0xff947f : 0xa9ffab,depthTest:false}));
  line.renderOrder = 101; line.userData.sheepTagCreatorHelper = true; scene.add(line); stCreator.helper = line;
}
function stCreatorInspectPath(payload = {}) {
  if (typeof stInspectPath !== 'function') return {ok:false,reason:'Route inspection is not available.'};
  const validPoint = point => Array.isArray(point) && [2,3].includes(point.length) && point.every(value => typeof value === 'number' && Number.isFinite(value));
  if (!validPoint(payload.from) || !validPoint(payload.to)) return {ok:false,reason:'Choose a finite start and destination on the map.'};
  const results = ['sheep','wolf'].map(species => stInspectPath({...payload,species}));
  stCreatorDisposeGraphic(stCreator.paths); stCreator.paths = new THREE.Group();
  stCreator.paths.name = 'Sheep and wolf route comparison'; stCreator.paths.userData.sheepTagCreatorHelper = true;
  results.forEach((result,index) => {
    const points = result.points || result.path || [];
    const from = result.from || payload.from, to = result.to || payload.to;
    const list = result.reachable && points.length ? points : [from,to];
    const vectors = list.map(point => new THREE.Vector3(point[0],(point.length === 3 ? point[1] : 0)+.20+index*.06,point[point.length === 3 ? 2 : 1]));
    const material = result.reachable ? new THREE.LineBasicMaterial({color:index ? 0xffa08c : 0x83ffc0,depthTest:false}) :
      new THREE.LineDashedMaterial({color:index ? 0xffa08c : 0x83ffc0,dashSize:.45,gapSize:.3,depthTest:false});
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(vectors),material);
    if (!result.reachable) line.computeLineDistances(); line.renderOrder = 102; stCreator.paths.add(line);
  });
  scene.add(stCreator.paths);
  stCreatorMessage(results.map(result => (result.species === 'wolf' ? 'Wolf' : 'Sheep') + ': ' +
    (result.reachable ? 'route open' + (Number.isFinite(result.length) ? ' · ' + result.length.toFixed(1) + ' m' : '') : result.reason || 'route blocked')).join(' | ') +
    '. Dashed lines are blocked. These route marks are never saved.');
  return {ok:results.every(result => result.ok !== false),results};
}

// This portable map schema accepts only curated objects and flat game settings.
// No user components, blueprints, scripts or native project payloads are imported.
function stCreatorValidateMap(input) {
  try {
    if (typeof input === 'string') {
      if (input.length > 2000000) throw new Error('Map files must be smaller than 2 MB.');
      input = JSON.parse(input);
    }
    const object = (value,label) => {
      if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(label + ' must be an object.');
      return value;
    };
    const keys = (value,allowed,label) => {
      for (const key of Object.keys(value)) if (!allowed.includes(key)) throw new Error(label + ' contains an unsupported field: ' + key + '.');
    };
    const finite = (value,label,min,max) => {
      if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw new Error(label + ' is outside its allowed range.');
      return value;
    };
    const text = (value,fallback,max = 90) => typeof value === 'string' ? value.replace(/[\u0000-\u001f\u007f]/g,'').trim().slice(0,max) || fallback : fallback;
    object(input,'Map'); keys(input,['schema','name','rules','layers','actors'],'Map');
    if (input.schema !== ST_CREATOR_SCHEMA) throw new Error('Choose a swyrl-sheep-tag-map-v1 file, or use native Load for a project file.');
    const rulesInput = object(input.rules || {},'Rules');
    for (const [key,value] of Object.entries(rulesInput)) {
      if (!ST_CREATOR_RULE_KEYS.has(key)) throw new Error('Unsupported Sheep Tag rule: ' + key + '.');
      if (Array.isArray(value)) {
        if (!['eventPool','permittedStructures'].includes(key) || value.length > 6 || value.some(item => typeof item !== 'string'))
          throw new Error('Invalid list for ' + key + '.');
        const allowed = key === 'eventPool' ? ['pressure','fog','supply'] : ['st-farm','st-income','st-fort','st-wall','st-ramp'];
        if (value.some(item => !allowed.includes(item))) throw new Error('Unsupported choice in ' + key + '.');
      } else if (!['number','boolean','string'].includes(typeof value) || typeof value === 'number' && !Number.isFinite(value))
        throw new Error('Invalid value for ' + key + '.');
    }
    const rules = stCleanRules(rulesInput), bounds = rules.bounds;
    if (!Array.isArray(input.layers) || input.layers.length > 32) throw new Error('Use at most 32 map layers.');
    const layers = input.layers.map((value,index) => {
      object(value,'Layer'); keys(value,['id','name','visible'],'Layer');
      if (typeof value.id !== 'string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(value.id)) throw new Error('Invalid layer ID.');
      if (value.visible !== undefined && typeof value.visible !== 'boolean') throw new Error('Invalid layer visibility.');
      return {id:value.id,name:text(value.name,'Layer ' + (index+1),64),visible:value.visible !== false};
    });
    if (new Set(layers.map(layer => layer.id)).size !== layers.length) throw new Error('Layer IDs must be unique.');
    if (!Array.isArray(input.actors) || input.actors.length < 3 || input.actors.length > 1500) throw new Error('Use between three and 1,500 map pieces.');
    const ids = new Set(), counts = {}, layerIds = new Set(layers.map(layer => layer.id));
    const mapActors = input.actors.map((value,index) => {
      object(value,'Map piece'); keys(value,['id','type','name','position','rotation','scale','layers','visible','baked'],'Map piece');
      if (!ST_CREATOR_TYPES.includes(value.type)) throw new Error('Unsupported map piece: ' + String(value.type) + '.');
      const id = typeof value.id === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(value.id) ? value.id : 'piece-' + index;
      if (ids.has(id)) throw new Error('Map piece IDs must be unique.'); ids.add(id); counts[value.type] = (counts[value.type] || 0) + 1;
      const vector = (array,label,min,max) => {
        if (!Array.isArray(array) || array.length !== 3) throw new Error(label + ' must have three values.');
        return array.map((number,axis) => finite(number,label + ' axis ' + axis,min,max));
      };
      const position = vector(value.position,'Position',-bounds,bounds);
      if (Math.abs(position[1]) > .05) throw new Error('Map pieces must start on the ground. Raised routes use wall and ramp pieces.'); position[1] = 0;
      const rotation = vector(value.rotation || [0,0,0],'Rotation',-10000,10000);
      if (Math.abs(rotation[0]) > .001 || Math.abs(rotation[2]) > .001) throw new Error('Map pieces rotate around their upright axis only.');
      rotation[1] = ((rotation[1] % (Math.PI*2)) + Math.PI*2) % (Math.PI*2);
      const scale = vector(value.scale || [1,1,1],'Scale',.25,16);
      if (['st-sheep','st-wolf'].includes(value.type) && scale.some(number => Math.abs(number - 1) > .001)) throw new Error('Creature spawns use their standard size so routes match collision.');
      if (['st-wall','st-ramp'].includes(value.type) && scale.some(number => Math.abs(number - 1) > .001)) throw new Error('Walls and ramps use their standard size so raised routes line up.');
      if (value.type !== 'st-meadow' && (scale[0] > 8 || scale[1] > 8 || scale[2] > 8)) throw new Error('Scenery pieces may be scaled up to eight times.');
      if (!Array.isArray(value.layers || []) || (value.layers || []).length > 8 || (value.layers || []).some(id => !layerIds.has(id))) throw new Error('Map piece refers to an unknown layer.');
      for (const key of ['visible','baked']) if (value[key] !== undefined && typeof value[key] !== 'boolean') throw new Error('Invalid ' + key + ' flag.');
      return {id,type:value.type,name:text(value.name,value.type.slice(3)),position,rotation,scale,layers:[...new Set(value.layers || [])],visible:value.visible !== false,baked:value.baked !== false};
    });
    if (!(counts['st-sheep'] >= 1 && counts['st-sheep'] <= 24)) throw new Error('The map needs one to 24 sheep spawns.');
    if (!(counts['st-wolf'] >= 1 && counts['st-wolf'] <= 8)) throw new Error('The map needs one to eight wolf spawns.');
    if (counts['st-pen'] !== 1) throw new Error('The map needs exactly one central wisp pen.');
    if ((counts['st-shop'] || 0) > 12 || (counts['st-meadow'] || 0) > 1) throw new Error('Use one meadow base and at most 12 merchants.');
    const usable = type => mapActors.some(actor => actor.type === type && actor.visible && actor.baked &&
      actor.layers.every(id => layers.find(layer => layer.id === id)?.visible !== false));
    if (!usable('st-sheep') || !usable('st-wolf') || !usable('st-pen')) throw new Error('At least one sheep, wolf and the pen must be visible and baked.');
    const checked = stAuthoredMapPreflight({rules,requireRoster:true,pieces:mapActors.map(actor => ({...actor,
      active:actor.visible && actor.baked && actor.layers.every(id => layers.find(layer => layer.id === id)?.visible !== false)}))});
    if (!checked.ok) throw new Error(checked.reason);
    return {ok:true,map:{schema:ST_CREATOR_SCHEMA,name:text(input.name,'My Sheep Tag map'),rules,layers,actors:mapActors},errors:[]};
  } catch (error) {return {ok:false,reason:String(error?.message || 'Invalid map file.'),errors:[String(error?.message || 'Invalid map file.')]};}
}
function stCreatorExportMap() {
  if (currentProject?.kind !== 'sheep-tag') return {ok:false,reason:'Open a Sheep Tag map first.'};
  if (stSession) return {ok:false,reason:'Stop the match before saving a portable map. Native Save still preserves the authored project.'};
  const source = projectData(), sourceLayers = source.editor?.layers || [];
  const layers = sourceLayers.map((layer,index) => ({id:'layer-' + index,name:String(layer.name || 'Layer').slice(0,64),visible:layer.visible !== false}));
  const layerMap = new Map(sourceLayers.map((layer,index) => [layer.id,layers[index].id]));
  const saved = source.scene.actors.filter(actor => ST_CREATOR_TYPES.includes(actor.type));
  const liveWorld = new Map();
  if (!stSession) for (const actor of actors) if (ST_CREATOR_TYPES.includes(actor.userData.actorType)) {
    actor.updateWorldMatrix(true,false); const p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3();
    actor.matrixWorld.decompose(p,q,s);
    const forward = new THREE.Vector3(0,0,1).applyQuaternion(q), up = new THREE.Vector3(0,1,0).applyQuaternion(q);
    const e = new THREE.Euler().setFromQuaternion(q);
    const rotation = Math.abs(up.x) < .0001 && Math.abs(up.z) < .0001 && up.y > .999 ?
      [0,Math.atan2(forward.x,forward.z),0] : [e.x,e.y,e.z];
    liveWorld.set(actor.userData.id,{position:p.toArray(),rotation,scale:s.toArray()});
  }
  const map = {schema:ST_CREATOR_SCHEMA,name:currentProject.name,rules:stRules(),layers,
    actors:saved.map((actor,index) => ({id:'piece-' + index,type:actor.type,name:actor.name,
      ...(liveWorld.get(actor.id) || {position:actor.position,rotation:actor.rotation,scale:actor.scale}),
      layers:(actor.editorLayerIds || []).map(id => layerMap.get(id)).filter(Boolean),visible:actor.manualVisible !== false,baked:actor.baked !== false}))};
  return stCreatorValidateMap(map);
}
function stCreatorImportMap(input) {
  if (!stCreatorAvailable()) return {ok:false,reason:'Stop a Sheep Tag match before importing a map.'};
  const checked = stCreatorValidateMap(input); if (!checked.ok) return checked;
  const map = checked.map;
  const base = structuredClone(ST_CANONICAL_PROJECT), layerIds = new Map(map.layers.map(layer => [layer.id,'layer-' + uid()]));
  // Construct a new native scene from allowlisted data rather than merging
  // arbitrary fields into an existing project or trusting incoming engine JSON.
  const native = {
    engine:base.engine,version:base.version,
    project:{name:map.name,template:'sheep-tag-meadow',canonicalId:'sheep-tag-meadow',kind:'sheep-tag',environment:'spatial-workspace',
      sheepTag:map.rules,workspaces:{schema:'swyrl-workspaces-v1',stations:{}},teleportZones:[],
      environmentSettings:{background:'#b5d9db',fogNear:130,fogFar:230,exposure:1.05,showTerrain:false,showScenery:false}},
    editor:{transformSpace:'world',snapEnabled:true,terrainSnapEnabled:true,viewMode:'lit',cameraView:'perspective',
      layers:map.layers.map(layer => ({id:layerIds.get(layer.id),name:layer.name,visible:layer.visible})),activeLayerId:layerIds.values().next().value || null},
    scene:{background:'#b5d9db',waveInterval:7,paths:{},actors:map.actors.map(actor => ({
      id:uid(),type:actor.type,name:actor.name,position:actor.position,rotation:actor.rotation,scale:actor.scale,
      baked:actor.baked,manualVisible:actor.visible,visible:actor.visible,
      editorLayerIds:actor.layers.map(id => layerIds.get(id)),folder:'Sheep Tag/Creator',groupParentId:null,groupChildIds:[]
    }))}
  };
  if (!native.scene.actors.some(actor => actor.type === 'st-meadow')) native.scene.actors.unshift({
    id:uid(),type:'st-meadow',name:'Map meadow',position:[0,0,0],rotation:[0,0,0],scale:[map.rules.bounds/40,1,map.rules.bounds/40],baked:true,manualVisible:true,editorLayerIds:[]
  });
  const result = stCreatorTransaction('Import Sheep Tag map', () => {loadProject(native,{preserveHistory:true,workspaceLocal:true});return {ok:true,count:map.actors.length};});
  if (result.ok) {stFrameMap(); stCreator.selection = []; stCreatorSyncRules(); $('stCreatorMapName').value = currentProject.name;}
  stCreatorMessage(result.ok ? 'Map imported. Native Undo restores your previous map.' : result.reason);
  return result;
}
function stCreatorDownloadMap() {
  const result = stCreatorExportMap();
  if (!result.ok) {stCreatorMessage(result.reason); return result;}
  const blob = new Blob([JSON.stringify(result.map,null,2)],{type:'application/json'}), url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url;
  link.download = currentProject.name.replace(/[^a-z0-9]+/gi,'-').slice(0,70) + '.sheep-tag-map.json';
  document.body.appendChild(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url),1000);
  stCreatorMessage('Saved a portable Sheep Tag map with its pieces, layers and rules.'); return result;
}
function stCreatorSyncRules() {
  if (!$('stCreatorFog')) return;
  const rules = stRules(); $('stCreatorFog').value = rules.fogMode || 'team';
  for (const key of ['thorns','totems','elevated','split','events']) $('stCreatorRule-' + key).checked = rules[key] === true;
  for (const input of $('stCreatorPanel').querySelectorAll('[data-st-permitted]'))
    input.checked = (rules.permittedStructures || ['st-farm','st-income','st-fort','st-wall','st-ramp']).includes(input.dataset.stPermitted);
}
function stCreatorApplyRules() {
  const patch = {fogMode:$('stCreatorFog').value,
    permittedStructures:[...$('stCreatorPanel').querySelectorAll('[data-st-permitted]:checked')].map(input => input.dataset.stPermitted)};
  for (const key of ['thorns','totems','elevated','split','events']) patch[key] = $('stCreatorRule-' + key).checked;
  const result = stConfigureRules(patch);
  stCreatorMessage(result.ok ? 'Map rules saved. Experimental choices remain adjustable in Rules & tuning.' : result.reason); return result;
}

function stInstallCreator() {
  if (stCreator.installed) return; stCreator.installed = true;
  const style = document.createElement('style'); style.id = 'stCreatorStyle';
  style.textContent = `#stCreatorLauncher{min-width:44px;min-height:44px;border-color:#899365;background:#243d2d;color:#edebc4}
  #stCreatorPanel{position:fixed;z-index:46;right:14px;top:110px;width:310px;max-height:calc(100dvh - 125px);overflow:auto;box-sizing:border-box;padding:14px;border:1px solid #a0a575;border-radius:12px;background:#182d23f7;box-shadow:0 12px 40px #0008;color:#e8efd3;font:12px/1.45 system-ui,sans-serif}
  #stCreatorPanel[hidden]{display:none!important}#stCreatorPanel header{display:flex;align-items:center;gap:6px}#stCreatorPanel h2{font:700 20px Georgia,serif;margin:0;flex:1;color:#f1d990}#stCreatorPanel p{margin:8px 0;color:#bdd1b7}#stCreatorPanel label{display:block;color:#c6d7bb}#stCreatorPanel button,#stCreatorPanel input,#stCreatorPanel select{box-sizing:border-box;min-height:44px;min-width:44px;color:#eef4da;border:1px solid #728362;border-radius:7px;background:#243c2d;padding:7px;font:inherit;touch-action:manipulation}#stCreatorPanel select,#stCreatorMapName{width:100%;margin:3px 0 7px}#stCreatorPanel button{cursor:pointer}#stCreatorPanel button:focus-visible,#stCreatorPanel input:focus-visible,#stCreatorPanel select:focus-visible{outline:2px solid #ebdc9b;outline-offset:2px}#stCreatorPanel .stc-row{display:flex;gap:7px;margin:7px 0}#stCreatorPanel .stc-row>*{flex:1;min-width:0}#stCreatorPanel .stc-row label{width:0}#stCreatorPanel .stc-actions{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:8px 0}#stCreatorPanel details{border-top:1px solid #49624b;padding-top:8px;margin-top:8px}#stCreatorPanel summary{min-height:44px;display:flex;align-items:center;cursor:pointer;color:#e6d596}#stCreatorPanel .stc-checks{display:grid;grid-template-columns:1fr 1fr;gap:4px}#stCreatorPanel .stc-checks label{display:flex;align-items:center;gap:5px;min-height:44px}#stCreatorPanel .stc-checks input{width:22px;min-width:22px;height:22px;min-height:22px;accent-color:#d4d796}#stCreatorFeedback{min-height:32px;color:#f0dda3;margin-top:8px;font-size:11px}#stCreatorPanel small{font-size:10px;color:#a6c09e}#stCreatorPlay{background:#6b7440!important;border-color:#d5cc88!important;color:#fff4c2!important}
  @media(max-width:620px){.topbar #stCreatorLauncher:not(.hidden){display:block!important;min-height:44px;font-size:10px;padding:4px}#stCreatorPanel{right:6px;left:6px;top:auto;bottom:6px;width:auto;max-height:52dvh;padding:11px}#stCreatorPanel h2{font-size:18px}#stCreatorPanel .stc-row{margin:5px 0}#stCreatorPanel .stc-actions{grid-template-columns:1fr 1fr}#stCreatorPanel p{font-size:11px}}
  `; document.head.appendChild(style);
  const launcher = document.createElement('button'); launcher.id = 'stCreatorLauncher'; launcher.type = 'button';
  launcher.textContent = 'Map Creator'; launcher.title = 'Build and test a Sheep Tag map';
  const rulesButton = $('sheepTagRulesBtn');
  if (rulesButton) rulesButton.insertAdjacentElement('afterend',launcher); else $('playBtn').insertAdjacentElement('beforebegin',launcher);
  launcher.onclick = () => stCreator.open ? stCreatorClose() : stCreatorOpen();
  const panel = document.createElement('section'); panel.id = 'stCreatorPanel'; panel.hidden = true;
  panel.setAttribute('aria-label','Sheep Tag map creator');
  panel.innerHTML = `<header><h2>Sheep Tag Map Creator</h2><button id="stCreatorClose" type="button" aria-label="Close map creator">Close</button></header>
    <small id="stCreatorCount"></small><label>Map name<input id="stCreatorMapName" maxlength="90"></label>
    <label>Brush / tool<select id="stCreatorTool"><optgroup label="Paint terrain"><option value="st-grass">Grass</option><option value="st-earth">Earth</option><option value="st-road">Road</option></optgroup><optgroup label="Woodland & hazards"><option value="forest">Forest brush</option><option value="st-tree">Tree</option><option value="st-rock">Rock</option><option value="st-pond">Pond</option><option value="st-thorn">Thorn bush</option></optgroup><optgroup label="Spawns & landmarks"><option value="st-sheep">Sheep spawn</option><option value="st-wolf">Wolf spawn</option><option value="st-pen">Wisp pen · move existing</option><option value="st-shop">Merchant</option><option value="st-zone">No-build zone · walkable</option></optgroup><optgroup label="Structures"><option value="st-farm">Farm</option><option value="st-income">Income farm</option><option value="st-fort">Strong farm</option><option value="st-wall">Raised castle wall</option><option value="st-ramp">Ramp</option></optgroup><optgroup label="Inspect & revise"><option value="route">Compare sheep / wolf routes</option><option value="erase">Erase map pieces</option><option value="select">Pan / select · native editor</option></optgroup></select></label>
    <div class="stc-row"><label>Brush width<select id="stCreatorCells"><option value="1">1 cell · 3 m</option><option value="2">2 cells · 6 m</option><option value="3">3 cells · 9 m</option></select></label><label>Placement snap<select id="stCreatorSnap"><option value="3">3 m grid</option><option value="1.5">1.5 m grid</option><option value="0.15">Fine · 0.15 m</option></select></label></div>
    <div class="stc-row"><label>Orientation<select id="stCreatorRotation"><option value="0">North · 0°</option><option value="90">East · 90°</option><option value="180">South · 180°</option><option value="270">West · 270°</option></select></label><button id="stCreatorRotate" type="button">Rotate 90°</button></div>
    <p id="stCreatorHint"></p><div class="stc-actions"><button id="stCreatorPan" type="button">Pan / select</button><button id="stCreatorFrame" type="button">Frame map</button><button id="stCreatorUndo" type="button">Undo</button><button id="stCreatorRedo" type="button">Redo</button><button id="stCreatorClearRoute" type="button">Clear route marks</button><button id="stCreatorPlay" type="button">Playtest map</button></div>
    <details><summary>Map rules & experiments</summary><label>Fog / vision<select id="stCreatorFog"><option value="team">Shared team vision</option><option value="solo">Individual vision</option><option value="off">Fog off</option></select></label><div class="stc-checks"><label><input id="stCreatorRule-thorns" type="checkbox">Thorn sensing</label><label><input id="stCreatorRule-totems" type="checkbox">Stealth totems</label><label><input id="stCreatorRule-elevated" type="checkbox">Walls & ramps</label><label><input id="stCreatorRule-split" type="checkbox">Illusive Split</label><label><input id="stCreatorRule-events" type="checkbox">Warned events</label></div><p>Experimental mechanics and balance values are choices to playtest. Events use only your selected pool.</p><label>Allowed player structures</label><div class="stc-checks"><label><input data-st-permitted="st-farm" type="checkbox">Farm</label><label><input data-st-permitted="st-income" type="checkbox">Income farm</label><label><input data-st-permitted="st-fort" type="checkbox">Strong farm</label><label><input data-st-permitted="st-wall" type="checkbox">Castle wall</label><label><input data-st-permitted="st-ramp" type="checkbox">Ramp</label></div><div class="stc-row"><button id="stCreatorApplyRules" type="button">Apply choices</button><button id="stCreatorRules" type="button">Rules & tuning</button></div></details>
    <details><summary>Save / load</summary><p>Portable maps contain curated Sheep Tag pieces and rules. Native project files also retain the full editor.</p><div class="stc-actions"><button id="stCreatorExport" type="button">Save map file</button><button id="stCreatorImport" type="button">Load map file</button><button id="stCreatorSaveProject" type="button">Save project</button><button id="stCreatorLoadProject" type="button">Load project</button></div></details>
    <div id="stCreatorFeedback" role="status" aria-live="polite"></div><input id="stCreatorFile" type="file" accept=".json,application/json" hidden>`;
  document.body.appendChild(panel);
  panel.addEventListener('pointerdown',event => event.stopPropagation());
  panel.addEventListener('keydown',event => event.stopPropagation());
  $('stCreatorClose').onclick = () => stCreatorClose();
  $('stCreatorMapName').onchange = () => {
    const name = $('stCreatorMapName').value.replace(/[\u0000-\u001f\u007f]/g,'').trim().slice(0,90);
    if (!name) {$('stCreatorMapName').value = currentProject.name; return;}
    const result = stCreatorTransaction('Rename Sheep Tag map', () => {applyProjectMeta({...currentProject,name});return {ok:true};});
    stCreatorMessage(result.ok ? 'Map renamed.' : result.reason);
  };
  $('stCreatorTool').onchange = () => {stCreator.tool = $('stCreatorTool').value;stCreatorClearHelpers();stCreatorUpdateInteraction();};
  $('stCreatorCells').onchange = () => {stCreator.cells = Number($('stCreatorCells').value);stCreatorDisposeGraphic(stCreator.helper);stCreator.helper = null;stCreatorUpdateInteraction();};
  $('stCreatorSnap').onchange = () => {stCreator.snap = Number($('stCreatorSnap').value);};
  $('stCreatorRotation').onchange = () => {stCreator.rotation = Number($('stCreatorRotation').value)*Math.PI/180;};
  $('stCreatorRotate').onclick = () => {$('stCreatorRotation').value = String((Number($('stCreatorRotation').value)+90)%360);$('stCreatorRotation').onchange();};
  $('stCreatorPan').onclick = () => {$('stCreatorTool').value = 'select';$('stCreatorTool').onchange();};
  $('stCreatorFrame').onclick = () => {stFrameMap();stCreatorUpdateInteraction();};
  for (const [id,native] of [['stCreatorUndo','undoBtn'],['stCreatorRedo','redoBtn']]) $(id).onclick = () => {
    // Native history reloads the scene and its view mode. Keep the creator's
    // working camera so undoing a brush does not lose the next painting site.
    const view={object:camera,kind:editorCameraView,position:camera.position.clone(),quaternion:camera.quaternion.clone(),
      up:camera.up.clone(),target:orbit.target.clone(),fov:perspectiveCamera.fov,enableRotate:orbit.enableRotate,fog:scene.fog?.clone()||null};
    $(native).click();stCreatorClearHelpers();stCreatorRefresh();stCreatorSyncRules();stCreator.selection = [];
    setActiveCamera(view.object);editorCameraView=view.kind;camera.position.copy(view.position);camera.quaternion.copy(view.quaternion);
    camera.up.copy(view.up);orbit.target.copy(view.target);perspectiveCamera.fov=view.fov;perspectiveCamera.updateProjectionMatrix();orbit.update();
    orbit.enableRotate=view.enableRotate;scene.fog=view.fog;$('cameraView').value=view.kind;updateViewLabel();
    $('stCreatorMapName').value = currentProject.name;stCreatorUpdateInteraction();stCreatorMessage(native === 'undoBtn' ? 'Native Undo applied.' : 'Native Redo applied.');
  };
  $('stCreatorClearRoute').onclick = () => {stCreatorClearPaths();stCreatorMessage('Route marks cleared.');};
  $('stCreatorPlay').onclick = () => {
    const checked = stCreatorExportMap();
    if (!checked.ok) {stCreatorMessage(checked.reason);return;}
    if (!stCreatorApplyRules().ok) return;
    $('playBtn').click();
  };
  $('stCreatorApplyRules').onclick = stCreatorApplyRules;
  $('stCreatorRules').onclick = () => {stCreatorClose();stUiOpenRules();};
  $('stCreatorExport').onclick = stCreatorDownloadMap;
  $('stCreatorImport').onclick = () => {$('stCreatorFile').value = '';$('stCreatorFile').click();};
  $('stCreatorFile').onchange = async event => {
    const file = event.target.files?.[0]; if (!file) return;
    if (file.size > 2000000) {stCreatorMessage('Map files must be smaller than 2 MB.');return;}
    try {stCreatorImportMap(await file.text());} catch {stCreatorMessage('This map file could not be read.');}
  };
  $('stCreatorSaveProject').onclick = () => $('saveBtn').click();
  $('stCreatorLoadProject').onclick = () => {stCreatorClose();$('loadBtn').click();};
  const viewport = $('viewport');
  const pointAt = event => stCreatorPoint(stUiGround(event.clientX,event.clientY));
  const intercept = event => {event.preventDefault();event.stopImmediatePropagation();};
  const stamp = point => {
    if (!point || stCreator.strokeCount >= 80) return;
    if (stCreator.lastStamp && Math.hypot(point.x-stCreator.lastStamp.x,point.z-stCreator.lastStamp.z) < Math.max(.14,stCreator.snap*.8)) return;
    stCreator.lastStamp = point;stCreator.strokeCount++;
    const result = stCreator.tool === 'erase' ? stCreatorErase(point) : stCreatorPaint(point);
    stCreatorMessage(result.ok ? (stCreator.tool === 'erase' ? 'Removed ' : 'Placed ') + result.count + ' map piece' + (result.count === 1 ? '.' : 's.') : result.reason);
  };
  viewport.addEventListener('pointerdown',event => {
    if (!stCreator.open || !stCreatorAvailable() || stCreator.tool === 'select' || event.button > 0) return;
    intercept(event);const point = pointAt(event);if (!point) return;
    viewport.setPointerCapture?.(event.pointerId);stCreator.pointer = event.pointerId;
    stCreator.lastStamp = null;stCreator.strokeCount = 0;stCreatorOutline(point);
    if (stCreator.tool === 'route') {
      if (!stCreator.routeFrom) {stCreator.routeFrom = [point.x,point.z];stCreatorMessage('Start marked. Tap the route destination.');}
      else {const from = stCreator.routeFrom;stCreator.routeFrom = null;stCreatorInspectPath({from,to:[point.x,point.z]});}
    } else stamp(point);
  },true);
  viewport.addEventListener('pointermove',event => {
    if (!stCreator.open || !stCreatorAvailable() || stCreator.tool === 'select') return;
    intercept(event);const point = pointAt(event);stCreatorOutline(point);
    if (event.pointerId === stCreator.pointer && stCreator.tool !== 'route') stamp(point);
  },true);
  const end = event => {
    if (event.pointerId !== stCreator.pointer) return;intercept(event);stCreator.pointer = null;
    if (viewport.hasPointerCapture?.(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  };
  viewport.addEventListener('pointerup',end,true);viewport.addEventListener('pointercancel',end,true);
  viewport.addEventListener('lostpointercapture',event => {if (event.pointerId === stCreator.pointer) stCreator.pointer = null;},true);
  window.addEventListener('keydown',event => {
    if (!stCreator.open) return;
    if (event.key === 'Escape') {event.preventDefault();event.stopImmediatePropagation();stCreatorClose();return;}
    if (event.target.closest?.('#stCreatorPanel')) return;
    if (stCreator.tool !== 'select' && !['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)) {
      if ((event.ctrlKey || event.metaKey) && ['z','y'].includes(event.key.toLowerCase())) {
        event.preventDefault();event.stopImmediatePropagation();
        $(event.key.toLowerCase() === 'y' || event.shiftKey ? 'stCreatorRedo' : 'stCreatorUndo').click();
      } else if (['w','e','r','Delete',' '].includes(event.key)) {event.preventDefault();event.stopImmediatePropagation();}
    }
  },true);
  const title = $('currentProjectName');
  if (title) new MutationObserver(stCreatorRefresh).observe(title,{childList:true,characterData:true,subtree:true});
  window.SWYRL_ENGINE_SHEEP_TAG_CREATOR = {
    schema:ST_CREATOR_SCHEMA,open:stCreatorOpen,close:() => stCreatorClose(),paint:stCreatorPaint,erase:stCreatorErase,
    inspectPath:stCreatorInspectPath,exportMap:stCreatorExportMap,validateMap:stCreatorValidateMap,importMap:stCreatorImportMap,
    state:() => ({open:stCreator.open,tool:stCreator.tool,cells:stCreator.cells,rotation:stCreator.rotation,snap:stCreator.snap,available:stCreatorAvailable()})
  };
  stCreatorRefresh();
}
