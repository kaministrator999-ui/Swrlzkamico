// §E v11.56 — monotone, editable native sculpt falloff control points.
// Opt-in five-node envelope at normalized distances [0,.25,.5,.75,1].
// Strictly preserve historical falloff behavior when no curve exists.
function atelierSculptCurveValid(curve){
 return curve===undefined||(
  Array.isArray(curve)&&curve.length===5&&curve.every((v,i)=>
   Number.isFinite(v)&&v>=0&&v<=1&&(i===0?v===1:i===4?v===0:true))&&
  curve.every((v,i)=>i===0||v<=curve[i-1])
 );
}
function atelierSculptCurveWeight(normalizedDistance,stroke){
 const curve=stroke.falloffCurve;
 if(!curve)return atelierSculptFalloff(normalizedDistance,stroke.falloff,
  stroke.plateau,stroke.taper);
 if(normalizedDistance<=0)return 1;
 if(normalizedDistance>=1)return 0;
 const k=normalizedDistance*4,i=Math.min(3,Math.floor(k)),t=k-i;
 const a=curve[i],b=curve[i+1];
 // Monotone smoothstep within each native knot interval. No overshoot,
 // ringing, negative influence or imported arbitrary function/eval.
 const w=t*t*(3-2*t);
 return a*(1-w)+b*w;
}
function atelierSculptCurveInput(){
 const text=String($m('SculptBrushCurveValues')?.value||'');
 const raw=text.split(',').map(s=>s.trim());
 if(raw.length!==3||raw.some(s=>s===''))return null;
 const knots=[1,...raw.map(Number),0];
 return atelierSculptCurveValid(knots)?knots:null;
}
function atelierSculptCurveRefresh(){
 const enabled=!!$m('SculptBrushCurveEnabled')?.checked;
 const values=$m('SculptBrushCurveValues');
 if(values)values.disabled=!enabled;
 const hint=$m('SculptBrushCurveInfo');
 if(hint)hint.textContent=enabled?
   'Edit three descending influence values, each 0–1. Distances: 0%, 25%, 50%, 75%, 100%. Full at center; zero at edge.':
   'Classic Smooth/Soft/Flat/Sharp and plateau/taper retain exact legacy behavior.';
}
function atelierSculptCurveInstall(){
 $m('SculptBrushCurveEnabled')?.addEventListener('change',atelierSculptCurveRefresh);
 atelierSculptCurveRefresh();
}
