"""§E v11.118 — semantic tool categories, informed by modeling-editor patterns.

Forward-only UI adjustments. Native buttons/fields retain original DOM identity,
event listeners, persisted values, edit history and source-of-truth behavior.
"""
from pathlib import Path
import json,hashlib

def once(html,old,new):
    n=html.count(old)
    assert n==1,(old[:150],n)
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    js=(root/'runtime/model_atelier_tool_arrange_v11_118.js').read_text(encoding='utf8')
    html=once(html,'function atelierAdaptiveInstall(panel){',
      js+'\nfunction atelierAdaptiveInstall(panel){')
    # The original GROUPS list is retained; relocate entries to their
    # appropriate category rather than creating parallel tool implementations.
    html=once(html,' const GROUP_META={',""" // Curated tool placement: objects, sculpting, topology, facial work,
 // materials and animation are distinct operations, not miscellaneous.
 GROUPS.Meshes[2]=['Mesh identity',['Name','Kind']];
 GROUPS.Meshes.push(['Model export',['Export','OBJ']]);
 GROUPS.Sculpt.splice(1,0,['Precision circle cut',[
  'BoreWhich','BoreRadius','BoreDepth','BoreCap','BoreRelocate',
  'BoreGizmoRadius','BoreGizmoDepth','BorePreview','BoreApply','BoreHide'
 ]]);
 GROUPS.Face.unshift(['Portrait & anatomy',
   ['PortraitFinish','HeadAnatomy','HeadSections','HeadApply']]);
 GROUPS.Appearance=[
  ['Materials & colors',['Material','Color']],
  ['Surface finish',['HDDetail','HDFinish']]
 ];
 const GROUP_META={""")
    for a,b in [
       ("Meshes:'Select mesh • transform • material'","Meshes:'Objects • select • transform • export'"),
       ("Sculpt:'Brush placement • shape • density'","Sculpt:'Brushes • precision cut • density'"),
       ("Face:'Landmarks • cutout • UV face'","Face:'Portrait • landmarks • cutout'"),
       ("Appearance:'Materials • detail • export'","Appearance:'Material • color • surface detail'"),
    ]:html=once(html,a,b)
    old=""" function detectGroup(id){
  if(/^Lasso/.test(id))return 'Lasso';
  if(/^Sculpt/.test(id)||/^Refine/.test(id))return 'Sculpt';
  if(/^Face/.test(id)||/^Portrait/.test(id)||/^Head/.test(id))return 'Face';
  if(/Topology|LOD|^UV|BoundaryCap|Audit/.test(id))return 'Topology';
  if(/^Reference/.test(id))return 'References';
  if(/Pose|Motion|Animation|Frame/.test(id))return 'Motion';
  return 'Appearance';
 }"""
    new=""" function detectGroup(id,fallback='Meshes'){
  const suffix=String(id||'').replace(/^modelAtelier/,'');
  if(/^(Lasso)/.test(suffix))return 'Lasso';
  if(/^(Bore|Sculpt|Refine|Density|Brush)/.test(suffix))return 'Sculpt';
  if(/^(Face|Portrait|Head)/.test(suffix))return 'Face';
  if(/^(Topology|AdaptiveTopology|LOD|RuntimeLOD|UV|BoundaryCap|Audit)/.test(suffix))return 'Topology';
  if(/^Reference/.test(suffix))return 'References';
  if(/^(Pose|Motion|Animation|Frame)/.test(suffix))return 'Motion';
  if(/^(Material|Color|Texture|Shading|HDDetail|HDFinish)/.test(suffix))return 'Appearance';
  if(/^(Parts|Add|Duplicate|Delete|Undo|Redo|position|rotation|scale|Name|Kind|Mesh|Transform|Component|Select|Group|Export|OBJ)/.test(suffix))return 'Meshes';
  return fallback;
 }"""
    html=once(html,old,new)
    old="""   const suffix=section.id.slice('modelAtelier'.length);
   const category=detectGroup(suffix),ids=unique(untracked.map(n=>n.id.slice('modelAtelier'.length)));
   catalog[category].push({name:titleFromId(section.id),ids});
   untracked.forEach(n=>tracked.add(n.id));"""
    new="""   const sectionName=section.id.slice('modelAtelier'.length);
   const sectionGroup=detectGroup(sectionName);
   const buckets={};
   for(const node of untracked){
    const id=node.id.slice('modelAtelier'.length);
    const category=detectGroup(id,sectionGroup);
    (buckets[category]??=[]).push(id);
    tracked.add(node.id);
   }
   for(const [category,rawIds] of Object.entries(buckets)){
    const ids=unique(rawIds);
    if(ids.length)catalog[category].push({name:titleFromId(section.id),ids});
   }"""
    html=once(html,old,new)
    # The three extra context categories are added at the end of v11.61.
    # Arrange all nine native rail controls after that installation,
    # preserving original click callbacks, favorites and custom sheet state.
    html=once(html,
      " // Inspector may change selection after native edits; refresh only displayed proxies.",
      " atelierToolRailArrange(panel);\n // Inspector may change selection after native edits; refresh only displayed proxies.")
    html=once(html,
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_117_EDITOR_NATIVE_CALLOUT_GUARD',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_118_SEMANTIC_TOOL_ORGANIZATION')
    for a,b in [
      ('ENGINE · MAKER v11.117','ENGINE · MAKER v11.118'),
      ('v11.117 · no browser hold menu','v11.118 · organized modeling tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.117'","window.SWRLZ_FORGE_BUILD={version:'v11.118'"),
      ('<title>§wyrl§ Engine · Maker v11.117</title>',
       '<title>§wyrl§ Engine · Maker v11.118</title>'),
    ]:html=once(html,a,b)
    prefix='const SE_RELEASE_NOTES='
    at=html.index(prefix)+len(prefix)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Model Atelier: semantic tool placement and thumb-friendly navigation',
      date='2026-10-25',changes=[
        'Order primary tool categories as Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion, References and More on phone and desktop.',
        'Keep circular cut radius/depth and precision gizmos in Sculpt instead of the old unclassified Appearance fallback.',
        'Place portrait/anatomy with Face, materials/colors with Appearance, and export with Meshes; retain all original buttons.',
        'Classify newly discovered tools by their own action ID and containing section, rather than dumping entire sections in Appearance.',
        'Preserve native control identities/listeners, reference tools, context presets, mobile favorites, inspector layouts and gestures.',
        'Preserve all previous mesh/scene data, 149 historical patches, 68 assets, explicit Apply/Undo and browser menu protections.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V11118_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
