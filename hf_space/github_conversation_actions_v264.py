"""v264 conversational GitHub actions: inspect first, no pop-ups, no silent writes.

The accepted user's Chat turn is the sole source of requested paths/content.
Read-only repository preflight precedes a bounded one-action approval. Pending
approvals are bound to Google account + chat thread, expire, and are consumed
by the next direct 'yes'/'no' turn. Never select a fuzzy file for mutation.
"""
from __future__ import annotations
import base64
import difflib
import re
import threading
import time

from github_general_create_v262 import ALLOWED_REPOS, CreateFileError, safe_path
import github_general_create_v262 as create
import github_rename_v263 as rename

_lock = threading.RLock()
_pending = {}
TTL = 300
_YES = re.compile(r"\s*(?:yes|yes please|yep|yup|confirm|approve|go ahead|do it|proceed|yes[,]? rename(?: it)?|yes[,]? create(?: it)?)\s*[.!]?\s*", re.I)
_NO = re.compile(r"\s*(?:no|nope|cancel|decline|stop|don't|do not|never mind|nevermind)\s*[.!]?\s*", re.I)
_RENAME = re.compile(r"\b(?:rename|move)\s+(?:the\s+|my\s+|a\s+)?(?:file\s+)?", re.I)
_CREATE = re.compile(r"\b(?:create|make|add|upload|save|write)\s+(?:a\s+|the\s+|new\s+|me\s+|an\s+)?(?:file\s+)?", re.I)
_EXPLAIN = re.compile(r"\b(?:how\s+(?:do|can|to|would)|explain|tutorial|show\s+me\s+how|"
                      r"implement|add\s+(?:a\s+)?(?:feature|capability|support)|"
                      r"(?:needs?|should)\s+(?:to\s+)?be\s+able)\b", re.I)
_CODE_REQUEST = re.compile(r"\b(?:write|create|generate)\s+(?:\w+\s+){0,4}(?:code|script|function|program)\s+to\s+(?:rename|move|create)\b",re.I)
_NEGATE = re.compile(r"\b(?:do\s+not|don't|dont|never)\s+(?:\w+\s+){0,3}(?:rename|move|create|make|add|upload|save|write)\b", re.I)
_PATH = r"(?:" + r"\x60([^\x60\n]+)\x60" + r"|[\"“]([^\"”\n]+)[\"”]|([^\s\x60\"“”<>?*|]+))"
_RENAME_PATHS = re.compile(r"\b(?:rename|move)\s+(?:the\s+|my\s+|a\s+)?(?:file\s+)?"+_PATH+
                           r"\s+(?:to|as|into)\s+"+_PATH,re.I)
_FOLLOWUP_RENAME = re.compile(r"\brename\s+(?:(?:that|this|the|same)\s+file|it)\b",re.I)
_FOLLOWUP_DESTINATION = re.compile(r"\b(?:to|too|as|into)\s+"+_PATH+r"\s*[.!]?\s*$",re.I)
_FILE_NAME = re.compile(r"\b(?:named|called|filename|path)\s*[:=]?\s*"+_PATH,re.I)
_SIMPLE_FILE = re.compile(r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.[A-Za-z0-9_-]{1,16})(?![\w])")
_TEXT_FIELD = re.compile(r"(?:^|\n)\s*(?:file\s+)?contents?\s*:\s*([\s\S]+)$",re.I)
_QUOTED_TEXT = re.compile(r"\b(?:containing|saying|with\s+the\s+text)\s+[\"“]([^\"”]+)[\"”]\s*[.!]?\s*$",re.I)


def _path_part(match, offset=1):
    return next((match.group(i) for i in range(offset, offset + 3) if match.group(i) is not None), "")


def _trim_path(s):
    return str(s or "").strip().rstrip(".,;!?")


def _clean_label(s):
    # Paths may contain uncommon Unicode or markup punctuation. Escape Markdown
    # rather than allowing arbitrary user filenames to create links or HTML.
    return chr(96) + str(s).replace("\\", "\\\\").replace(chr(96), "\\"+chr(96)).replace("\n", " ")[:512] + chr(96)


