"""New independent model projects, 4K native materials and portable textured GLB."""
from pathlib import Path
import json

def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 r=Path(__file__).resolve().parents[1]
 scene=json.loads((r/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())
 encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 js=(r/'runtime/model_atelier_courier_v11_77.js').read_text()
 html=once(html,'  function geometry(part){','  function atelierCourierBaseGeometry(part){')
 html=once(html,'function atelierSetPoseCamera(view){',"function atelierSetPoseCamera(view){\n if(['comet-courier','blank-model'].includes(currentProject?.canonicalId))return atelierCourierCamera(view);")
 html=once(html,'function material(part){','function atelierCourierBaseMaterial(part){')
 html=once(html,'  function refreshList(){',js+'\n  function refreshList(){')
 html=once(html,'  function checkPart(p){','  function checkPart(p){\n    if(!atelierCourierBindingValid(p))return false;')
 html=once(html,'atelierHeadAnatomyRefresh();','atelierHeadAnatomyRefresh();atelierCourierRefresh();')
 html=once(html,'atelierHeadAnatomyInstall();','atelierHeadAnatomyInstall();atelierCourierInstall();')
 deck='''<section id="modelAtelierAtlasDeck" hidden><h3>4K material atlas</h3><label>Surface region<select id="modelAtelierAtlasTile"><option value="none">No atlas</option>fur</option><option>ivory</option><option>cloth</option><option>leather</option><option>brass</option><option>comet</option><option>lapis</option><option>amber</option></select></label><label>Normal detail<input id="modelAtelierAtlasNormal" type="number" min="0" max="2" step=".05" value=".65"></label><button id="modelAtelierAtlasApply">Apply material atlas</button><p id="modelAtelierAtlasStatus"></p></section>'''.replace('<option>fur</option>','<option>fur</option>').replace('</option>fur</option>','</option><option>fur</option>')
 deck+='''<section id="modelAtelierGroupNameDeck" hidden><h3>Assembly name</h3><input id="modelAtelierGroupName" maxlength="100" aria-label="Assembly name"><button id="modelAtelierGroupRename">Rename assembly</button></section>'''
 html=once(html,'<section id="modelAtelierHeadAnatomy"',deck+'<section id="modelAtelierHeadAnatomy"')
 html=once(html,'<button id="modelAtelierOBJ">','<button id="modelAtelierCourierStudio" hidden aria-pressed="false">Studio view</button><button id="modelAtelierExportGLB">Export textured GLB</button><button id="modelAtelierOBJ">')
 loader='''
const COMET_COURIER_PROJECT='''+encoded+''';
function loadCourierProject(blank=false,force=false){
 if(dirty&&!force&&!confirm('Open a different model project and discard unsaved changes?'))return false;
 ModelAtelier.close();const data=structuredClone(COMET_COURIER_PROJECT);
 if(blank){data.project.name='Untitled Model';data.project.canonicalId='blank-model';data.project.template='blank-model';data.project.modelAtelier={schema:'swyrl-model-atelier-v1',name:'Untitled Model',parts:[{id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.5,.6,.8],color:'#ffffff',material:'silk',group:'Model'}],meshGroups:[],poseFrames:[],poseNeutral:null,editedAt:'local'};}
 loadProject(data,{workspaceLocal:true});initializeHistory('Opened independent model project');markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();const panel=document.getElementById('modelAtelierPanel'),studio=document.getElementById('modelAtelierCourierStudio');panel.classList.toggle('courier-studio',!blank);studio.hidden=blank;studio.textContent=blank?'Studio view':'Edit model';studio.setAttribute('aria-pressed',String(!blank));queueMicrotask(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three'));return true;
}
const courierPreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){if(template==='comet-courier'||template==='blank-model')return loadCourierProject(template==='blank-model',force);return courierPreviousTemplate(template,force);};
if(['comet-courier','blank-model'].includes(new URLSearchParams(location.search).get('project')))queueMicrotask(()=>loadCourierProject(new URLSearchParams(location.search).get('project')==='blank-model',true));
'''
 html=once(html,'  function syncProject(){',"  function syncProject(){\n    if(panel&&currentProject?.canonicalId!=='comet-courier'){panel.classList.remove('courier-studio');$m('CourierStudio').hidden=true;}")
 html=once(html,'ModelAtelier.install();',loader+'\nModelAtelier.install();')
 assert html.index('</head>')<html.index('<script type="module">')
 html=html.replace('</head>','<style>#modelAtelierPanel.courier-studio #modelAtelierViewportModes,#modelAtelierPanel.courier-studio #modelAtelierInspectorDock,#modelAtelierPanel.courier-studio #modelAtelierToolRail,#modelAtelierPanel.courier-studio .atelier-viewport-controls,#modelAtelierPanel.courier-studio .atelier-mesh-quick,#modelAtelierPanel.courier-studio .atelier-camera-help,#modelAtelierPanel.courier-studio [data-component-controls]{display:none!important}</style></head>',1)
 anchor='<span class="hint den-glow">Open Model Atelier</span></button>'
 cards='''<button class="project-card den" data-project-template="comet-courier"><span class="project-icon">🦊</span><strong>Astra · Comet Courier</strong><span class="template-tag">TEXTURED MODEL PROJECT · 4K</span><p>A celestial fox with sculpted fur, traveling gear and a luminous comet tail. Edit every mesh; export a textured GLB.</p><span class="hint den-glow">Open Astra model project</span></button><button class="project-card den" data-project-template="blank-model"><span class="project-icon">✧</span><strong>New Model Project</strong><span class="template-tag">EMPTY MODEL WORKSPACE</span><p>Start an independent 3D model with the full Model Atelier sculpt, component, UV and material tools.</p><span class="hint den-glow">Create a model project</span></button>'''
 html=once(html,anchor,anchor+cards)
 for a,b in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_76_DESKTOP_MODELING_REPAIR','SWYRL_ENGINE_DEPLOY_MARKER: V11_77_COMET_COURIER_MODEL_PROJECT'),('ENGINE · MAKER v11.76','ENGINE · MAKER v11.77'),('v11.76 · precise desktop modeling','v11.77 · textured model projects'),("window.SWRLZ_FORGE_BUILD={version:'v11.76'","window.SWRLZ_FORGE_BUILD={version:'v11.77'"),('<title>§wyrl§ Engine · Maker v11.76</title>','<title>§wyrl§ Engine · Maker v11.77</title>')]:html=once(html,a,b)
 return html
