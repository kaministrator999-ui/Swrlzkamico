// §E v11.335 — owner-approved pinky-side palm silhouette correction.
// ONLY the Smooth Cliff Hand starter uses this SDF. No change to base hand,
// rigging, rock atlas, crystals, materials, other models or project schemas.
// The owner reference hand has a nearly straight ulnar edge under the pinky.
// Positive X is the pinky side. More POSITIVE sampling X pulls the surface
// inward on that side; multiplying X by < 1 would incorrectly widen it.
const se335UlnarDebug={builds:0,photoReference:'owner hand, pinky-side palm silhouette',
  maximumInwardShift:.105,meshObjectsAdded:0};
function se335NarrowUlnarField(math){
 const original=se334ReferenceHandField(math);
 const smooth=(a,b,x)=>{
  const t=Math.max(0,Math.min(1,(x-a)/(b-a)));
  return t*t*(3-2*t);
 };
 se335UlnarDebug.builds++;
 return (x,y,z)=>{
  // The hypothenar is too round between the lower pinky MCP and wrist.
  // A localized x-coordinate remap naturally compresses the right outline;
  // unlike a plane clip, it retains the smooth continuous SDF contour.
  // Fade before the wrist and before the knuckle/bone origins so that
  // articulation, finger widths and finger-root spacing remain unchanged.
  const lower=smooth(1.24,1.51,y);
  const upper=1-smooth(1.96,2.19,y);
  const onUlnarSide=smooth(.07,.49,x);
  const inward=.105*lower*upper*onUlnarSide;
  return original(x+inward,y,z);
 };
}
window.SWYRL_ENGINE_CLIFF_ULNAR_335=Object.freeze({
 status:()=>({...se335UlnarDebug,geometry:'one connected SDF gauntlet',
   affectedRegion:'pinky outer palm, y 1.24..2.19 only',
   thumbSideUntouched:true,wristAndKnuckleRootsPreserved:true})
});
