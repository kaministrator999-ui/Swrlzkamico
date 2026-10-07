"""Promote the native sightline refinements alongside shared destination tools."""
import json
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent / "scenes"
    projects = []
    for filename, count, zones in [("embervault-atelier.swyrl.json", 170, 8), ("starforge-observatory.swyrl.json", 123, 7)]:
        p = json.loads((root / filename).read_text(encoding="utf-8"))
        actors = p["scene"]["actors"]
        assert len(actors) == count and len({a["id"] for a in actors}) == count, "Authored actors must remain intact"
        assert len(p["editor"]["layers"]) == 3, "Preserve the three project layers"
        assert sum(bool(a.get("workspace")) for a in actors) == 6, "Preserve six stations"
        assert len(p["project"]["teleportZones"]) == zones, "Preserve authored destinations"
        p["engine"] = "§wyrl§ Engine · Maker v8.4"
        p["version"] = 8.4
        projects.append(p)
    encode = lambda p: json.dumps(p, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    start = html.index("const CANONICAL_GLITCH_DEN_PROJECT=")
    end = html.index(";\nfunction loadCanonicalGlitchDen", start)
    s = html[:start] + "const CANONICAL_GLITCH_DEN_PROJECT=" + encode(projects[0]) + ";\nconst CANONICAL_STARFORGE_PROJECT=" + encode(projects[1]) + html[end:]
    assert s.count("V8_3_ZONES_STARFORGE") == 1, "Expected prior release marker"
    s = s.replace("V8_3_ZONES_STARFORGE", "V8_4_WAYFINDING_ZONE_PREVIEW")
    s = s.replace("Maker v8.3", "Maker v8.4").replace("MAKER v8.3", "MAKER v8.4")
    s = s.replace("version:'v8.3'", "version:'v8.4'").replace("version:8.3", "version:8.4")
    s = s.replace("version:'swyrl-engine-agent-v6.3'", "version:'swyrl-engine-agent-v6.4'")
    s = s.replace("§E v8.3 Tools", "§E v8.4 Tools")
    s = s.replace("v8.3 · ZONES & STARFORGE", "v8.4 · WAYFINDING & ZONE PREVIEW")
    s = s.replace("§wyrl§ Engine v8.3 · project workspace ready", "§wyrl§ Engine v8.4 · both project workspaces ready")
    return s
