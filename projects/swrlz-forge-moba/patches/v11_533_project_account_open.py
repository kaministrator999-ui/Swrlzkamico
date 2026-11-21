"""§E v11.533 appends a fix for the composed native account load path."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = "SWYRL_ENGINE_DEPLOY_MARKER: V11_532_PROJECT_ACCOUNT_SAVE_RECEIPT"
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_533_PROJECT_ACCOUNT_OPEN"


def one(text, before, after):
    count = text.count(before)
    if count != 1:
        raise AssertionError(("v11.533", count, before[:120]))
    return text.replace(before, after, 1)


def apply_account_open(html):
    runtime = (ROOT / "runtime/project_account_open_v11_533.js").read_text("utf8")
    start = html.index("loadCloud=async function(projectKey){")
    end = html.index("let se528SaveBusy=false;", start)
    html = html[:start] + runtime + "\n" + html[end:]
    html = one(
        html,
        "if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX_RAW||!result.project?.id)throw Error('Invalid account project download.');",
        """if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX_RAW||
       result.project?.id!==projectId||!Number.isSafeInteger(result.project.revision)||result.project.revision<1)
      throw Error('Invalid account project download or revision. The editor was preserved.');""",
    )
    return one(
        html,
        "    const loaded=await se518CloudCache.load(choice.slice(6));\n    if(!loaded)setStatus('Account project could not be loaded; current workspace preserved.',true);",
        """    const diagnostics=window.SWYRL_ENGINE_PROJECT_LOAD_493;
    diagnostics.reset();
    const loaded=await se518CloudCache.load(choice.slice(6));
    if(!loaded&&!diagnostics.getError())
      se533AccountOpenFailure('Account project could not be loaded. Check that §Chat is connected and the editor is idle.');""",
    )


def apply(html):
    html = apply_account_open(html)
    for before, after in (
        (PREVIOUS, MARKER),
        ("ENGINE · MAKER v11.532", "ENGINE · MAKER v11.533"),
        ("v11.532 · verified account saves and preserved project identity",
         "v11.533 · verified account project opening"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.532'", "window.SWRLZ_FORGE_BUILD={version:'v11.533'"),
        ("<title>§wyrl§ Engine · Maker v11.532</title>", "<title>§wyrl§ Engine · Maker v11.533</title>"),
    ):
        html = one(html, before, after)
    provenance = " source.engine='§wyrl§ Engine · Maker v11.532';source.version=11.532;"
    assert html.count(provenance) == 5
    html = html.replace(provenance, provenance.replace("11.532", "11.533"))
    start = html.index("const SE_RELEASE_NOTES=") + len("const SE_RELEASE_NOTES=")
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes["history"] = [item for item in notes["history"] if item.get("version") != "v11.532"]
    notes["history"].insert(0, {"version": "v11.532", "changes": notes["changes"]})
    notes.update(version="v11.533", date="2026-11-21", title="Verified account project opening", changes=[
        "Account project opening passes the explicit project ID to the native loader from project cards, startup, §Chat and immersive projects.",
        "Opening requires a newly confirmed import and matching account revision. A failed reopen preserves the current editor and explains the error.",
        "Native history, account saves, model assets and the same-revision on-device cache stay on their established paths.",
    ])
    release = json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")
    return html[:start] + release + html[start + width:]
