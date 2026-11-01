"""§E v11.194 — Emberfall Shattered Vale original hack-and-slash starter.
Own native authored scene + transient Play-only combat. No second engine.
Append-only patch: preserve independent starter, modeler, Quest, Sheep, Maul and chat.
"""
from pathlib import Path
import json

def once(html,old,new):
    n=html.count(old)
    if n!=1:
        raise AssertionError(("v11.194 missing/ambiguous anchor",old[:160],n))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/emberfall_arpg_v11_194.js').read_text(encoding='utf-8')
    css=(root/'runtime/emberfall_arpg_v11_194.css').read_text(encoding='utf-8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=html.replace('</head>','<style id="ef194Style">\n'+css+'\n</style>\n</head>',1)
    card=('<button class="project-card ef194-project-card" data-project-template="emberfall-arpg">'
      '<span class="project-icon">⚔️</span><strong>Emberfall · Shattered Vale</strong>'
      '<span class="template-tag">HACK-AND-SLASH RPG STARTER</span>'
      '<p>Explore the blighted vale. Hunt enemy packs, slash, cast spells, collect gear, level skills and defeat the Cinder Warden.</p>'
      '<span class="hint">Create editable dark-fantasy ARPG</span></button>')
    html=once(html,'<span class="hint den-glow">Open Frostveil Maul</span></button>',
      '<span class="hint den-glow">Open Frostveil Maul</span></button>'+card)
    html=html.replace('</head>','<style id="ef194ProjectCard">'
      '.ef194-project-card{border-color:#896c4780;background:radial-gradient(circle at 65% 15%,#a46b3342,transparent 43%),'
      'linear-gradient(155deg,#28201c,#11171b)}.ef194-project-card:hover{border-color:#e8bc72}'
      '.ef194-project-card .template-tag{color:#f0c28b;border-color:#a98052a0}'
      '</style></head>',1)
    # Existing starter choice checkbox and new project UI already discover cards
    # by data-project-template; never override the user's saved default.
    html=once(html,
      'function se128LaunchStartupProject(){',
      "function se128LaunchStartupProject(){\n"
      " if(new URLSearchParams(location.search).get('project')==='emberfall-arpg'){\n"
      "  ef194MakeStarter();window.se128StartupPending=false;return;\n"
      " }")
    # Add to existing runtime template router, retaining every previous wrapper
    # and independent project factory. Direct ?project= and user-saved defaults
    # both reach this same native starter builder.
    hook="""
const ef194NativeTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template!==ef194.id)return ef194NativeTemplate(template,force);
 if(dirty&&!force&&!confirm('Create Emberfall and discard unsaved changes?'))return false;
 return ef194MakeStarter();
};
const ef194NativePlay=beginPlay,ef194NativeSimulate=beginSimulate,ef194NativeStop=stopSession;
beginPlay=function(...args){
 if(currentProject?.kind!==ef194.kind)return ef194NativePlay(...args);
 const result=ef194NativePlay(...args);
 if(playing&&!ef194.session)ef194Start();
 return result;
};
beginSimulate=function(...args){
 if(currentProject?.kind!==ef194.kind)return ef194NativeSimulate(...args);
 return beginPlay(...args);
};
stopSession=function(...args){
 const owned=!!ef194.session;
 if(owned)ef194Stop();
 const result=ef194NativeStop(...args);
 if(owned&&currentProject?.kind===ef194.kind)ef194FrameMap(true);
 return result;
};
"""
    html=once(html,'window.SWRLZ_FORGE_BUILD=',hook+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,
      "if(currentProject.kind==='maul')maulUpdate(dt);",
      "if(currentProject.kind==='maul')maulUpdate(dt);\n"
      "    if(currentProject.kind==='emberfall-arpg')ef194Update(dt);")
    html=once(html,
      "if(playing&&currentProject.kind!=='maul'){updateHero(dt,t);updateTeleportRecovery(t);}",
      "if(playing&&currentProject.kind!=='maul'&&currentProject.kind!=='emberfall-arpg'){updateHero(dt,t);updateTeleportRecovery(t);}")
    # Ensure explicit game interactions also use the ARPG view rather than the
    # generic perspective pawn viewpoint when entering Play from the topbar.
    html=once(html,
      "if(currentProject.kind==='sheep-tag')stFrameMap();if(currentProject.kind==='maul')maulFrameMap();editorLog",
      "if(currentProject.kind==='sheep-tag')stFrameMap();if(currentProject.kind==='maul')maulFrameMap();"
      "if(currentProject.kind==='emberfall-arpg')ef194FrameMap(true);editorLog")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_193_SHEEP_VR_CAPTURE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_194_EMBERFALL_ARPG_STARTER'),
      ('ENGINE · MAKER v11.193','ENGINE · MAKER v11.194'),
      ('v11.193 · immersive Sheep Tag and capture','v11.194 · Emberfall hack-and-slash RPG starter'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.193'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.194'"),
      ('<title>§wyrl§ Engine · Maker v11.193</title>',
       '<title>§wyrl§ Engine · Maker v11.194</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Emberfall: native editable dark-fantasy hack-and-slash starter',
      date='2026-10-31',changes=[
      'Add Emberfall · Shattered Vale to the native §E Projects / starter gallery with its own persisted project type, native editable hero/enemy actors, blighted ruins, cliffs, camp portal and environmental props.',
      'Implement real Play-in-Editor top-down click/tap move and target-chase combat, keyboard movement, basic slash, arcane bolt and area nova on cooldown and mana, enemy chase/attack AI and boss objective.',
      'Award experience, levels, upgrade points, gold, randomized original equipment rarity and auto-loot/equip, limited health potions, and a simple assisting lantern companion; no third-party assets are copied.',
      'Show adaptive dark-fantasy combat HUD with mobile ability buttons, health/mana/XP bars, skills and equipment stats. Editor save/export retains native authored map but transient session loot and AI never modify scene files.',
      'Explicit ?project=emberfall-arpg opens this starter; existing per-device saved default preference and old starter choices continue working unchanged.',
      'No second renderer or animation loop. VR game rendering uses the existing scene, but dedicated VR ARPG combat controller bindings, cooperative multiplayer and deep character talent trees remain separate future features.',
      'Preserve Sheep Tag, Dragon Den, Model Atelier, Chat authentication and all previous saved-project versions. Physical browser/mobile/Quest gameplay acceptance remains pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
