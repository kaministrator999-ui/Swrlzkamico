"""Adaptive source-pixel panel discovery for multi-view reference sheets.

This layout pass locates artwork and gutters; it DOES NOT identify a subject,
read labels or assign anatomical direction. Its region names are positional.
No network, OCR, model identity shortcuts, or new dependencies.
"""
from __future__ import annotations

from PIL import Image


def discover_view_panels(original: Image.Image) -> list[tuple[str, tuple[int, int, int, int]]]:
    """Return source-coordinate crops for separated view panels and support row.

    A conservative false-negative is preferable to inventing a view layout.
    The calling vision router has already checked for sheet-like context.
    """
    width, height = original.size
    if width < 600 or height < 400 or width < height * 1.15:
        return []
    small = original.copy()
    small.thumbnail((420, 420), Image.Resampling.BILINEAR)
    sw, sh = small.size
    pix = small.convert("RGB").load()

    def ink(x: int, y: int) -> bool:
        red, green, blue = pix[x, y]
        return min(red, green, blue) < 175 or max(red, green, blue) - min(red, green, blue) > 70

    # A central cross-section avoids titles, lower swatches and view captions.
    sample_y = range(round(sh * .28), round(sh * .56), 2)
    projection = [sum(ink(x, y) for y in sample_y) / max(1, len(sample_y))
                  for x in range(sw)]
    smoothed = [
        sum(projection[max(0, x - 2):min(sw, x + 3)]) /
        (min(sw, x + 3) - max(0, x - 2)) for x in range(sw)
    ]
    runs = []
    begin = None
    for x, density in enumerate(smoothed + [0.0]):
        if density > .12 and begin is None:
            begin = x
        elif density <= .12 and begin is not None:
            runs.append((begin, x))
            begin = None
    merged: list[list[int]] = []
    for lo, hi in runs:
        if merged and lo - merged[-1][1] <= max(2, round(sw * .008)):
            merged[-1][1] = hi
        else:
            merged.append([lo, hi])
    spans = [(lo, hi) for lo, hi in merged if hi - lo >= sw * .075]
    if not 3 <= len(spans) <= 6:
        return []
    if sum(hi - lo for lo, hi in spans) < sw * .38:
        return []
    if any(spans[i + 1][0] - spans[i][1] < sw * .01
           for i in range(len(spans) - 1)):
        return []

    # Locate an actual whitespace separator before a lower reference row.
    row_density = []
    x_samples = list(range(round(sw * .13), round(sw * .87), 3))
    for y in range(round(sh * .60), round(sh * .83)):
        row_density.append((y, sum(ink(x, y) for x in x_samples) /
                            max(1, len(x_samples))))
    blanks = []
    begin = None
    for y, density in row_density + [(round(sh * .83), 1.0)]:
        if density < .025 and begin is None:
            begin = y
        elif density >= .025 and begin is not None:
            if y - begin >= sh * .014:
                blanks.append((begin, y))
            begin = None
    candidates = [(lo, hi) for lo, hi in blanks
                  if .665 <= (lo + hi) / (2 * sh) <= .8]
    separator = (min(candidates, key=lambda z: abs((z[0] + z[1]) / (2 * sh) - .72))
                 if candidates else None)
    lower_ink = [ink(x, y) for y in range(round(sh * .83), round(sh * .95), 3)
                 for x in x_samples]
    has_footer = (separator is not None and bool(lower_ink)
                  and sum(lower_ink) / len(lower_ink) > .06)
    upper_end = (round((separator[0] + separator[1]) / 2)
                 if has_footer else round(sh * .81))
    upper_start = round(sh * .10)
    if upper_end - upper_start < sh * .4:
        return []

    # Boundaries follow observed white gutters rather than uniform columns.
    boundaries = [max(0, spans[0][0] - round(sw * .022))]
    boundaries.extend(round((left[1] + right[0]) / 2)
                      for left, right in zip(spans, spans[1:]))
    boundaries.append(min(sw, spans[-1][1] + round(sw * .022)))
    result = []
    for index, (lo, hi) in enumerate(zip(boundaries, boundaries[1:]), 1):
        result.append((f"View panel {index}",
                       (round(width * lo / sw), round(height * upper_start / sh),
                        round(width * hi / sw), round(height * upper_end / sh))))
    if has_footer:
        result.append(("Supporting reference panels",
                       (round(width * .02), round(height * upper_end / sh),
                        round(width * .98), round(height * .98))))
    return result