def _out(text, widget=None, github_context=None):
    result={"handled": True, "text": text, "widget": widget}
    # Context is supplied only by a verified provider receipt from an action,
    # never by a natural-language filename or an unapproved proposal.
    if github_context is not None:result["githubContext"]=github_context
    return result


def is_file_action(prompt, context=None, history=None):
    if not isinstance(prompt, str) or len(prompt) > 10000 or _EXPLAIN.search(prompt) or _NEGATE.search(prompt) or _CODE_REQUEST.search(prompt):
        return False
    lower=prompt.lower()
    if _RENAME.search(prompt):
        return bool(_RENAME_PATHS.search(prompt) or re.search(r"\b(?:github|repo|repository)\b",prompt,re.I)
                    or _contextual_rename(prompt,context,history))
    if _CREATE.search(prompt):
        return bool(re.search(r"\b(?:github|repo|repository)\b",prompt,re.I)
                    and (re.search(r"\b(?:file|script|document|upload)\b",prompt,re.I) or _SIMPLE_FILE.search(prompt)))
    return False


def pending_kind(user_id,thread_id):
    with _lock:
        p=_pending.get((user_id,thread_id))
        return p["kind"] if p and p["expiry"]>time.monotonic() else None


def is_reply(prompt):
    return bool(isinstance(prompt,str) and (_YES.fullmatch(prompt) or _NO.fullmatch(prompt)))


def expire_interrupted(user_id,thread_id):
    """User changed topics: an older conversational yes cannot approve a write."""
    _consume(user_id,thread_id)


def has_pending(user_id, thread_id):
    with _lock:
        p = _pending.get((user_id, thread_id))
        return bool(p and p["expiry"] > time.monotonic())


def _remember(user_id, thread_id, value):
    with _lock:
        for key,p in list(_pending.items()):
            if p["expiry"] < time.monotonic(): _pending.pop(key,None)
        _pending[(user_id,thread_id)] = {**value, "expiry": time.monotonic()+TTL}


def _consume(user_id, thread_id):
    with _lock:
        return _pending.pop((user_id,thread_id),None)


def _read_tree(user_id):
    # Read authorization is distinct from write scope; a missing file should
    # still be reported when the user has connected read access only.
    from github_connection import _config,_load,_effective_access
    if not isinstance(user_id,str) or not user_id.startswith("google:"):
        raise CreateFileError("GOOGLE_SIGN_IN_REQUIRED",401)
    record = _load(_config(),user_id)
    if not record: raise CreateFileError("GITHUB_NOT_CONNECTED",403)
    repo = record.get("repo")
    if repo not in ALLOWED_REPOS:
        raise CreateFileError("SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED",403)
    try:
        permission = _effective_access(record,repo,"read")
    except Exception as exc:
        from fastapi import HTTPException
        if isinstance(exc,HTTPException):
            raise CreateFileError("GITHUB_READ_ACCESS_REQUIRED",exc.status_code) from None
        raise
    if not permission.get("allowed"):
        raise CreateFileError("GITHUB_READ_ACCESS_REQUIRED",403)
    branch = permission.get("defaultBranch")
    if not isinstance(branch,str) or not branch:
        raise CreateFileError("INVALID_DEFAULT_BRANCH",403)
    auth={"repo":repo,"branch":branch,"token":record["token"]}
    head,root=rename._head(auth)
    entries=rename._tree(auth,root)
    return auth,entries,head


def _closest(entries,requested):
    names=[p for p,item in entries.items() if item.get("type")=="blob"]
    base=requested.rsplit("/",1)[-1].casefold()
    rank=[]
    for p in names:
        fname=p.rsplit("/",1)[-1].casefold()
        score=difflib.SequenceMatcher(None,base,fname).ratio()
        if fname==base:score=1.0
        elif p.casefold()==requested.casefold():score=.99
        if score>=.57:rank.append((score,p))
    rank.sort(key=lambda item:(-item[0],len(item[1]),item[1].casefold()))
    return [p for _,p in rank[:3]]


