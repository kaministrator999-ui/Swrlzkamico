"""§wyrl§ Engine v6.1: expose Glitch Dragon Den starter and clarify project version label."""
def _once(s, old, new):
    if old not in s:
        raise RuntimeError("v6.1 token missing: " + old[:220])
    return s.replace(old, new, 1)

def apply(html):
    s = html

    for a,b in {
      "V6_0_GLITCH_DRAGON_DEN":"V6_1_GLITCH_DEN_STARTER",
      "Maker v6.0":"Maker v6.1",
      "MAKER v6.0":"MAKER v6.1",
      "v6.0 · GLITCH DRAGON DEN":"v6.1 · GLITCH DEN STARTER",
      "version:'v6.0'":"version:'v6.1'",
      "version:'swyrl-engine-agent-v4.0'":"version:'swyrl-engine-agent-v4.1'",
      "engine:'§wyrl§ Engine · Maker v6.0'":"engine:'§wyrl§ Engine · Maker v6.1'",
      "version:6.0":"version:6.1",
      "editorLog('§wyrl§ Engine v6.0 initialized · researched Glitch Dragon Den variant','ok')":"editorLog('§wyrl§ Engine v6.1 initialized · Glitch Dragon Den starter exposed','ok')"
    }.items():
        s = _once(s,a,b)

    seed_card = '''<button class="project-card den" data-project-template="dragons-den"><span class="project-icon">🐉</span><strong>Dragon's Den — Seed Chamber</strong><span class="template-tag">DEFAULT STARTER</span><p>Immersive under-realm seed chamber: wake nook, council floor, throne side, dragon perch, creator alcove, and exits to future deeper systems.</p><span class="hint den-glow">Wake up in the Den</span></button>'''
    glitch_card = seed_card + '''
            <button class="project-card den" data-project-template="glitch-dragons-den"><span class="project-icon">🐲</span><strong>Glitch Dragon Den — Fracture Forge</strong><span class="template-tag">v6.1 STARTER</span><p>Oversized fractured megacavern with human-scale forge and traversal spaces, chromatic crystal veins, rune pylons, route gates, and §wyrl§ / Frost / Ember dragons.</p><span class="hint den-glow">Enter the Fracture Forge</span></button>'''
    s = _once(s, seed_card, glitch_card)

    s = _once(
      s,
      "if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den')return buildGlitchDragonsDenProject();",
      "if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den')buildGlitchDragonsDenProject();"
    )

    s = _once(
      s,
      'toast("Dragon\'s Den v5.3 · grouped architecture + immersive cavern");',
      'toast("Seed Chamber · architecture baseline v5.3 · §wyrl§ Engine v6.1");'
    )

    return s
