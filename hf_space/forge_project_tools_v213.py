"""v213 project-aware §E development tools for the existing GitHub OAuth owner.

The actual engine source lives on this repo's main branch, NOT in the separate
§wyrlz Chat/LALM release source tree. No engine deployment or arbitrary code
execution is authorized by an inspection or scene-scaffold request.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from urllib.parse import quote

import github_workflows_v212 as workflow
from fastapi import HTTPException

ENGINE_REPO = "kaministrator999-ui/Swrlzkamico"
ROOT = "projects/swrlz-forge-moba"
SOURCE = ROOT + "/source-manifest.json"
SCENES = ROOT + "/scenes"
BUILD = ROOT + "/build_space.py"
DEPLOY = ROOT + "/DEPLOY_REQUEST.json"
START = "§tart_§E.md"
_SCENE = re.compile(r"^[a-z][a-z0-9-]{2,48}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_PLAN = re.compile(r"^engine plan (.{4,260})$", re.I | re.S)
_CLONE = re.compile(r"^engine clone ([a-z][a-z0-9-]{2,48}) as ([a-z][a-z0-9-]{2,48}) on (\S+)$", re.I)
_REVIEW = re.compile(r"^engine review (\S+)$", re.I)
_COMMAND = re.compile(r"^@github\s+engine\s+(?:help|status|starters|plan|clone|review)(?:\s|$)", re.I)
_SOURCE_STARTERS = frozenset({"sheep-tag-meadow", "starforge-observatory", "embervault-atelier"})


def is_command(prompt):
    return bool(_COMMAND.match(str(prompt or "").strip()))


def is_conversation(prompt):
    q = str(prompt or "").strip()
    return bool(
        re.match(r"^(?:please\s+)?(?:(?:can|could|would)\s+you\s+)?(?:check|show|review|inspect|map|explain|plan)\b", q, re.I)
        and re.search(r"(?:§e\b|§wyrl§\s+engine|our\s+(?:game\s+engine|editor)|starter\s+packs?)", q, re.I)
    )


def _repo(gh, rec):
    value = gh._repo_name(rec.get("repo"))
    if value.casefold() != ENGINE_REPO.casefold():
        raise HTTPException(409, "Select " + ENGINE_REPO + " in GitHub settings to work on §E. No repository changed.")
    return value


def _access(gh, rec, repo, op="read"):
    check = gh._effective_access(rec, repo, op)
    if not check["allowed"]:
        raise HTTPException(409, gh._permission_message(check))
    if check["defaultBranch"] != "main":
        raise HTTPException(409, "§E project main branch is not verified; no work attempted.")
    return check


def _github(gh, rec, repo, suffix):
    return gh._api(rec["token"], "/repos/" + repo + suffix)


def _file(gh, rec, repo, path, ref="main", max_bytes=500000):
    item = gh._text(rec["token"], repo, path, ref, max_bytes=max_bytes)
    if not item or not _GIT_SHA.fullmatch(str(item.get("sha") or "")):
        raise HTTPException(409, "Required §E source file is unreadable or unverified: " + path)
    return item


def _manifest(gh, rec, repo):
    item = _file(gh, rec, repo, SOURCE, max_bytes=18000)
    try:
        data = json.loads(item["body"])
    except ValueError as exc:
        raise HTTPException(409, "Engine source-manifest is invalid JSON") from exc
    if (not isinstance(data, dict) or data.get("schema") != "swrlz-forge-source-v2"
            or not isinstance(data.get("patches"), list)
            or not data["patches"] or not all(isinstance(x, str) and x.startswith("patches/") for x in data["patches"])):
        raise HTTPException(409, "Engine source manifest contract is unverified")
    return item, data


def _scene_path(slug):
    if not _SCENE.fullmatch(str(slug or "")):
        raise HTTPException(422, "Starter ID must be a short lowercase dash-separated slug")
    return SCENES + "/" + slug + ".swyrl.json"


def _scene(gh, rec, repo, slug, ref="main"):
    item = _file(gh, rec, repo, _scene_path(slug), ref, max_bytes=500000)
    try:
        data = json.loads(item["body"])
    except ValueError as exc:
        raise HTTPException(409, "Source starter scene JSON is invalid") from exc
    if not isinstance(data, dict) or not all(isinstance(data.get(k), dict) for k in ("project", "scene", "editor")):
        raise HTTPException(409, "Scene does not match editor-native project/scene/editor envelope")
    if (data["project"].get("canonicalId") or data["project"].get("template")) != slug:
        raise HTTPException(409, "Starter identity mismatches requested source")
    if not isinstance(data["editor"].get("layers"), list):
        raise HTTPException(409, "Editor layers are not a valid list")
    return item, data


def _inventory(gh, rec, repo):
    data = _github(gh, rec, repo, "/contents/" + SCENES + "?ref=main")
    if not isinstance(data, list):
        raise HTTPException(409, "Engine scene inventory not verified")
    found = {}
    for entry in data[:80]:
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path") or "")
        m = re.fullmatch(re.escape(SCENES) + r"/([a-z][a-z0-9-]{2,48})\.swyrl\.json", path)
        if m and entry.get("type") == "file":
            found[m.group(1)] = int(entry.get("size") or 0)
    return found


def _branch_head(gh, rec, repo, name):
    branch = workflow._safe_ref(name, authoring=True)
    sha = workflow._branch_sha(gh, rec["token"], repo, branch)
    return branch, sha


def _exists(gh, rec, repo, path, branch):
    return workflow._already_exists(gh, rec["token"], repo, path, branch)


def _version_label(info):
    return str(info.get("name") or "unknown")[:110]


def _status(gh, rec, repo):
    manifest_item, manifest = _manifest(gh, rec, repo)
    scenes = _inventory(gh, rec, repo)
    deploy = _file(gh, rec, repo, DEPLOY, "main", 18000)
    try:
        deployment = json.loads(deploy["body"])
    except ValueError:
        deployment = {}
    return (
        "## §wyrl§ Engine — verified GitHub source map\n"
        "Repository: " + repo + " · source branch: main\n"
        "Engine directory: " + ROOT + "\n"
        "Source manifest: " + _version_label(manifest) +
        " · " + str(len(manifest["patches"])) + " ordered patches · blob " + manifest_item["sha"][:12] + "\n"
        "Latest patch: " + manifest["patches"][-1] + "\n"
        "Native scene files: " + str(len(scenes)) + "\n"
        "Build: " + BUILD + " (sealed checksum and ordered patch sequence)\n"
        "Release owner: " + DEPLOY + " → dedicated engine workflow → dedicated §E Hugging Face Space\n"
        "Current deployment request source: " + str(deployment.get("sourceCommit") or "unverified")[:40] + "\n"
        "A deployment request is NOT proof of a successful live host. Use dedicated workflow/host receipts.\n"
        "Engine source and Chat/LALM have separate deployment paths. §wyrlz cannot silently deploy or merge."
    )


def _starters(gh, rec, repo):
    found = _inventory(gh, rec, repo)
    lines = ["## §E editor-native saved scenes (GitHub main)"]
    for slug, size in sorted(found.items()):
        category = ("RTS Sheep Tag prototype" if slug == "sheep-tag-meadow" else
                    "Spatial workspace" if slug == "starforge-observatory" else
                    "Anime production scene" if slug.startswith("ghosts-in-") else "Saved scene")
        lines.append("- " + slug + " · " + category + " · " + str(size) + " bytes")
    lines.extend((
        "\nScene presence in GitHub does NOT mean it appears as a Projects starter card or is bundled.",
        "A new game mode needs an engine patch, its registration and editor/play tests—not just a copied JSON scene.",
        "Safe first drafting command: @GitHub engine clone sheep-tag-meadow as my-meadow on feature/my-meadow",
    ))
    return "\n".join(lines)


def _plan(gh, rec, repo, goal):
    goal = str(goal or "").strip()
    if not 4 <= len(goal) <= 260:
        raise HTTPException(422, "Describe an engine/editor/starter project goal in 4–260 characters")
    manifest_item, manifest = _manifest(gh, rec, repo)
    scenes = _inventory(gh, rec, repo)
    lower = goal.casefold()
    if any(x in lower for x in ("engine core", "update engine", "engine update", "runtime", "render", "physics", "tooling")):
        lane, files = "engine core / renderer", ["source-manifest.json", "patches/", "runtime/", "build_space.py"]
        work = "Write a new deterministic, ordered engine patch with a verified once-only anchor; update the sealed manifest only after generated build/tests pass."
    elif any(x in lower for x in ("editor", "viewport", "inspector", "layer", "undo", "redo", "save", "load")):
        lane, files = "editor behavior", ["patches/v7_4_editor_workspaces.py", "patches/v8_3_editor_authoring.py", "runtime/", "tests/"]
        work = "Reuse editor transactions, native scene envelope, Save/Load and Undo/Redo. Modify editor/runtime through governed patch, not by editing packed HTML directly."
    else:
        lane, files = "starter pack / playable mode", ["scenes/", "patches/v10_0_sheep_tag.py", "runtime/sheep_tag_game.js", "build_space.py", "tests/"]
        work = "Clone/import a compatible saved scene as a DRAFT, then implement mode-specific rules, actors, editor registration and Play/Pause/Stop before calling it a playable starter."
    present = "; ".join(p for p in files)
    base = "sheep-tag-meadow" if "sheep-tag-meadow" in scenes else (next(iter(scenes), "none"))
    return (
        "## §E development mission · verified context, not completed code\n"
        "Goal: " + goal + "\n"
        "Lane: " + lane + "\n"
        "Authoritative GitHub: " + repo + "/main:" + ROOT + "\n"
        "Sealed manifest: " + _version_label(manifest) + " · " + str(len(manifest["patches"])) +
        " patches · blob " + manifest_item["sha"][:12] + "\n"
        "Related source paths under engine root: " + present + "\n"
        "Available scene seed: " + base + "\n"
        "1. Read §tart_§E.md and current editor, mode, manifest and build contracts from GitHub main.\n"
        "2. Make a scoped feature branch; read exact source files and define measurable editor/gameplay acceptance.\n"
        "3. " + work + "\n"
        "4. Run the engine-specific build/checksum, JavaScript syntax, native editor Save/Load/Undo/Redo, and relevant desktop/mobile Playwright suites.\n"
        "5. Open a review PR; prove CI and no regression to existing starters/engine core before merge.\n"
        "6. Only after approval follow the separate §E DEPLOY_REQUEST/hosted audit route; never the Chat/LALM deployment gate.\n"
        "Every stage needs real tool/source/CI receipts. A plan or a draft scene is not a built game."
    )


def _draft(gh, c, rec, user, repo, source, slug, branch):
    source, dest = _scene_path(source), _scene_path(slug)
    if source == dest or source not in {_scene_path(x) for x in _SOURCE_STARTERS}:
        return "Select a supported distinct seed (sheep-tag-meadow, starforge-observatory, embervault-atelier). No write proposed."
    access = _access(gh, rec, repo, "branch-write")
    branch, branch_sha = _branch_head(gh, rec, repo, branch)
    source_slug = source.split("/")[-1][:-len(".swyrl.json")]
    original, data = _scene(gh, rec, repo, source_slug)
    if _exists(gh, rec, repo, dest, branch):
        return "A scene with that ID exists on the selected branch; no overwrite or proposal."
    main_sha = workflow._branch_sha(gh, rec["token"], repo, access["defaultBranch"])
    code = workflow._store(gh, c, user, repo, {
        "kind": "engine-scene-draft", "source": source_slug, "slug": slug,
        "branch": branch, "branchSha": branch_sha, "mainSha": main_sha, "sourceBlob": original["sha"]
    })
    return (
        "**§E native scene draft proposal — NOTHING WRITTEN YET**\n"
        "Source: " + source + "\nNew scene: " + dest + "\n"
        "Branch: " + branch + " @" + branch_sha[:12] + "\n"
        "Source snapshot: " + original["sha"][:12] + "\n"
        "Existing actors/layers and mode semantics remain identical; this is a renamed scene copy, "
        "not a newly implemented MOBA/anime game mode.\n"
        "NOT registered in Projects or the engine's sealed asset list. Import/review in editor; "
        "a separate patch, tests, manifest build and dedicated deployment are needed.\n"
        "To create the draft within 10 minutes, explicitly send @GitHub confirm " + code
    )


def _confirm_draft(gh, rec, repo, proposal):
    access = _access(gh, rec, repo, "branch-write")
    source_slug = str(proposal.get("source") or "")
    slug = str(proposal.get("slug") or "")
    if source_slug not in _SOURCE_STARTERS or source_slug == slug:
        return "Unrecognized engine starter derivation; no write."
    destination = _scene_path(slug)
    branch, sha = _branch_head(gh, rec, repo, proposal.get("branch"))
    if sha != proposal.get("branchSha"):
        return "Review branch moved; no scene written. Request a new proposal."
    main_sha = workflow._branch_sha(gh, rec["token"], repo, access["defaultBranch"])
    if main_sha != proposal.get("mainSha"):
        return "Engine main changed; no scene written. Reinspect the current engine source."
    original, scene = _scene(gh, rec, repo, source_slug)
    if original["sha"] != proposal.get("sourceBlob"):
        return "Source starter changed; no file written."
    if _exists(gh, rec, repo, destination, branch):
        return "Destination scene already exists; no overwrite."
    result = copy.deepcopy(scene)
    result["project"]["name"] = slug.replace("-", " ").title()
    result["project"]["canonicalId"] = slug
    result["project"]["template"] = source_slug  # preserve known original engine play rules
    result["project"]["derivedFrom"] = source_slug
    data = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(data) > 700000:
        return "Derived scene exceeds bounded file-write budget. Nothing changed."
    receipt = workflow._write_request(rec["token"], "PUT",
                gh.GITHUB_API + "/repos/" + repo + "/contents/" + destination,
                {"message": "scene: draft " + slug + " from " + source_slug,
                 "content": __import__("base64").b64encode(data).decode("ascii"),
                 "branch": branch})
    path = (receipt.get("content") or {}).get("path")
    commit = str((receipt.get("commit") or {}).get("sha") or "")
    if path != destination or not _GIT_SHA.fullmatch(commit):
        return "GitHub file-write receipt unverified; inspect branch before retrying."
    return (
        "GitHub confirmed a new editor-native DRAFT scene: https://github.com/" + repo +
        "/blob/" + branch + "/" + destination + "\nCommit " + commit[:12] +
        ". Source scene is preserved; NOT merged or deployed. "
        "This is a starting scene copy; gameplay divergence/Projects-card registration and CI remain to be authored."
    )


def _review(gh, c, rec, user, repo, branch):
    access = _access(gh, rec, repo, "branch-write")
    branch, head = _branch_head(gh, rec, repo, branch)
    compare = _github(gh, rec, repo, "/compare/main..." + quote(branch, safe="/"))
    files = compare.get("files") if isinstance(compare, dict) else None
    if not isinstance(files, list) or not 1 <= len(files) <= 75:
        return "No bounded verified engine diff available; no PR proposal."
    allowed = all(
        isinstance(f, dict) and str(f.get("filename") or "").startswith(ROOT + "/")
        and not str(f.get("filename") or "").endswith("/DEPLOY_REQUEST.json")
        and str(f.get("status") or "") in ("added", "modified")
        for f in files
    )
    if not allowed:
        return "The branch includes non-engine, deleted or engine deployment-request changes. Split/review these separately; no PR proposed."
    code = workflow._store(gh, c, user, repo, {
        "kind":"engine-review-pr", "branch":branch, "branchSha":head,
        "mainSha":workflow._branch_sha(gh, rec["token"], repo, access["defaultBranch"]),
        "files":[str(f["filename"]) for f in files]
    })
    return (
        "**§E engine review draft PR — NOT CREATED YET**\n" +
        str(len(files)) + " scoped engine source files changed on " + branch + ":\n" +
        "\n".join("- " + str(f["filename"]) for f in files[:40]) +
        "\nNo merge, workflow dispatch, sealed build or deployment authorized. "
        "Check engine-specific CI first and explicitly send @GitHub confirm " + code
    )


def _confirm_review(gh, rec, repo, pending):
    _access(gh, rec, repo, "branch-write")
    branch, sha = _branch_head(gh, rec, repo, pending.get("branch"))
    if sha != pending.get("branchSha") or workflow._branch_sha(gh, rec["token"], repo, "main") != pending.get("mainSha"):
        return "Engine branch or main changed since review. No PR created."
    compare = _github(gh, rec, repo, "/compare/main..." + quote(branch, safe="/"))
    files = compare.get("files") if isinstance(compare, dict) else None
    if not isinstance(files, list) or [f.get("filename") for f in files] != pending.get("files"):
        return "Engine PR diff changed; no PR created."
    if not all(str(f.get("filename") or "").startswith(ROOT + "/")
               and not str(f.get("filename") or "").endswith("/DEPLOY_REQUEST.json")
               and f.get("status") in ("added", "modified") for f in files):
        return "Engine review includes unsupported changes; no PR created."
    receipt = workflow._write_request(rec["token"], "POST",
        gh.GITHUB_API + "/repos/" + repo + "/pulls", {
            "title": "Review §E engine/editor starter work on " + branch,
            "head": branch, "base": "main", "draft": True,
            "body": "Draft §E engine change. Review scoped source, required governed patch/manifest checks, native editor and desktop/phone tests before any merge. Never use Chat/LALM deployment for §E."
        })
    uri = str(receipt.get("html_url") or "")
    if not uri.startswith("https://github.com/" + repo + "/pull/"):
        return "GitHub did not return a validated draft PR URL; inspect repo before retrying."
    return "GitHub confirmed DRAFT §E review PR " + uri + ". NOT merged, tested or deployed."


def confirm(gh, c, rec, user, repo, pending):
    _repo(gh, rec)
    kind = pending.get("kind")
    if kind == "engine-scene-draft":
        return _confirm_draft(gh, rec, repo, pending)
    if kind == "engine-review-pr":
        return _confirm_review(gh, rec, repo, pending)
    return "Unsupported §E proposal; nothing written."


def execute(gh, user, prompt):
    if not str(user).startswith("google:"):
        return "Sign in with a verified Google account to access the connected engine repository."
    c = gh._config()
    rec = gh._load(c, user)
    if rec is None:
        return "GitHub is not connected. Approve access in Chat Settings; §wyrlz cannot grant itself permissions."
    repo = _repo(gh, rec)
    cmd = re.sub(r"^@github\s+", "", str(prompt or "").strip(), flags=re.I).strip()
    if cmd == "engine help":
        return (
            "## §E / §wyrl§ Engine project assistant\n"
            "@GitHub engine status — verify the real main-branch engine manifest and release ownership\n"
            "@GitHub engine starters — list native editor starter scene files\n"
            "@GitHub engine plan build a MOBA starter pack — plan real source, editor, tests and dedicated release\n"
            "@GitHub engine clone sheep-tag-meadow as arena-draft on feature/arena — propose a new draft native scene on an existing feature branch\n"
            "@GitHub engine review feature/arena — propose a draft PR for scoped engine project files\n"
            "Writes require actual GitHub scope/repo role, a second explicit @GitHub confirm CODE and source/ref rechecks. "
            "Draft scene copies are NOT new game engines or playable-mode registrations."
        )
    clone = _CLONE.fullmatch(cmd)
    review = _REVIEW.fullmatch(cmd)
    if clone:
        source, slug, branch = clone.groups()
        return _draft(gh, c, rec, user, repo, source, slug, branch)
    if review:
        return _review(gh, c, rec, user, repo, review.group(1))
    _access(gh, rec, repo)
    if cmd == "engine status":
        return _status(gh, rec, repo)
    if cmd == "engine starters":
        return _starters(gh, rec, repo)
    plan = _PLAN.fullmatch(cmd)
    if plan:
        return _plan(gh, rec, repo, plan.group(1))
    return "Unsupported engine request. Use @GitHub engine help."


def events(gh, data):
    prompt = str(data.get("prompt") or "")
    if not is_command(prompt):
        prompt = "@GitHub engine plan " + prompt[:260]
    write = bool(_CLONE.fullmatch(re.sub(r"^@github\s+", "", prompt, flags=re.I)) or
                 _REVIEW.fullmatch(re.sub(r"^@github\s+", "", prompt, flags=re.I)))
    yield {"type":"STATUS", "phase":"GITHUB_ENGINE_REPO_PREFLIGHT",
           "reason":"Checking selected GitHub owner, §E engine main-branch source and " +
                    ("feature-branch write authority." if write else "read authority."),
           "categories":["GITHUB","ENGINE","PERMISSION"]}
    try:
        result = execute(gh, str(data.get("userId") or ""), prompt)
    except HTTPException as exc:
        result = "§E operation unverified (" + str(exc.status_code) + "): " + str(exc.detail) + ". No change confirmed."
    except Exception:
        result = "§E tool could not verify source or complete operation. No write or successful release claimed."
    yield {"type":"STATUS","phase":"GITHUB_ENGINE_EVIDENCE",
           "reason":"Engine GitHub source evidence checked; results or approval boundary available.",
           "categories":["GITHUB","ENGINE","TOOL"]}
    yield {"type":"DELTA","text":result}
    yield {"type":"COMPLETED","phase":"COMPLETE"}
