#!/usr/bin/env python3
"""Route §E browser CI by the latest commit's affected subsystems.

Routine PR and main commits run only impacted suites. Shared packaging/manifest
edits get source-seal verification elsewhere, not 22 unrelated browser suites.
Ambiguous shared runtime edits fail OPEN to all suites. Explicit dispatch and
deployment promotion run the entire integration suite.
"""
import argparse
import fnmatch
import json
import os
import subprocess
from pathlib import Path

ROOT = "projects/swrlz-forge-moba/"
SUITES = (
    ("sheep_archive", "desktop", "sheep"),
    ("sheep_archive", "mobile", "sheep"),
    ("model_reference", "desktop", "model"),
    ("model_reference", "mobile", "model"),
    ("character_relief", "desktop", "anime"),
    ("character_relief", "mobile", "anime"),
    ("character_rig", "desktop", "anime"),
    ("character_rig", "mobile", "anime"),
    ("native_anime", "", "anime"),
    ("storybook_authoring", "", "anime"),
    ("depth_theatre", "", "anime"),
    ("character_alignment", "", "anime"),
    ("socket_emergence", "", "anime"),
    ("episode_transport", "", "anime"),
    ("sheep_tag", "", "sheep"),
    ("sheep_touch", "", "sheep"),
    ("sheep_run", "", "sheep"),
    ("maul", "", "maul"),
    ("maul_layout", "", "maul"),
    ("maul_batch", "", "maul"),
    ("episode_performance", "", "anime"),
    ("model_atelier", "", "model"),
)
COMPONENTS = frozenset(("model", "anime", "sheep", "maul"))
# Changes to these shared release receipts are handled by their focused
# source-integrity workflow. They do not change runtime behavior themselves.
SEALED_METADATA = frozenset(
    (ROOT + "source-manifest.json", ROOT + "SPACE_README.md",
     ROOT + "DEPLOY_REQUEST.json", ROOT + "README.md", ROOT + "ROADMAP.md",
     "§tart_§E.md"))
CI_ROUTER = ROOT + "scripts/route_ci_suites.py"


def classify(filename):
    """Return affected components, empty set (metadata), or all (unknown core)."""
    path = filename.replace("\\", "/")
    if path == ROOT + "DEPLOY_REQUEST.json":
        return set(COMPONENTS)  # Live promotion is an integration gate.
    if path in SEALED_METADATA or path == CI_ROUTER:
        return set()
    if path.startswith(".github/workflows/"):
        # Workflow edits are checked by the lightweight routing job; deployment
        # and explicit full-sweep workflow changes remain integration-sensitive.
        if path.endswith("deploy-swrlz-forge-moba.yml"):
            return set(COMPONENTS)
        return set()
    if not path.startswith(ROOT):
        return set()
    rel = path[len(ROOT):]
    if rel.startswith(("reports/",)) or rel.endswith((".md", ".txt")):
        return set()
    if rel.startswith(("payload/", "assets/")) or rel == "build_space.py":
        return set(COMPONENTS)
    if rel.startswith(("scripts/verify_v", "scripts/measure_v", "scripts/prepare_v")):
        return set()
    if rel.startswith("patches/"):
        name = rel[len("patches/"):]
        if name.startswith(("v11_", "v11.")):
            return {"model"}
        if name.startswith(("v10_0", "v10_1", "v10_2", "v10_3", "v10_4", "v10_5")):
            return {"sheep"}
        if name.startswith(("v10_6", "v10_7", "v10_8")):
            return {"maul"}
        if name.startswith(("v8_6", "v8_7", "v8_8", "v8_9", "v9_")):
            return {"anime"}
        # Core engine patches can impact all scenes.
        return set(COMPONENTS)
    if rel.startswith(("runtime/", "tests/", "scenes/", "authoring/", "episodes/")):
        name = rel.rsplit("/", 1)[-1].lower()
        if name.startswith(("model_", "prism_", "festival_", "mobile_adaptive_", "atelier_")) or "atelier" in name:
            return {"model"}
        if name.startswith(("sheep_", "run_replay_")):
            return {"sheep"}
        if name.startswith(("maul_",)):
            return {"maul"}
        if name.startswith(("anime_", "episode_", "character_", "storybook_", "depth_theatre", "socket_",
                            "ghosts-in-", "native_anime")):
            return {"anime"}
        # Unknown runtime/test/scene code may be shared.
        return set(COMPONENTS)
    # Unknown engine code is never silently skipped.
    return set(COMPONENTS)


