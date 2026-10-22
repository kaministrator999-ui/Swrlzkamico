"""Truthful building clearances, sanctuary protection and release-gated hunters."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    html=once(html,'function stRemember(observer,target){if(observer.isIllusion)return;',"function stRemember(observer,target){if(observer.isIllusion||!stHuntReleased()&&(observer.kind==='wolf'||target.kind==='wolf'))return;")
    html=once(html,'if(observer.id===target.id||observer.kind===target.kind)return true;',"if(!stHuntReleased()&&(observer.kind==='wolf'||target.kind==='wolf'))return false;if(observer.id===target.id||observer.kind===target.kind)return true;")
    html=once(html,"const s=stSession;if(!s||s.simulate||s.rules.fogMode==='off')return true;","const s=stSession;if(s&&!stHuntReleased()&&(entity.kind==='wolf'||role==='wolf'))return false;if(!s||s.simulate||s.rules.fogMode==='off')return true;")
    html=once(html,'function stUpdateVision(s,force=false){',"function stUpdateVision(s,force=false){\n  if(!stHuntReleased(s)){for(const u of s.units)if(u.kind==='wolf'){u.memory?.clear();u.order=null;u.path=[];u.destination=null;}for(const [id,m] of s.viewMemory)if(m.kind==='wolf'||s.role==='wolf')s.viewMemory.delete(id);}")
    html=once(html,"let viewers=s.units.filter(u=>u.kind===s.role&&!u.captured&&!u.isIllusion);", "let viewers=s.units.filter(u=>u.kind===s.role&&!u.captured&&!u.isIllusion&&(u.kind!=='wolf'||stHuntReleased(s)));")
    html=once(html,'function stArchiveScent(s,unit){','function stArchiveScent(s,unit){if(!stHuntReleased(s))return;')
    html=once(html,'if(unit.order)return;if(!unit.base)unit.base=stChooseBase(unit);',"if(unit.order)return;if(unit.base&&Math.hypot(unit.base.x-s.pen.x,unit.base.z-s.pen.z)<stSanctuaryRadius()+4.5)unit.base=null;if(!unit.base)unit.base=stChooseBase(unit);if(!unit.base){unit.aiIntent='seek clear building ground outside the sanctuary';return;}")
    html=once(html,'nav=stBuildNavigation(proposed,stUnitRadius(unit)),exits=', 'nav=s.rules.bounds>80?null:stBuildNavigation(proposed,stUnitRadius(unit)),exits=')
    html=once(html,'if(!exits.some(p=>stFindPath(nav,unit.pos,p)))continue;', 'if(!exits.some(p=>nav?stFindPath(nav,unit.pos,p):stVastFindPath(proposed,unit.pos,p,stUnitRadius(unit))))continue;')
    html=once(html,'if(stSegmentClear(context,start,target,radius))return [new THREE.Vector3(target.x,0,target.z)];', 'if(stSegmentClear(context,start,target,radius))return [new THREE.Vector3(target.x,0,target.z)];const portal=stClarityPortalRoute(context,start,target,radius);if(portal)return portal;')
    html=once(html,'stUiUpdateRings(state);','stUiUpdateRings(state);stClarityUpdateOverlay(state);')
    html=once(html,'function stDisposeUI() {','function stDisposeUI() {stClarityDisposeOverlay();')
    html=once(html,"type === 'st-wolf' ? .68 : type === 'st-sheep' ? .27", "type === 'st-wolf' ? .9 : type === 'st-sheep' ? .27")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",(root/'runtime/sheep_clarity_v11_81.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_80_VAST_WILDWOOD_WISPS','SWYRL_ENGINE_DEPLOY_MARKER: V11_81_SHEEP_CLEARANCE'),
      ('ENGINE · MAKER v11.80','ENGINE · MAKER v11.81'),
      ('v11.80 · vast woodland & captive wisps','v11.81 · clear paths & hidden hunters'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.80'","window.SWRLZ_FORGE_BUILD={version:'v11.81'"),
      ('<title>§wyrl§ Engine · Maker v11.80</title>','<title>§wyrl§ Engine · Maker v11.81</title>')
    ):html=once(html,old,new)
    return html
