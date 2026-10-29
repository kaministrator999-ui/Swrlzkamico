"""Ship the editor-authored, three-tier Embervault project without engine-owned layout."""
import json
from pathlib import Path


def apply(html):
    scene_path = Path(__file__).resolve().parent.parent / "scenes" / "embervault-atelier.swyrl.json"
    project = json.loads(scene_path.read_text(encoding="utf-8"))
    actors = project["scene"]["actors"]
    assert len({a["id"] for a in actors}) == len(actors), "Duplicate canonical actor ID"
    assert len(project["editor"]["layers"]) == 3, "The den must carry its authored layers"
    assert sum(bool(a.get("workspace")) for a in actors) == 6, "Six usable stations required"
    assert any(a.get("blueprintClass") == "DEN_ramp" for a in actors), "Walkable terraces required"
    project["engine"] = "§wyrl§ Engine · Maker v8.0"
    project["version"] = 8.0
    encoded = json.dumps(project, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    start = html.index("const CANONICAL_GLITCH_DEN_PROJECT=")
    end = html.index(";\nfunction loadCanonicalGlitchDen", start)
    s = html[:start] + "const CANONICAL_GLITCH_DEN_PROJECT=" + encoded + html[end:]
    s = s.replace("V7_9_SANCTUARY_CANONICAL_PROJECT", "V8_0_EMBERVAULT_WORKSPACE")
    s = s.replace("Maker v7.9", "Maker v8.0").replace("MAKER v7.9", "MAKER v8.0")
    s = s.replace("version:'v7.9'", "version:'v8.0'")
    s = s.replace("version:'swyrl-engine-agent-v5.9'", "version:'swyrl-engine-agent-v6.0'")
    s = s.replace("version:7.9", "version:8.0")
    s = s.replace("v7.9 · SANCTUARY CANONICAL PROJECT", "v8.0 · EMBERVAULT WORKSPACE")
    s = s.replace("Glitch Dragon Den — Sanctuary & Makers Grotto", "Dragon Den — Embervault Atelier")
    s = s.replace("Open Sanctuary & Makers Grotto", "Open Embervault Atelier")
    s = s.replace("Glitch Dragon Den · Sanctuary & Makers Grotto", "Dragon Den · Embervault Atelier")
    s = s.replace("canonicalStarter:'sanctuary-makers-grotto-r14'", "canonicalStarter:'embervault-atelier-v8'")
    s = s.replace("stamp:'2026.10.05'", "stamp:'2026.10.07'")
    s = s.replace("Forge v5 Tools", "§E v8.0 Tools")
    s = s.replace("defaultDenAvatar:'wisp'", "defaultDenAvatar:'walking-visitor'")
    s = s.replace("  currentProject={...p.project};\n", "")
    s = s.replace("authored Sanctuary revision 14 · 120 actors", "three walkable tiers · " + str(len(actors)) + " actors")
    s = s.replace("The editor-authored 120-actor Sanctuary & Makers Grotto, promoted directly from the saved §E project.", "A three-tier project sanctuary with six usable workstations, ramps, galleries, and dragon guardians.")
    boot = 'buildDragonsDenProject();refreshAssetList();initializeHistory("Initial Dragon\'s Den — Seed Chamber");setCameraView(\'perspective\');editorLog(\'§wyrl§ Engine v7.6 initialized · polished desktop editor chrome\',\'ok\');setSessionButtons();tick();'
    if boot not in s:
        raise RuntimeError("v8.0 canonical bootstrap anchor missing")
    s = s.replace(boot, "loadCanonicalGlitchDen();refreshAssetList();setCameraView('perspective');editorLog('§wyrl§ Engine v8.0 · Embervault Atelier · three-tier workspace ready','ok');setSessionButtons();tick();", 1)
    return s
