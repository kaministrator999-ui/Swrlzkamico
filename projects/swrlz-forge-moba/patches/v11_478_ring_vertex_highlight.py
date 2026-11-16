"""§E v11.478: highlight every selected ring / filled-radius vertex on native meshes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_478_RING_VERTEX_HIGHLIGHT'

def once(html,old,new):
    count=html.count(old)
    assert count==1,('v11.478 unique patch anchor',old[:120],count)
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_477_VERTEX_SELECTION_HIERARCHY' in html
    runtime=(ROOT/'runtime/model_ring_vertex_highlight_v11_478.js').read_text('utf8')
    assert '/* SE478_RING_VERTEX_HIGHLIGHT_END */' in runtime
    # The original native touch path chooses component slots. Ring and Fill
    # consume the clicked center and call the audited, non-mutating ring API.
    html=once(html,'/* SE477_VERTEX_ENTRY_END */',
              '/* SE477_VERTEX_ENTRY_END */\n'+runtime)
    # An indexed/welded mesh's source vertex ID need not equal the displayed
    # THREE geometry slot. Map by original local-space coordinates instead.
    html=once(html,
      '  const selectedKeys=new Set(result.vertexIds.map(i=>top.keys[i]));',
      '''  const selectedKeys=new Set(result.vertexIds.map(i=>
    p.topologyMesh.positions.slice(i*3,i*3+3)
     .map(v=>Math.round(Math.fround(v)*100000)).join(',')));''')
    # Gizmotransforms use component slot -> topology representative, not the
    # raw slot interpreted as a geometry position index.
    html=once(html,
      '    const key=topology.keys[id];',
      '    const vertex=topology.vertices[id],key=topology.keys[vertex];')
    # Highlight every selected slot (no sampling/192-item selection cap).
    # Unselected points alone retain the usual large-mesh downsampling.
    html=once(html,
      '   make([...selected].map(i=>top.vertices[i]).filter(x=>x!==undefined),0xffd776,11);',
      '''   const selectedSlots=[...selected].filter(i=>Number.isInteger(i)&&i>=0&&i<top.vertices.length);
   const shape=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.shape;
   const ringMode=shape==='ring'||shape==='fill';
   make(selectedSlots.map(i=>top.vertices[i]),
    shape==='fill'?0xffa56a:shape==='ring'?0xffe369:0xffd776,
    ringMode?(typeof matchMedia==='function'&&matchMedia('(pointer:coarse)').matches?16:13):11);
   if(selectedSlots.length){
    const marker=root.children[root.children.length-1];
    if(marker?.isPoints){marker.userData.se478SelectedVertices=true;
     marker.userData.se478SelectionShape=ringMode?shape:'single';}
   }''')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_477_VERTEX_SELECTION_HIERARCHY',MARKER),
      ('ENGINE · MAKER v11.477','ENGINE · MAKER v11.478'),
      ('v11.477 · selectable vertices and contextual modeling modes','v11.478 · complete vertex-ring highlighting'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.477'","window.SWRLZ_FORGE_BUILD={version:'v11.478'"),
      ('<title>§wyrl§ Engine · Maker v11.477</title>','<title>§wyrl§ Engine · Maker v11.478</title>')
    ):html=once(html,old,new)
    original=" source.engine='§wyrl§ Engine · Maker v11.477';source.version=11.477;"
    assert html.count(original)==5,('v11.478 provenance',html.count(original))
    html=html.replace(original,
      " source.engine='§wyrl§ Engine · Maker v11.478';source.version=11.478;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.477']
    notes['history'].insert(0,{'version':'v11.477','changes':notes.get('changes',[])})
    notes.update(version='v11.478',date='2026-11-16',
      title='Complete connected ring and filled-radius vertex highlighting',
      changes=[
       'Extrude and Inset vertex-ring selections highlight every connected ring vertex, not only the center.',
       'Filled vertex ring highlights the center and every connected vertex inside the selected radius; ring outline highlights only the selected outer edge-distance layer.',
       'Tap a new vertex in either ring mode to move the center and update the entire highlighted group, including when Multi is enabled.',
       'Selected topology vertices map by source coordinates to native screen points, keeping transformed and welded geometry aligned with selection and transform gizmos.',
       'Ring outline and fill use distinguishable, touch-sized selected points; unselected large meshes may still use display sampling, never selected vertices.',
       'Mesh geometry, UV coordinates, Undo, project saves, native preview/apply and the existing VR controls remain unchanged.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
