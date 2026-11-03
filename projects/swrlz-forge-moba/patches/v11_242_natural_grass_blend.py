"""§E v11.242 · Remove tiled checkerboard from the v11.241 Sheep Tag grass.
Owner Moto screenshot shows visible 16x16 square camouflage grass panels.
Preserve authored roads, underlying meadow art, PBR normal/roughness, and
current Quest + Particle Studio changes. Append-only targeted correction.
"""
import json

def once(s, old, new, label):
    n=s.count(old)
    if n!=1: raise AssertionError(("v11.242 natural grass anchor", label, n))
    return s.replace(old,new,1)

def apply(html):
    # Fewer, softer repeats; no replacement with high-contrast green square colors.
    html=once(html,"prepared:new WeakSet(),waiting:new WeakSet(),tileCount:16};",
                   "prepared:new WeakSet(),waiting:new WeakSet(),tileCount:8};","grass UV frequency")
    old="""      const blend=green*.75;
      d[i]=Math.round(d[i]*(1-blend)+s[i]*blend);
      d[i+1]=Math.round(d[i+1]*(1-blend)+s[i+1]*blend);
      d[i+2]=Math.round(d[i+2]*(1-blend)+s[i+2]*blend);"""
    new="""      // Keep original terrain palette/shape. The tiny grass swatch supplies
      // just low-contrast surface grain, never a patchwork of repeated colors.
      // Center its green luminance on the measured source-tile mean.
      const grain=(s[i+1]-102)/255;
      const modulation=1+green*grain*.14;
      d[i]=Math.max(0,Math.min(255,Math.round(d[i]*modulation)));
      d[i+1]=Math.max(0,Math.min(255,Math.round(d[i+1]*modulation)));
      d[i+2]=Math.max(0,Math.min(255,Math.round(d[i+2]*modulation)));"""
    html=once(html,old,new,"high-contrast albedo compositing")
    html=once(html,"material.normalScale.set(.24,.24); // subtle relief; no Quest stereo crawling",
                   "material.normalScale.set(.07,.07); // gentle relief; no large repetitive grass pattern","normal strength")
    before=" source.engine='§wyrl§ Engine · Maker v11.241';source.version=11.241;"
    after=" source.engine='§wyrl§ Engine · Maker v11.242';source.version=11.242;"
    if html.count(before)!=2:raise AssertionError(("v11.242 provenance",html.count(before)))
    html=html.replace(before,after)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_241_SHEEP_GRASS_PBR',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_242_SHEEP_NATURAL_GRASS'),
      ('ENGINE · MAKER v11.241','ENGINE · MAKER v11.242'),
      ('v11.241 · Sheep Tag full grass material','v11.242 · Natural grass without square tiling'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.241'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.242'"),
      ('<title>§wyrl§ Engine · Maker v11.241</title>',
       '<title>§wyrl§ Engine · Maker v11.242</title>')
    ):html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag grass smooth blending without green checkerboard',
       date='2026-11-03',
       changes=[
         'Fix owner-observed square bright/dark checkerboard caused by replacing 75 percent of authored ground colors with 16 repeated nonseamless mini swatches.',
         'Keep original vegetation hue and authored map art while applying only a mild, zero-centered grass detail modulation on green areas. Preserve roads, paths, sanctuary and team fog.',
         'Keep the actual MeshStandardMaterial base, normal, and roughness maps, but reduce the normal relief and tile frequency to prevent shimmering on Quest 2.',
         'No extra geometry, new render loop, gameplay/controller/building change, or edit to previous patch history. Owner phone and Quest 2 acceptance required.'
       ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
