"""§E v11.438 — nonblocking NPC route worker / engine frame diagnostics.

No new renderer loop, no headset pose changes, no LAN authority modifications.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_438_RENDER_SIMULATION_BRIDGE'

def one(s,old,new,label):
    n=s.count(old)
    assert n==1,('v11.438',label,n,old[:140])
    return s.replace(old,new,1)

def apply(html):
    source=(ROOT/'runtime/engine_simulation_render_bridge_v11_438.js').read_text('utf-8')
    assert 'SE438_ENGINE_SIMULATION_RENDER_BRIDGE_START' in source
    assert 'setAnimationLoop(' not in source and 'requestAnimationFrame(' not in source
    start=html.index('stMoveUnit = function(unit,target,dt) {')
    end=html.index('function stLanesSheepApproach(',start)
    block=html[start:end]
    # The standard AI path search in the v11.419 congestion-aware movement
    # branch is a pure numeric A* computation and can use the worker. Alternate
    # lane recovery, user movement, physical collisions and multiplayer retain
    # the original guarded implementation.
    block=one(block,'stPath(unit.pos,aim,radius)',
       'se438Route(unit,unit.pos,aim,radius)','native AI movement route')
    html=html[:start]+block+html[end:]
    html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
       source+'\ninstallPerformanceSettings();se189InstallPerfUI();',
       'shared render and simulation runtime')
    # Correct the v11.437 diagnostics exposure in the resulting new build,
    # without rewriting the sealed historical patch.
    html=one(html,'window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_436=',
       'window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_437=','capture diagnostics identifier')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_437_SHEEP_TERRITORY_CAPTURE',MARKER),
      ('ENGINE · MAKER v11.437','ENGINE · MAKER v11.438'),
      ('v11.437 · independent sheep territories and smoother capture',
       'v11.438 · nonblocking AI paths and frame diagnostics'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.437'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.438'"),
      ('<title>§wyrl§ Engine · Maker v11.437</title>',
       '<title>§wyrl§ Engine · Maker v11.438</title>')
    ]:
        html=one(html,old,new,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.437';source.version=11.437;"
    assert html.count(old)==5,('v11.438 provenance',html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.438';source.version=11.438;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,
       {'version':'v11.437','changes':notes.get('changes',[])})
    notes.update(version='v11.438',date='2026-11-13',
       title='Engine-render continuity: nonblocking solo VR NPC route searches',
       changes=[
         'Solo Quest NPC primary A* paths now run on a bounded Web Worker with numeric navigation snapshots. Only matching live session/navigation/target results apply; game movement and collision still run in the native simulation.',
         'The native WebXR renderer, headset tracking, rendering loop, player movement, simulation and LAN match authority are unchanged. If a Worker is unsupported or unavailable, the existing native route solver runs.',
         'A shared engine diagnostic records simulation CPU cost, render submission CPU cost, visible XR callback gaps, worker completions, stale replies and queue pressure, without extra timers or another render loop.',
         'Existing Sheep Tag scene batching, editor shadow cache, AI congestion budgets, independent home territories, spirit prewarming and Model Studio tools remain intact. The captured-sheep diagnostic is correctly exposed with its v11.437 name.',
         'This separates the expensive pure NPC A* job, not every game-logic operation or the GPU compositor. Physical Quest capture and long-session tests are still required.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
