/* SE390_MODEL_VR_HOTKEY_HINTS_START */
// Extend the existing controller-attached labels with live profile modifiers.
// No input dispatch, model mutation, renderer or additional frame loop lives here.
const se390PreviousHintLabel=se362CleanLabel;
se362CleanLabel=function(action,s){
 const placing=!!s.se390Creation||s.mode==='create';
 if(action==='create-menu')return 'Create menu';
 if(action==='duplicate')return 'Copy selection';
 if(action==='tool')return s.mode==='sculpt'?'Next brush':'Move / Rotate / Scale';
 if(action==='select'&&placing)return 'Place shape';
 if(action==='grab'&&s.mode==='grab')return 'Move + turn selected';
 if(action==='orbit'&&s.gesture?.mode==='grab')return 'Resize grabbed selection';
 if(action==='orbit'&&placing)return 'Size the new shape';
 if(action==='fine')return ['group','two-hand','extrude'].includes(s.gesture?.kind)
  ?s.gesture?.mode==='grab'?'Fine grab':'Fine transform':'';
 if(action==='cancel'&&placing)return 'Cancel placement';
 return se390PreviousHintLabel(action,s);
};
const se390PreviousCurrentBindings=se362CurrentBindings;
function se390ControllerBindingHints(s){
 const base=se390PreviousCurrentBindings(s),direct={...base.direct},secondary={...base.secondary};
 let profile=null;
 try{profile=window.SWYRL_VR_CONTROLS?.currentProfile?.();}catch(_){}
 const context=['sculpt','draw','lasso'].includes(s.mode)?'sculpt':'model';
 const rows=[...(profile?.bindings?.[context]||SE350_MODEL_VR_BINDINGS[context]||[]),...(profile?.bindings?.global||[])];
 const buttons=s.inputSample?.buttons||{},down=key=>!!buttons[key]?.down;
 const combinations=[],seen=new Set();
 const parse=binding=>{
  if(typeof binding!=='string')return null;
  try{
   const parsed=window.SWYRL_VR_CONTROLS?.inspectBinding?.(binding);
   if(parsed?.kind&&Array.isArray(parsed.buttons))return {kind:parsed.kind,keys:parsed.buttons};
  }catch(_){return null;}
  const match=/^(tap|hold|axis|chord):([A-Z+]+)$/.exec(binding);
  return match?{kind:match[1],keys:match[2].split('+')}:null;
 };
 for(const row of rows){
  if(!Array.isArray(row)||row.length<2)continue;
  const [action,binding]=row,p=parse(binding);if(!p||p.keys.length<2||!['hold','chord'].includes(p.kind))continue;
  const identity=p.kind+':'+p.keys.slice().sort().join('+');if(seen.has(identity))continue;seen.add(identity);
  const label=se362CleanLabel(action,s);if(!label)continue;
  const held=p.keys.filter(down),missing=p.keys.filter(key=>!down(key));
  combinations.push({action,binding,keys:p.keys.slice(),label,active:missing.length===0});
  // A held face modifier shows what its partner actually does. In particular,
  // the alternate-hand preset uses A+X/A+LT rather than hardcoded right-hand keys.
  if(p.kind==='chord'&&['create-menu','duplicate','redo'].includes(action)){
   const modifier=action==='create-menu'?(profile?.dominantHand==='left'?'A':'X'):
    p.keys.find(key=>key==='X'||key==='A')||p.keys[0];
   if(!down(modifier))continue;
   if(missing.length===1)direct[missing[0]]=label;
   else if(missing.length===0)for(const key of p.keys)direct[key]=label;
  }else if(action==='fine'&&p.kind==='hold'&&s.gesture&&held.length&&missing.length<=1){
   for(const key of missing)direct[key]='Hold for fine motion';
   if(!missing.length){
    for(const key of p.keys){
     const own=rows.find(r=>r?.[0]==='grab'&&parse(r[1])?.keys.length===1&&parse(r[1]).keys[0]===key);
     direct[key]=own?(s.gesture.mode==='grab'?'Move + turn · fine':'Transform · fine'):label;
    }
   }
  }
 }
 return {...base,context,direct,secondary,combinations};
}
se362CurrentBindings=se390ControllerBindingHints;
/* SE390_MODEL_VR_HOTKEY_HINTS_END */
