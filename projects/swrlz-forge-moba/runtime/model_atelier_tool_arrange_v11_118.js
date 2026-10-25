// §E v11.118 — intentional category order for desktop + thumb-friendly rail.
// Reorder existing native buttons in place. Never clone, delete or rebind tools.
function atelierToolRailArrange(panel){
 const rail=panel?.querySelector?.('#modelAtelierToolRail');
 if(!rail)return false;
 const order=['Meshes','Sculpt','Lasso','Topology','Face',
              'Appearance','Motion','References','More'];
 const descriptions={
  Meshes:'Objects, selection, transforms and groups',
  Sculpt:'Surface brushes and precision circular cuts',
  Lasso:'Region selection, masks and deformations',
  Topology:'Vertices, edges, faces, remeshing, UV and LOD',
  Face:'Portrait anatomy, facial landmarks and cutouts',
  Appearance:'Materials, colors and surface detail',
  Motion:'Posing, keyframes and animation',
  References:'Reference pictures and comparison views',
  More:'Original inspector and advanced settings'
 };
 const existing=Array.from(rail.querySelectorAll('button'));
 const name=b=>b.textContent.trim();
 // Keep currently installed controls, unknown extensions and listeners intact.
 for(const label of order){
  const node=existing.find(b=>name(b)===label);
  if(!node)continue;
  node.title=descriptions[label];
  node.dataset.atelierToolCategory=label;
  rail.append(node);
 }
 for(const button of existing){
  if(!order.includes(name(button)))rail.append(button);
 }
 rail.dataset.organized='v11.118';
 return true;
}
