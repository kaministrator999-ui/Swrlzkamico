#!/usr/bin/env python3
"""Validate §E editor-native scenes and v215 starter-pack provenance offline.

This is a read-only tool in the dedicated engine lane. Passing validation does
not install a Projects card, make a game mode playable, or release an engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "swyrl-engine-starter-pack-v1"
SLUG = re.compile(r"^[a-z][a-z0-9-]{2,48}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_FILE = 750000
MAX_ACTORS = 1200
MAX_LAYERS = 64


class InvalidPack(ValueError):
    """Fail-closed validation error; no source mutation."""


def _slug(raw):
    if not isinstance(raw, str) or not SLUG.fullmatch(raw):
        raise InvalidPack("Invalid starter ID; expected lowercase dash-separated slug")
    return raw


def _read(path):
    if not path.is_file() or path.is_symlink():
        raise InvalidPack("Required source file does not exist as a normal file: " + path.name)
    size = path.stat().st_size
    if not 1 <= size <= MAX_FILE:
        raise InvalidPack("Source file size is outside permitted range: " + path.name)
    data = path.read_bytes()
    try:
        parsed = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise InvalidPack("Invalid UTF-8 JSON in " + path.name) from exc
    return parsed, data


def scene_report(scene, expected_id):
    _slug(expected_id)
    if not isinstance(scene, dict):
        raise InvalidPack("Scene root must be an object")
    project = scene.get("project")
    editor = scene.get("editor")
    content = scene.get("scene")
    if not all(isinstance(x, dict) for x in (project, editor, content)):
        raise InvalidPack("Native project/editor/scene envelope is missing")
    if (project.get("canonicalId") or project.get("template")) != expected_id:
        raise InvalidPack("Scene canonical identity does not match expected starter ID")
    layers = editor.get("layers")
    actors = content.get("actors")
    if not isinstance(layers, list) or not 1 <= len(layers) <= MAX_LAYERS:
        raise InvalidPack("Editor layers absent or exceed supported bounds")
    if not isinstance(actors, list) or not 1 <= len(actors) <= MAX_ACTORS:
        raise InvalidPack("Scene actors absent or exceed supported bounds")
    lid = []
    for layer in layers:
        if not isinstance(layer, dict) or not isinstance(layer.get("id"), str) or not 1 <= len(layer["id"]) <= 100:
            raise InvalidPack("Invalid layer ID")
        lid.append(layer["id"])
    if len(set(lid)) != len(lid):
        raise InvalidPack("Duplicate editor layer IDs")
    aid = []
    for actor in actors:
        if not isinstance(actor, dict) or not isinstance(actor.get("id"), str) or not 1 <= len(actor["id"]) <= 100:
            raise InvalidPack("Invalid actor ID")
        assigned = actor.get("editorLayerIds", [])
        if not isinstance(assigned, list) or any(layer not in lid for layer in assigned):
            raise InvalidPack("Actor references a missing layer")
        aid.append(actor["id"])
    if len(set(aid)) != len(aid):
        raise InvalidPack("Duplicate actor IDs")
    return {
        "actors": len(actors), "layers": len(layers),
        "projectKind": str(project.get("kind") or "unknown")[:80],
        "template": str(project.get("template") or "")[:80],
        "name": str(project.get("name") or "")[:120],
    }


def verify_scene(root, name):
    name = _slug(name)
    path = root / "scenes" / (name + ".swyrl.json")
    scene, raw = _read(path)
    details = scene_report(scene, name)
    return {"valid": True, "level": "scene-source-only", "id": name,
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), **details}


def verify_pack(root, name):
    name = _slug(name)
    path = root / "starter-packs" / (name + ".starter.json")
    metadata, _raw = _read(path)
    if not isinstance(metadata, dict) or metadata.get("schema") != SCHEMA or metadata.get("id") != name:
        raise InvalidPack("Pack descriptor schema/ID mismatch")
    if metadata.get("status") != "draft-unregistered" or metadata.get("type") != "existing-mode-map-variant":
        raise InvalidPack("Pack may only claim a draft existing-mode map variant")
    origin = metadata.get("source")
    if not isinstance(origin, dict) or not isinstance(origin.get("seed"), str):
        raise InvalidPack("Starter provenance missing seed")
    _slug(origin["seed"])
    for key in ("seedBlob", "manifestBlob", "engineMainSha"):
        if not SHA1.fullmatch(str(origin.get(key) or "")):
            raise InvalidPack("Pack's " + key + " source Git identity is not verified")
    if not isinstance(origin.get("orderedPatchCount"), int) or not 50 <= origin["orderedPatchCount"] <= 250:
        raise InvalidPack("Pack source manifest does not declare a plausible ordered patch count")
    scene_info = metadata.get("scene")
    if not isinstance(scene_info, dict):
        raise InvalidPack("Descriptor lacks scene metadata")
    expected_path = "projects/swrlz-forge-moba/scenes/" + name + ".swyrl.json"
    if scene_info.get("path") != expected_path or not SHA256.fullmatch(str(scene_info.get("sha256") or "")):
        raise InvalidPack("Scene path or SHA-256 in descriptor is invalid")
    report = verify_scene(root, name)
    if (report["sha256"] != scene_info.get("sha256")
            or report["bytes"] != scene_info.get("bytes")
            or report["actors"] != scene_info.get("actorCount")
            or report["layers"] != scene_info.get("layerCount")
            or report["projectKind"] != scene_info.get("projectKind")
            or report["template"] != origin["seed"]):
        raise InvalidPack("Pack metadata and actual scene bytes/type disagree")
    return {**report, "valid": True, "level": "draft-pack-source-only",
            "registration": "NOT REGISTERED", "gameplay": "NOT VERIFIED",
            "id": name, "sourceMain": origin["engineMainSha"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only §wyrl§ Engine scene/pack verifier")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="project root containing scenes/ and starter-packs/")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--scene", metavar="ID")
    choice.add_argument("--pack", metavar="ID")
    args = parser.parse_args(argv)
    try:
        result = verify_pack(args.root, args.pack) if args.pack else verify_scene(args.root, args.scene)
    except (InvalidPack, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