def _contextual_rename(prompt,context,history):
    """Use a recent user-named file only when there is a verified same-thread scope.

    Prior user text is an intent hint, never authorization for a GitHub write.
    A case-sensitive Git blob lookup and fresh approval are mandatory.
    """
    if not isinstance(context,dict) or not isinstance(history,list):
        return None
    if not (context.get("repo") and context.get("branch")
            and re.fullmatch(r"[0-9a-f]{40}",str(context.get("sourceSha") or ""))):
        return None
    m=_FOLLOWUP_RENAME.search(str(prompt or ""))
    if not m:return None
    destination_match=_FOLLOWUP_DESTINATION.search(str(prompt or "")[m.end():])
    destination=_trim_path(_path_part(destination_match)) if destination_match else ""
    # Prefer a verified file context over guesses from older user messages.
    last_file=str(context.get("lastFile") or "").strip()
    if last_file and context.get("kind")=="file":
        return last_file,destination
    for msg in reversed(history[-10:]):
        if not isinstance(msg,dict) or msg.get("role")!="user":continue
        prior=str(msg.get("text") or "")
        if not re.search(r"\b(?:file|see|read|find|open|check)\b",prior,re.I):continue
        names=_SIMPLE_FILE.findall(prior)
        if len(names)==1:
            return names[0],destination
        if names:return None
    return None


def _rename_paths(prompt,context=None,history=None):
    m = _RENAME_PATHS.search(prompt)
    if m:return _trim_path(_path_part(m,1)), _trim_path(_path_part(m,4)), False
    prior=_contextual_rename(prompt,context,history)
    return (*prior,True) if prior else None


def _create_parts(prompt):
    match=_FILE_NAME.search(prompt)
    path=_trim_path(_path_part(match)) if match else ""
    if not path:
        m=_SIMPLE_FILE.search(prompt)
        if m:path=m.group(1)
    content=_TEXT_FIELD.search(prompt)
    if content:return path,content.group(1)
    q=_QUOTED_TEXT.search(prompt)
    if q:return path,q.group(1)
    return path,None


def _user_friendly_failure(exc):
    code=getattr(exc,"code",None)
    mapped={
        "GOOGLE_SIGN_IN_REQUIRED":"Please sign in with Google so I can check the selected GitHub repository.",
        "GITHUB_NOT_CONNECTED":"Your GitHub account isn't connected. Connect it first and I'll check the files.",
        "SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED":"Select one of your supported GitHub repositories first.",
        "GITHUB_WRITE_SCOPE_REQUIRED":"I found the file, but GitHub hasn't authorized writing to this repository yet. Approve the GitHub public-write scope before renaming it.",
        "GITHUB_READ_ACCESS_REQUIRED":"GitHub read access isn't currently authorized for the selected repository.",
        "GITHUB_PUSH_PERMISSION_REQUIRED":"The connected account cannot write to the selected repository.",
        "DESTINATION_ALREADY_EXISTS":"That destination already exists. I didn't overwrite it.",
        "SOURCE_FILE_NOT_FOUND":"That source file no longer exists. Nothing changed.",
        "REPOSITORY_CHANGED_REPREPARE_REQUIRED":"The branch changed since the proposal. No rename was confirmed; ask again to recheck.",
        "GITHUB_RENAME_CONFLICT_OR_PROTECTION":"GitHub rejected the rename (branch changed or protected). Nothing further was attempted.",
        "GITHUB_FILE_EXISTS_OR_CONFLICT":"That file already exists or GitHub rejected the create. I didn't overwrite it.",
        "APPROVAL_EXPIRED_OR_WRONG_ACCOUNT":"That approval expired or doesn't match this account. Please request the change again.",
        "GITHUB_WORKFLOW_SCOPE_REQUIRED":"GitHub needs a separate workflow permission for that path; I didn't change it.",
        "GITHUB_TREE_UNAVAILABLE_OR_TRUNCATED":"GitHub couldn't provide a complete file listing. I can't safely identify or rename the file.",
    }
    return mapped.get(code,"I couldn't verify the GitHub operation ("+str(code or "UNAVAILABLE")+"). I didn't attempt another change.")


