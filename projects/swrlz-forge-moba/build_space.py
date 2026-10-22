#!/usr/bin/env python3
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "payload"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_space_metadata(readme: str) -> None:
    """Catch the Space's single-line summary limit before writing a package."""
    sections = readme.split("---", 2)
    if len(sections) != 3 or sections[0].strip():
        raise SystemExit("SPACE_README.md needs YAML front matter")
    fields = dict(line.split(":", 1) for line in sections[1].splitlines() if ":" in line)
    description = fields.get("short_description", "").strip()
    if description[:1] in ("\"", "'") and description[-1:] == description[:1]:
        description = description[1:-1]
    if not description or description.startswith(("|", ">")) or len(description) > 60:
        raise SystemExit("Space short_description must be a single line of 1–60 characters")

def load_patch(path: Path):
    spec = importlib.util.spec_from_file_location(f"swrlz_patch_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load patch module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "apply"):
        raise SystemExit(f"Patch module has no apply(html) function: {path}")
    return module.apply

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    space_readme = (ROOT / "SPACE_README.md").read_text(encoding="utf-8")
    validate_space_metadata(space_readme)

    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    part_names = manifest.get("chunks") or [p.relative_to(ROOT).as_posix() for p in sorted(PAYLOAD.glob("part-*.txt"))]
    parts = [ROOT / name for name in part_names]
    if not parts or any(not p.exists() for p in parts):
        raise SystemExit("One or more payload chunks are missing")

    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    base_html = gzip.decompress(base64.b64decode(encoded))

    base_expected_sha = manifest.get("baseSha256", manifest.get("sha256"))
    base_expected_bytes = manifest.get("baseBytes", manifest.get("bytes"))
    got_base_sha = sha256(base_html)
    if got_base_sha != base_expected_sha:
        raise SystemExit(f"Base source SHA mismatch: expected {base_expected_sha}, got {got_base_sha}")
    if len(base_html) != base_expected_bytes:
        raise SystemExit(f"Base source byte-size mismatch: expected {base_expected_bytes}, got {len(base_html)}")

    html_text = base_html.decode("utf-8")
    applied_patches = []
    for rel in manifest.get("patches", []):
        patch_path = ROOT / rel
        apply = load_patch(patch_path)
        html_text = apply(html_text)
        applied_patches.append(rel)

    html = html_text.encode("utf-8")
    final_expected_sha = manifest.get("finalSha256", base_expected_sha)
    final_expected_bytes = manifest.get("finalBytes", base_expected_bytes)
    got_final_sha = sha256(html)
    if got_final_sha != final_expected_sha:
        raise SystemExit(f"Final source SHA mismatch: expected {final_expected_sha}, got {got_final_sha}")
    if len(html) != final_expected_bytes:
        raise SystemExit(f"Final source byte-size mismatch: expected {final_expected_bytes}, got {len(html)}")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_bytes(html)
    (out / "README.md").write_text(space_readme, encoding="utf-8")
    # Native game starter source and episode screening travel with the engine.
    assets = {}
    media_paths = ["episodes/ghosts-in-different-forms-ep01.html",
                   "scenes/ghosts-in-different-forms-ep01.swyrl.json",
                   "scenes/sheep-tag-meadow.swyrl.json",
                   "scenes/sheep-tag-moonbell-archive.swyrl.json"]
    for authored in ("scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-depth.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json",
                     "scenes/ghosts-in-different-forms-ep01-performance.swyrl.json"):
        if (ROOT / authored).exists():
            media_paths.append(authored)
    if (ROOT / "scenes/maul-frostveil.swyrl.json").exists():
        media_paths.append("scenes/maul-frostveil.swyrl.json")
    if (ROOT / "scenes/maul-frostveil-classic.swyrl.json").exists():
        media_paths.append("scenes/maul-frostveil-classic.swyrl.json")
    if (ROOT / "scenes/maul-frostveil-groups.swyrl.json").exists():
        media_paths.append("scenes/maul-frostveil-groups.swyrl.json")
    if (ROOT / "scenes/maul-frostveil-flight.swyrl.json").exists():
        media_paths.append("scenes/maul-frostveil-flight.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-festival-v11-5.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-festival-v11-5.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-festival-v11-6.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-festival-v11-6.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-festival-v11-7.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-festival-v11-7.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-festival-v11-8.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-festival-v11-8.swyrl.json")
    if (ROOT / "scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json").exists():
        media_paths.append("scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-reference-v11-13.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-refined-v11-14.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-surface-v11-15.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-detail-v11-16.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-hd-v11-17.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-reference-v11-18.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-polish-v11-19.swyrl.json")
    media_paths.append("scenes/model-atelier-festival-anatomy-v11-20.swyrl.json")
    media_paths.extend(p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "assets/anime").glob("*.png")))
    media_paths.append("scenes/model-atelier-comet-courier-v11-77.swyrl.json")
    media_paths.extend(p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "assets/models/comet-courier").glob("*")) if p.is_file())
    for rel in media_paths:
        source = ROOT / rel
        data = source.read_bytes()
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        assets[rel] = {"sha256": sha256(data), "bytes": len(data)}
    (out / "SOURCE.json").write_text(json.dumps({
        "schema": "swrlz-forge-source-v2",
        "sourceVersion": manifest.get("name"),
        "baseSha256": got_base_sha,
        "baseBytes": len(base_html),
        "finalSha256": got_final_sha,
        "finalBytes": len(html),
        "payloadParts": [p.relative_to(ROOT).as_posix() for p in parts],
        "patches": applied_patches,
        "assets": assets,
        "projectPath": "projects/swrlz-forge-moba",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out),
        "baseSha256": got_base_sha,
        "finalSha256": got_final_sha,
        "bytes": len(html),
        "parts": len(parts),
        "patches": applied_patches,
    }))

if __name__ == "__main__":
    main()
