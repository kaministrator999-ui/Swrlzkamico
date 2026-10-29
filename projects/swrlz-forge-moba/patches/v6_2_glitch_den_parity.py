"""§wyrl§ Engine v6.2: Glitch Den is an exact structural clone of the regular Dragon Den."""
def _once(s,old,new):
    if old not in s:
        raise RuntimeError("v6.2 token missing: "+old[:220])
    return s.replace(old,new,1)

def apply(html):
    s=html
    for a,b in {
      "V6_1_GLITCH_DEN_STARTER":"V6_2_GLITCH_DEN_PARITY",
      "Maker v6.1":"Maker v6.2",
      "MAKER v6.1":"MAKER v6.2",
      "v6.1 · GLITCH DEN STARTER":"v6.2 · GLITCH DEN PARITY",
      "version:'v6.1'":"version:'v6.2'",
      "version:'swyrl-engine-agent-v4.1'":"version:'swyrl-engine-agent-v4.2'",
      "engine:'§wyrl§ Engine · Maker v6.1'":"engine:'§wyrl§ Engine · Maker v6.2'",
      "version:6.1":"version:6.2",
      "editorLog('§wyrl§ Engine v6.1 initialized · Glitch Dragon Den starter exposed','ok')":"editorLog('§wyrl§ Engine v6.2 initialized · Glitch Den exact-layout parity','ok')",
      "Seed Chamber · architecture baseline v5.3 · §wyrl§ Engine v6.1":"Seed Chamber · architecture baseline v5.3 · §wyrl§ Engine v6.2",
      '<span class="template-tag">v6.1 STARTER</span><p>Oversized fractured megacavern with human-scale forge and traversal spaces, chromatic crystal veins, rune pylons, route gates, and §wyrl§ / Frost / Ember dragons.</p><span class="hint den-glow">Enter the Fracture Forge</span>':'<span class="template-tag">v6.2 VARIANT</span><p>The regular Dragon Den exactly — same architecture, layout, rooms, placements, exits and framing — with the Glitch visual identity layered over it.</p><span class="hint den-glow">Enter the Glitch Den</span>'
    }.items():
        s=_once(s,a,b)

    start=s.find("function buildGlitchDragonsDenProject(){")
    if start<0: raise RuntimeError("v6.2 glitch builder start missing")
    end=s.find("\nfunction inferProjectMeta(p){",start)
    if end<0: raise RuntimeError("v6.2 glitch builder end missing")
    block=r'''function buildGlitchDragonsDenProject(){
  // Structural source of truth: build the regular Den first. Do not fork its geometry.
  buildDragonsDenProject();
  applyProjectMeta({name:"Glitch Dragon Den — Fracture Forge",template:'glitch-dragons-den',kind:'dragons-den',environment:'dragon-den'});
  setProjectBackground('#01030a');scene.fog.near=16;scene.fog.far=62;renderer.toneMappingExposure=1.12;

  // Retheme the already-built regular Den in place so object positions, scales,
  // groups, rooms, exits, collision layout and camera framing stay identical.
  const glitchPalette=['#7657ff','#42d9ff','#d653ff','#55ffd1','#ff5fa2'];
  let n=0;
  for(const a of actors){
    a.userData.tags=[...(a.userData.tags||[]),'glitch-den'];
    if(a.userData.folder?.startsWith('Dragon Den/'))a.userData.folder=a.userData.folder.replace('Dragon Den/','Glitch Den/');
    a.traverse?.(o=>{
      if(!o?.isMesh||!o.material)return;
      const mats=Array.isArray(o.material)?o.material:[o.material];
      for(const original of mats){
        const m=original.clone();o.material=m;
        if(m.color){
          const base=new THREE.Color(glitchPalette[n++%glitchPalette.length]);
          m.color.lerp(base,.38);
        }
        if('emissive' in m&&m.emissive){
          m.emissive.lerp(new THREE.Color(glitchPalette[n%glitchPalette.length]),.24);
          m.emissiveIntensity=Math.max(m.emissiveIntensity||0,.16);
        }
      }
    });
  }

  const rename=[
    ['§wyrl§ Dragon','§wyrl§ Glitch Dragon'],
    ['Forge Dragon','Frost Forge Dragon'],
    ['Coder Dragon','Ember Glitch Dragon'],
    ['Council Rune Dais','Glitch Council Rune Dais'],
    ['Memory Crystal','Glitch Memory Crystal']
  ];
  for(const [from,to] of rename){const a=actors.find(x=>x.name===from);if(a)a.name=to;}
  rebuildHierarchy();selectActor(null);
  toast("Glitch Dragon Den · exact Dragon Den layout · glitch variant");
}'''
    s=s[:start]+block+s[end:]
    return s
