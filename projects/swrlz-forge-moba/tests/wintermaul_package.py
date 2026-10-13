#!/usr/bin/env python3
"""Validate the native Wintermaul Wars scene and its sealed release package."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WARS_SCENE = "scenes/maul-wars-frostveil.swyrl.json"
EXPECTED_ASSETS = {
    "episodes/ghosts-in-different-forms-ep01.html",
    "scenes/ghosts-in-different-forms-ep01.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-depth.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json",
    "scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json",
    "scenes/sheep-tag-meadow.swyrl.json",
    "scenes/sheep-tag-moonbell-archive.swyrl.json",
    "scenes/maul-frostveil.swyrl.json",
    WARS_SCENE,
} | {"assets/anime/" + name + ".png" for name in (
    "kami", "swyrlz", "cathedral", "workshop", "foreground", "kami-rig",
    "swyrlz-rig", "scenery-parts", "kami-grip-layers", "mage-faces-painted", "kami-full-staff"
)}


def validate_scene(scene):
    project = scene["project"]
    assert project["canonicalId"] == "maul-wars-frostveil"
    assert project["kind"] == "maul-wars"
    rules = project["maulWars"]
    assert rules == {"lives": 25, "startGold": 450, "startIncome": 25, "preparation": 30,
                     "incomeInterval": 25, "spawnInterval": 0.55, "soloSupport": True,
                     "opponentAI": True, "difficulty": 1, "selectedSector": 0, "seed": 1317}, "Unexpected starter Wars rules"
    assert type(rules["soloSupport"]) is bool and type(rules["opponentAI"]) is bool
    actors = scene["scene"]["actors"]
    assert actors and len({actor["id"] for actor in actors}) == len(actors)
    assert all(actor["baked"] and actor["visible"] for actor in actors)
    layers = scene["editor"]["layers"]
    assert len(layers) == 7 and len({layer["id"] for layer in layers}) == 7
    assert all(any(layer["id"] in actor["editorLayerIds"] for actor in actors) for layer in layers)
    assert all(any(layer["id"] in actor["editorLayerIds"] for layer in layers) for actor in actors)
    by_type = lambda kind: [actor for actor in actors if actor["type"] == kind]
    builders = by_type("maul-wars-builder")
    assert len(builders) == 6
    assert {actor["wars"]["sector"] for actor in builders} == set(range(6))
    assert all(actor["wars"]["team"] == actor["wars"]["sector"] // 3 for actor in builders)
    for kind in ("maul-wars-spawn", "maul-wars-exit"):
        entries = by_type(kind)
        assert len(entries) == 2, kind
        assert {actor["wars"]["team"] for actor in entries} == {0, 1}, kind
    gates = by_type("maul-wars-gate")
    assert len(gates) == 10
    assert {(actor["wars"]["team"], actor["wars"]["stage"]) for actor in gates} == {
        (team, stage) for team in range(2) for stage in range(5)
    }, "Each team needs one beacon for each ordered route stage"
    assert len(by_type("maul-wars-sector")) == 2
    assert by_type("maul-wars-cliff"), "The mirrored map needs authored raised terrain"
    for actor in actors:
        for field in ("position", "rotation", "scale"):
            values = actor[field]
            assert len(values) == 3 and all(type(value) in (int, float) and math.isfinite(value) for value in values), (actor["id"], field)
    return {"actors": len(actors), "layers": len(layers), "builders": len(builders), "teams": 2, "routeBeacons": len(gates)}


def validate_package(package):
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    receipt = json.loads((package / "SOURCE.json").read_text())
    source = (package / "index.html").read_bytes()
    assert manifest["name"] == "§wyrl§ Engine v10.7"
    assert manifest["finalArtifact"] == "swyrl_engine_v10_7.html"
    assert len(manifest["patches"]) == 67 and manifest["patches"][-1] == "patches/v10_7_wintermaul_wars.py"
    assert receipt["patches"] == manifest["patches"]
    assert len(source) == manifest["finalBytes"] == receipt["finalBytes"]
    assert hashlib.sha256(source).hexdigest() == manifest["finalSha256"] == receipt["finalSha256"]
    assert b"SWYRL_ENGINE_DEPLOY_MARKER: V10_7_WINTERMAUL_WARS" in source
    assert b'<title>\xc2\xa7wyrl\xc2\xa7 Engine \xc2\xb7 Maker v10.7</title>' in source
    assert set(receipt["assets"]) == EXPECTED_ASSETS and len(EXPECTED_ASSETS) == 25, "Unexpected packaged asset set"
    for name, metadata in receipt["assets"].items():
        data = (package / name).read_bytes()
        assert data == (ROOT / name).read_bytes(), name
        assert len(data) == metadata["bytes"], name
        assert hashlib.sha256(data).hexdigest() == metadata["sha256"], name
    summary = validate_scene(json.loads((package / WARS_SCENE).read_text()))
    print("WINTERMAUL_WARS_NATIVE_PACKAGE_OK " + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    validate_package(parser.parse_args().package)
