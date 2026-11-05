"""§E v11.280 — full native particle preset library + 18 mage spell emitters,
with a blank-VR controller casting sandbox using the canonical Arcane Gloves.

Adds no second renderer, independent animation loop, external asset or
saved-project migration. All 14 existing native particle presets remain.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(source,old,new,reason):
    count=source.count(old)
    if count!=1:raise AssertionError(("v11.280",reason,count,old[:120]))
    return source.replace(old,new,1)

PRESETS=r"""
 emberBolt:{label:'Ember Bolt',mode:'burst',shape:'point',rate:0,burst:54,life:1.25,speed:6.6,spread:.12,gravity:-.15,drag:.12,size:.17,radius:.07,direction:[0,0,-1],startColor:'#fff19b',endColor:'#ed4316',blend:'additive'},
 infernoBreath:{label:'Inferno Breath',mode:'continuous',shape:'sphere',rate:75,burst:72,life:.85,speed:6.5,spread:1.25,gravity:-.2,drag:.8,size:.23,radius:.16,direction:[0,0,-1],startColor:'#fff5a6',endColor:'#eb2c0a',blend:'additive'},
 frostNova:{label:'Frost Nova',mode:'burst',shape:'circle',rate:0,burst:70,life:1.9,speed:3.4,spread:1.2,gravity:0,drag:.25,size:.19,radius:.38,direction:[0,.12,0],startColor:'#e9ffff',endColor:'#4789ff',blend:'additive'},
 iceLance:{label:'Ice Lance',mode:'burst',shape:'point',rate:0,burst:50,life:1.1,speed:9.5,spread:.08,gravity:.15,drag:.08,size:.12,radius:.04,direction:[0,0,-1],startColor:'#f6ffff',endColor:'#39bafa',blend:'additive'},
 stormArc:{label:'Storm Arc',mode:'burst',shape:'point',rate:0,burst:75,life:.72,speed:7.5,spread:.65,gravity:0,drag:.07,size:.12,radius:.07,direction:[0,0,-1],startColor:'#fffaad',endColor:'#65aaff',blend:'additive'},
 chainStorm:{label:'Chain Storm',mode:'burst',shape:'sphere',rate:0,burst:86,life:.82,speed:7.8,spread:1.7,gravity:0,drag:.07,size:.105,radius:.1,direction:[0,0,-1],startColor:'#edffff',endColor:'#5179f8',blend:'additive'},
 arcaneMissile:{label:'Arcane Missile',mode:'burst',shape:'point',rate:0,burst:54,life:1.55,speed:6.0,spread:.17,gravity:0,drag:.13,size:.18,radius:.07,direction:[0,0,-1],startColor:'#f3adff',endColor:'#4b6dfd',blend:'additive'},
 runeCircle:{label:'Runic Halo',mode:'continuous',shape:'circle',rate:46,burst:55,life:2.2,speed:.38,spread:.1,gravity:0,drag:.2,size:.14,radius:1.24,direction:[0,0,0],startColor:'#f1a7ff',endColor:'#815af8',blend:'additive'},
 healingCircle:{label:'Healing Bloom',mode:'continuous',shape:'sphere',rate:41,burst:62,life:2.7,speed:1.55,spread:.55,gravity:-1.2,drag:.5,size:.20,radius:.8,direction:[0,1,0],startColor:'#edffd2',endColor:'#34f6b9',blend:'additive'},
 holyNova:{label:'Radiant Nova',mode:'burst',shape:'sphere',rate:0,burst:84,life:1.6,speed:4.7,spread:1.8,gravity:0,drag:.35,size:.20,radius:.25,direction:[0,0,0],startColor:'#ffffff',endColor:'#ffd36d',blend:'additive'},
 shadowPulse:{label:'Shadow Pulse',mode:'burst',shape:'sphere',rate:0,burst:78,life:1.55,speed:4.1,spread:1.8,gravity:0,drag:.40,size:.27,radius:.18,direction:[0,0,0],startColor:'#bc78ff',endColor:'#301065',blend:'additive'},
 voidOrb:{label:'Void Orb',mode:'continuous',shape:'sphere',rate:52,burst:60,life:2.5,speed:.8,spread:.3,gravity:0,drag:.65,size:.22,radius:.36,direction:[0,0,0],startColor:'#cb8aff',endColor:'#302a7d',blend:'additive'},
 gravityWell:{label:'Gravity Well',mode:'continuous',shape:'circle',rate:49,burst:60,life:3.2,speed:1.1,spread:.25,gravity:0,drag:.4,size:.17,radius:1.15,direction:[0,0,0],startColor:'#63fff9',endColor:'#5a29b8',blend:'additive'},
 earthBurst:{label:'Stone Burst',mode:'burst',shape:'sphere',rate:0,burst:80,life:1.75,speed:4.8,spread:2.0,gravity:6.2,drag:.18,size:.26,radius:.2,direction:[0,.9,0],startColor:'#fff5c9',endColor:'#a66e3e',blend:'normal'},
 meteorShower:{label:'Meteor Rain',mode:'continuous',shape:'box',rate:62,burst:75,life:1.75,speed:8.4,spread:.22,gravity:5.0,drag:.04,size:.2,radius:2.7,direction:[0,-1,0],startColor:'#fffcc5',endColor:'#ec4a23',blend:'additive'},
 windSpiral:{label:'Wind Cyclone',mode:'continuous',shape:'circle',rate:54,burst:65,life:2.9,speed:1.5,spread:.3,gravity:-.25,drag:.3,size:.15,radius:.85,direction:[0,1,0],startColor:'#f1ffff',endColor:'#41e7da',blend:'additive'},
 crystalBloom:{label:'Crystal Bloom',mode:'burst',shape:'sphere',rate:0,burst:80,life:2.0,speed:2.2,spread:1.5,gravity:-.2,drag:.24,size:.24,radius:.28,direction:[0,.3,0],startColor:'#ffdcff',endColor:'#63d6ff',blend:'additive'},
 thunderRing:{label:'Thunder Ring',mode:'burst',shape:'circle',rate:0,burst:86,life:1.4,speed:5.4,spread:1.1,gravity:0,drag:.12,size:.14,radius:.24,direction:[0,0,0],startColor:'#ffffff',endColor:'#4f92f9',blend:'additive'},
