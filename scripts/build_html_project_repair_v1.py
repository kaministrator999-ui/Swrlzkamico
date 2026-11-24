#!/usr/bin/env python3
"""Build a targeted locally bundled artifact from an existing HTML project.

No generated HTML. Exact source regions are surgically replaced; bundled output
is produced by esbuild from the original inline JavaScript module.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORTMAP = re.compile(r'(?is)<script\s+type=["\x27]importmap["\x27]\s*>[\s\S]*?</script>')
MODULE = re.compile(r'(?is)<script\s+type=["\x27]module["\x27]\s*>([\s\S]*?)</script>')
REMOTE = ("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
          "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/")
BUNDLE_NAME = "viewer.bundle.js"


def extract(source: str) -> str:
    if not isinstance(source, str) or len(source.encode()) > 150_000:
        raise ValueError("SOURCE_SIZE_INVALID")
    if len(IMPORTMAP.findall(source)) != 1 or len(MODULE.findall(source)) != 1:
        raise ValueError("UNSUPPORTED_OR_AMBIGUOUS_HTML_MODULES")
    block = IMPORTMAP.search(source).group()
    try:
        parsed = json.loads(re.sub(r'(?is)^<script[^>]*>|</script>$', "", block).strip())
    except (ValueError, TypeError) as exc:
        raise ValueError("IMPORTMAP_INVALID") from exc
    if parsed != {"imports": {"three": REMOTE[0], "three/addons/": REMOTE[1]}}:
        raise ValueError("UNSUPPORTED_THREE_IMPORT_MAP")
    entry = MODULE.search(source).group(1)
    if ("import * as THREE from 'three';" not in entry
            or "three/addons/controls/OrbitControls.js" not in entry):
        raise ValueError("UNSUPPORTED_SCENE_ENTRY")
    return entry


def transform(source: str) -> str:
    extract(source)
    no_map = IMPORTMAP.sub("", source, count=1)
    result = MODULE.sub('<script src="./' + BUNDLE_NAME + '"></script>', no_map, count=1)
    if "cdn.jsdelivr.net" in result or "type=\"importmap\"" in result:
        raise ValueError("EXTERNAL_DEPENDENCY_LEFT_IN_HTML")
    if result.count('src="./' + BUNDLE_NAME + '"') != 1:
        raise ValueError("LOCAL_BUNDLE_REFERENCE_INVALID")
    # Confirm no unrelated markup or UI changed.
    if len(IMPORTMAP.findall(source)) != 1 or result == source:
        raise ValueError("HTML_TRANSFORM_NOT_TARGETED")
    return result


def validate(source: str, changed: str, bundle: bytes) -> None:
    if transform(source) != changed:
        raise ValueError("NONDETERMINISTIC_HTML_CHANGE")
    if not bundle or len(bundle) > 900_000 or len(changed.encode()) + len(bundle) > 1_000_000:
        raise ValueError("BUNDLE_SIZE_EXCEEDS_PROJECT_LIMIT")
    text = bundle.decode("utf-8")
    if re.search(r'(?m)^\s*(?:import|export)\s', text):
        raise ValueError("UNBUNDLED_MODULE_REMAINED")
    sys.path.insert(0, str(ROOT / "api"))
    from lightweight_webpage_inspector_v1 import inspect_files
    checks = inspect_files({"index.html": changed, BUNDLE_NAME: bundle})
    if not checks.get("staticPass") or checks.get("issues"):
        raise ValueError("STATIC_PROJECT_GATE_FAILED: " + str(checks["issues"][:6]))
    if checks.get("functionalVerified") is not False:
        raise ValueError("RUNTIME_CLAIM_NOT_ALLOWED")


def build(project: str, source_root: Path, output_root: Path, tools_root: Path):
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?", project):
        raise ValueError("INVALID_PROJECT_SLUG")
    original = source_root / "html-projects" / project / "index.html"
    if not original.is_file() or original.is_symlink():
        raise ValueError("SOURCE_PROJECT_MISSING")
    source = original.read_text(encoding="utf-8")
    module_text = extract(source)
    tools_root = tools_root.resolve()
    if not tools_root.is_dir() or not (tools_root / "node_modules" / "three" / "package.json").is_file():
        raise ValueError("PINNED_TOOLCHAIN_NOT_INSTALLED")
    versions = json.loads((tools_root / "node_modules" / "three" / "package.json").read_text())
    if versions.get("version") != "0.160.0":
        raise ValueError("THREE_VERSION_MISMATCH")
    entry = tools_root / "swrlz-existing-viewer-entry.mjs"
    entry.write_text(module_text, encoding="utf-8")
    output = output_root / project
    output.mkdir(parents=True, exist_ok=True)
    bundle_path = output / BUNDLE_NAME
    cli = tools_root / "node_modules" / ".bin" / "esbuild"
    if not cli.is_file():
        raise ValueError("ESBUILD_NOT_INSTALLED")
    subprocess.run([str(cli), str(entry), "--bundle", "--format=iife",
                    "--platform=browser", "--target=es2020", "--minify",
                    "--outfile=" + str(bundle_path.resolve())],
                   check=True, cwd=tools_root, timeout=180)
    bundle = bundle_path.read_bytes()
    updated = transform(source)
    validate(source, updated, bundle)
    (output / "index.html").write_text(updated, encoding="utf-8")
    print("SOURCE_PRESERVED_DEPENDENCY_BUNDLE_PASS", project,
          {"original": len(source.encode()), "html": len(updated.encode()),
           "bundle": len(bundle)}, flush=True)


def selftest():
    fixture = (
        '<html><head><script type="importmap">{"imports":{"three":"'
        + REMOTE[0] + '","three/addons/":"' + REMOTE[1] + '"}}</script></head>'
        '<body><button id="reset">Reset</button><script type="module">'
        "import * as THREE from 'three';\n"
        "import { OrbitControls } from 'three/addons/controls/OrbitControls.js';\n"
        "document.getElementById('reset').onclick = ()=>{};"
        "</script></body></html>")
    result = transform(fixture)
    assert '<button id="reset">Reset</button>' in result
    assert "type=\"importmap\"" not in result
    assert 'src="./viewer.bundle.js"' in result
    assert "new THREE" not in result
    try:
        extract(fixture.replace("0.160.0","0.161.0"))
    except ValueError:
        pass
    else:
        raise AssertionError("DRIFT_NOT_REJECTED")
    print("TARGETED_EXISTING_HTML_REPAIR_SELFTEST_PASS", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["selftest", "build"])
    p.add_argument("--project")
    p.add_argument("--source-root", default="reviewed-source")
    p.add_argument("--output-root", default="repair-output")
    p.add_argument("--tools-root", default="repair-tools")
    args = p.parse_args()
    selftest()
    if args.mode == "build":
        build(args.project, Path(args.source_root), Path(args.output_root),
              Path(args.tools_root))
