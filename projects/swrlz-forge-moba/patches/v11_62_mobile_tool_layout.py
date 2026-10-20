"""§E v11.62 governed mobile layout, preserving native tool/state authority."""
from pathlib import Path
import json,runpy
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_LAYOUT'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def scene(html):
    assert html.count(CANONICAL)==1
    src=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(src)
    return src[:end]
def apply(html):
    assert html.count(OLD)==1,'Incorrect input release marker'
    orig=scene(html)
    preview=Path(__file__).with_name('v11_62_mobile_tool_layout_preview.py')
    updated=runpy.run_path(str(preview))['apply'](html)
    for before,after in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.61','ENGINE · MAKER v11.62'),
      ('v11.61 · adaptive Model Atelier tools','v11.62 · mobile adaptive Model Atelier tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.61'","window.SWRLZ_FORGE_BUILD={version:'v11.62'"),
      ('<title>§wyrl§ Engine · Maker v11.61</title>','<title>§wyrl§ Engine · Maker v11.62</title>'),
    ):
        assert updated.count(before)==1,(before,updated.count(before))
        updated=updated.replace(before,after,1)
    assert scene(updated)==orig,'Original 283-part canonical scene was modified'
    assert updated.count(NEW)==1
    assert updated.count('function atelierMobileLayoutInstall()')==1
    return updated