def _confirmation(user_id,thread_id,prompt):
    pending=_consume(user_id,thread_id)
    if not pending:return None
    if _NO.fullmatch(prompt):
        # The underlying ticket is still account-bound; decline consumes it.
        try:
            if pending["kind"]=="rename":
                rename.confirm(user_id,pending["ticket"],False)
            elif pending["kind"]=="create":
                create.confirm(user_id,pending["ticket"],False)
        except CreateFileError:
            pass
        return _out("Cancelled. Nothing changed.")
    if pending["kind"]=="need-destination":
        if _YES.fullmatch(prompt):
            _remember(user_id,thread_id,pending)
            return _out("What new filename should I use? No file has changed.")
        # A filename-only answer or an explicit "rename it too NAME" is accepted
        # as a destination, never as approval to mutate.
        requested=str(prompt or "").strip()
        match=_FOLLOWUP_DESTINATION.search(requested)
        if match and _FOLLOWUP_RENAME.search(requested):
            requested=_trim_path(_path_part(match))
        if not _SIMPLE_FILE.fullmatch(requested):
            return _out("Please give one new filename, such as testing1.txt. Nothing changed.")
        return _prepare_rename(user_id,thread_id,"rename that file to "+requested,
                               pending["context"],[])
    if pending["kind"]=="need-content":
        if _YES.fullmatch(prompt):
            return _out("I still need the file contents. Paste the exact text you want saved.")
        if len(prompt.encode("utf-8"))>create.MAX_FILE_BYTES:
            return _out("That content exceeds the 1,000,000-byte file limit. Nothing changed.")
        return _prepare_create(user_id,thread_id,pending["path"],prompt)
    if not _YES.fullmatch(prompt):
        return None
    try:
        if pending["kind"]=="rename":
            receipt=rename.confirm(user_id,pending["ticket"],True)
            from github_rename_receipt_v263 import make_rename_widget
            widget=make_rename_widget(receipt)
            # The verified post-commit receipt, not the stale pre-rename
            # file selection, now defines this conversation's source context.
            destination=receipt["destinationPath"]
            context={
                "repo":receipt["repo"],"branch":receipt["branch"],
                "sourceSha":receipt["commitSha"],
                "directory":destination.rsplit("/",1)[0] if "/" in destination else "",
                "lastFile":destination,"kind":"file",
            }
            return _out("Renamed "+_clean_label(receipt["sourcePath"])+" → "+
                        _clean_label(destination)+
                        " in "+_clean_label(receipt["repo"])+". Verified the original Git blob and mode at the new path. "+
                        "[View commit]("+receipt["commitUrl"]+").",widget,github_context=context)
        receipt=create.confirm(user_id,pending["ticket"],True)
        return _out("Created "+_clean_label(receipt["path"])+" in "+
                    _clean_label(receipt["repo"])+". Verified the exact file bytes. "+
                    "[View commit](https://github.com/"+receipt["repo"]+"/commit/"+receipt["commitSha"]+").",
                    receipt.get("widget"))
    except CreateFileError as exc:
        return _out(_user_friendly_failure(exc))


