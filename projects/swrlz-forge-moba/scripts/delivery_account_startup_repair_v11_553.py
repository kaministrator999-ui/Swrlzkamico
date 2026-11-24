"""Delivery-only recovery for §E v11.552 account-first startup.

The sealed historical 526-patch engine source and its SHA receipt stay immutable.
Only the external JS module uploaded to Hugging Face is modified, with strict
anchors and auditable fingerprints. No project data or credentials are touched.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "/* SE476_ENGINE_ACCOUNT_START_START */"
END = "/* SE476_ENGINE_ACCOUNT_START_END */"

OLD_DEADLINE = """   state.timeout=setTimeout(()=>{
    complete(state,false,'Account project not available yet. Sign in through § Chat, then load it in My Projects.');
   },11000);"""
NEW_DEADLINE = """   // Google authentication can take longer than eleven seconds. The native
   // cloud RPC handles its own load timeout after authentication completes.
   // Keep the first-paint local workspace escape available meanwhile.
   state.timeout=null;"""
OLD_RECEIPT = "report:()=>boot?{attempted:true,source:boot.source,pending:boot.pending,loading:boot.loading,success:boot.success??null,reason:boot.reason||''}:{attempted:false}"
NEW_RECEIPT = "report:()=>boot?{attempted:true,source:boot.source,id:boot.id,pending:boot.pending,loading:boot.loading,success:boot.success??null,reason:boot.reason||''}:{attempted:false}"


def once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Account delivery repair: {name} anchor expected once, got {count}")
    return text.replace(old, new, 1)


def apply(module):
    """Return the patched delivery JS and its transparent verification receipt."""
    text = module.decode("utf-8")
    start = text.find(START)
    end = text.find(END, start)
    if start < 0 or end < start or text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Account startup section missing or duplicated in sealed JS")
    end += len(END)
    current = (ROOT / "runtime/engine_account_start_delivery_v11_553.js").read_text("utf-8").strip()
    if not current.startswith(START) or not current.endswith(END):
        raise ValueError("Repair runtime lacks the exact startup section markers")
    if "const entry=automatic?(override||defaults()):(override||chosenRow());" not in current:
        raise ValueError("Explicit current workspace selection fix is missing")
    if "receipt.id===entry.id" not in current:
        raise ValueError("Saved-default receipt identity check is missing")
    before = text[start:end]
    if "const entry=override||chosenRow()||defaults();" not in before:
        raise ValueError("Expected historical startup section is not present")
    text = text[:start] + current + text[end:]
    text = once(text, OLD_DEADLINE, NEW_DEADLINE, "premature cloud deadline")
    text = once(text, OLD_RECEIPT, NEW_RECEIPT, "receipt identity")
    if OLD_DEADLINE in text or OLD_RECEIPT in text:
        raise ValueError("Stale default boot remained in delivery output")
    delivered = text.encode("utf-8")
    return delivered, {
        "mode": "source-sealed-delivery-account-recovery-v11.553",
        "originalModuleSha256": hashlib.sha256(module).hexdigest(),
        "patchedModuleSha256": hashlib.sha256(delivered).hexdigest(),
        "startupBeforeSha256": hashlib.sha256(before.encode("utf-8")).hexdigest(),
        "startupAfterSha256": hashlib.sha256(current.encode("utf-8")).hexdigest(),
        "earlyCloudDeadlineRemoved": True,
        "receiptIdentityChecked": True,
        "explicitWorkspaceChoice": True,
        "credentialsChanged": False,
        "projectDataChanged": False,
    }
