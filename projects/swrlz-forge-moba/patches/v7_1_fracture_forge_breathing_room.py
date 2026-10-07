"""§wyrl§ Engine v7.1: mobile breathing room + expanded Fracture Forge composition."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.1 token missing: "+old[:200])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_0_FRACTURE_FORGE_ASCENDANT":"V7_1_FRACTURE_FORGE_BREATHING_ROOM",
      "Maker v7.0":"Maker v7.1","MAKER v7.0":"MAKER v7.1",
      "v7.0 · FRACTURE FORGE ASCENDANT":"v7.1 · FRACTURE FORGE BREATHING ROOM",
      "version:'v7.0'":"version:'v7.1'",
      "version:'swyrl-engine-agent-v5.0'":"version:'swyrl-engine-agent-v5.1'",
      "engine:'§wyrl§ Engine · Maker v7.0'":"engine:'§wyrl§ Engine · Maker v7.1'",
      "version:7.0":"version:7.1",
      "editorLog('§wyrl§ Engine v7.0 initialized · Command Deck · Fracture Forge Ascendant','ok')":"editorLog('§wyrl§ Engine v7.1 initialized · expanded Fracture Forge · mobile breathing room','ok')"
    }.items(): s=_once(s,a,b)

    # Mobile command UI: keep the power, stop covering the viewport.
    css=r"""
@media(max-width:720px){
 .engine-command-deck{top:auto!important;left:12px!important;right:auto!important;bottom:92px!important;transform:none!important;max-width:calc(100vw - 24px)!important;padding:4px!important;border-radius:12px!important}
 .engine-command-deck button{display:none!important}
 .engine-command-deck button:last-child{display:block!important;padding:8px 12px!important}
 .engine-command-deck button:last-child::before{content:'⚡ ';color:#a98cff}
 .engine-stats-pill{top:auto!important;right:12px!important;bottom:94px!important;max-width:52vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Expand the authored den itself instead of packing more detail into the old footprint.
    # Move dragon territories outward and give the central circulation a clean buffer.
    moves={
      "makeGlitchDragonV3([17,0,8]":"makeGlitchDragonV3([25,0,11]",
      "makeGlitchDragonV3([-18,0,-5]":"makeGlitchDragonV3([-27,0,-8]",
      "makeGlitchDragonV3([14,0,-15]":"makeGlitchDragonV3([22,0,-24]",
      "makeDenStructure('pillar',[-7,0,18]":"makeDenStructure('pillar',[-10,0,27]",
      "makeDenStructure('pillar',[7,0,18]":"makeDenStructure('pillar',[10,0,27]",
      "makeDenStructure('arch',[0,0,18]":"makeDenStructure('arch',[0,0,27]",
      "makeDenStructure('floorPlate',[0,0,11]":"makeDenStructure('floorPlate',[0,0,17]",
      "makeDenStructure('floorPlate',[0,0,-9]":"makeDenStructure('floorPlate',[0,0,-14]",
      "makeDenStructure('arch',[-18,0,-5]":"makeDenStructure('arch',[-27,0,-8]",
      "makeDenStructure('arch',[14,0,-15]":"makeDenStructure('arch',[22,0,-24]"
    }
    for a,b in moves.items(): s=_once(s,a,b)

    # Wayfinders and paths now describe the expanded territories.
    s=_once(s,"[[0,1,18,'#a26cff'],[0,1,-18,'#ff6dba'],[-18,1,-5,'#65eaff'],[14,1,-15,'#ff8b62'],[-12,1,11,'#77a8ff'],[12,1,11,'#ae75ff']]",
              "[[0,1,27,'#a26cff'],[0,1,-28,'#ff6dba'],[-27,1,-8,'#65eaff'],[22,1,-24,'#ff8b62'],[-18,1,17,'#77a8ff'],[18,1,17,'#ae75ff']]")
    s=_once(s,"[[0,18],[0,12],[-7,7],[0,2],[7,7],[0,12]]","[[0,27],[0,20],[-11,13],[0,5],[11,13],[0,20]]")
    s=_once(s,"[[-18,-5],[-10,-7],[0,-9],[8,-12],[14,-15]]","[[-27,-8],[-17,-11],[0,-14],[13,-19],[22,-24]]")

    # Scale central authored surfaces with the larger footprint.
    s=_once(s,"overlook.scale.set(7,.55,3.4)","overlook.scale.set(9,.55,4.2)")
    s=_once(s,"bridge.scale.set(3.2,.38,9)","bridge.scale.set(3.8,.38,13)")

    # Lighting follows the new territories.
    old="[[0,8,0,'#8c64ff',4.2,30],[0,5,17,'#9a72ff',2.2,20],[-18,7,-5,'#55ddff',3.0,23],[14,7,-15,'#ff5d8d',2.8,22],[0,10,-18,'#ff9b55',2.1,20],[-11,4,10,'#557dff',1.5,15],[11,4,10,'#bb65ff',1.5,15]]"
    new="[[0,8,0,'#8c64ff',3.6,27],[0,6,26,'#9a72ff',2.4,22],[-27,8,-8,'#55ddff',3.2,25],[22,8,-24,'#ff5d8d',3.0,24],[0,10,-28,'#ff9b55',2.3,22],[-18,5,17,'#557dff',1.7,17],[18,5,17,'#bb65ff',1.7,17]]"
    s=_once(s,old,new)
    return s
