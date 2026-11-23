#!/usr/bin/env python3
"""Register a generated armor atlas against an EXISTING §E mannequin UV paint.

An image generator draws approximate UV islands; this tool uses the baked
texture's island coverage as an authoritative destination. It optically aligns
the approximate silhouettes, paints only inside the native UV islands, fills
uncovered island texels by nearest detailed-artwork color, and pads edges for
filtering. It NEVER changes scene UVs, geometry, or topology.

Usage:
  python register_concept_uv_to_native.py --artwork /path/to/concept.png \
    --reference ../assets/models/futuristic-humanoid-v11-548-finished-robot-skin-4096.png \
    --output /path/to/registered-4096.png

Requires numpy, Pillow, scipy, opencv-python-headless. Artwork and reference
must use the SAME atlas topology/layout, not arbitrary generic robot atlases.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'assets/models/futuristic-humanoid-v11-548-finished-robot-skin-4096.png'


def rgb(path, side):
    return np.asarray(Image.open(path).convert('RGB').resize(
        (side, side), Image.Resampling.LANCZOS))


def background(arr):
    h, w = arr.shape[:2]
    d = max(4, min(h, w) // 64)
    corners = np.concatenate([
        arr[:d, :d].reshape(-1, 3),
        arr[:d, -d:].reshape(-1, 3),
        arr[-d:, :d].reshape(-1, 3),
        arr[-d:, -d:].reshape(-1, 3)
    ], axis=0)
    return np.median(corners, axis=0).astype(np.float32)


def silhouette(arr, bg, threshold):
    delta = np.linalg.norm(arr.astype(np.float32) - bg, axis=2)
    mask = (delta > threshold).astype(np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            np.ones((3, 3), np.uint8))


def flow_from_silhouette(artwork_mask, native_mask):
    n = len(artwork_mask)
    flow = np.zeros((n, n, 2), dtype=np.float32)
    # Four independent packed UV neighborhoods: each side's limb stacks,
    # helmet, and torso. Avoid cross-island attraction.
    regions = [(0, 0, .475, .535), (.565, 0, 1, .535),
               (0, .605, .385, 1), (.395, .52, 1, 1)]
    for x0, y0, x1, y1 in regions:
        l, t, r, b = map(int, (x0*n, y0*n, x1*n, y1*n))
        a = cv2.GaussianBlur(artwork_mask[t:b, l:r].astype('float32'),
                              (0, 0), 3)
        d = cv2.GaussianBlur(native_mask[t:b, l:r].astype('float32'),
                              (0, 0), 3)
        optical = cv2.DISOpticalFlow_create(
            cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        optical.setFinestScale(1)
        optical.setPatchSize(8)
        optical.setPatchStride(4)
        optical.setGradientDescentIterations(15)
        # Destination => source displacement for image resampling.
        backwards = optical.calc((d * 255).astype(np.uint8),
                                 (a * 255).astype(np.uint8), None)
        flow[t:b, l:r] = np.clip(backwards, -14, 14)
    flow = cv2.GaussianBlur(flow, (0, 0), 2)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    shifted = cv2.remap(artwork_mask.astype(np.float32),
                        xx + flow[:, :, 0], yy + flow[:, :, 1],
                        cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    iou = lambda a, b: (
        np.logical_and(a, b).sum() /
        max(int(np.logical_or(a, b).sum()), 1))
    before = float(iou(artwork_mask > 0, native_mask > 0))
    after = float(iou(shifted > .5, native_mask > 0))
    # A bad estimated flow must not silently worsen the registration.
    if after < before:
        return np.zeros_like(flow), before, before
    return flow, before, after


def register(artwork, reference, output, render_side=4096):
    small = 768
    art = rgb(artwork, small)
    native = rgb(reference, small)
    art_bg, native_bg = background(art), background(native)
    am = silhouette(art, art_bg, 15)
    nm = silhouette(native, native_bg, 8)
    flow, before, after = flow_from_silhouette(am, nm)
    # Different atlas UV layouts cannot be fixed by optical-flow alignment.
    if before < .57:
        raise ValueError(
            'Artwork does not match native UV atlas layout; '
            f'initial overlap={before:.3f}')
    full_art = np.asarray(Image.open(artwork).convert('RGB'))
    full_native = rgb(reference, render_side)
    target = silhouette(full_native, background(full_native), 8).astype(bool)
    fx = cv2.resize(flow[:, :, 0], (render_side, render_side),
                    interpolation=cv2.INTER_CUBIC) * (render_side / small)
    fy = cv2.resize(flow[:, :, 1], (render_side, render_side),
                    interpolation=cv2.INTER_CUBIC) * (render_side / small)
    ax = np.arange(render_side, dtype=np.float32)[None, :]
    ay = np.arange(render_side, dtype=np.float32)[:, None]
    mapx = (ax + fx) * (full_art.shape[1] - 1) / (render_side - 1)
    mapy = (ay + fy) * (full_art.shape[0] - 1) / (render_side - 1)
    transferred = cv2.remap(full_art, mapx, mapy,
                            cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    coverage = silhouette(transferred, background(full_art), 14).astype(bool)
    # No gray background paint inside actual islands.
    _, nearest = distance_transform_edt(~coverage, return_indices=True)
    missing = target & ~coverage
    transferred[missing] = transferred[nearest[0][missing],
                                        nearest[1][missing]]
    result = full_native.copy()
    result[target] = transferred[target]
    # 12 px bleed outside exact UV islands to avoid bilinear/mipmap seams.
    distance, edge = distance_transform_edt(~target, return_indices=True)
    padding = (~target) & (distance <= 12)
    result[padding] = result[edge[0][padding], edge[1][padding]]
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result, 'RGB').save(output, optimize=True)
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    report = {
        'artwork': str(artwork), 'referenceUVMaterial': str(reference),
        'output': str(output), 'resolution': [render_side, render_side],
        'artworkSourceResolution': list(Image.open(artwork).size),
        'nativeUvModified': False, 'geometryModified': False,
        'islandIoUBefore': round(before, 4), 'islandIoUAfter': round(after, 4),
        'uncoveredPixelsRepaired': int(missing.sum()),
        'artworkSha256': digest(artwork), 'referenceSha256': digest(reference),
        'resultSha256': digest(output),
        'scope': 'raster island registration; inspect final model from 3D views'
    }
    output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('SE_EXACT_UV_RASTER_REGISTRATION', json.dumps(report))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artwork', required=True, type=Path)
    parser.add_argument('--reference', type=Path, default=REFERENCE)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--size', type=int, default=4096,
                        choices=(1024, 2048, 4096))
    args = parser.parse_args()
    register(args.artwork, args.reference, args.output, args.size)
