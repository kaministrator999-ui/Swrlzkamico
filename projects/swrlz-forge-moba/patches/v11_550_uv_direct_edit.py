"""Append direct UV editing to the native UV preview during source assembly."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(html):
    source=(ROOT/'runtime/model_atelier_uv_preview_v11_356.js').read_text('utf8')
    a=source.index('/* SE UV direct edit:')
    b=source.index('const se356BaseEnsurePanel=ensurePanel;',a)
    editor=source[a:b]
    marker='const se356BaseEnsurePanel=ensurePanel;'
    assert html.count(marker)==1,('native UV preview anchor',html.count(marker))
    html=html.replace(marker,editor+'\n'+marker,1)
    old="""  viewport.addEventListener('pointerdown',se356UVPick3D,true);
 }
 se356UVPreviewSchedule();
}"""
    new=old.replace(' se356UVPreviewSchedule();',' se356EditInstall();\n se356UVPreviewSchedule();')
    assert html.count(old)==1,('native UV install anchor',html.count(old))
    html=html.replace(old,new,1)
    return html
