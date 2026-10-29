// §E v11.126 · Sheep-centered touch building, persistent world routes,
// and sheep magic available immediately with shorter repeat cooldowns.
// All changes reuse the existing build preview, native collision, world
// scene actor serialization, and Sheep Tag match-state mechanisms.
const ST126_ROUTES=Object.freeze([
 ['pinewatch','Pinewatch stone crossing',-52.5,-45],
 ['moonflower','Moonflower raised crossing',60,-52.5],
 ['amberglade','Amberglade stone crossing',-52.5,60]
]);
function st126RouteData(actor,type,id,name,x,z,angle=0){
 const piece=structuredClone(actor);
 piece.id=id;piece.name=name;piece.type=type;
 piece.position=[x,0,z];piece.rotation=[0,angle,0];piece.scale=[1,1,1];
 piece.baked=true;piece.visible=true;piece.manualVisible=true;
 piece.tags=['sheep-tag','permanent-world-route','indestructible'];
 piece.role='';piece.team='neutral';piece.folder='Sheep Tag/Permanent raised routes';
 piece.blueprintClass='SheepTag/'+type.slice(3);
 piece.components=['Transform','Scene','StaticMesh','Collider'];
 piece.colliderRadius=Math.hypot(1.2,3);
 piece.editorLayerIds=[piece.editorLayerIds?.[0]||'wildwood-layer-0'];
 piece.groupParentId=null;piece.groupChildIds=[];
 return piece;
}
function st126InstallStarterRoutes(){
 const project=typeof ST_CANONICAL_PROJECT==='undefined'?null:ST_CANONICAL_PROJECT;
 if(!project?.scene?.actors||project.project?.kind!=='sheep-tag')return 0;
 const actors=project.scene.actors,template=actors.find(a=>a.type==='st-rock'||a.type==='st-farm');
 if(!template)return 0;
 let created=0;
 for(const [id,title,x,z] of ST126_ROUTES){
  // Both ramp upper ends physically touch opposite ends of a 6m deck.
  for(const [piece,kind,dz,angle] of [
   ['south-ramp','st-ramp',6,0],
   ['center-deck','st-wall',0,0],
   ['north-ramp','st-ramp',-6,Math.PI]
  ]){
   const routeId='st-permanent-route-'+id+'-'+piece;
   if(actors.some(a=>a.id===routeId))continue;
   actors.push(st126RouteData(template,kind,routeId,title+' · '+piece,x,z+dz,angle));
   created++;
  }
 }
 if(created){
  const rule=project.project.sheepTag;
  if(rule){rule.elevated=true;rule.split=true;rule.totems=true;
   rule.splitUnlock=1;rule.splitCooldown=12;rule.totemLimit='cooldown';rule.totemCooldown=25;}
 }
 return created;
}
st126InstallStarterRoutes();
// A completed, authored walkway is still a normal walkable collision surface.
// Only world-prefab route IDs are protected; player buildings are untouched.
function st126PermanentRoute(building){
 return !!building&&(building.permanentRoute===true||
  (typeof building.id==='string'&&building.id.startsWith('st-permanent-route-')));
}
const st126BuildBase=stNewBuilding;
stNewBuilding=function(kind,x,z,owner,authored=null,rotation=0){
 const result=st126BuildBase(kind,x,z,owner,authored,rotation);
 if(result&&authored?.userData?.id?.startsWith('st-permanent-route-')&&
    (kind==='st-wall'||kind==='st-ramp')){
  result.permanentRoute=true;result.owner='world';result.progress=1;
  result.cost=0;result.attackFlash=0;
 }
 return result;
};
const st126DamageBase=stAttackBuilding;
stAttackBuilding=function(wolf,building){
 if(st126PermanentRoute(building))return;
 return st126DamageBase(wolf,building);
};
const st126RemoveBase=stRemoveBuilding;
stRemoveBuilding=function(building){
 if(st126PermanentRoute(building))return;
 return st126RemoveBase(building);
};
const st126CommandBase=stCommand;
stCommand=function(action,payload={}){
 if(['attack','sell','upgrade'].includes(action)&&stSession?.buildings?.some(
  b=>b.id===(payload.id||stSession.selectedId)&&st126PermanentRoute(b))){
  return stResult(false,'This finished world ramp or walkway is indestructible.');
 }
 return st126CommandBase(action,payload);
};
// Give all living sheep their archive abilities at round start when the
// preset enables them; do not override explicit Classic/off selections.
const st126ArchiveStartBase=stArchiveStart;
stArchiveStart=function(s){
 if(s?.rules){
  if(s.rules.split){s.rules.splitUnlock=1;s.rules.splitCooldown=Math.min(12,s.rules.splitCooldown||12);}
  if(s.rules.totems){s.rules.totemLimit='cooldown';s.rules.totemCooldown=Math.min(25,s.rules.totemCooldown||25);}
 }
 return st126ArchiveStartBase(s);
};
// The conversion still needs a COMPLETED owned house to target. It no longer
// requires building nine houses before the ability is usable.
stArchiveTotemReady=function(s,unit,building){
 return !!(s.rules.totems&&unit&&unit.kind==='sheep'&&!unit.captured&&!unit.isIllusion&&
   building&&building.owner===unit.id&&building.hp>0&&building.progress>=1&&
   ST_ARCHIVE_HOUSES.has(building.kind)&&building.kind!=='st-totem'&&
   (s.rules.totemLimit!=='once'||!unit.archiveTotemUsed)&&
   s.elapsed>=unit.archiveTotemAt+(s.rules.totemLimit==='cooldown'?s.rules.totemCooldown:0));
};
// Starting a build tool seeds the existing live ghost EXACTLY at your sheep.
// A later meadow drag/tap retains all the original aiming and safety checks.
function st126SeedAtSheep(){
 if(!stTouchPlacementEnabled()||!stUi.preview)return false;
 const unit=stSession.units.find(u=>u.id===stSession.controlledId);
 if(!unit?.pos)return false;
 const point=unit.pos.clone();point.y=terrainHeight(point.x,point.z);
 stUi.placementPoint=point.clone();
 stUiPlacePreview(point);
 return true;
}
stPlacementGridSeed=st126SeedAtSheep;
const st126StarterBase=stLoadStarter;
stLoadStarter=function(){
 st126InstallStarterRoutes();
 return st126StarterBase();
};
const st126StatusBase=stUiStatus;
stUiStatus=function(){
 const data=st126StatusBase();
 return {...data,permanentRoutes:stSession?.buildings.filter(st126PermanentRoute).map(
 b=>({id:b.id,kind:b.kind,hp:b.hp,progress:b.progress}))||[],
 sheepCenteredPlacement:!!(stUi.build&&stUi.placementPoint)};
};