"""

def apply(html):
    js=(ROOT/"runtime/mage_spell_lab_v11_280.js").read_text("utf8")
    css=(ROOT/"runtime/mage_spell_lab_v11_280.css").read_text("utf8")
    for key in (
      "const SE223_PRESETS=Object.freeze({",
      "const SE223_MAX_EMITTERS=12",
      "function se223Default(key='magic'){",
      "function se223PointCloud(config){",
      "function se223DisposeRecord(rec){",
      "function se223Mutate(label,fn,allowRepair=false){",
      "const se279GameId='blank-vr-hands';",
      "function se279XRFrame(){",
      "function se279Cleanup(){",
      "const se248StarterParticles",
      "window.SWRLZ_FORGE_BUILD=",
    ):
      if key=="const se248StarterParticles":
       assert "se248StarterParticles" in html,("v11.280 native Starter Particles tab missing",)
      else:assert key in html,("v11.280 prerequisite",key)
    html=once(html,"const SE223_PRESETS=Object.freeze({",
      "const SE223_PRESETS=Object.freeze({"+PRESETS,
      "append eighteen schema-native particle presets")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      js+"\nwindow.SWRLZ_FORGE_BUILD=","native UI plus single-loop glove casting")
    # The assembled source contains an inert additional </head> literal in JS.
    # Insert only before the real document's FIRST closing head tag.
    assert "</head>" in html
    html=html.replace("</head>",
      '<style id="se280MageSpellLibrary">'+css+'</style>\n</head>',1)

    before=" source.engine='§wyrl§ Engine · Maker v11.279';source.version=11.279;"
    n=html.count(before)
    assert n==3,("v11.280 provenance: two native model starters plus mirrored glove",n)
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.280';source.version=11.280;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_279_BLANK_VR_ARCANE_HANDS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_280_MAGE_SPELL_LAB"),
      ("ENGINE · MAKER v11.279","ENGINE · MAKER v11.280"),
      ("v11.279 · blank VR hands and mirrored left glove",
       "v11.280 · native Mage Spell particle library and VR glove casts"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.279'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.280'"),
      ("<title>§wyrl§ Engine · Maker v11.279</title>",
       "<title>§wyrl§ Engine · Maker v11.280</title>"),
    ):
      html=once(html,old,new,"release identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Mage Spell Lab: 32 native particle effects and dual glove casting",
      date="2026-11-05",changes=[
       "Expand the pre-existing Starter Particles tab and particle editor sidebar into a searchable library of every registered native particle preset: 10 engine originals, 4 Astral Vortex layers and 18 new Mage spells.",
       "Add 18 independently editable particle presets covering elemental fire, ice, lightning, arcane, life, light, shadow, void, stone, meteor and wind effects. Add a one-click 8-spell pack subject to the existing 12-emitter project limit, with standard transaction, saved JSON and curves.",
       "Blank VR · Arcane Hands now casts selected particles from tracked Quest hand controllers using each trigger's pressed edge. Clicking each hand's thumbstick changes its selected spell with a controller-mounted readable label. Grip animations remain unchanged.",
       "The caster uses the exact native emitter preset definitions and original point-cloud geometry/materials in a pooled transient visual path, maximum six simultaneous effects. It shares §E's existing renderer/XR animation callback, and never creates authoring actors, duplicate canvases or a second game loop.",
       "Both glove spells can be equipped using dropdowns in the Particle Library before entering VR. New effects are accessible one at a time in the native Particle Editor and export with the saved project.",
       "No spell damage, collisions, projectiles with gameplay authority, hand-tracking APIs, new multiplayer traffic or external assets. No changes to Sheep Tag, VR menu bindings outside blank hands, the saved glove models or previous source lineage. Quest 2 acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
