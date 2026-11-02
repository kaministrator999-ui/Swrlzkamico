// §E v11.219 · Floating Hand dorsal finger-rail contact geometry.
// One rail per non-thumb digit: mounted to the raised dorsal armor, crosses
// under both retention links, and ends in the back-of-fingertip socket.
// Kept parametric so four different finger lengths/splays align independently.
function se219FingerRailPoint(f,t){
 const h=f.to-f.from,endT=1-.085/h;
 const u=Math.max(0,Math.min(1,(t-.67)/(endT-.67)));
 const ease=u*u*(3-2*u);
 // Back-facing Z surface: on top of armor until the distal joint, then
 // conform toward the narrower terminal. Never a floating straight beam.
 const depth=-.196+.080*ease+f.z*.24;
 return [f.x+f.splay*t,f.from+h*t,depth];
}
function se219FingerRailPath(f){
 const h=f.to-f.from,endT=1-.085/h;
 return [.14,.27,.45,.60,.77,endT].map(t=>se219FingerRailPoint(f,t));
}
