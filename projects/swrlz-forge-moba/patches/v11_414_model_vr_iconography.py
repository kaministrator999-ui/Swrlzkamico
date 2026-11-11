"""§E v11.414 — complete Model VR console iconography, append-only."""
import json

MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_414_MODEL_VR_ICONOGRAPHY'

def one(src, old, new):
    n = src.count(old)
    if n != 1:
        raise AssertionError(('v11.414 anchor', old[:90], n))
    return src.replace(old, new, 1)

ICON_ROUTING = """  // Preserve existing tool dispatch; customize only the pictogram for each control.
  const se414Icons={
   selector:'select','selector-sweep':'sweep','selector-lasso-front':'lasso-front',
   'selector-lasso-through':'lasso-through',projects:'folder',grab:'grab',
   'save-local':'save','save-account':'cloud','clone-project':'clone',
   'menu-reset':'reset-menu','menu-hide':'hide-menu','aim-hand':'controller',
   'aim-reset':'reset','aim-reset-all':'reset-both',
   'display-textured':'texture','display-solid':'solid',
   'display-wireframe':'wire','display-xray':'xray','display-normals':'normals'
  };
  if(se414Icons[id])return se414Icons[id];
  if(id.startsWith('view-'))return id;
  if(id.startsWith('aim-yaw-'))return 'yaw';
  if(id.startsWith('aim-pitch-'))return 'pitch';
"""

ICON_DRAW = """   if(type==='select'){path([[-19,-18],[-19,15],[0,5],[9,22],[16,18],[7,1],[21,-2],[-19,-18]],true);}
   else if(type==='sweep'){c.setLineDash?.([4,4]);rounded(c,-21,-17,42,31,5);c.stroke();c.setLineDash?.([]);path([[-16,19],[-4,8],[6,17],[19,3]]);}
   else if(type==='lasso-front'||type==='lasso-through'){c.setLineDash?.([4,4]);c.beginPath();c.ellipse?.(0,0,19,14,-.25,0,Math.PI*2);c.stroke();c.setLineDash?.([]);if(type==='lasso-through'){c.beginPath();c.ellipse?.(4,-3,12,20,.3,0,Math.PI*2);c.stroke();}else circle(0,0,5);}
   else if(type==='folder'||type==='clone'){path([[-21,-14],[-7,-14],[-2,-8],[21,-8],[21,15],[-21,15],[-21,-14]],true);if(type==='clone')path([[-13,-20],[8,-20],[13,-15]]);}
   else if(type==='save'){rounded(c,-19,-21,38,42,4);c.stroke();rounded(c,-10,-20,21,14,2);c.stroke();rounded(c,-12,5,24,16,2);c.stroke();path([[5,-20],[5,-8]]);}
   else if(type==='cloud'){c.beginPath();c.moveTo(-13,14);c.bezierCurveTo(-26,13,-24,-7,-12,-8);c.bezierCurveTo(-8,-28,15,-25,18,-9);c.bezierCurveTo(32,2,22,16,12,15);c.closePath();c.stroke();path([[0,18],[0,-6],[-7,1],[0,-6],[7,1]]);}
   else if(type==='reset-menu'||type==='hide-menu'){rounded(c,-21,-16,42,32,5);c.stroke();path([[-21,-6],[21,-6]]);if(type==='reset-menu'){c.beginPath();c.arc(1,4,9,-Math.PI*.65,Math.PI*.8);c.stroke();path([[-9,-5],[-10,4],[-1,1]]);}else{path([[-23,22],[23,-22]]);}}
   else if(type==='grab'){rounded(c,-12,-4,24,26,7);c.stroke();for(const x of [-9,-3,3,9])path([[x,-5],[x,-19]]);path([[13,10],[22,2],[22,-4]]);}
   else if(type==='controller'){rounded(c,-11,-19,22,31,9);c.stroke();circle(0,-9,4);path([[0,12],[0,22]]);path([[5,-9],[20,-17]]);}
   else if(type==='yaw'||type==='pitch'){c.save();if(type==='pitch')c.rotate(Math.PI/2);circle(0,0,7);c.beginPath();c.arc(0,0,19,-Math.PI*.75,Math.PI*.60);c.stroke();path([[-19,-16],[-19,-6],[-8,-9]]);c.restore();}
   else if(type==='reset-both'){rounded(c,-23,-11,18,26,5);c.stroke();rounded(c,5,-11,18,26,5);c.stroke();path([[-8,-21],[0,-16],[8,-21]]);}
   else if(type==='texture'){rounded(c,-20,-20,40,40,3);c.stroke();for(let y=0;y<2;y++)for(let x=0;x<2;x++)if((x+y)%2===0)c.fillRect(-20+x*20,-20+y*20,20,20);}
   else if(type==='xray'){path([[0,-20],[18,-10],[18,11],[0,21],[-18,11],[-18,-10],[0,-20]],true);path([[-18,-10],[0,0],[18,-10]]);c.setLineDash?.([3,3]);path([[0,0],[0,21]]);path([[-18,11],[18,-10]]);c.setLineDash?.([]);}
   else if(type==='solid'){path([[0,-20],[18,-10],[18,11],[0,21],[-18,11],[-18,-10],[0,-20]],true);path([[-18,-10],[0,0],[18,-10]]);path([[0,0],[0,21]]);c.globalAlpha=.30;path([[0,0],[18,-10],[18,11],[0,21]],true);c.globalAlpha=1;}
   else if(type.startsWith('view-')){const side=type.slice(5),tag={front:'F',back:'B',left:'L',right:'R',top:'T',bottom:'D',iso:'3D'}[side]||'V';path([[-18,-18],[18,-18],[18,18],[-18,18],[-18,-18]],true);c.font='700 23px system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText(tag,0,1);}
   else if(type==='rotate'){c.beginPath();c.arc(0,0,17,-Math.PI*.60,Math.PI*.13);c.stroke();c.beginPath();c.arc(0,0,17,Math.PI*.38,Math.PI*1.1);c.stroke();path([[16,-13],[18,2],[7,-1]]);path([[-16,13],[-18,-2],[-7,1]]);}
   else if(type==='eye'){"""

