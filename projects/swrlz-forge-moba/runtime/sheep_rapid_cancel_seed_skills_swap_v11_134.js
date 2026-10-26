// §E v11.134 — rapid OFF cancels pending placement, every build tool
// selects a sheep-centered ghost, and both ability slots remain discoverable.
// Only affects §E Sheep Tag HUD; preserves native building safety/drag logic.

const st134RapidBase=st132SetRapid;
st132SetRapid=function(enabled){
 const was=st132Rapid;
 const result=st134RapidBase(enabled);
 if(was&&!st132Rapid){
  // Cancelling rapid mode also cancels the STILL-UNPLACED hologram.
  // Do not delete a constructed house or a successfully issued build order.
  if(stBuildInput.pointer!==null){
   stBuildInputFinish('Rapid build turned off');
  }else{
   stTouchPlacementReset('Rapid build turned off');
   stUi.build=null;stUi.buildingId=null;
   stUiClearPreview();stUi.placementPoint=null;
  }
  if(stSession&&stUi.shown)stRefreshHUD(true);
 }
 return result;
};

const st134SeedBase=st126SeedAtSheep;
st126SeedAtSheep=function(){
 const result=st134SeedBase();
 if(!result||!stUi.preview||!stUi.build||!stSession)return result;
 const controlled=stSession.units?.find(u=>u.id===stSession.controlledId);
 if(!controlled?.pos)return result;
 // The engine's snapping fit may offset an obstructed building footprint.
 // Here selection shows the GHOST at the sheep's actual position, not at a
 // snapped build site. Meadow drag then resumes native placement validation.
 stUi.preview.position.set(controlled.pos.x,0,controlled.pos.z);
 stUi.preview.visible=true;
 stUi.preview.updateMatrixWorld?.(true);
 return result;
};
stPlacementGridSeed=st126SeedAtSheep;

// A simple click/keyboard tap previously created an invisible mesh until the
// later pointer gesture fired. Seed on EVERY successful build selection.
const st134ChooseBase=stUiChooseBuild;
stUiChooseBuild=function(kind){
 const result=st134ChooseBase(kind);
 if(stSession&&stUi.build===kind&&stUi.preview)st126SeedAtSheep();
 return result;
};

// Keep Mirror and Totem present even if a custom project disables an ability.
// Active starter rules still govern casting; do NOT silently change a custom
// user's rule selection. A disabled icon explains what needs enabling.
const st134AbilitiesBase=stUiRefreshArchive;
stUiRefreshArchive=function(state,controlled,building,mayBuild,now){
 const result=st134AbilitiesBase(state,controlled,building,mayBuild,now);
 if(state?.role!=='sheep')return result;
 const rules=state.rules||stUiRules();
 for(const [id,enabled,name] of [
  ['stSplit',!!rules.split,'Mirror'],
  ['stTotem',!!rules.totems,'Totem']
 ]){
  const button=$(id);
  if(!button)continue;
  button.hidden=false;
  if(!enabled){
   button.disabled=true;
   button.title=name+' is disabled in this project\'s Sheep Tag rules';
   button.setAttribute('aria-label',name+' ability disabled · enable in Sheep Tag rules');
   button.classList.add('st134-rule-disabled');
  }else{
   button.classList.remove('st134-rule-disabled');
   if(button.title.includes('disabled in this project'))button.removeAttribute('title');
  }
 }
 return result;
};
