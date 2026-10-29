"""Governed §E v11.59 precision Model Atelier production release.

The verified cumulative preview's historical title substitution was broad.
Restore the exact original serialized canonical scene, not just JSON equality,
before sealing the v11.59 binary; the user's model data must remain identical.
"""
from pathlib import Path
import json
import runpy

PREVIEW_MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW"
RELEASE_MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER"
CANONICAL = "const MODEL_ATELIER_CANONICAL_PROJECT="

def _canonical_source(html):
    assert html.count(CANONICAL)==1,"Canonical model declaration must be unique"
    source=html.split(CANONICAL,1)[1]
    lead=len(source)-len(source.lstrip())
    value,end=json.JSONDecoder().raw_decode(source.lstrip())
    return CANONICAL+source[:lead+end],value

def apply(html):
    original,original_model=_canonical_source(html)
    source=Path(__file__).resolve().with_name("v11_21_vertex_sphere_brush_preview.py")
    result=runpy.run_path(str(source))["apply"](html)
    assert result.count(PREVIEW_MARKER)==1
    result=result.replace(PREVIEW_MARKER,RELEASE_MARKER,1)
    assert result.count("Maker v11.21 preview")>=1
    result=result.replace("Maker v11.21 preview","Maker v11.59")
    changed,changed_model=_canonical_source(result)
    # Never let the historical preview's global text substitution mutate the
    # author-owned original scene data (even embedded metadata strings).
    result=result.replace(changed,original,1)
    authoritative,restored_model=_canonical_source(result)
    assert authoritative==original and restored_model==original_model

    # Only the live UI/build badge changes. The embedded canonical scene's
    # engine/version remain byte-for-byte historical for old save compatibility.
    for old, new in (
        ("ENGINE · MAKER v11.20", "ENGINE · MAKER v11.59"),
        ("v11.20 · anatomical head studio", "v11.59 · precision Model Atelier"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.20'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.59'"),
    ):
        assert result.count(old) == 1, "Expected one old live editor label: " + old
        result = result.replace(old, new, 1)
        assert result.count(new) == 1, "New release label missing or duplicated: " + new
    final_canonical, final_model = _canonical_source(result)
    assert final_canonical == original and final_model == original_model
    assert result.count(RELEASE_MARKER)==1
    assert "<title>§wyrl§ Engine · Maker v11.59</title>" in result
    return result
