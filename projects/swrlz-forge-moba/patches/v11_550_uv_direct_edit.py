"""Append UV direct editing after the checksum-locked historical patch chain."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(html):
    editor=(ROOT/'runtime/uv_direct_edit_v11_550.js').read_text('utf8')
    anchor='const se356BaseEnsurePanel=ensurePanel;'
    assert html.count(anchor)==1,('UV editor insertion anchor',html.count(anchor))
    assert 'function se356EditInstall()' not in html,'UV editor already injected'
    html=html.replace(anchor,editor+'\n'+anchor,1)
    old="""  viewport.addEventListener('pointerdown',se356UVPick3D,true);
 }
 se356UVPreviewSchedule();
}"""
    assert html.count(old)==1,('UV install anchor',html.count(old))
    html=html.replace(old,old.replace(' se356UVPreviewSchedule();',' se356EditInstall();\n se356UVPreviewSchedule();'),1)
    assert html.count('function se356EditInstall()')==1
    assert html.count('se356EditInstall();')==1
    return html
