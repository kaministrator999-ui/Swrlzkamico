"""256 m Sheep Tag world, central sheep starts, slow tethered captured wisps."""
import json
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    scene=json.loads((root/'scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json').read_text())
    prefix='const ST_CANONICAL_PROJECT=';start=html.index(prefix)+len(prefix);_,size=json.JSONDecoder().raw_decode(html[start:])
    html=html[:start]+json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    html=once(html,"const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-wildwood-v11-79.swyrl.json';","const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json';")
    js=(root/'runtime/sheep_vast_wisps_v11_80.js').read_text()
    html=once(html,'function stUpdateSheep(unit,dt){',js+'\nfunction stUpdateSheep(unit,dt){')
    start=html.index('  const s=stSession;if(unit.captured){if(unit.spiritOrder)',html.index('function stUpdateSheep(unit,dt){'))
    end=html.index('\n  if(unit.isIllusion)return;',start)
    html=html[:start]+'  const s=stSession;if(unit.captured){stUpdateCapturedWisp(unit,dt);return;}'+html[end:]
    html=once(html,'scene.add(unit.spirit);unit.spiritOrder=null;unit.rescueBy=',
              'scene.add(unit.spirit);unit.spiritHome=unit.spirit.position.clone();unit.wispReturns=0;unit.spiritOrder=null;unit.rescueBy=')
    html=once(html,'unit.captured=true;unit.actor.visible=false;',
              'unit.captured=true;unit.archiveOnUpper=false;unit.archiveHeight=undefined;unit.actor.visible=false;')
    html=once(html,"if(unit.captured){unit.spiritOrder={x:THREE.MathUtils.clamp(x,s.pen.x-s.pen.halfX+.8,s.pen.x+s.pen.halfX-.8),z:THREE.MathUtils.clamp(z,s.pen.z-s.pen.halfZ+.8,s.pen.z+s.pen.halfZ-.8)};return stResult(true,'Wisps stay in the spirit pen until rescued.');}",
              "if(unit.captured){unit.spiritOrder={x:THREE.MathUtils.clamp(x,-s.rules.bounds,s.rules.bounds),z:THREE.MathUtils.clamp(z,-s.rules.bounds,s.rules.bounds)};return stResult(true,'Wisps move slowly. Drift only a little outside the pen or return home; a living sheep must revive you.');}")
    html=once(html,'captured:u.captured,controlled:u.id===s.controlledId,order:',
              "captured:u.captured,wisp:u.captured?{speed:ST_WISP_MOTION.speed,outsideAllowance:ST_WISP_MOTION.outsideAllowance,returns:u.wispReturns||0,home:u.spiritHome?.toArray()||null}:null,controlled:u.id===s.controlledId,order:")
    html=once(html,"bounds:number('bounds',16,80)","bounds:number('bounds',16,160)")
    html=once(html,'function stFrameMap(){','function stFrameMap(){if(stRules().bounds>80)return stVastFrameMap();')
    html=once(html,'base.position.y=-.65;root.add(base);','base.position.y=-.65;stVastOpenGroundBase(base);root.add(base);')
    html=once(html,'function stPath(start,target,radius){return ',
              'function stPath(start,target,radius){if(stSession.rules.bounds>80)return stVastFindPath({rules:stSession.rules,obstacles:stObstacles()},start,target,radius);return ')
    html=once(html,'const route=stFindPath(stBuildNavigation(context,radius),from,to)',
              'const route=context.rules.bounds>80?stVastFindPath(context,from,to,radius):stFindPath(stBuildNavigation(context,radius),from,to)')
    html=once(html,'stSession.navVersion++;stSession.navigation.clear();','stSession.navVersion++;stSession.navigation.clear();stSession.vastNavigation?.clear();')
    # Extend the native textured meadow to either authored size; geometry stays
    # 80 m locally, using the saved floor transform and portable-map contract.
    html=once(html,"if(type==='st-meadow'&&stRules().bounds===64)","if(type==='st-meadow'&&[64,128].includes(stRules().bounds))")
    html=once(html,"stRules().bounds!==64)return;","![64,128].includes(stRules().bounds))return;")
    html=once(html,"regions:stRules().bounds===64?","regions:[64,128].includes(stRules().bounds)?")
    html=once(html,"if(bounds===64&&stWildwoodGroundTexture", "if([64,128].includes(bounds)&&stWildwoodGroundTexture")
    html=once(html,"stUiRules().bounds===64?'MOONBELL WILDWOOD'","[64,128].includes(stUiRules().bounds)?'MOONBELL WILDWOOD'")
    html=once(html,'128 × 128 m · Sheep Tag','256 × 256 m · Sheep Tag')
    html=once(html,'A captured sheep becomes a glowing wisp in the center pen. A free sheep must reach that wisp to rescue its teammate. Wisps cannot build.',
              'A captured sheep becomes a very slow wisp. You can drift a little outside the center pen, but going too far teleports you back. A living sheep must reach you to revive you. Wisps cannot build.')
    html=once(html,'Explore a 128 × 128 m woodland with four building glades, linked roads, hidden sheep passages and 4K ground artwork. Build, hunt and rescue with Astra hunters.',
              'A vast 256 × 256 m woodland. Sheep start together around the central sanctuary. Build far afield, hunt with Astra, and revive slow wandering wisps.')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_79_MOONBELL_WILDWOOD','SWYRL_ENGINE_DEPLOY_MARKER: V11_80_VAST_WILDWOOD_WISPS'),
      ('ENGINE · MAKER v11.79','ENGINE · MAKER v11.80'),
      ('v11.79 · Moonbell Wildwood','v11.80 · vast woodland & captive wisps'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.79'","window.SWRLZ_FORGE_BUILD={version:'v11.80'"),
      ('<title>§wyrl§ Engine · Maker v11.79</title>','<title>§wyrl§ Engine · Maker v11.80</title>')
    ):html=once(html,old,new)
    return html
