"""§E v11.532 — checked native account-save receipts without write replay.

The release owner adds this append-only patch to the manifest and synchronizes
runtime/release identity. apply_save_repair is also used by the focused composed
source regression before packaging; it does not build or reseal an artifact.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def one(text, before, after, label):
    count = text.count(before)
    if count != 1:
        raise AssertionError(("v11.532", label, count, before[:120]))
    return text.replace(before, after, 1)


def apply_save_repair(html):
    runtime = (ROOT / "runtime/project_account_save_receipt_v11_532.js").read_text("utf8")
    html = one(html, "/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START */",
               runtime + "\n/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START */",
               "receipt guard inside original authenticated closure")
    # Instrument only the full native project writer. The asset writer and
    # private authenticated RPC remain separate and unchanged.
    html = one(html, "const result=await rpc('cloud.save',{bytes:bytes.buffer,\n",
               "const result=await se532ProjectSaveRpc('cloud.save',{bytes:bytes.buffer,\n",
               "project-only write dispatch receipt")
    start = html.index("/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START */")
    end = html.index("/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_END */", start)
    block = html[start:end]
    block = one(block, "  await se371SaveLocal();",
                "  await se532PrepareProjectAccountSave();\n  await se371SaveLocal();",
                "restore persisted account linkage before snapshot overwrite")
    block = one(block, "const confirmed=await se371PreviousSaveCloud()===true;",
                "const confirmed=await se532SaveCheckedProjectAccount()===true;",
                "checked v371 facade captured before model asset redirection")
    block = one(block,
                "(!linkedBefore||linked.id===linkedBefore.id&&linked.revision>linkedBefore.revision);",
                "(!linkedBefore||linked.id===linkedBefore.id&&linked.revision>linkedBefore.revision||\n"
                "    se532RecoveredReceiptMatches(idBefore,linked));",
                "verified recovery receipt without an extra account write")
    return html[:start] + block + html[end:]


def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_MENU_GIZMO_ACCOUNT" in html
    html = apply_save_repair(html)
    for before, after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_MENU_GIZMO_ACCOUNT",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_532_PROJECT_ACCOUNT_SAVE_RECEIPT"),
        ("ENGINE · MAKER v11.531", "ENGINE · MAKER v11.532"),
        ("v11.531 · stable Quest menu, held-axis gizmos and cloud project open",
         "v11.532 · verified account saves and preserved project identity"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.531'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.532'"),
        ("<title>§wyrl§ Engine · Maker v11.531</title>",
         "<title>§wyrl§ Engine · Maker v11.532</title>"),
    ):
        html = one(html, before, after, "release identity")
    before = " source.engine='§wyrl§ Engine · Maker v11.531';source.version=11.531;"
    assert html.count(before) == 5, ("v532 provenance", html.count(before))
    html = html.replace(before, " source.engine='§wyrl§ Engine · Maker v11.532';source.version=11.532;")
    key = "const SE_RELEASE_NOTES="
    at = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes["history"] = [item for item in notes.get("history", []) if item.get("version") != "v11.531"]
    notes["history"].insert(0, {"version": "v11.531", "changes": notes.get("changes", [])})
    notes.update(version="v11.532", date="2026-11-20", title="Verified project account saves and recovery receipts", changes=[
        "Full-project account saving uses the checked native save facade, confirming a durable revision and remembering the project account link instead of reporting a successful write as failure.",
        "Startup saves restore the persisted account identity and revision before refreshing the local snapshot, preserving same-project saves after reopening.",
        "A small local receipt is stored before account write dispatch; an uncertain response is never blindly replayed as another project or revision.",
        "Recovery verifies the exact account project ID, revision, local identity and saved bytes through authenticated reads before accepting a lost acknowledgement.",
        "Local autosave, project history, model assets, geometry, UVs, rigging, existing projects and the established GitHub to Hugging Face workflow are preserved.",
    ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/") + html[at + width:]
