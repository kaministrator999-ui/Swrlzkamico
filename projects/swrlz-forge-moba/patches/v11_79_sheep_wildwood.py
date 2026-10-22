"""Larger native Sheep Tag map, four woodland regions and original 4K ground."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    scene=json.loads((root/'scenes/sheep-tag-wildwood-v11-79.swyrl.json').read_text())
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    prefix='const ST_CANONICAL_PROJECT=';start=html.index(prefix)+len(prefix)
    _,length=json.JSONDecoder().raw_decode(html[start:]);html=html[:start]+encoded+html[start+length:]
    html=once(html,"const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-moonbell-archive.swyrl.json';","const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-wildwood-v11-79.swyrl.json';")
    js=(root/'runtime/sheep_wildwood_v11_79.js').read_text()
    html=once(html,'function stMakeVisual(type){',js+'\nfunction stMakeVisual(type){\n  if(type===\'st-meadow\'&&stRules().bounds===64)return stWildwoodVisual();')
    html=once(html,'actor.position.fromArray(pos);actor.userData.spawnPos=actor.position.toArray();return actor;',
              'actor.position.fromArray(pos);stWildwoodStyle(actor);actor.userData.spawnPos=actor.position.toArray();return actor;')
    html=once(html,'sourceScene:ST_ARCHIVE_SOURCE_SCENE,status:()=>stStatus()',
              'sourceScene:ST_ARCHIVE_SOURCE_SCENE,mapStatus:stWildwoodMapStatus,status:()=>stStatus()')
    html=once(html,"initializeHistory('Opened Moonbell Meadow Sheep Tag')","initializeHistory('Opened Moonbell Wildwood Sheep Tag')")
    html=once(html,"toast('Moonbell Meadow · Sheep Tag')","toast('Moonbell Wildwood · 128 × 128 m · Sheep Tag')")
    html=once(html,"context.clearRect(0, 0, size, size); context.fillStyle = '#203c2e'; context.fillRect(0, 0, size, size);",
              "context.clearRect(0, 0, size, size); context.fillStyle = '#203c2e'; context.fillRect(0, 0, size, size);\n  if(bounds===64&&stWildwoodGroundTexture?.image?.complete){context.drawImage(stWildwoodGroundTexture.image,0,0,size,size);receipt.terrain='moonbell-wildwood';}")
    html=once(html,'<h2 id="stRulesTitle">Sheep Tag · Moonbell Meadow</h2>',
              '<h2 id="stRulesTitle">Sheep Tag · Moonbell Wildwood</h2>')
    html=once(html,'<strong>Sheep Tag · Moonbell Meadow</strong>','<strong>Sheep Tag · Moonbell Wildwood</strong>')
    html=once(html,'MOONBELL MEADOW · <span id="stRole">','<span id="stMapName">MOONBELL WILDWOOD</span> · <span id="stRole">')
    html=once(html,'function stRefreshHUD(force = false) {',
              "function stRefreshHUD(force = false) {\n  stUiText('stMapName',stUiRules().bounds===64?'MOONBELL WILDWOOD':'MOONBELL MEADOW');")
    # Update the actual project card while retaining its stable query/template.
    html=once(html,'Craft precise house mazes, breach defenses, and rescue wisps. Curated map creator and optional archive magic: thorns, totems, raised routes and Illusive Split.',
              'Explore a 128 × 128 m woodland with four building glades, linked roads, hidden sheep passages and 4K ground artwork. Build, hunt and rescue with Astra hunters.')
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_78_SHEEP_TAG_COURIER','SWYRL_ENGINE_DEPLOY_MARKER: V11_79_MOONBELL_WILDWOOD'),
      ('ENGINE · MAKER v11.78','ENGINE · MAKER v11.79'),
      ('v11.78 · Astra in Sheep Tag','v11.79 · Moonbell Wildwood'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.78'","window.SWRLZ_FORGE_BUILD={version:'v11.79'"),
      ('<title>§wyrl§ Engine · Maker v11.78</title>','<title>§wyrl§ Engine · Maker v11.79</title>')
    ):html=once(html,old,new)
    return html
