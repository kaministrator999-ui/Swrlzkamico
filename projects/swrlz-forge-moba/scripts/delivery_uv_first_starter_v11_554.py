"""Delivery-only registration of a distinct UV-first model starter.

The original 526-patch engine remains SHA-sealed. This script injects a native
scene loader and its Starter Models card into the existing executable module,
with exact anchors, without modifying existing robot scenes or user saves.
"""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[1]
INSERT='window.SWRLZ_FORGE_BUILD='
CATEGORY=" const modelIds=new Set([\n  'robotic-humanoid-mannequin',"
CATEGORY_NEW=" const modelIds=new Set([\n  'clean-topology-humanoid',\n  'robotic-humanoid-mannequin',"
def once(text,old,new,label):
    count=text.count(old)
    if count!=1:
        raise ValueError(f'UV-first starter: {label} anchor expected once, got {count}')
    return text.replace(old,new,1)
def apply(module):
    text=module.decode('utf8')
    runtime=(ROOT/'runtime/clean_topology_humanoid_v11_554.js').read_text('utf8')
    for required in ('function se554Open(', 'function se554Install(',
        "loadProject(scene,{workspaceLocal:true})",
        "se232ActivateSelectedModelWorkspace()",
        'SE554_UV_FIRST_STARTER_END'):
        if required not in runtime:raise ValueError('UV-first native runtime missing '+required)
    text=once(text,INSERT,runtime+'\n'+INSERT,'root starter runtime')
    # UV controls require the private ModelAtelier lexical scope: se552Open,
    # se551Target, checkpoint, status, and signalEdited are not root globals.
    # Install after the existing UV hooks but before the ModelAtelier wrapper.
    uv_anchor='/* SE552_BIDIRECTIONAL_REGIONS_END */'
    uv_runtime=(ROOT/'runtime/uv_auto_unwrap_v11_555.js').read_text('utf8')
    text=once(text,uv_anchor,uv_anchor+'\n'+uv_runtime+'\n','ModelAtelier-scoped conformal UV tools')
    text=once(text,CATEGORY,CATEGORY_NEW,'native Starter Models category')
    if text.count('SE554_UV_FIRST_STARTER_END')!=1:raise ValueError('Starter module duplicated')
    if text.count('SE555_XATLAS_REAL_UNWRAP_END')!=1:raise ValueError('xatlas UV runtime missing')
    delivered=text.encode('utf8')
    return delivered,{
      'starter':'clean-topology-humanoid',
      'originalModuleSha256':hashlib.sha256(module).hexdigest(),
      'patchedModuleSha256':hashlib.sha256(delivered).hexdigest(),
      'quadBasedStarter':True,'oldRobotChanged':False,
      'nativeConformalUnwrap':True,'uvRuntimeScope':'ModelAtelier','seamEditor':True,'uvDistortionOverlay':True,
      'newScene':'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'}
