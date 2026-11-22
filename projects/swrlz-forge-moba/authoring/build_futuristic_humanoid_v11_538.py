#!/usr/bin/env python3
"""Author one original watertight humanoid shell with a native six-island UV material atlas.

Run only during release authoring, never on a phone. Baked output is an ordinary
native §E model-atelier scene with one topologyMesh (not 178 assembled primitives).
"""
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from skimage.measure import marching_cubes

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json"
STEP = 0.052
x = np.arange(-2.75, 2.75 + STEP, STEP, dtype=np.float32)
y = np.arange(-.12, 4.95 + STEP, STEP, dtype=np.float32)
z = np.arange(-.64, .76 + STEP, STEP, dtype=np.float32)
X, Y, Z = x[:, None, None], y[None, :, None], z[None, None, :]
field = np.full((len(x), len(y), len(z)), 10, dtype=np.float32)


def blend(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * .25


def ellipsoid(center, radius, softness=.075):
    global field
    d = (np.sqrt(((X-center[0])/radius[0])**2 +
                 ((Y-center[1])/radius[1])**2 +
                 ((Z-center[2])/radius[2])**2)-1)*min(radius)
    field = blend(field, d, softness)


def capsule(a, b, r0, r1=None, softness=.07, zscale=1):
    global field
    if r1 is None:
        r1 = r0
    vec = np.array(b, dtype=np.float32)-np.array(a, dtype=np.float32)
    t = np.clip(((X-a[0])*vec[0]+(Y-a[1])*vec[1]+(Z-a[2])*vec[2])/(vec@vec), 0, 1)
    d = np.sqrt((X-a[0]-t*vec[0])**2 +
                (Y-a[1]-t*vec[1])**2 +
                ((Z-a[2]-t*vec[2])/zscale)**2) - (r0+(r1-r0)*t)
    field = blend(field, d, softness)


def anatomy():
    # One smooth anatomical envelope. Blended joints do not retain separate
    # shells, holes, pins or visible muscle-bubble intersections.
    ellipsoid((0, 3.55, 0), (.45, .46, .256), .085)
    ellipsoid((0, 3.17, 0), (.315, .47, .19), .13)
    ellipsoid((0, 2.57, 0), (.41, .34, .235), .13)
    ellipsoid((0, 2.36, 0), (.355, .245, .23), .075)
    capsule((0, 3.84, 0), (0, 4.22, 0), .12, .105, .05)
    ellipsoid((0, 4.48, -.005), (.25, .338, .246), .09)
    ellipsoid((0, 4.34, .097), (.192, .218, .173), .07)
    for side in (-1, 1):
        s = side
        # True horizontal T-pose, shoulders blended into body topology.
        ellipsoid((s*.49, 3.65, -.008), (.235, .203, .216), .19)
        capsule((s*.54, 3.655, 0), (s*1.36, 3.65, 0), .176, .109, .095, .97)
        ellipsoid((s*.92, 3.648, .01), (.23, .149, .166), .08)
        capsule((s*1.34, 3.65, 0), (s*2.055, 3.65, 0), .11, .074, .064)
        ellipsoid((s*1.69, 3.65, .01), (.29, .11, .124), .08)
        ellipsoid((s*2.18, 3.65, 0), (.214, .08, .15), .06)
        # Fingers are part of the same field and surface, not floating parts.
        for i, (depth, length) in enumerate(zip((-.112, -.040, .039, .108),
                                                 (.18, .255, .246, .190))):
            capsule((s*2.30, 3.649, depth),
                    (s*(2.30+length), 3.649, depth+(i-1.5)*.007),
                    .031, .018, .012)
        capsule((s*2.17, 3.62, .112), (s*2.37, 3.63, .249), .046, .024, .032)
        ellipsoid((s*.277, 2.31, -.015), (.221, .229, .22), .13)
        capsule((s*.286, 2.25, 0), (s*.332, 1.43, 0), .21, .133, .12, 1.04)
        ellipsoid((s*.347, 1.87, .007), (.19, .29, .18), .08)
        ellipsoid((s*.328, 1.326, .04), (.14, .134, .144), .035)
        capsule((s*.330, 1.25, -.017), (s*.333, .34, 0), .124, .085, .06, 1.05)
        ellipsoid((s*.323, 1.01, -.066), (.149, .238, .145), .095)
        ellipsoid((s*.333, .20, .175), (.144, .135, .302), .075)
        ellipsoid((s*.333, .118, .357), (.162, .086, .156), .045)
        for i in range(5):
            ellipsoid((s*(.333+(i-2)*.057), .098, .466-abs(i-1)*.019),
                      (.028, .039, .095), .015)
    # Actual shallow, integral geometry creases, not floating plates.
    global field
    field += .009*np.exp(-((Y-3.40)/.034)**2)*np.exp(-(X/.39)**8)*np.exp(-((Z-.26)/.12)**2)
    field += .005*np.exp(-((Y-2.54)/.03)**2)*np.exp(-(X/.28)**8)*np.exp(-((Z-.22)/.07)**2)


def topology():
    vertices, triangles, _, _ = marching_cubes(
        field, level=0, spacing=(STEP, STEP, STEP), allow_degenerate=False)
    vertices += np.array((x[0], y[0], z[0]))
    # Check connectedness on original geometry *before* UV seam duplication.
    def adjacency(faces, count):
        a, b, c = faces[:, 0], faces[:, 1], faces[:, 2]
        ii = np.concatenate((a, b, c, a, b, c))
        jj = np.concatenate((b, c, a, c, a, b))
        matrix = coo_matrix((np.ones(len(ii)), (ii, jj)), shape=(count, count)).tocsr()
        matrix.data.fill(1)
        return matrix
    adj = adjacency(triangles, len(vertices))
    count, labels = connected_components(adj)
    assert count == 1, f"Mannequin contains {count} disconnected shells"
    # Taubin smoothing for natural volume, avoids shrink at shoulders/knees.
    degree = np.asarray(adj.sum(axis=1)).ravel()
    for strength in (.35, -.36, .35, -.36, .35, -.36):
        average = adj.dot(vertices)/np.maximum(degree[:, None], 1)
        vertices = vertices + strength*(average-vertices)
    # Boundary/edge manifoldness of the marching-cubes surface.
    e = np.sort(np.concatenate((triangles[:, (0, 1)],
                                triangles[:, (1, 2)],
                                triangles[:, (2, 0)])), axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    assert np.all(cnt == 2), "Unexpected open or non-manifold body geometry"
    return vertices, triangles


def region(point):
    xx, yy, zz = point
    if yy > 4.13:
        return 0
    if yy > 3.33 and abs(xx) > .54:
        return 2 if xx < 0 else 3
    if yy > 2.32:
        return 1
    return 4 if xx < 0 else 5


def mapping(point, group):
    xx, yy, zz = point
    if group in (0, 1):
        u = (np.arctan2(xx, zz)+np.pi)/(2*np.pi)  # UV seam behind head/torso.
        v = (yy-(4.08 if group == 0 else 2.30)) / (.83 if group == 0 else 1.8)
    elif group in (2, 3):
        u = (np.arctan2(yy-3.65, zz)+np.pi)/(2*np.pi)
        v = (abs(xx)-.52)/2.12
    else:
        u = (np.arctan2(xx-(.33 if group == 5 else -.33), zz)+np.pi)/(2*np.pi)
        v = yy/2.42
    return [float(np.clip(u, 0, 1)), float(np.clip(v, 0, 1))]


def six_island_uv(vertices, faces):
    # Six unique square UV islands (head, trunk, L/R arms, L/R legs).
    # Duplicating seam vertices preserves continuity of the geometric shell
    # while keeping every UV coordinate unambiguous and within 0..1.
    packed_v, packed_uv, packed_i, lookup = [], [], [], {}
    for face in faces:
        group = region(vertices[face].mean(axis=0))
        local = [mapping(vertices[i], group) for i in face]
        if max(p[0] for p in local)-min(p[0] for p in local) > .55:
            majority = round(sum(p[0] for p in local)/3)
            for p in local:
                if majority and p[0] < .5:
                    p[0] = 1.
                if not majority and p[0] > .5:
                    p[0] = 0.
        row = []
        for i, (u, v) in zip(face, local):
            uu = ((group % 3)+.02+.96*u)/3
            vv = ((group // 3)+.02+.96*v)/2
            key = (int(i), round(uu, 6), round(vv, 6))
            if key not in lookup:
                lookup[key] = len(packed_v)
                packed_v.append(vertices[i])
                packed_uv.append((uu, vv))
            row.append(lookup[key])
        packed_i.append(row)
    v = np.asarray(packed_v)
    uv = np.asarray(packed_uv)
    faces = np.asarray(packed_i)
    assert len(v) <= 9000 and len(faces) <= 16000, (
        f"Native mesh ceiling exceeded: {len(v)} vertices, {len(faces)} triangles")
    assert np.isfinite(v).all() and np.isfinite(uv).all()
    assert (uv >= 0).all() and (uv <= 1).all()
    return v, uv, faces


def atlas():
    """Paint original soft-tech material regions, no external copyrighted artwork."""
    size = 1024
    im = Image.new("RGB", (size, size), "#c7d0d5")
    d = ImageDraw.Draw(im)
    def p(group, u, v):
        return (round(((group % 3)+.02+.96*u)/3*(size-1)),
                round((1-((group//3)+.02+.96*v)/2)*(size-1)))
    def poly(group, coords, color):
        d.polygon([p(group, u, v) for u, v in coords], fill=color)
    def line(group, coords, color, width=2):
        d.line([p(group, u, v) for u, v in coords], fill=color, width=width, joint="curve")
    for g, color in enumerate(("#c3cbd1", "#d1d6da", "#9faab3", "#9faab3",
                               "#b5bec5", "#b5bec5")):
        poly(g, ((0,0),(1,0),(1,1),(0,1)), color)
    # Faceplate is a UV material zone, integral to the main shell, not a mask mesh.
    poly(0, ((.27,.40),(.34,.28),(.65,.28),(.74,.40),(.72,.66),(.65,.77),
             (.35,.77),(.28,.66)), "#343c49")
    poly(0, ((.32,.51),(.35,.44),(.65,.44),(.69,.51),(.65,.57),(.35,.57)), "#5a8390")
    line(0, ((.32,.72),(.5,.78),(.68,.72)), "#dce5eb", 3)
    line(0, ((.34,.24),(.5,.20),(.66,.24)), "#8e9da8")
    poly(1, ((.33,.69),(.44,.86),(.56,.86),(.67,.69),(.58,.59),(.42,.59)), "#87939d")
    poly(1, ((.44,.70),(.5,.74),(.56,.70),(.54,.62),(.46,.62)), "#404b57")
    for v in (.36,.43,.50):
        line(1, ((.40,v),(.60,v)), "#8b98a2")
    line(1, ((.37,.24),(.5,.20),(.63,.24)), "#53606b", 3)
    line(1, ((.28,.85),(.38,.91),(.62,.91),(.72,.85)), "#647481", 3)
    for g in (2,3):
        poly(g, ((.38,.20),(.44,.22),(.44,.77),(.38,.79)), "#adb9c0")
        poly(g, ((.57,.22),(.62,.20),(.62,.79),(.57,.77)), "#7c8895")
        line(g, ((.15,.39),(.85,.39)), "#34414d", 4)
        line(g, ((.18,.42),(.82,.42)), "#dfe6eb")
        line(g, ((.22,.72),(.5,.81),(.78,.72)), "#576671", 3)
        line(g, ((.36,.12),(.64,.12)), "#5a6571", 3)
    for g in (4,5):
        poly(g, ((.42,.20),(.46,.38),(.54,.38),(.58,.20),(.54,.12),(.46,.12)), "#9aa9b4")
        poly(g, ((.34,.47),(.40,.54),(.60,.54),(.66,.47),(.60,.40),(.40,.40)), "#556673")
        line(g, ((.36,.51),(.64,.51)), "#dce9ed", 3)
        line(g, ((.39,.24),(.43,.38)), "#596a76")
        line(g, ((.61,.24),(.57,.38)), "#596a76")
        line(g, ((.32,.10),(.68,.10)), "#3d4a54", 3)
    for g in range(6):
        line(g, ((.45,.87),(.55,.87)), "#4d99a1")
    png = io.BytesIO()
    im.save(png, format="PNG", optimize=True)
    encoded = "data:image/png;base64,"+base64.b64encode(png.getvalue()).decode("ascii")
    assert len(encoded) <= 360000
    return encoded


def main():
    anatomy()
    positions, indices = topology()
    positions, uvs, indices = six_island_uv(positions, indices)
    part = {
        "id": "humanoid-body-unified",
        "name": "Futuristic Humanoid · continuous sculpted body",
        "group": "Primary Body / UV Material", "kind": "topologyMesh",
        "position": [0,0,0], "rotation": [0,0,0], "scale": [1,1,1],
        "color": "#ffffff", "material": "silk",
        "topologyMesh": {
            "positions": np.round(positions, 5).ravel().tolist(),
            "uvs": np.round(uvs, 6).ravel().tolist(),
            "indices": indices.astype(int).ravel().tolist(),
        },
        "uvPaintPNG": atlas(),
    }
    scene = {
        "engine": "§wyrl§ Engine · Maker v11.538", "version": 11.538,
        "project": {
            "name": "Futuristic Humanoid · Smooth Mannequin",
            "canonicalId": "robotic-humanoid-mannequin",
            "template": "robotic-humanoid-mannequin",
            "kind": "model-atelier", "environment": "spatial-workspace",
            "environmentSettings": {
                "background": "#1e2732", "fogNear": 80, "fogFar": 140,
                "exposure": 1.14, "showTerrain": False, "showScenery": False,
            },
            "modelAtelier": {
                "schema": "swyrl-model-atelier-v1",
                "name": "Futuristic Humanoid · Smooth UV Base",
                "reference": (
                    "Original smooth continuous humanoid shell in horizontal T-pose. "
                    "One UV-painted topologyMesh, six atlas islands for head, torso, arms "
                    "and legs, original graphite/satin/cyan material graphics. Embedded "
                    "native PNG, no external assets. No skeletal rig or animations yet."
                ),
                "parts": [part], "meshGroups": [],
                "poseFrames": [], "poseNeutral": None, "editedAt": None,
            },
        },
        "editor": {
            "transformSpace": "world", "snapEnabled": False,
            "terrainSnapEnabled": False, "viewMode": "edit",
            "cameraView": "perspective", "revision": 0,
            "layers": [{"id": "atelier-scene", "name": "Model Atelier Base", "visible": True}],
            "activeLayerId": "atelier-scene",
        },
        "scene": {"actors": []},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(scene, ensure_ascii=False, separators=(",", ":")), "utf8")
    print("SE538_UNIFIED_HUMANOID_BAKED", json.dumps({
        "parts": 1, "vertices": len(positions), "triangles": len(indices),
        "atlasBytes": len(part["uvPaintPNG"]), "sceneBytes": OUTPUT.stat().st_size,
        "file": OUTPUT.name,
    }), flush=True)


if __name__ == "__main__":
    main()
