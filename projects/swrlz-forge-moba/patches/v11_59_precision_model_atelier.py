"""Governed §E v11.59 precision Model Atelier production release.

Assembles the validated v11.21–v11.59 native editor tools atop the sealed
v11.20 anatomical starter, without replacing or rewriting historical assets.
"""
from pathlib import Path
import runpy

PREVIEW_MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW"
RELEASE_MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER"

def apply(html):
    source=Path(__file__).resolve().with_name("v11_21_vertex_sphere_brush_preview.py")
    result=runpy.run_path(str(source))["apply"](html)
    assert result.count(PREVIEW_MARKER)==1
    result=result.replace(PREVIEW_MARKER,RELEASE_MARKER,1)
    assert result.count("Maker v11.21 preview")==1
    result=result.replace("Maker v11.21 preview","Maker v11.59",1)
    assert result.count(RELEASE_MARKER)==1
    assert "<title>§wyrl§ Engine · Maker v11.59</title>" in result
    return result
