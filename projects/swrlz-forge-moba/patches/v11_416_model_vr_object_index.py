"""§E v11.416 — native VR Object Index and per-part silhouette, append-only."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_416_MODEL_VR_OBJECT_INDEX'

def one(src,old,new):
    count=src.count(old)
    if count!=1:
        raise AssertionError(('v11.416 patch anchor',old[:110],count))
    return src.replace(old,new,1)

def enhance_ui(js):
    js=one(js,'/* SE415_MODEL_VR_ICONOGRAPHY */',
           '/* SE415_MODEL_VR_ICONOGRAPHY */\n/* SE416_MODEL_VR_OBJECT_INDEX_UI */')
    js=one(js,"  const se414Icons={", """  if(id==='objects')return 'layers';
  if(id==='index-add')return 'multi';
  if(id==='index-prev')return 'left-arrow';
  if(id==='index-next')return 'right-arrow';
  if(id.startsWith('index-part-'))return 'cube';
  const se414Icons={""")
    js=one(js,"   if(type==='select'){", """   if(type==='layers'){for(const [x,y]of [[0,-12],[-3,0],[0,12]]){path([[-19+x,y],[0+x,y-10],[19+x,y],[0+x,y+10],[-19+x,y]],true);}}
   else if(type==='multi'){rounded(c,-20,-18,24,24,3);c.stroke();rounded(c,-7,-5,24,24,3);c.stroke();path([[5,-20],[5,-9]]);path([[-1,-14],[11,-14]]);}
   else if(type==='left-arrow'||type==='right-arrow'){c.save();if(type==='left-arrow')c.scale(-1,1);path([[-16,-13],[0,-13],[0,-21],[18,0],[0,21],[0,13],[-16,13]]);c.restore();}
   else if(type==='select'){""")
    js=one(js,"selectedCount:0,sculptTool:'push'", "selectedCount:0,indexEntries:[],indexSelected:[],indexTotal:0,indexPage:0,indexMulti:false,sculptTool:'push'")
    js=one(js,"  selector:[\n", "  objects:[],\n  selector:[\n")
    js=one(js,"const details={'accessory-menu':", """const details={objects:'All named meshes in the current project','index-add':'Toggle additive selection · up to 32 parts','index-prev':'Previous objects · same selection','index-next':'Next objects · same selection','accessory-menu':""")
    js=one(js,"const pageTitles={accessory:", "const pageTitles={objects:['Object Index','NAMES · SINGLE · MULTI · SILHOUETTE'],accessory:")
    js=one(js,"['projects','Projects'],['help','Guide']].forEach", "['projects','Projects'],['objects','Objects']].forEach")
    js=one(js," function enabled(id){if(id.startsWith('accessory-')", """ function enabled(id){
  if(id==='index-prev')return state.indexPage>0;
  if(id==='index-next')return state.indexPage<Math.ceil(state.indexTotal/9)-1;
  if(id.startsWith('accessory-')""")
    js=one(js," function active(item){const id=item.id;if(item.role==='nav'){", """ function active(item){const id=item.id;
  if(id==='index-add')return !!state.indexMulti;
  if(id.startsWith('index-part-')){const i=Number(id.slice(11))-state.indexPage*9;return state.indexSelected.includes(state.indexEntries[i]?.id);}
  if(item.role==='nav'){""")
    js=one(js," function label(item){if(item.id==='create-pouch'", """ function label(item){if(item.id==='index-add')return state.indexMulti?'Multi: ON':'Multi: OFF';if(item.id==='create-pouch'""")
    js=one(js," function description(item){if(item.id.startsWith('accessory-')", """ function description(item){
  if(item.id.startsWith('index-part-')){const i=Number(item.id.slice(11))-state.indexPage*9;return state.indexSelected.includes(state.indexEntries[i]?.id)?'SELECTED · Trigger to '+(state.indexMulti?'remove':'keep'):'Trigger · '+(state.indexMulti?'add to selection':'select only this');}
  if(item.id==='index-add')return state.indexMulti?'Add / remove named parts':'Select only one named part';
  if(item.id==='index-prev'||item.id==='index-next')return 'Page '+(state.indexPage+1)+' / '+Math.max(1,Math.ceil(state.indexTotal/9));
  if(item.id.startsWith('accessory-')""")
    js=one(js,"const helping=page==='guide',entries=wheelKind?wheels[wheelKind]:helping?[['help','Back to menu'],['exit','Exit VR']]:pages[page]||pages.tools;",
    """const helping=page==='guide';
  let entries=wheelKind?wheels[wheelKind]:helping?[['help','Back to menu'],['exit','Exit VR']]:pages[page]||pages.tools;
  if(page==='objects'&&!wheelKind&&!helping){
   const start=state.indexPage*9;
   entries=state.indexEntries.map((part,i)=>['index-part-'+(start+i),part.name||'Unnamed object']);
   while(entries.length<9)entries.push(['','']);
   entries.push(['index-add','Multi select'],['index-prev','Previous'],['index-next','Next']);
  }""")
    js=one(js,"const pageKey=wheelKind?'wheel-'+wheelKind:state.helpVisible?'guide':page;if(pageKey!==currentPage)installPage(pageKey);",
    """const pageKey=wheelKind?'wheel-'+wheelKind:state.helpVisible?'guide':page==='objects'?page+':'+state.indexPage+':'+state.indexEntries.map(e=>String(e.id)+'='+String(e.name)).join('|'):page;if(pageKey!==currentPage){installPage(pageKey.startsWith('objects:')?'objects':pageKey);currentPage=pageKey;}""")
    # The list signature must not be mistaken for a page identifier on reinstallation.
    js=one(js,"const count=Math.max(Number(state.selectedCount)||0,state.selectedName?1:0),radius=", "const count=Math.max(Number(state.selectedCount)||0,state.selectedName?1:0),radius=")
    js=one(js,"const context=accessoryPages.has(page)", """const context=page==='objects'?'OBJECTS '+state.indexTotal+' · PAGE '+(state.indexPage+1)+'/'+Math.max(1,Math.ceil(state.indexTotal/9))+' · '+count+' SELECTED':accessoryPages.has(page)""")
    js=one(js,"const controller=wheelKind?'Release off a card", """const controller=page==='objects'&&!wheelKind?'Trigger: select · Multi ON: add/remove · Next / Previous: browse':wheelKind?'Release off a card""")
    js=one(js,"inspect:()=>({width:WIDTH,height:HEIGHT,page:currentPage,", "inspect:()=>({width:WIDTH,height:HEIGHT,indexPage:state.indexPage,indexTotal:state.indexTotal,indexMulti:!!state.indexMulti,page:currentPage,")
    return js

def apply(html):
    start=html.index('/* SE360_MODEL_VR_UI_START */')
    end=html.index('/* SE360_MODEL_VR_UI_END */',start)+len('/* SE360_MODEL_VR_UI_END */')
    html=html[:start]+enhance_ui(html[start:end])+html[end:]
    helper=(ROOT/'runtime/model_vr_object_index_v11_416.js').read_text(encoding='utf8')
    assert helper.count('SE416_MODEL_VR_OBJECT_INDEX_START')==1
    html=one(html,'function se340SyncUI(){',helper+'\nfunction se340SyncUI(){')
    html=one(html,'  const state={selectedRegionId:', '  se416UpdateHighlights(s,entries,selectedIds);\n  const state={...se416IndexState(s,entries,selectedIds),selectedRegionId:')
    html=one(html,"const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;\n  if(action==='exit')",
            "const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;\n  if(action==='objects'||action.startsWith('index-'))return se416IndexAction(action,record);\n  if(action==='exit')")
    html=one(html,"['inspect','move','rotate','scale','undo','redo','focus'", "['objects','index-add','index-prev','index-next','inspect','move','rotate','scale','undo','redo','focus'")
    html=one(html,"  se345RestoreDisplay();\n  try{se340Bridge()?.releaseRoot?.();",
            "  se416DisposeHighlights(s);\n  se345RestoreDisplay();\n  try{se340Bridge()?.releaseRoot?.();")
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_415_MODEL_VR_ICONOGRAPHY',MARKER),
        ('ENGINE · MAKER v11.415','ENGINE · MAKER v11.416'),
        ('v11.415 · clearer Model VR icons','v11.416 · VR Object Index & mesh highlights'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.415'","window.SWRLZ_FORGE_BUILD={version:'v11.416'"),
        ('<title>§wyrl§ Engine · Maker v11.415</title>','<title>§wyrl§ Engine · Maker v11.416</title>')]:
        html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.415';source.version=11.415;"
    assert html.count(old)==5,('v11.416 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.416';source.version=11.416;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.415','changes':notes.get('changes',[])})
    notes.update(version='v11.416',date='2026-11-11',
        title='Model VR Object Index and selected-mesh silhouette highlighting',
        changes=[
        'Adds an Object Index tab showing the actual names of model parts, nine at a time, with Previous and Next paging.',
        'Trigger picks an object; Multi toggle switches to additive selection where tapping a chosen part removes it, preserving native 32-part selection rules.',
        'Selected parts receive individual backface silhouette shells; existing hover/transform and grouped bounds remain available without changing source geometry or saved documents.',
        'Object list is populated only when active and highlights are transient, tracked by mesh ownership and disposed on VR exit; no new XR loops or head-follow panels.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
