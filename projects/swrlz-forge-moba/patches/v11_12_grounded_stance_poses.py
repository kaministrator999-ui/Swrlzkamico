"""§E v11.12: replace rubber-leg preset logic after owner multi-angle screenshot rejection."""
from pathlib import Path

def once(src,old,new):
    count=src.count(old)
    if count!=1: raise AssertionError(f'v11.12 expected exactly one anchor {old[:70]!r}; got {count}')
    return src.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    previous=(root/'runtime/model_atelier_pose_frames_v11_11.js').read_text('utf8')
    old=previous[previous.index('function atelierBendNativeLeg('):previous.index('function atelierApplySavedPose(')]
    new=(root/'runtime/model_atelier_grounded_poses_v11_12.js').read_text('utf8')
    assert 'V11_12_GROUNDED_STANCE_POSES' in new
    html=once(html,old,new+'\n')
    # UI labels reflect grounded asymmetric support rather than exaggerated bending.
    html=once(html,"['idle','Relaxed idle · bent knees']","['idle','Relaxed idle · planted stance']")
    html=once(html,"['victory','Victory · right knee']","['victory','Victory · right-foot stance']")
    html=once(html,"['victory-b','Victory B · left knee']","['victory-b','Victory B · left-foot stance']")
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_11_FACE_POSE_FRAMES',
                  'SWYRL_ENGINE_DEPLOY_MARKER: V11_12_GROUNDED_STANCE_POSES')
    html=html.replace('Maker v11.11','Maker v11.12').replace('MAKER v11.11','MAKER v11.12')
    html=html.replace("version:'v11.11'","version:'v11.12'").replace('version:11.11','version:11.12')
    html=once(html,'v11.11 · expressive face and pose frame studio','v11.12 · grounded anatomical pose studio')
    return html
