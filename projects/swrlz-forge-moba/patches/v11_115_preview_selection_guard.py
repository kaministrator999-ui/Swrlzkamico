"""§E v11.115: guard precision-preview selection and whole-mesh transforms."""
from pathlib import Path
import hashlib,json

def once(src,old,new):
    n=src.count(old)
    assert n==1,(old[:120],n)
    return src.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    runtime=(root/'runtime/model_atelier_precision_preview_guard_v11_115.js').read_text(encoding='utf8')
    html=once(html,'function atelierSculptGhostInstall(){',
      runtime+'\nfunction atelierSculptGhostInstall(){')
    html=once(html,' atelierPrecisionGizmoInstall();\n',
      ' atelierPrecisionGizmoInstall();\n atelierPrecisionGuardInstall();\n')
    html=once(html,
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_114_CIRCLE_VIEWPORT_HANDLES',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_115_SAFE_PRECISION_PREVIEW_SELECTION')
    for old,new in [
      ('ENGINE · MAKER v11.114','ENGINE · MAKER v11.115'),
      ('v11.114 · radius/depth viewport handles','v11.115 · safe precision preview selection'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.114'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.115'"),
      ('<title>§wyrl§ Engine · Maker v11.114</title>',
       '<title>§wyrl§ Engine · Maker v11.115</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='No stranded second sphere: safe precision cut preview selection',
      date='2026-10-24',changes=[
       'Ensure temporary holed-sphere previews are cleared automatically whenever the real editable part is rebuilt, selected, transformed or Undone.',
       'Block accidental Move/Rotate/Scale gizmo drag and quick-strip +/- nudges while the non-destructive precision cut preview is on-screen.',
       'Tapping a temporary holed mesh now reselects the original editable part rather than leaving an unselectable visual duplicate.',
       'Label cut previews as unsaved; clarify that orange Radius and violet Depth handles edit the hole while Mesh tools transform the whole part.',
       'Preserve existing sculpt brushes, 146 prior patches, 68 assets, source geometry, numeric gizmos, owner-controlled Apply and Undo.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V11115_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
