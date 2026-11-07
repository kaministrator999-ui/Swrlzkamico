"""§E v11.331 — finish Smooth Cliff Hand PBR plumbing without changing its mesh or rig."""
import json

MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_331_SMOOTH_CLIFF_MATERIAL_UV"
def once(html, old, new, label):
    count = html.count(old)
    if count != 1:
        diag = {}
        if label == "provide a second UV channel for the cliff AO texture":
            for key in ("function atelierTopologyGeometry(part){", "function se220RigMesh(part){", "setAttribute('uv'", "setAttribute('uv2'"):
                at = html.find(key)
                diag[key] = (at, html[max(0, at - 100):at + 620] if at >= 0 else "")
        raise AssertionError(("v11.331", label, count, old[:110], diag))
    return html.replace(old, new, 1)

def apply(html):
    # A later rigged-mesh pass ALREADY adds uv2 for cliff materials. Do not
    # duplicate its working channel. Recent Three.js versions call the same
    # second set "uv1"; alias the existing attribute just for this starter.
    old = (" if(part.cliffPBR&&g.getAttribute('uv')&&!g.getAttribute('uv2'))\n"
           "  g.setAttribute('uv2',g.getAttribute('uv').clone());")
    new = old + ("\n if(part.cliffPBR?.atlas==='cliff_pbr_atlas_384'&&"
                 "g.getAttribute('uv2')&&!g.getAttribute('uv1'))\n"
                 "  g.setAttribute('uv1',g.getAttribute('uv2'));")
    html = once(html, old, new, "preserve existing AO uv2 and alias modern uv1")

    # Newer Three versions select the uv2 attribute using Texture.channel.
    # Older versions ignore this property and use the uv2 attribute directly.
    html = once(html,
        " tex.colorSpace=kind==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;",
        " tex.colorSpace=kind==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;\n if(kind==='ao')tex.channel=1;",
        "route cliff ambient occlusion map through UV1")

    # Use the source albedo without adding another orange tint. Keep physically
    # plausible stone roughness, normal strength, and matched painted knuckles.
    html = once(html,
        "function se292WristMossKnuckleMaterial(part){\n const t=se292TextureSet();\n const mat=new THREE.MeshStandardMaterial({\n  color:'#fff2e6',",
        "function se292WristMossKnuckleMaterial(part){\n const t=se292TextureSet();\n const mat=new THREE.MeshStandardMaterial({\n  color:'#ffffff',",
        "do not double-tint authored sandstone albedo")
    html = once(html,
        "  aoMap:t.ao,aoMapIntensity:1.24,",
        "  aoMap:t.ao,aoMapIntensity:1,",
        "normalize AO intensity after actually enabling it")

    previous = " source.engine='§wyrl§ Engine · Maker v11.330';source.version=11.330;"
    if html.count(previous) != 3:
        raise AssertionError(("v11.331", "scene provenance", html.count(previous)))
    html = html.replace(previous,
        " source.engine='§wyrl§ Engine · Maker v11.331';source.version=11.331;")
    for old, new in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_330_MATERIAL_STUDIO_LAYOUT", MARKER),
        ("ENGINE · MAKER v11.330", "ENGINE · MAKER v11.331"),
        ("v11.330 · dedicated Materials workspace and responsive authoring",
         "v11.331 · Smooth Cliff Hand mapped PBR and AO UV repair"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.330'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.331'"),
        ("<title>§wyrl§ Engine · Maker v11.330</title>",
         "<title>§wyrl§ Engine · Maker v11.331</title>"),
    ):
        html = once(html, old, new, "release identity")
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, used = json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version') == 'v11.330' for x in notes.get('history', [])):
        notes.setdefault('history', []).insert(0, {
            'version': 'v11.330', 'changes': notes.get('changes', [])})
    notes.update(
        version='v11.331',
        title='Smooth Cliff Hand: restore mapped crevice shading and sandstone fidelity',
        date='2026-11-07',
        changes=[
            'Give the Smooth Cliff Hand a dedicated second native UV channel for ambient occlusion; the original connected geometry supplied only a primary UV set.',
            'Explicitly select the secondary map channel on modern Three.js while retaining compatibility with the older uv2 sampling path.',
            'Remove unintended material tint so the owner-sourced sandstone albedo appears in its mapped colors, and return AO intensity to the physically supported range.',
            'Keep existing normal and roughness maps, wrist-only moss mask, four painted knuckle ridges, one connected hand/gauntlet mesh, original 17-bone rig, and animation untouched.',
            'Leave unrelated starters, Material Studio, VR controllers, Sheep Tag, saved projects and AI Chat unchanged; phone and Quest visual acceptance belongs to owner.'
        ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[at + used:]