def route(paths, event="pull_request", full=False):
    paths = list(paths)
    if full or event == "workflow_dispatch" or not paths:
        groups = set(COMPONENTS)
    else:
        groups = set()
        for path in paths:
            groups.update(classify(path))
        # The manifest is also an executable patch-order/build recipe. If it
        # changes without a corresponding patch edit, scope is unknowable.
        if ROOT + "source-manifest.json" in paths and not any(
                p.startswith(ROOT + "patches/") for p in paths):
            groups.update(COMPONENTS)
    selected = [{"suite": suite, "mode": mode} for suite, mode, group in SUITES if group in groups]
    return {"groups": sorted(groups), "matrix": {"include": selected}, "any": bool(selected),
            "full": groups == set(COMPONENTS)}


def changed_files(base, head):
    if not base or not head:
        raise ValueError("CI routing requires explicit base and head SHA")
    return subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=ACDMRT", base, head],
        text=True).splitlines()


def self_test():
    tests = [
        (["projects/swrlz-forge-moba/patches/v11_63_sculpt.py", ROOT + "source-manifest.json"], {"model"}),
        (["projects/swrlz-forge-moba/tests/model_atelier_playwright.mjs"], {"model"}),
        (["projects/swrlz-forge-moba/patches/v10_0_sheep_tag.py"], {"sheep"}),
        (["projects/swrlz-forge-moba/runtime/maul_core.js"], {"maul"}),
        (["projects/swrlz-forge-moba/patches/v9_2_depth_theatre.py"], {"anime"}),
        ([ROOT + "source-manifest.json"], set(COMPONENTS)),
        ([ROOT + "runtime/unknown_shared_engine.js"], set(COMPONENTS)),
        ([ROOT + "DEPLOY_REQUEST.json"], set(COMPONENTS)),
        ([CI_ROUTER], set()),
    ]
    for paths, expected in tests:
        actual = set(route(paths)["groups"])
        assert actual == expected, (paths, actual, expected)
    assert len(route(["anything"], full=True)["matrix"]["include"]) == 22
    assert len(route(["anything"], event="workflow_dispatch")["matrix"]["include"]) == 22
    assert len(route([ROOT + "patches/v11_63_sculpt.py"])["matrix"]["include"]) == 3
    print("SE_CI_ROUTER_SELF_TEST_OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", default="pull_request")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--files-json", help="Synthetic list for local testing")
    parser.add_argument("--component", choices=sorted(COMPONENTS))
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", help="GitHub Actions output path (normally $GITHUB_OUTPUT)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    try:
        paths = json.loads(args.files_json) if args.files_json is not None else (
            [] if args.event == "workflow_dispatch" else changed_files(args.base, args.head))
        if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            raise ValueError("Expected a JSON array of changed paths")
        result = route(paths, args.event, args.full)
    except (subprocess.CalledProcessError, ValueError) as exc:
        # Missing git history, unusual merge or malformed payload => full,
        # not a silent omission of important tests.
        print("ROUTER_FAIL_OPEN:", exc)
        paths = []
        result = route(paths, full=True)
    enabled = args.component is None or args.component in result["groups"]
    output = {
        "matrix": json.dumps(result["matrix"], separators=(",", ":")),
        "any": str(result["any"]).lower(),
        "run": str(enabled).lower(),
        "full": str(result["full"]).lower(),
        "groups": ",".join(result["groups"]),
    }
    print("SE_CI_ROUTING", json.dumps({"event": args.event, "changed": paths,
                                       "groups": result["groups"],
                                       "suites": len(result["matrix"]["include"]),
                                       "component": args.component}, sort_keys=True))
    if args.output:
        with open(args.output, "a", encoding="utf-8") as f:
            for key, value in output.items():
                f.write(f"{key}={value}\n")
    else:
        print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
