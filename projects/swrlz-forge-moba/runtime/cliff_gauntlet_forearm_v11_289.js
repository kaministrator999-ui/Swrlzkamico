// §E v11.289 · short connected forearm / gauntlet, not a separate cuff mesh.
// Apply only to the existing Plain Hand Base / Smooth Cliff Hand generator.
const SE289_GAUNTLET_EXTENSION=.74;
function se289ExtendGauntletTopology(part){
 const topo=part?.topologyMesh,positions=topo?.positions;
 if(!positions||positions.length<300||positions.length%3)
  throw Error('Gauntlet requires the intact connected hand topology.');
 const jointY=1.28,baseY=.57,span=jointY-baseY;
 let originalMin=Infinity,originalMax=-Infinity,extendedMin=Infinity;
 for(let i=1;i<positions.length;i+=3){
  const y=positions[i];
  if(!Number.isFinite(y))throw Error('Non-finite native hand vertex');
  originalMin=Math.min(originalMin,y);originalMax=Math.max(originalMax,y);
 }
 if(!(originalMin>.3&&originalMin<.9&&originalMax>2.7))
  throw Error('Unexpected hand geometry bounds; refusing to reshape an unrelated model.');
 // Smooth monotonic y transformation: preserves palm, thumb and fingers.
 // The lower carpal segment lengthens by roughly 0.74 model units. A gentle
 // 9% flare toward the forearm end suggests the edge of a stone gauntlet.
 // The taper is sculpted into THE SAME original vertex buffer: no added
 // topology, overlapping rock shapes, thick bracelet, or 3D seam tubes.
 for(let i=0;i<positions.length;i+=3){
  const y=positions[i+1];
  const t=Math.max(0,Math.min(1,(jointY-y)/span));
  const eased=t*t*(3-2*t);
  const flare=1+.09*eased*eased;
  positions[i]*=flare;
  positions[i+1]=y-SE289_GAUNTLET_EXTENSION*eased;
  positions[i+2]*=1+.065*eased*eased;
  extendedMin=Math.min(extendedMin,positions[i+1]);
 }
 const added=originalMin-extendedMin;
 if(!(added>.60&&added<.81))throw Error('Gauntlet extension outside expected range');
 return {oldMinY:originalMin,newMinY:extendedMin,oldMaxY:originalMax,
  forearmExtension:added,vertices:positions.length/3,meshCount:1};
}
function se289ProjectGauntletUV(part){
 // One continuous stone-material layout across hand + new forearm. The old
 // fixed v=(y-.53)/2.96 would clamp the extension's texture to the bottom
 // pixels, creating a muddy untextured cuff.
 const topo=part.topologyMesh,p=topo.positions;
 let low=Infinity,high=-Infinity;
 for(let i=1;i<p.length;i+=3){low=Math.min(low,p[i]);high=Math.max(high,p[i]);}
 const uv=[];
 for(let i=0;i<p.length;i+=3){
  const x=p[i],y=p[i+1],z=p[i+2];
  const u=(x+1.52+.14*z)/2.35;
  const v=(y-low+.06+.04*z)/(high-low+.12);
  uv.push(Math.max(.002,Math.min(.998,u)),Math.max(.002,Math.min(.998,v)));
 }
 topo.uvs=uv;
 return uv.length/2;
}
window.SWYRL_ENGINE_CLIFF_GAUNTLET_289=Object.freeze({
 extension:SE289_GAUNTLET_EXTENSION,
 extend:se289ExtendGauntletTopology,
 remapUV:se289ProjectGauntletUV,
 geometry:'one connected skinned hand and forearm, textured rock detail'
});
