"""§E v11.263 — artist-supplied texture shapes for *live* nebula puffs.

The user supplied galaxy_transparent_layers.zip. Its alpha-mask passes
contain one shared RGB composition, NOT independently clean RGB assets.
We crop four smoke-only excerpts from 01_Nebula_Smoke and compact them as a
128px grayscale tile atlas to texture the existing camera-facing mist points.
The source image is NOT pasted as a billboard or a static galaxy.
No additional WebGL draw calls, native emitters, or update loops.
"""
import json

def once(src,old,new,reason):
    count=src.count(old)
    if count!=1: raise AssertionError(("v11.263",reason,count,old[:160]))
    return src.replace(old,new,1)

def apply(html):
    atlas_b64 = "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"
    assert len(atlas_b64)==3284
    atlas_code = """// Derived from owner-supplied galaxy_layers/01_Nebula_Smoke.png.
 // Four cropped feathered smoke textures packed into one 128px alpha atlas.
 // Decoded once; shader has a graceful analytic fallback while loading.
 const se263AtlasReady={value:0};
 const se263AtlasTexture=new THREE.TextureLoader().load(
  'data:image/png;base64,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',
  ()=>{se263AtlasReady.value=1;},undefined,
  error=>{console.warn('[§E] Nebula reference atlas unavailable, using fallback',error);}
 );
 se263AtlasTexture.magFilter=THREE.LinearFilter;
 se263AtlasTexture.minFilter=THREE.LinearMipmapLinearFilter;
 se263AtlasTexture.wrapS=THREE.ClampToEdgeWrapping;
 se263AtlasTexture.wrapT=THREE.ClampToEdgeWrapping;
 """
    atlas_code=atlas_code.replace("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",atlas_b64)
    html=once(html,"const MIST_N=54;","const MIST_N=54;\n"+atlas_code,
       "load tiny reference-derived smoke atlas once, with fallback")
    html=once(html,"'attribute float aMistSeed;',\n 'attribute vec3 aMistTint;',",
       "'attribute float aMistSeed;',\n 'attribute float aMistVariant;',\n 'attribute vec3 aMistTint;',",
       "new atlas tile index vertex attribute")
    assert html.count("'varying float vMistSeed;',")==2
    html=html.replace("'varying float vMistSeed;',",
       "'varying float vMistSeed;',\n 'varying float vMistVariant;',")
    html=once(html,
       "' vMistSeed=aMistSeed;vMistTint=aMistTint;',",
       "' vMistSeed=aMistSeed;vMistVariant=aMistVariant;vMistTint=aMistTint;',",
       "forward selected tile index to shader")
    html=once(html,
       "gl_PointSize=clamp(aMistSize*uMistPixels*(265.0/max(1.0,-mv.z)),3.0,76.0);",
       "gl_PointSize=clamp(aMistSize*uMistPixels*(510.0/max(1.0,-mv.z)),4.0,116.0);",
       "broader, still bounded smoke trails")
    html=once(html,
       "'uniform float uMistDensity;',",
       "'uniform float uMistDensity;',\n 'uniform sampler2D uMistAtlas;',\n 'uniform float uMistAtlasReady;',",
       "bind reference-derived grayscale alpha texture")
    html=once(html,
       """' float n=mn(p*3.1+drift+vec2(vMistSeed*9.0,vMistSeed*13.0));',
 ' float n2=mn(p*7.2-drift*.6+vec2(vMistSeed*21.0,4.2));',
 ' vec2 warped=p+vec2((n-.5)*.52,(n2-.5)*.43);',
 ' float radius=length(warped*vec2(.92,1.22));',
 ' float feather=1.0-smoothstep(.30,.79,radius);',
 ' float texture=smoothstep(.26,.63,.60*n+.40*n2);',
 ' float vein=(p.y-.18*sin(p.x*5.0+vMistSeed*14.0))*4.8;',
 ' float curl=exp(-vein*vein);',
 ' float cloudy=feather*(.30+.70*texture)*(.70+.30*curl);',
 ' float alpha=min(.37,cloudy*(.36+.21*n)*uMistDensity);',
 ' gl_FragColor=vec4(vMistTint*(1.28+.90*n),alpha);',""",
       """' vec2 tile=vec2(mod(vMistVariant,2.0),floor(vMistVariant*.5));',
 ' vec2 localUV=clamp(p*.46+.5,vec2(.02),vec2(.98));',
 ' float painted=texture2D(uMistAtlas,(tile+localUV)*.5).r;',
 ' float radius=length(p*vec2(.89,1.1));',
 ' float edge=1.0-smoothstep(.58,1.06,radius);',
 ' float fallback=(1.0-smoothstep(.15,.86,radius))*.23;',
 ' float wisp=mix(fallback,painted*2.2,uMistAtlasReady);',
 ' float shimmer=.88+.12*sin(uMistTime*.11+vMistSeed*13.0);',
 ' float alpha=clamp(wisp*edge*uMistDensity*shimmer,0.0,.48);',
 ' gl_FragColor=vec4(vMistTint*vec3(1.60,1.44,1.73),alpha);',""",
       "render textured feathering rather than noisy circular blobs")
    html=once(html,
       "const sizes=new Float32Array(MIST_N),seeds=new Float32Array(MIST_N),",
       "const sizes=new Float32Array(MIST_N),seeds=new Float32Array(MIST_N),variants=new Float32Array(MIST_N),",
       "allocate tile variation attribute")
    html=once(html,
       "sizes[i]=size;seeds[i]=seed;",
       "sizes[i]=size;seeds[i]=seed;variants[i]=i%4;",
       "interleave four smoke textures through the three short arms")
    html=once(html,
       "g.setAttribute('aMistSeed',new THREE.BufferAttribute(seeds,1));",
       "g.setAttribute('aMistSeed',new THREE.BufferAttribute(seeds,1));\n g.setAttribute('aMistVariant',new THREE.BufferAttribute(variants,1));",
       "upload static atlas tile selectors")
    html=once(html,
       "uMistTime:{value:0},uMistDensity:{value:1}}",
       "uMistTime:{value:0},uMistDensity:{value:1},\n   uMistAtlas:{value:se263AtlasTexture},uMistAtlasReady:se263AtlasReady}",
       "reuse one texture across violet/cyan shaders")
    html=once(html,
       "nebulaPuffsPerColor:MIST_N,starsPerArm:STARS,rendererCount:1,",
       "nebulaPuffsPerColor:MIST_N,atlasTiles:4,atlasSource:'owner nebula mask',starsPerArm:STARS,rendererCount:1,",
       "make texture integration inspectable")
    for marker in (
       "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
       "['nebulaDensity','Smoke density',.1,2,.05,1]",
       "const nextPoint=location(Math.min(1,u+.001)",
       "const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u)",
       "updateNebulaMist(rec.se251Nebula.mist,cfg,rec,origin);",
    ):
       assert marker in html,("v11.263 legacy",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.262';source.version=11.262;"
    assert html.count(old)==2,("v11.263 identity",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.263';source.version=11.263;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_262_BILLOWING_GALAXY_MIST",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_263_REFERENCE_TEXTURED_MIST"),
      ("ENGINE · MAKER v11.262","ENGINE · MAKER v11.263"),
      ("v11.262 · billowing camera-facing galaxy mist",
       "v11.263 · reference-textured nebula mist"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.262'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.263'"),
      ("<title>§wyrl§ Engine · Maker v11.262</title>",
       "<title>§wyrl§ Engine · Maker v11.263</title>")
    ):
       html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Reference-derived feathered galaxy smoke textures",
       date="2026-11-04",changes=[
       "Use the owner's separated galaxy ZIP as source material for four compact translucent nebula stroke textures, masked and cropped from 01_Nebula_Smoke.png.",
       "Apply the 128px grayscale smoke atlas to the existing batch of 54 camera-facing mist puffs per violet/cyan native emitter, preserving six short live spiral paths, stars, and the white core.",
       "Keep responsive real 3D particle geometry (not a flat composite image) and edit-mode smoke density, smoke spread, slow vortex motion, and per-emitter fault containment.",
       "Decode the tiny embedded asset once, use a simple fallback until it loads, and reuse the same renderer, emitters, update tick, and two mist draw calls. No network textures.",
       "Mobile browser and Quest hands-on acceptance required for texture appearance and frame performance."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
       separators=(",",":")).replace("</","<\\/")+html[at+width:]
