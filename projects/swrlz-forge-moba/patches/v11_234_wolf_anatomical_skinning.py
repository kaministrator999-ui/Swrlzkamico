"""§E v11.234: match Astra's 3D wolf skinning to its actual anatomy.

The original wolf skin weights were inferred from coarse fixed loci: fore
knees at y=.70 vs the authored organic leg bend at y=1.13, hind knees at
y=.55 vs y=.75, and a head anchor at y=2.12 vs skull centre y=2.43.
Worse, paws far from those old loci inherited large wolf_spine weights,
visibly stretching legs during run. This adjusts only the rigged Astra
Model Atelier preview/authoring path, not Sheep Tag gameplay or locomotion.
"""
import json


def once(s,old,new,why):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.234',why,n,old[:120]))
    return s.replace(old,new,1)


def apply(html):
    html=once(html,
      "{id:'wolf_neck',parent:'wolf_spine',rest:[0,1.83,.30]},\n  {id:'wolf_head',parent:'wolf_neck',rest:[0,2.12,.43]},\n  {id:'wolf_jaw',parent:'wolf_head',rest:[0,2.26,.83]},",
      "{id:'wolf_neck',parent:'wolf_spine',rest:[0,1.94,.30]},\n  {id:'wolf_head',parent:'wolf_neck',rest:[0,2.43,.43]},\n  {id:'wolf_jaw',parent:'wolf_head',rest:[0,2.25,.83]},",
      'head and neck joint rest alignment')
    html=once(html,
      """for(const [kind,x,y,z,lowerY] of [['hind',side*.35,1.04,-.61,.55],
                                    ['fore',side*.36,1.72,.42,.70]]){
   const joint='wolf_'+kind+'_'+label;
   bones.push({id:joint,parent:'wolf_spine',rest:[x,y,z]});
   bones.push({id:joint+'_knee',parent:joint,rest:[x,lowerY,z]});""",
      """for(const [kind,x,y,z,kneeX,kneeY,kneeZ] of [['hind',side*.34,1.18,-.61,side*.48,.75,-.43],
                                    ['fore',side*.29,1.72,.27,side*.33,1.13,.40]]){
   const joint='wolf_'+kind+'_'+label;
   bones.push({id:joint,parent:'wolf_spine',rest:[x,y,z]});
   bones.push({id:joint+'_knee',parent:joint,rest:[kneeX,kneeY,kneeZ]});""",
      'hind and fore elbow hock alignment')
    # Apply a region-local anatomical weighting scheme for the wolf only.
    # Original weight helpers for the hand and Sheep Tag game stay untouched.
    a=html.index('function se224WolfVertexWeights(pos,rig,part,indexById=null){')
    b=html.index('\n}\n',a)+2
    old=html[a:b]
    new="""function se224WolfVertexWeights(pos,rig,part,indexById=null){
 const [x,y,z]=pos,ids=indexById||Object.fromEntries(rig.bones.map((b,i)=>[b.id,i]));
 const pId=String(part?.id||'').toLowerCase(),region=String(part?.organicSurface?.region||'').toLowerCase();
 const named=String(part?.name||'').toLowerCase();
 const skin=new Map();
 const add=(id,weight)=>{if(weight>0&&ids[id]!==undefined)skin.set(id,(skin.get(id)||0)+weight);};
 const limb=pId.match(/(?:^|astra-fur-)(?:astra-living-)?(fore|hind)-(-?1)(?:-|$)/)||
            pId.match(/astra-living-(fore|hind)-(-?1)(?:-|$)/);
 if(limb){
  // Entire original limb, separately authored fur coat and claw meshes all
  // share their own limb bones. Do not pin toes back to the wolf's torso.
  const kind=limb[1],side=Number(limb[2])<0?'l':'r';
  const upper=kind==='fore'?1.72:1.18,knee=kind==='fore'?1.13:.75;
  const shoulder=(1-se224Ease((upper+.02-y)/.18))*.10;
  const lower=se224Ease((knee+.13-y)/.26);
  add('wolf_spine',shoulder);
  add('wolf_'+kind+'_'+side,(1-shoulder)*(1-lower));
  add('wolf_'+kind+'_'+side+'_knee',(1-shoulder)*lower);
 }else if(part?.wolf224Joint==='jaw'||region==='jaw'){
  add('wolf_jaw',1);
 }else if(part?.wolf224Joint==='head'||region==='face'||region==='muzzle'||
           named.includes('eye')||named.includes('ear ·')){
  add('wolf_head',1);
 }else{
  add('wolf_spine',1);
  const blend=(bone,amount)=>{
   amount=se224Saturate(amount);
   for(const [id,w] of skin)skin.set(id,w*(1-amount));
   add(bone,amount);
  };
  const neck=se224Ease((y-1.83)/.50)*se224Ease((z-.10)/.40);
  blend('wolf_neck',neck*.65);
  const head=se224Ease((y-2.15)/.34)*se224Ease((z-.14)/.42);
  blend('wolf_head',head);
  // Rear coat and tail accessories share one tail pivot. No artificial
  // upper-leg contribution to the torso's broad organic surface.
  const tail=se224Ease((-.78-z)/.40)*(1-se224Ease((y-1.26)/.8));
  blend('wolf_tail',tail);
 }
 const strongest=[...skin].filter(([,w])=>w>1e-6).sort((a,b)=>b[1]-a[1]).slice(0,4);
 const sum=strongest.reduce((n,[,w])=>n+w,0)||1;
 const indexes=strongest.map(([id])=>ids[id]),weights=strongest.map(([,w])=>w/sum);
 while(indexes.length<4){indexes.push(0);weights.push(0);}
 return {indexes,weights};
}"""
    html=once(html,old,new,'original wolf weight helper')
    # Make pose previews deterministic while dragging or when browser delays
    # frames. The native render loop remains the single renderer; no duplicate
    # RAF or WebGL workload is introduced. A paused preview samples cleanly.
    html=once(html,
      "se224WolfPreview.start=performance.now()/1000-se224WolfPreview.elapsed;",
      "se224WolfPreview.start=performance.now()/1000-se224WolfPreview.elapsed;\n  if(se224WolfPreview.playing)se224WolfPreviewFrame();",
      'immediate first preview sample')

    old=" source.engine='§wyrl§ Engine · Maker v11.233';source.version=11.233;"
    if html.count(old)!=2:raise AssertionError(('v11.233 project version sources',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.234';source.version=11.234;")
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_233_CHAT_NATIVE_STUDIO_BRIDGE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_234_WOLF_ANATOMICAL_SKINNING'),
      ('ENGINE · MAKER v11.233','ENGINE · MAKER v11.234'),
      ('v11.233 · Chat Studio Commands v1 reviewed native editing',
       'v11.234 · corrected Astra wolf skeletal deformation'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.233'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.233'"),
      ('<title>§wyrl§ Engine · Maker v11.233</title>',
       '<title>§wyrl§ Engine · Maker v11.234</title>')
    ]:
        html=once(html,a,b,'release identity')
    key='const SE_RELEASE_NOTES='
    i=html.index(key)+len(key)
    obj,n=json.JSONDecoder().raw_decode(html[i:])
    obj.update(
      title='Astra Wolf: anatomy-matched skin weights and motion preview',
      date='2026-11-02',
      changes=[
        'Correct Astra wolf foreleg and hind-leg joint positions to match the actual authored elbow/hock mesh points. Align head and neck pivots with the detailed skull.',
        'Bind each separately authored limb and fur/claw mesh to its own upper/lower limb bones, not the torso; preserve smooth bending at the knee/elbow without detached or stretched paws.',
        'Keep facial details attached to their head/jaw joints and restrict tail influence to rear coat/tail geometry. Preserve all original fur, equipment, facial materials and ten editable motion clips.',
        'Preview Play samples the first frame immediately, then uses the existing native animation/render loop (no second renderer or extra RAF). Verify motion without orbiting on owner phone.',
        'Only native wolf-model skeletal preview/authoring changes; Sheep Tag live wolf gameplay, navigation, character dimensions, saved projects and editor studios remain unchanged.',
        'Physical Moto/Quest motion quality and timing acceptance required; prior user-authored keys in saved model copies are not migrated.'
      ])
    return html[:i]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
