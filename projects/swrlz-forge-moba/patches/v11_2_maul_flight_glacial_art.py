"""v11.2: independent Frostveil flying builders and original glacial art.

Additive after sealed v11.1. Historical map profiles and earlier patches remain unchanged.
"""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1, "Ambiguous §E v11.2 integration anchor: "+old[:100]
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    modules="\n".join((root/"runtime"/name).read_text(encoding="utf-8") for name in (
        "maul_flight_core.js","maul_flight_integration.js","maul_frostveil_art.js"
    ))
    import json
    starter=json.loads((root/"scenes/maul-frostveil-flight.swyrl.json").read_text(encoding="utf-8"))
    assert starter["project"]["maulBuilderFlight"]=="hover-v1" and starter["project"]["maulVisualStyle"]=="glacial-v2"
    canonical="const MAUL_FLIGHT_CANONICAL_PROJECT="+json.dumps(starter,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+";\n"
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        "// MAUL_FLIGHT_ART_V11_2_BEGIN\n"+canonical+modules+"\nwindow.SWRLZ_FORGE_BUILD=")
    html=once(html,"V11_1_MAUL_WALK_BUILDER","V11_2_MAUL_FLIGHT_GLACIAL_ART")
    html=html.replace("Maker v11.1","Maker v11.2").replace("MAKER v11.1","MAKER v11.2")
    html=html.replace("version:'v11.1'","version:'v11.2'").replace("version:11.1","version:11.2")
    html=html.replace("§E v11.1 Tools","§E v11.2 Tools")
    html=html.replace("v11.1 · FROSTVEIL BUILDERS · PROTECTED ENTRANCES",
        "v11.2 · FLYING BUILDERS · GLACIAL ART")
    html=html.replace("§wyrl§ Engine v11.1 · Builder construction and protected spawns",
        "§wyrl§ Engine v11.2 · Flying builders and glacial map art")
    return html
