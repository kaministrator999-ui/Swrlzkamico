import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
function fn(name){const a=html.indexOf('function '+name+'(');assert(a>=0,name);let i=html.indexOf('{',a),d=0;for(;i<html.length;i++){if(html[i]==='{')d++;else if(html[i]==='}'&&!--d)return html.slice(a,i+1);}throw Error(name);}
const a=html.indexOf('/* SE440_ASSEMBLY_MENU_SYNC_START */'),b=html.indexOf('/* SE440_ASSEMBLY_MENU_SYNC_END */',a);assert(a>=0&&b>a);
let doc=null,rebuilds=0,calls=0,fieldRefreshes=0;
function picker(){return {value:'',options:[],replaceChildren(){rebuilds++;this.options=[];this.value='';},append(o){this.options.push(o);if(!this.value)this.value=o.value;}};}
const fields={AssemblyDeck:{hidden:false},AssemblyComponent:picker(),AssemblyAmplitude:{},AssemblySpeed:{},AssemblyTime:{}};
const c=vm.createContext({document:{createElement:()=>({})},$m:k=>fields[k],model:()=>doc,refreshInspector:()=>{calls++;return 'native-result';},atelierAssemblyFields:()=>fieldRefreshes++,atelierAssemblyTime:0});
vm.runInContext(fn('atelierAssemblyData')+'\n'+fn('atelierAssemblyChoose')+'\n'+fn('atelierAssemblyRefresh')+'\n'+html.slice(a,b),c);
const data=id=>({assemblies:{duration:3,components:[{id,name:id,state:'free',amplitude:0,speed:1}]}});let groups=0;
doc=data('old-project');assert.equal(c.refreshInspector(),'native-result');assert.equal(fields.AssemblyComponent.value,'old-project');groups++;
doc=data('new-project');c.refreshInspector();assert.deepEqual(fields.AssemblyComponent.options.map(o=>o.value),['new-project']);assert.equal(fields.AssemblyDeck.hidden,false);groups++;
const saved=doc,rebuilt=rebuilds;c.refreshInspector();assert.equal(rebuilds,rebuilt,'Pointer previews must not rebuild unchanged motion controls');assert.equal(doc,saved);groups++;
doc={};c.refreshInspector();assert.equal(fields.AssemblyDeck.hidden,true);doc=data('undo-restored');c.refreshInspector();assert.equal(fields.AssemblyDeck.hidden,false);assert.equal(fields.AssemblyComponent.value,'undo-restored');groups++;
fields.AssemblyComponent=picker();c.refreshInspector();assert.equal(fields.AssemblyComponent.value,'undo-restored','Recreated native picker must hydrate even for the same document');assert(calls>=6&&fieldRefreshes>=4);groups++;
console.log('MODEL_MOTION_MENU_440_PASS',JSON.stringify({groups,actualNativeAssemblyRefresh:true,documentAndPickerIdentity:true,pointerPreviewsDoNotRebuild:true,sourceUnchanged:true}));