def _prepare_rename(user_id,thread_id,prompt,context=None,history=None):
    pair=_rename_paths(prompt,context,history)
    if not pair:
        return _out("Which existing file should I rename, and what should its new name or path be?")
    src,dst,contextual=pair
    try:
        src=safe_path(src)
        if dst: dst=safe_path(dst)
        auth,entries,_=_read_tree(user_id)
    except CreateFileError as exc:
        return _out(_user_friendly_failure(exc))
    if contextual:
        if (str(context.get("repo") or "").casefold()!=auth["repo"].casefold()
                or context.get("branch")!=auth["branch"]):
            return _out("The selected GitHub repository or branch changed. Specify the file again; nothing changed.")
        directory=str(context.get("directory") or "").strip("/")
        intended=(src if "/" in src else directory+"/"+src) if directory else src
        candidates=[p for p,item in entries.items()
                    if item.get("type")=="blob" and
                    (p.casefold()==intended.casefold() if directory
                     else p.rsplit("/",1)[-1].casefold()==src.casefold())]
        if len(candidates)!=1:
            options=(", ".join(_clean_label(p) for p in candidates[:3])
                     if candidates else "No exact filename match")
            return _out("I can't identify one verified file from that reference. "+
                        options+". Give its full path; nothing changed.")
        # Present actual case-sensitive GitHub path before the user approves.
        src=candidates[0]
    if src not in entries:
        # An explicitly requested path never silently resolves to a fuzzy match.
        similar=_closest(entries,src)
        note=(" Closest files I found: "+", ".join(_clean_label(x) for x in similar)+"."
              if similar else " I didn't find any close matches.")
        return _out("Checked "+_clean_label(auth["repo"])+" ("+_clean_label(auth["branch"])+
                    "). No file named "+_clean_label(src)+"."+note+" Nothing changed.")
    if entries[src].get("type")!="blob":
        return _out(_clean_label(src)+" is not a regular file. I didn't change it.")
    if not dst:
        # A question without a destination must not fall through to code generation.
        _remember(user_id,thread_id,{"kind":"need-destination",
                                     "context":{"repo":auth["repo"],"branch":auth["branch"],
                                                "sourceSha":context.get("sourceSha") if contextual else "",
                                                "lastFile":src,"directory":src.rsplit("/",1)[0] if "/" in src else "",
                                                "kind":"file"}})
        return _out("I found "+_clean_label(src)+". What new filename should it have? Nothing changed.")
    if "/" in src and "/" not in dst:
        dst=src.rsplit("/",1)[0]+"/"+dst
    try:
        dst=safe_path(dst)
        if src==dst: return _out("That's already the file's current path. Nothing changed.")
        if dst in entries:
            return _out("Checked the repo: "+_clean_label(dst)+" already exists. I won't overwrite it.")
        # The transactional prepare also checks source, destination, current
        # permissions, mode, branch, and HEAD independently from our preflight.
        proposal=rename.prepare(user_id,src,dst)
    except CreateFileError as exc:
        return _out(_user_friendly_failure(exc))
    _remember(user_id,thread_id,{"kind":"rename","ticket":proposal["approvalToken"]})
    return _out("Found "+_clean_label(src)+" in "+_clean_label(proposal["repo"])+
                " ("+_clean_label(proposal["branch"])+"). Ready to rename it to "+
                _clean_label(dst)+" without changing its contents. "+
                "**Yes** to confirm or **no** to cancel (expires in 5 minutes). Nothing changed yet.")


def _prepare_create(user_id,thread_id,path,content):
    try:
        path=safe_path(path)
        if content is None:
            _remember(user_id,thread_id,{"kind":"need-content","path":path})
            return _out("What should go in "+_clean_label(path)+"? Paste the exact text here. I won't create anything until you confirm.")
        encoded=base64.b64encode(content.encode("utf-8")).decode("ascii")
        proposal=create.prepare(user_id,path,encoded,"text/plain; charset=utf-8")
    except CreateFileError as exc:
        return _out(_user_friendly_failure(exc))
    _remember(user_id,thread_id,{"kind":"create","ticket":proposal["approvalToken"]})
    return _out("Ready to create "+_clean_label(path)+" in "+_clean_label(proposal["repo"])+
                " ("+_clean_label(proposal["branch"])+"), "+
                str(proposal["bytes"])+" bytes (SHA-256: "+proposal["sha256"][:16]+"…). "+
                "**Yes** to confirm or **no** to cancel (expires in 5 minutes). Nothing changed yet.")


def handle(user_id,thread_id,prompt,context=None,history=None):
    """Return a user-facing, evidence-bound message and optional verified widget."""
    if not isinstance(prompt,str):
        return _out("I couldn't read the file request. Nothing changed.")
    if has_pending(user_id,thread_id):
        decision=_confirmation(user_id,thread_id,prompt)
        if decision is not None:return decision
        # Any other reply leaves prior ticket unapproved and consumed; it can
        # never turn a later casual "yes" into an unintended write.
    if _RENAME.search(prompt):
        return _prepare_rename(user_id,thread_id,prompt,context,history)
    if _CREATE.search(prompt):
        path,content=_create_parts(prompt)
        if not path:return _out("What filename or repository path should I use?")
        return _prepare_create(user_id,thread_id,path,content)
    return _out("I couldn't identify a specific file action. Nothing changed.")
