"""§E v11.535: make the existing Chat-origin Google recovery code reachable at startup.

The v11.177 first-stage pairing proof is displayed inside the Chat iframe.
The v11.476 account gate unintentionally covered that iframe, leaving only its
popup-continuation button reachable. Expose the existing panel for sign-in;
never copy or inspect the proof in the §E host.
"""
import json

PREVIOUS = "SWYRL_ENGINE_DEPLOY_MARKER: V11_534_CHAT_MESH_SHAPE_EDIT"
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_535_STARTUP_SIGNIN_CODE"


def one(html, before, after):
    count = html.count(before)
    if count != 1:
        raise AssertionError(("v11.535 source anchor drift", count, before[:120]))
    return html.replace(before, after, 1)


def apply(html):
    # Bridge code lives inside the existing Chat host closure, where openPanel()
    # and the previously verified two-stage signIn() are already defined.
    html = one(html, " signIn:()=>signIn(),",
               " signIn:()=>{openPanel();return signIn();},")
    # The Chat panel is appended as a sibling after the first-paint startup gate.
    # Only raise it when the gate is visible; do not change regular editor layers.
    html = one(html,
               "#se476StartupCard #se476SignIn[hidden]{display:none!important}",
               "#se476StartupCard #se476SignIn[hidden]{display:none!important}\n"
               "#se476StartupGate:not([hidden]) ~ #seChatAccountPanel:not([hidden]){z-index:2147482460!important}")
    html = one(html,
               "  note('Complete Google sign-in in the secure account window.');\n"
               "  // Synchronous user-click path preserves the popup user gesture.",
               "  note('Copy the one-time code at the top of the secure §Chat panel, then tap Continue to Google there.');\n"
               "  // The Chat-origin first step prepares its proof without opening Google yet.")
    for before, after in (
        (PREVIOUS, MARKER),
        ("ENGINE · MAKER v11.534", "ENGINE · MAKER v11.535"),
        ("v11.534 · native in-place mesh reshaping for §Chat",
         "v11.535 · accessible Google sign-in recovery code"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.534'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.535'"),
        ("<title>§wyrl§ Engine · Maker v11.534</title>",
         "<title>§wyrl§ Engine · Maker v11.535</title>"),
    ):
        html = one(html, before, after)
    previous = " source.engine='§wyrl§ Engine · Maker v11.534';source.version=11.534;"
    assert html.count(previous) == 5
    html = html.replace(previous, previous.replace("11.534", "11.535"))
    start = html.index("const SE_RELEASE_NOTES=") + len("const SE_RELEASE_NOTES=")
    notes, length = json.JSONDecoder().raw_decode(html[start:])
    notes["history"] = [item for item in notes["history"] if item.get("version") != "v11.534"]
    notes["history"].insert(0, {"version": "v11.534", "changes": notes["changes"]})
    notes.update(
        version="v11.535", date="2026-11-22",
        title="Google sign-in code available from the account startup screen",
        changes=[
            "The first-paint account sign-in opens the existing §Chat panel so its one-time recovery code can be read and copied before Google opens.",
            "Continue to Google remains a separate user click in the Chat panel. The proof stays on the Chat origin and is never sent to §E or included in a URL.",
            "The raised Chat panel appears above the startup gate only during startup; regular editor, account project and immersive UI layer rules are unchanged.",
            "Cloud project ownership, session verification, PKCE, native save/revision checks and local offline editing remain under their existing handlers.",
        ],
    )
    release = json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\\/")
    return html[:start] + release + html[start + length:]
