"""v11.112: repeat existing stitched spherical subdivision twice so bowl stays round."""
import hashlib
import json

OLD_BLOCK = """ // One exact stitched subdivision pass keeps round lip/equator edges circular.
 const boundary=new Map();
 function tag(ring,cx,cy,r){
  for(let i=0;i<ring.length;i++)
   boundary.set(edge(ring[i],ring[(i+1)%ring.length]),{cx,cy,r});
 }
 tag(outer,0,0,radius);
 lip.forEach((r,k)=>tag(r,holes[k].x,holes[k].y,holes[k].r));
 const midpoint=new Map();
 function mid(a,b){
  const key=edge(a,b);
  if(midpoint.has(key))return midpoint.get(key);
  let x=(xy[a][0]+xy[b][0])/2,y=(xy[a][1]+xy[b][1])/2;
  const circle=boundary.get(key);
  if(circle){
   const dx=x-circle.cx,dy=y-circle.cy,len=Math.hypot(dx,dy);
   if(len<1e-9)throw Error('Collapsed radial edge');
   x=circle.cx+dx*circle.r/len;
   y=circle.cy+dy*circle.r/len;
  }
  const id=xy.length;xy.push([x,y]);midpoint.set(key,id);return id;
 }
 const children=[];
 for(const [a,b,c] of front){
  const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
  children.push([a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]);
 }
 front=children;
 function splitLoop(loop){
  const next=[];
  for(let i=0;i<loop.length;i++){
   next.push(loop[i],mid(loop[i],loop[(i+1)%loop.length]));
  }
  return next;
 }
 outer=splitLoop(outer);
 lip=lip.map(splitLoop);"""

NEW_BLOCK = """ // The earlier single pass produced huge triangles between finger lips
 // and the sphere equator. Their straight chords made a crumpled ball even
 // though the mesh was topologically valid. Run TWO independently stitched
 // passes, reproject every new surface midpoint to the exact sphere below.
 // Reset midpoint/boundary caches per level so loops remain consistently
 // shared with the actual exterior and drilled wall topology.
 const boundary=new Map(),midpoint=new Map();
 function tag(ring,cx,cy,r){
  for(let i=0;i<ring.length;i++)
   boundary.set(edge(ring[i],ring[(i+1)%ring.length]),{cx,cy,r});
 }
 function mid(a,b){
  const key=edge(a,b);
  if(midpoint.has(key))return midpoint.get(key);
  let x=(xy[a][0]+xy[b][0])/2,y=(xy[a][1]+xy[b][1])/2;
  const circle=boundary.get(key);
  if(circle){
   const dx=x-circle.cx,dy=y-circle.cy,len=Math.hypot(dx,dy);
   if(len<1e-9)throw Error('Collapsed radial edge');
   x=circle.cx+dx*circle.r/len;
   y=circle.cy+dy*circle.r/len;
  }
  const id=xy.length;xy.push([x,y]);midpoint.set(key,id);return id;
 }
 function splitLoop(loop){
  const next=[];
  for(let i=0;i<loop.length;i++){
   next.push(loop[i],mid(loop[i],loop[(i+1)%loop.length]));
  }
  return next;
 }
 for(let level=0;level<2;level++){
  boundary.clear();midpoint.clear();
  tag(outer,0,0,radius);
  lip.forEach((ring,k)=>tag(ring,holes[k].x,holes[k].y,holes[k].r));
  const children=[];
  for(const [a,b,c] of front){
   const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
   children.push([a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]);
  }
  front=children;
  outer=splitLoop(outer);
  lip=lip.map(splitLoop);
 }"""

def once(s,a,b):
    n=s.count(a)
    assert n==1,(a[:100],n)
    return s.replace(a,b,1)

def improve_js(s):
    s=once(s,OLD_BLOCK,NEW_BLOCK)
    s=once(s,' for(const tri of front)face(...tri);\n',
              ' for(const tri of front)face(...tri);\n const frontTriangleCount=front.length;\n')
    s=once(s,
      'return {ok:true,data,holes:number,vertices:positions.length/3,triangles:faces.length/3};',
      'return {ok:true,data,holes:number,vertices:positions.length/3,triangles:faces.length/3,frontTriangles:frontTriangleCount};')
    return s

def apply(html):
    html=once(html,OLD_BLOCK,NEW_BLOCK)
    html=once(html,' for(const tri of front)face(...tri);\n',
              ' for(const tri of front)face(...tri);\n const frontTriangleCount=front.length;\n')
    html=once(html,
      'return {ok:true,data,holes:number,vertices:positions.length/3,triangles:faces.length/3};',
      'return {ok:true,data,holes:number,vertices:positions.length/3,triangles:faces.length/3,frontTriangles:frontTriangleCount};')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_111_ROUND_BOWLING_HOLE_KIT',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_112_SMOOTH_ROUND_BALL_SURFACE')
    for old,new in [
      ('ENGINE · MAKER v11.111','ENGINE · MAKER v11.112'),
      ('v11.111 · actual round bowling holes','v11.112 · smooth round bowling ball'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.111'","window.SWRLZ_FORGE_BUILD={version:'v11.112'"),
      ('<title>§wyrl§ Engine · Maker v11.111</title>','<title>§wyrl§ Engine · Maker v11.112</title>'),
    ]:html=once(html,old,new)
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Smooth sphere curvature around drilled bowling-ball holes",
      date="2026-10-24",changes=[
        "Correct the jagged/folded sphere caused by coarse triangulation between round drilled mouths and the equator.",
        "Add a second conforming indexed midpoint-subdivision pass with exact spherical reprojection; keep smooth circular bore mouths and attached internal walls.",
        "Conserve the native portable 9000-vertex/16000-triangle cap and reject any invalid geometry before mutation.",
        "Preserve before-Apply preview, Undo, saved and exported topology, earlier organic sculpt tools, wireframe/shaded views and 68 bundled assets."
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
    raw=html.encode("utf-8")
    print("SWRLZ_V11112_BUILD_MEASURE",len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
