"""Reliable native prefab results and immediate Outliner/Details updates."""

def apply(html):
    old="spawn:(type,options={})=>{beginTransaction('Agent spawn '+type);createPrefab(type);const a=selected;if(a&&options.position)a.position.fromArray(options.position);if(a&&options.name)a.name=options.name;if(a&&options.folder)a.userData.folder=options.folder;commitTransaction('Agent spawn '+type);return a?.userData.id||null;},"
    new="""spawn:(type,options={})=>{
    const previous=new Set(actors);beginTransaction('Agent spawn '+type);createPrefab(type);const a=selected;
    if(!a||previous.has(a)){transactionBefore=null;editorLog('Unknown prefab: '+String(type),'warn');return null;}
    if(options.position)a.position.fromArray(options.position);if(options.name)a.name=options.name;if(options.folder)a.userData.folder=options.folder;
    a.userData.spawnPos=a.position.toArray();rebuildHierarchy();syncInspector();commitTransaction('Agent spawn '+type);return a.userData.id;
  },"""
    if html.count(old)!=1:raise RuntimeError('v8.3 native spawn anchor missing')
    s=html.replace(old,new,1)
    anchor="function clearAll(){\n  closeTeleportMenu(false);"
    if s.count(anchor)!=1:raise RuntimeError('v8.3 layer reset expects teleport patch first')
    return s.replace(anchor,"function clearAll(){\n  if(playing||simulating)stopSession();\n  closeTeleportMenu(false);\n  editorLayers=[];activeEditorLayerId=null;renderLayerPanel();",1)
