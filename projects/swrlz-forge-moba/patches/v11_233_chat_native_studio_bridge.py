"""§E v11.233 candidate: typed Chat studio operations under existing host security.

The native Chat host source at v11.169 is a single canonical owner. This final
append-only patch changes only the governed release identity; it does not
redeclare an executor or change prior project/renderer logic.
"""
import json

def once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise AssertionError(("v11.233 expected one version/marker anchor", old[:90], count))
    return text.replace(old, new, 1)

def apply(html):
    needed = [
        "function seChatRigApply(op)", "function studioSnapshot(workspace)",
        "function validateStudioOperation(op,ctx)", "function executeStudio(op)",
        "swrlz-forge-studio-commands-v1",
        "SWYRL_ENGINE_MATERIALS", "SWYRL_ENGINE_PARTICLES",
        "function se224WolfRigSpec", "function se220RigAvailable",
    ]
    for marker in needed:
        if marker not in html:
            raise AssertionError(("missing studio bridge dependency", marker))
    old = " source.engine='§wyrl§ Engine · Maker v11.232';source.version=11.232;"
    new = " source.engine='§wyrl§ Engine · Maker v11.233';source.version=11.233;"
    if html.count(old) != 2:
        raise AssertionError(("v11.233 source provenance count", html.count(old)))
    html = html.replace(old, new)
    for before, after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_232_MODEL_STARTER_WORKSPACE_ACTIVATION",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_233_CHAT_NATIVE_STUDIO_BRIDGE"),
        ("ENGINE · MAKER v11.232", "ENGINE · MAKER v11.233"),
        ("v11.232 · model starter workspace activation",
         "v11.233 · Chat Studio Commands v1 reviewed native editing"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.232'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.233'"),
        ("<title>§wyrl§ Engine · Maker v11.232</title>",
         "<title>§wyrl§ Engine · Maker v11.233</title>"),
    ):
        html = once(html, before, after)
    marker = 'const SE_RELEASE_NOTES='
    at = html.index(marker) + len(marker)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(
        title="Chat-assisted material, particle and rig edits with native receipts",
        date="2026-11-02",
        changes=[
            "Add Studio Commands v1 discovery in the existing authenticated Chat host: material, particle and Model Atelier rig operations require an open matching editor and exact IDs.",
            "Material presets, PBR parameter edits and assignments reuse native Materials Studio transactions, validation, actors and history.",
            "Particle presets and bounded emitter parameter edits reuse native Particle Studio transactions and project saves.",
            "Pose one existing glove/wolf bone or save one bounded animation keyframe using the real Model Atelier source and skinning preview.",
            "Only single-step Studio Commands are accepted, under the existing host lease, frozen explicit preview, human approval and actual receipt flow; generated JavaScript never executes.",
            "Old Chat and old Engine revisions cannot gain these tools by inference. No new renderer, unguarded API, unrelated gameplay rules or VR control changes.",
            "Owner Moto G Power and Quest acceptance plus separate Chat-server release validation remain outstanding."
        ]
    )
    return html[:at] + json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/') + html[at+width:]
