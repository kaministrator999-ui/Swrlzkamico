"""§wyrl§ Engine v6.5: Fracture Forge runtime parity + default project."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.5 token missing: "+old[:180])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_4_GLITCH_DEN_DRAGON_V3":"V6_5_GLITCH_DEN_RUNTIME",
      "Maker v6.4":"Maker v6.5","MAKER v6.4":"MAKER v6.5",
      "v6.4 · GLITCH DEN DRAGON V3":"v6.5 · GLITCH DEN RUNTIME",
      "version:'v6.4'":"version:'v6.5'",
      "version:'swyrl-engine-agent-v4.4'":"version:'swyrl-engine-agent-v4.5'",
      "engine:'§wyrl§ Engine · Maker v6.4'":"engine:'§wyrl§ Engine · Maker v6.5'",
      "version:6.4":"version:6.5",
      "editorLog('§wyrl§ Engine v6.4 initialized · single Glitch Den · dragon anatomy v3','ok')":"editorLog('§wyrl§ Engine v6.5 initialized · Fracture Forge default · Wisp first-person runtime','ok')",
      "defaultProject:'dragons-den'":"defaultProject:'glitch-dragons-den'"
    }.items(): s=_once(s,a,b)

    # Fracture Forge gets the same player-avatar contract used by the regular Den.
    token="  const sw=makeGlitchDragonV3([17,0,8],'#7c55ff',true,'§wyrl§ Glitch Dragon',2.8,'#5cecff');"
    wisp="  const visitor=makeWispHero('blue',[0,0,9.1],true,'Wisp Visitor / Creator');visitor.userData.folder='Glitch Den/Visitors';visitor.userData.role='player-avatar';visitor.rotation.y=Math.PI;\n"+token
    s=_once(s,token,wisp)

    # Startup default now resolves to the Glitch Den, while explicit saved/template choices still work.
    candidates=[
      "buildDragonsDenProject();\nsetActiveProjectTab('editor');",
      "buildDragonsDenProject();\nsetProjectTab('editor');",
      "buildDragonsDenProject();"
    ]
    replaced=False
    for old in candidates:
      if old in s:
        new=old.replace("buildDragonsDenProject();","buildGlitchDragonsDenProject();")
        s=s.replace(old,new,1);replaced=True;break
    if not replaced: raise RuntimeError("v6.5 startup default call missing")

    s=s.replace('<span class="template-tag">v6.4 RESEARCHED</span>','<span class="template-tag">v6.5 DEFAULT</span>',1)
    return s
