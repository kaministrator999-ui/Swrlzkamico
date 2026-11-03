"""§E v11.244 — screenshot-driven Sheep Tag menu/grass/destroy frame fixes.
Append-only: preserve current Quest mappings, LAN authority and Particle Studio.
"""
from pathlib import Path
import json

def once(html,old,new,label):
    n=html.count(old)
    if n!=1: raise AssertionError(("v11.244 anchor",label,n,old[:135]))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/sheep_menu_blur_v11_244.css').read_text('utf8')
    js=(root/'runtime/sheep_removal_performance_v11_244.js').read_text('utf8')
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_243_PARTICLE_MOBILE_LAYOUT' in html
    html=html.replace('</head>','<style id="se244SheepMenuBlur">'+css+'</style>\n</head>',1)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=','native game wrappers')

    # Small authored swatch is not a true seamless scan. Add actual organic
    # fine meadow strokes at deterministic random world positions, once when
    # constructing the texture, only where its original base was vegetation.
    old='    ctx.putImageData(authored,0,0);\n    const material=original.clone();'
    new="""    ctx.putImageData(authored,0,0);
    // Thin 2D meadow sprigs, baked once: no alpha-sorted grass planes, extra
    // draw calls or XR frame-loop updates. This does not overwrite the paths.
    let sprigSeed=0x47ba2325;
    const sprigRand=()=>{
      sprigSeed^=sprigSeed<<13;sprigSeed^=sprigSeed>>>17;
      sprigSeed^=sprigSeed<<5;
      return (sprigSeed>>>0)/4294967296;
    };
    const sprigs=quest?6500:12000;
    for(let n=0;n<sprigs;n++){
      const x=(sprigRand()*size)|0,y=(sprigRand()*size)|0;
      const k=(y*size+x)*4;
      const meadow=Math.max(0,Math.min(1,((authored.data[k+1]-authored.data[k])/
        Math.max(1,authored.data[k+1])-.025)*8));
      if(meadow<.36)continue;
      const len=(quest?1.4:2.3)+sprigRand()*(quest?1.2:1.7);
      const bend=(sprigRand()-.5)*len*.7;
      ctx.strokeStyle=sprigRand()<.46?'rgba(208,225,151,.18)':'rgba(23,80,41,.16)';
      ctx.lineWidth=.65+(size/2048)*.36;
      ctx.beginPath();ctx.moveTo(x,y);
      ctx.quadraticCurveTo(x+bend*.4,y-len*.6,x+bend,y-len);
      ctx.stroke();
    }
    const material=original.clone();"""
    html=once(html,old,new,'nonrepeating meadow sprigs')

    before=" source.engine='§wyrl§ Engine · Maker v11.243';source.version=11.243;"
    if html.count(before)!=2:raise AssertionError(('v11.244 provenance',html.count(before)))
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.244';source.version=11.244;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_243_PARTICLE_MOBILE_LAYOUT',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_244_SHEEP_MENU_GRASS_REMOVAL'),
      ('ENGINE · MAKER v11.243','ENGINE · MAKER v11.244'),
      ('v11.243 · Particle Studio mobile workspace cleanup',
       'v11.244 · Sheep Tag menu, grass and destruction performance'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.243'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.244'"),
      ('<title>§wyrl§ Engine · Maker v11.243</title>',
       '<title>§wyrl§ Engine · Maker v11.244</title>')
    ):html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag tighter menu, natural meadow sprigs and destruction frame pacing',
      date='2026-11-03',
      changes=[
        'Keep menu background and blur inside the actual title card, not in a larger rectangular overlay behind the whole menu; editable preview never shines through runtime menu.',
        'Add fine deterministic 2D meadow sprigs to vegetation on existing authored ground at material build time. Retain the original color, paths, normal, roughness and mipmapped Quest grass without repeating square patches.',
        'Immediately hide removed runtime buildings, but free their heavy mesh/material trees one per idle slice, rather than synchronously on the fatal sheep-capture frame.',
        'Coalesce navigation invalidations across a sheep losing many structures and stagger surviving bot path recomputes while respecting collision and immediate player control.',
        'Preserve author-owned structures, sheep gameplay and rescue semantics, LAN synchronization, original Quest controls, editor project saves and Particle Studio. Owner phone and Quest hardware checks remain pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
