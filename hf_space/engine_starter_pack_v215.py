"""§E v215: atomic, owner-approved native starter-pack drafts.

This tool DOES NOT register a project card or create gameplay code. A pack is
two files: an editor-native scene and an auditable recipe/descriptor. Both are
one Git commit on an existing review branch, or neither branch file is changed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from urllib.parse import quote

import requests
from fastapi import HTTPException
import forge_project_tools_v213 as engine
import github_workflows_v212 as approvals

_COMMAND = re.compile(r"^@github\s+engine\s+pack(?:\s|$)", re.I)
_DRAFT = re.compile(r"^engine pack ([a-z][a-z0-9-]{2,48}) as ([a-z][a-z0-9-]{2,48}) on (\S+)$", re.I)
_VERIFY = re.compile(r"^engine pack verify ([a-z][a-z0-9-]{2,48}) on (\S+)$", re.I)
_SHA = re.compile(r"^[a-f0-9]{40}$")
_PACK_DIR = engine.ROOT + "/starter-packs"
_SCHEMA = "swyrl-engine-starter-pack-v1"
_MAX_SCENE = 700000
_MAX_ACTORS = 1200
_MAX_LAYERS = 64


def is_command(prompt):
    return bool(_COMMAND.match(str(prompt or "").strip()))


def _pack_path(slug):
    engine._scene_path(slug)  # apply canonical slug rules
    return _PACK_DIR + "/" + slug + ".starter.json"


def _validate_scene(data, slug=None):
    if not isinstance(data, dict) or not all(isinstance(data.get(x), dict) for x in ("project", "editor", "scene")):
        raise HTTPException(409, "Not a native editor project/scene/editor document")
    layers = data["editor"].get("layers")
    actors = data["scene"].get("actors")
    if not isinstance(layers, list) or not 1 <= len(layers) <= _MAX_LAYERS:
        raise HTTPException(409, "Starter must contain bounded editor layers")
    if not isinstance(actors, list) or not 1 <= len(actors) <= _MAX_ACTORS:
        raise HTTPException(409, "Starter must contain bounded scene actors")
    layer_ids = [str(x.get("id") or "") for x in layers if isinstance(x, dict)]
    if len(layer_ids) != len(layers) or any(not x or len(x) > 100 for x in layer_ids) or len(set(layer_ids)) != len(layer_ids):
        raise HTTPException(409, "Duplicate or invalid editor layer IDs")
    ids = []
    for a in actors:
        if not isinstance(a, dict) or not isinstance(a.get("id"), str) or not a["id"] or len(a["id"]) > 100:
            raise HTTPException(409, "Invalid scene actor identifier")
        assigned = a.get("editorLayerIds", [])
        if not isinstance(assigned, list) or any(x not in layer_ids for x in assigned):
            raise HTTPException(409, "Actor refers to a nonexistent editor layer")
        ids.append(a["id"])
    if len(ids) != len(set(ids)):
        raise HTTPException(409, "Duplicate scene actor identifiers")
    if slug and data["project"].get("canonicalId") != slug:
        raise HTTPException(409, "Starter's canonicalId does not match requested pack")
    return {"actors": len(actors), "layers": len(layers), "kind": str(data["project"].get("kind") or "unknown")[:80]}


def _contents(gh, rec, repo, path, ref):
    result = gh._read_optional(rec["token"], repo, path, ref, max_bytes=750000)
    if not result or not _SHA.fullmatch(str(result.get("sha") or "")):
        raise HTTPException(409, "Required GitHub source file was not verified: " + path)
    return result


def _build_pack(seed, dest, seed_scene, manifest, seed_blob, manifest_blob, base_commit):
    scene = copy.deepcopy(seed_scene)
    scene["project"]["name"] = dest.replace("-", " ").title()
    scene["project"]["canonicalId"] = dest
    scene["project"]["template"] = seed
    scene["project"]["derivedFrom"] = seed
    details = _validate_scene(scene, dest)
    source_bytes = (json.dumps(scene, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(source_bytes) > _MAX_SCENE:
        raise HTTPException(422, "Derived native scene exceeds the starter pack budget")
    scene_path = engine._scene_path(dest)
    pack_path = _pack_path(dest)
    description = {
        "schema": _SCHEMA, "id": dest, "name": scene["project"]["name"],
        "status": "draft-unregistered", "type": "existing-mode-map-variant",
        "source": {"seed": seed, "seedBlob": seed_blob, "engineMainSha": base_commit,
                   "manifestBlob": manifest_blob, "engineVersion": manifest.get("name"),
                   "orderedPatchCount": len(manifest.get("patches", []))},
        "scene": {"path": scene_path, "sha256": hashlib.sha256(source_bytes).hexdigest(),
                  "bytes": len(source_bytes), "actorCount": details["actors"],
                  "layerCount": details["layers"], "projectKind": details["kind"]},
        "requires": ["Projects registration", "explicit bundling in build_space.py",
                     "native Play/Stop/Save/Load/Undo/Redo regression",
                     "desktop and mobile engine tests", "governed engine patch/build/reseal",
                     "draft PR approval and independent §E deployment"],
        "note": "No new game rules, prefab behaviors, editor registration, or engine release is supplied by this draft."
    }
    desc_bytes = (json.dumps(description, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(desc_bytes) > 10000:
        raise HTTPException(422, "Starter descriptor exceeds the bounded budget")
    return [(scene_path, source_bytes.decode("utf-8")), (pack_path, desc_bytes.decode("utf-8"))], description


def _source(gh, rec, repo, seed):
    if seed not in engine._SOURCE_STARTERS:
        raise HTTPException(422, "Choose an existing supported source: sheep-tag-meadow, starforge-observatory, embervault-atelier")
    source, scene = engine._scene(gh, rec, repo, seed)
    _validate_scene(scene)
    manifest_item, manifest = engine._manifest(gh, rec, repo)
    if len(manifest["patches"]) < 50 or not _SHA.fullmatch(manifest_item["sha"]):
        raise HTTPException(409, "Existing engine version/ordered patches were not verified")
    return source, scene, manifest_item, manifest


def _propose(gh, cfg, rec, user, repo, seed, dest, branch):
    if seed == dest:
        raise HTTPException(422, "Derived pack must have a distinct ID")
    engine._access(gh, rec, repo, "branch-write")
    branch, head = engine._branch_head(gh, rec, repo, branch)
    main = approvals._branch_sha(gh, rec["token"], repo, "main")
    source, scene, manifest_item, manifest = _source(gh, rec, repo, seed)
    files, desc = _build_pack(seed, dest, scene, manifest, source["sha"], manifest_item["sha"], main)
    if any(engine._exists(gh, rec, repo, path, branch) for path, _ in files):
        return "Scene or pack descriptor already exists on review branch. No overwrite or proposal."
    payload = {"kind": "engine-atomic-pack", "seed": seed, "dest": dest, "branch": branch,
               "headSha": head, "mainSha": main, "sourceBlob": source["sha"],
               "manifestBlob": manifest_item["sha"],
               "sceneSha256": desc["scene"]["sha256"]}
    code = approvals._store(gh, cfg, user, repo, payload)
    return (
        "## §E atomic starter-pack proposal — NOTHING WRITTEN\n"
        "Seed: " + seed + " · existing gameplay mode: " + desc["scene"]["projectKind"] + "\n"
        "Draft ID: " + dest + " · actors: " + str(desc["scene"]["actorCount"]) +
        " · layers: " + str(desc["scene"]["layerCount"]) + "\n"
        "Review branch: " + branch + " @" + head[:12] + " · main @" + main[:12] + "\n"
        "The ONE atomic Git commit will create exactly these TWO files:\n" +
        "\n".join("- " + path for path, _ in files) +
        "\nBoth copies preserve the seed's existing actor arrangement and gameplay type. "
        "The descriptor records source hashes and required future engine work; it is NOT an installed "
        "Projects card, independent mode or live game. No build/merge/deploy authorized.\n"
        "To approve this exact source snapshot once, send @GitHub confirm " + code + " within 10 minutes."
    )


def _git_post(rec, repo, resource, payload):
    token = rec["token"]
    url = "https://api.github.com/repos/" + repo + "/git/" + resource
    try:
        response = requests.post(url, headers={
            "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }, json=payload, timeout=18)
        if response.status_code not in (200, 201):
            raise HTTPException(409 if response.status_code in (409, 422) else 502,
                                "GitHub did not accept the atomic staging operation; no branch update confirmed")
        result = response.json()
        if not isinstance(result, dict) or not _SHA.fullmatch(str(result.get("sha") or "")):
            raise HTTPException(502, "GitHub did not return a verifiable Git object SHA")
        return result
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(502, "GitHub Git object request failed; no branch mutation confirmed") from exc


def _git_ref_update(rec, repo, branch, commit):
    # force=false is mandatory: reject non-fast-forward changes between checks and publish.
    url = "https://api.github.com/repos/" + repo + "/git/refs/heads/" + quote(branch, safe="/")
    try:
        response = requests.patch(url, headers={
            "Authorization": "Bearer " + rec["token"], "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }, json={"sha": commit, "force": False}, timeout=18)
        if response.status_code != 200:
            raise HTTPException(409, "GitHub refused the branch fast-forward; no pack publish confirmed")
        obj = response.json()
        verified = str((obj.get("object") or {}).get("sha") or "")
        if verified != commit:
            raise HTTPException(502, "GitHub returned a branch state different from the requested pack commit")
        return True
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(502, "GitHub branch update response unavailable; inspect branch before retrying") from exc


def _confirm(gh, rec, repo, pending):
    engine._access(gh, rec, repo, "branch-write")
    seed, dest = str(pending.get("seed") or ""), str(pending.get("dest") or "")
    if seed not in engine._SOURCE_STARTERS or seed == dest:
        return "Invalid or unsupported starter seed; no commit attempted."
    branch, head = engine._branch_head(gh, rec, repo, pending.get("branch"))
    if head != pending.get("headSha"):
        return "Review branch changed since approval; no pack commit."
    main = approvals._branch_sha(gh, rec["token"], repo, "main")
    if main != pending.get("mainSha"):
        return "Engine main changed since approval; rebuild proposal from current source."
    source, scene, manifest_item, manifest = _source(gh, rec, repo, seed)
    if source["sha"] != pending.get("sourceBlob") or manifest_item["sha"] != pending.get("manifestBlob"):
        return "Starter/manifest changed since approval; no pack commit."
    files, descriptor = _build_pack(seed, dest, scene, manifest, source["sha"], manifest_item["sha"], main)
    if descriptor["scene"]["sha256"] != pending.get("sceneSha256"):
        return "Pack digest differs from approved proposal; no commit attempted."
    if any(engine._exists(gh, rec, repo, path, branch) for path, _ in files):
        return "Destination file already exists; no overwrite attempted."
    commit_info = engine._github(gh, rec, repo, "/git/commits/" + head)
    tree = str((commit_info.get("tree") or {}).get("sha") or "")
    if not _SHA.fullmatch(tree):
        return "Review branch tree not verified; no commit."
    # Two Git tree entries plus one commit plus one non-forced ref update.
    staged = _git_post(rec, repo, "trees", {
        "base_tree": tree,
        "tree": [{"path": path, "mode": "100644", "type": "blob", "content": body} for path, body in files]
    })
    commit = _git_post(rec, repo, "commits", {
        "message": "starter-pack: stage " + dest + " from " + seed + " as unregistered draft",
        "tree": staged["sha"], "parents": [head]
    })
    _git_ref_update(rec, repo, branch, commit["sha"])
    return ("GitHub confirmed one atomic two-file §E starter-pack draft commit: " + commit["sha"] +
            "\nScene and descriptor: " + ", ".join(path for path, _ in files) +
            "\nVerify with @GitHub engine pack verify " + dest + " on " + branch +
            ". NOT registered, merged, compiled, deployed, or verified in live editor Play.")


def _verify(gh, rec, repo, dest, branch):
    engine._access(gh, rec, repo, "read")
    branch, head = engine._branch_head(gh, rec, repo, branch)
    p = _contents(gh, rec, repo, _pack_path(dest), branch)
    s = _contents(gh, rec, repo, engine._scene_path(dest), branch)
    try:
        desc = json.loads(p["body"])
        scene = json.loads(s["body"])
    except ValueError as exc:
        raise HTTPException(409, "Saved starter pack contains invalid JSON") from exc
    if not isinstance(desc, dict) or desc.get("schema") != _SCHEMA or desc.get("id") != dest:
        raise HTTPException(409, "Starter pack metadata does not meet v1 schema")
    details = _validate_scene(scene, dest)
    actual = hashlib.sha256(s["body"].encode("utf-8")).hexdigest()
    recorded = desc.get("scene") if isinstance(desc.get("scene"), dict) else {}
    if (actual != recorded.get("sha256") or recorded.get("path") != engine._scene_path(dest)
            or len(s["body"].encode("utf-8")) != recorded.get("bytes")
            or details["actors"] != recorded.get("actorCount")
            or details["layers"] != recorded.get("layerCount")
            or details["kind"] != recorded.get("projectKind")
            or desc.get("status") != "draft-unregistered"):
        raise HTTPException(409, "Starter descriptor and native scene do not agree; no valid pack verdict")
    main = approvals._branch_sha(gh, rec["token"], repo, "main")
    return (
        "## §E starter pack verified (data only)\n"
        "Pack: " + dest + " on " + branch + " @" + head[:12] + "\n"
        "Native scene blob: " + s["sha"][:12] + " · descriptor blob: " + p["sha"][:12] +
        "\nSHA-256: " + actual + "\n"
        "Actors: " + str(details["actors"]) + " · layers: " + str(details["layers"]) +
        " · existing mode: " + details["kind"] + "\n"
        "Engine main ref currently @" + main[:12] +
        " (pack was authored using @" + str((desc.get("source") or {}).get("engineMainSha") or "")[:12] + ").\n"
        "Schema/identity/digest checks PASS. This does NOT verify editor registration, "
        "gameplay runtime, packed HTML or hosted game. NEXT: implement Projects registration, "
        "mode-specific runtime if needed, scene asset bundling, engine patch/manifest reseal, "
        "native editor & desktop/mobile tests, PR and dedicated §E release."
    )


def confirm(gh, cfg, rec, user, repo, proposal):
    if proposal.get("kind") != "engine-atomic-pack":
        return "Unsupported starter-pack approval; nothing written."
    engine._repo(gh, rec)
    return _confirm(gh, rec, repo, proposal)


def execute(gh, user, prompt):
    if not str(user).startswith("google:"):
        return "Sign in with your verified Google account to work on §E packs."
    cfg = gh._config()
    rec = gh._load(cfg, user)
    if rec is None:
        return "GitHub is not linked to this Google account; explicit connection is needed."
    repo = engine._repo(gh, rec)
    cmd = re.sub(r"^@github\s+", "", str(prompt).strip(), flags=re.I)
    if cmd == "engine pack help":
        return (
            "## §E atomic starter-pack workbench\n"
            "@GitHub engine pack sheep-tag-meadow as my-meadow on feature/my-meadow — review TWO source files "
            "(editor-native scene + starter descriptor) in one proposed commit; second @GitHub confirm CODE required.\n"
            "@GitHub engine pack verify my-meadow on feature/my-meadow — check actual GitHub scene/descriptor identity, "
            "actors, layers and SHA-256 consistency.\n"
            "This makes a reliable, unregistered existing-mode pack seed; it does not generate a new game mode, "
            "rebuild §E, activate Projects, run tests or deploy. Continue with @GitHub engine review feature/my-meadow."
        )
    verify = _VERIFY.fullmatch(cmd)
    if verify:
        return _verify(gh, rec, repo, *verify.groups())
    draft = _DRAFT.fullmatch(cmd)
    if draft:
        return _propose(gh, cfg, rec, user, repo, *draft.groups())
    return "Use @GitHub engine pack help for supported starter-pack draft and verify commands."


def events(gh, data):
    prompt = str(data.get("prompt") or "")
    op = "branch-write" if _DRAFT.fullmatch(re.sub(r"^@github\s+", "", prompt, flags=re.I)) else "read"
    yield {"type": "STATUS", "phase": "GITHUB_ENGINE_PACK_SOURCE_CHECK",
           "reason": "Verifying real §E engine main, native scene and review branch for " + op + ".",
           "categories": ["GITHUB", "ENGINE", "STARTER", "PERMISSION"]}
    try:
        result = execute(gh, str(data.get("userId") or ""), prompt)
    except HTTPException as exc:
        result = "Starter-pack request not verified (" + str(exc.status_code) + "): " + str(exc.detail) + ". No pack change confirmed."
    except Exception:
        result = "Starter-pack operation failed without a confirmed branch update. Inspect GitHub before retrying."
    yield {"type": "STATUS", "phase": "GITHUB_ENGINE_PACK_RESULT",
           "reason": "Pack proposal or source verification finished; any write still requires user approval.",
           "categories": ["GITHUB", "ENGINE", "STARTER", "TOOL"]}
    yield {"type": "DELTA", "text": result}
    yield {"type": "COMPLETED", "phase": "COMPLETE"}