def enhance_ui(js):
    js = one(js, '/* SE410_MODEL_VR_ACCESSORY_UI */',
                '/* SE410_MODEL_VR_ACCESSORY_UI */\n/* SE414_MODEL_VR_ICONOGRAPHY */')
    js = one(js, ' function iconType(id){\n',
                ' function iconType(id){\n' + ICON_ROUTING)
    js = one(js, "  if(type==='eye'){", ICON_DRAW)
    # Unknown future controls show neutral adjustment sliders, never a '?'.
    js = one(js,
       "  else{circle(0,0,20);c.font='700 29px system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText('?',0,1);}",
       "   else{path([[-19,-14],[19,-14]]);path([[-19,0],[19,0]]);path([[-19,14],[19,14]]);circle(-6,-14,4);circle(8,0,4);circle(-3,14,4);}")
    # Paired adjustment controls need a + / - cue in addition to their common icon.
    js = one(js,
        "    else{icon(c,iconType(item.id),56,h*.39,43,ink);c.textAlign='left';",
        """    else{icon(c,iconType(item.id),56,h*.39,43,ink);
     if(/-(?:plus|minus)$/.test(item.id)){
      c.beginPath();c.arc(76,h*.24,17,0,Math.PI*2);
      c.fillStyle=disabled?'#334052':on?'#68513a':'#244c49';c.fill();
      c.strokeStyle=ink;c.lineWidth=2;c.stroke();
      c.beginPath();c.moveTo(68,h*.24);c.lineTo(84,h*.24);
      if(item.id.endsWith('-plus')){c.moveTo(76,h*.24-8);c.lineTo(76,h*.24+8);}c.stroke();
     }
     c.textAlign='left';""")
    return js

def apply(html):
    a = html.index('/* SE360_MODEL_VR_UI_START */')
    b = html.index('/* SE360_MODEL_VR_UI_END */',a) + len('/* SE360_MODEL_VR_UI_END */')
    html = html[:a] + enhance_ui(html[a:b]) + html[b:]
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_413_SATCHEL_VR_TUTORIAL',MARKER),
        ('ENGINE · MAKER v11.413','ENGINE · MAKER v11.414'),
        ('v11.413 · satchel modeling plus VR quest','v11.414 · readable Model VR icons'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.413'","window.SWRLZ_FORGE_BUILD={version:'v11.414'"),
        ('<title>§wyrl§ Engine · Maker v11.413</title>','<title>§wyrl§ Engine · Maker v11.414</title>')
    ]:
        html = one(html,old,new)
    old = " source.engine='§wyrl§ Engine · Maker v11.413';source.version=11.413;"
    assert html.count(old)==5, ('v11.414 provenance',html.count(old))
    html = html.replace(old," source.engine='§wyrl§ Engine · Maker v11.414';source.version=11.414;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.413','changes':notes.get('changes',[])})
    notes.update(version='v11.414',date='2026-11-11',
       title='Readable icons for Model Studio VR tools and controls',changes=[
        'Every existing Model VR tool card and navigation action retains its control binding, readable name and context guidance, now with explicit pictograms for selection, front/through lasso, save/account/clone, visibility, pointer calibration and each camera direction.',
        'Rotate uses a distinct rotate icon rather than sharing the Undo arrow. Solid, textured, wireframe and X-ray each have a recognizable display mark. Increment/decrement buttons receive prominent plus/minus cues.',
        'No change to controller mappings, tool transactions, world-space menu ownership, XR render loop, saved model schema or the satchel quest.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
