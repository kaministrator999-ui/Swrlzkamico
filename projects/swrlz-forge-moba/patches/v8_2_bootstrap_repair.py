"""§wyrl§ Engine v8.2 — repair v8.1 performance bootstrap ordering."""
def apply(html):
    s=html
    bad="scene.add(sun);\ninstallPerformanceSettings();applyPerformanceSettings();"
    if s.count(bad)!=1: raise RuntimeError("v8.2 expected v8.1 early performance bootstrap")
    s=s.replace(bad,"scene.add(sun);",1)
    boot="loadCanonicalGlitchDen();refreshAssetList();setCameraView('perspective');editorLog('§wyrl§ Engine v8.0 · Embervault Atelier · three-tier workspace ready','ok');setSessionButtons();tick();"
    if s.count(boot)!=1: raise RuntimeError("v8.2 canonical bootstrap anchor missing")
    fixed="installPerformanceSettings();applyPerformanceSettings();loadCanonicalGlitchDen();refreshAssetList();setCameraView('perspective');editorLog('§wyrl§ Engine v8.2 · Embervault Atelier · bootstrap repaired','ok');setSessionButtons();tick();"
    s=s.replace(boot,fixed,1)
    s=s.replace("V8_1_PERFORMANCE_GRAPHICS","V8_2_BOOTSTRAP_REPAIR")
    s=s.replace("Maker v8.1","Maker v8.2").replace("MAKER v8.1","MAKER v8.2")
    s=s.replace("version:'v8.1'","version:'v8.2'").replace("version:'swyrl-engine-agent-v6.1'","version:'swyrl-engine-agent-v6.2'")
    s=s.replace("version:8.1","version:8.2").replace("v8.1 · PERFORMANCE + GRAPHICS","v8.2 · BOOTSTRAP REPAIR")
    s=s.replace("§E v8.1 Tools","§E v8.2 Tools")
    s=s.replace("§wyrl§ Engine v8.1 · Embervault Atelier · performance controls ready","§wyrl§ Engine v8.2 · Embervault Atelier · bootstrap repaired")
    return s
