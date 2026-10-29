"""Promote both native editor saves; shared capabilities remain in the engine."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent / "scenes"
    projects = []
    for filename, zones in [("embervault-atelier.swyrl.json", 8), ("starforge-observatory.swyrl.json", 7)]:
        p = json.loads((root / filename).read_text(encoding="utf-8"))
        actors = p["scene"]["actors"]
        assert len({a["id"] for a in actors}) == len(actors), "Duplicate authored actor IDs"
        assert len(p["editor"]["layers"]) == 3, "Three authored organizational layers required"
        assert sum(bool(a.get("workspace")) for a in actors) == 6, "Six usable stations required"
        assert len(p["project"]["teleportZones"]) == zones, "Native zone authoring required"
        p["engine"] = "§wyrl§ Engine · Maker v8.3"
        p["version"] = 8.3
        projects.append(p)
    den, starforge = projects
    encode = lambda p: json.dumps(p, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    start = html.index("const CANONICAL_GLITCH_DEN_PROJECT=")
    end = html.index(";\nfunction loadCanonicalGlitchDen", start)
    s = html[:start] + "const CANONICAL_GLITCH_DEN_PROJECT=" + encode(den) + ";\nconst CANONICAL_STARFORGE_PROJECT=" + encode(starforge) + html[end:]
    s = s.replace("  currentProject={...p.project,workspaces:currentProject.workspaces};\n", "", 1)
    s = s.replace("Opened canonical Glitch Dragon Den", "Opened Embervault Atelier", 1)
    s = re.sub(r"Canonical Glitch Dragon Den opened · three walkable tiers · \d+ actors", "Embervault Atelier opened · three walkable tiers · " + str(len(den["scene"]["actors"])) + " actors · eight zones", s, count=1)
    anchor = "function createProjectFromTemplate(template,force=false){"
    loader = """function loadCanonicalStarforge(){
  loadProject(structuredClone(CANONICAL_STARFORGE_PROJECT),{workspaceLocal:true});
  initializeHistory('Opened Starforge Observatory');markSaved();
  editorLog('Starforge Observatory opened · seven islands · six workstations · seven zones','ok');
  toast('Starforge Observatory');
}

"""
    assert s.count(anchor) == 1, "Project loader anchor missing"
    s = s.replace(anchor, loader + anchor, 1)
    s = s.replace("if(template==='moba')buildMobaProject();else if(template==='default')buildDefaultProject();else loadCanonicalGlitchDen();", "if(template==='moba')buildMobaProject();else if(template==='default')buildDefaultProject();else if(template==='starforge-observatory')loadCanonicalStarforge();else loadCanonicalGlitchDen();", 1)
    card_end = '<span class="hint den-glow">Open Embervault Atelier</span></button></div>'
    card = '<span class="hint den-glow">Open Embervault Atelier</span></button><button class="project-card den" data-project-template="starforge-observatory"><span class="project-icon">✦</span><strong>Starforge Observatory</strong><span class="template-tag">CELESTIAL WORKSHOP</span><p>Seven floating islands, garden paths, rising bridges, six project stations, and a quiet observatory.</p><span class="hint den-glow">Open Starforge Observatory</span></button></div>'
    assert s.count(card_end) == 1, "Project hub card anchor missing"
    s = s.replace(card_end, card, 1)
    s = s.replace("A three-tier project sanctuary with six usable workstations, ramps, galleries, and dragon guardians.", "A three-tier sanctuary with six workstations, eight travel zones, ramps, galleries, and dragon guardians.", 1)
    s = s.replace("  buildGlitchDragonsDen:()=>{loadCanonicalGlitchDen();return true;},", "  buildGlitchDragonsDen:()=>{loadCanonicalGlitchDen();return true;},\n  buildStarforgeObservatory:()=>{loadCanonicalStarforge();return true;},", 1)
    boot = "installPerformanceSettings();applyPerformanceSettings();loadCanonicalGlitchDen();refreshAssetList();"
    assert s.count(boot) == 1, "Final bootstrap anchor missing"
    s = s.replace(boot, "installPerformanceSettings();applyPerformanceSettings();if(new URLSearchParams(location.search).get('project')==='starforge-observatory')loadCanonicalStarforge();else loadCanonicalGlitchDen();refreshAssetList();", 1)
    s = s.replace("V8_2_BOOTSTRAP_REPAIR", "V8_3_ZONES_STARFORGE")
    s = s.replace("Maker v8.2", "Maker v8.3").replace("MAKER v8.2", "MAKER v8.3")
    s = s.replace("version:'v8.2'", "version:'v8.3'").replace("version:8.2", "version:8.3")
    s = s.replace("version:'swyrl-engine-agent-v6.2'", "version:'swyrl-engine-agent-v6.3'")
    s = s.replace("§E v8.2 Tools", "§E v8.3 Tools")
    s = s.replace("v8.2 · BOOTSTRAP REPAIR", "v8.3 · ZONES & STARFORGE")
    s = s.replace("§wyrl§ Engine v8.2 · Embervault Atelier · bootstrap repaired", "§wyrl§ Engine v8.3 · project workspace ready")
    return s
