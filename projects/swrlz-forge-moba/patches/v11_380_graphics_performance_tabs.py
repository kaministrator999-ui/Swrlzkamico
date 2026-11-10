"""§E v11.380 — real browser graphics / WebXR settings in existing panel.

Append-only. Native AA remains an immutable renderer context capability, WebXR
owns stereo rendering; visual knobs are bounded, persisted, and measured.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_380_ADVANCED_GRAPHICS_PERFORMANCE_TABS'

def once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise AssertionError(('v11.380 missing/ambiguous anchor',label,count,old[:100]))
    return source.replace(old,new,1)

def apply(html):
    runtime=(ROOT/'runtime/engine_advanced_graphics_v11_380.js').read_text(encoding='utf8')
    css=(ROOT/'runtime/engine_advanced_graphics_v11_380.css').read_text(encoding='utf8')
    for token in ('se380InstallUI','se380ScanScene','se380ApplyFoveation',
                  'se380PreviousFramebuffer','SWYRL_ENGINE_ADVANCED_GRAPHICS_380'):
        if token not in runtime:raise AssertionError(('v11.380 missing runtime',token))
    for token in ('se379PreviousOnFrame=se211OnFrame',
                  'SWYRL_ENGINE_SHEEP_VR_CADENCE_379',
                  'const se195OriginalFramebuffer=se191XRPrepareFramebuffer;',
                  "const PERFORMANCE_PREF_KEY='swyrl.engine.performance.v1'",'function openPerformanceSettings()'):
        if token not in html:raise AssertionError(('v11.380 missing prerequisite',token))
    if '</head>' not in html or 'id="se380AdvancedGraphicsStyles"' in html:raise AssertionError('v11.380 head insertion invalid')
    html=html.replace('</head>','<style id="se380AdvancedGraphicsStyles">\n'+css+'\n</style>\n</head>',1)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=',
              'inject settings after renderer and native XR adapters')
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_379_SHEEP_VR_VISIBLE_FRAME_CADENCE',MARKER,'deploy marker'),
        ('ENGINE · MAKER v11.379','ENGINE · MAKER v11.380','header'),
        ('v11.379 · Sheep Tag VR visible-frame stability','v11.380 · advanced graphics and Quest performance','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.379'", "window.SWRLZ_FORGE_BUILD={version:'v11.380'",'runtime version'),
        ('<title>§wyrl§ Engine · Maker v11.379</title>',
         '<title>§wyrl§ Engine · Maker v11.380</title>','title')
    ]:
        html=once(html,old,new,label)
    provenance=" source.engine='§wyrl§ Engine · Maker v11.379';source.version=11.379;"
    if html.count(provenance)!=5:raise AssertionError(('v11.380 provenance',html.count(provenance)))
    html=html.replace(provenance," source.engine='§wyrl§ Engine · Maker v11.380';source.version=11.380;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.379' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.379','changes':notes.get('changes',[])})
    notes.update(version='v11.380',date='2026-11-10',
      title='Tabbed graphics performance controls and bounded WebXR optimizations',
      changes=[
        'Reorganize the same Graphics & Performance window into Graphics, Performance and VR tabs; retain existing presets, frame cap, Mobile Boost, render scale, FPS overlay and draw-call inspection without duplicate controls.',
        'Offer real browser FXAA as an optional full-screen post-process while preserving immutable hardware antialias settings and bypassing all FXAA inside WebXR stereo.',
        'Control texture anisotropy with hardware limits, authored LOD distance, and existing directional shadow coverage; never hide live gameplay actors to simulate LOD.',
        'Set WebXR foveation only if the runtime exposes support; distinguish requested settings from reported headset behavior.',
        'Allow Sheep Tag VR framebuffer-scale override at next session entry, preserving original preset-aware v11.379 defaults, and avoid mid-session stereo reallocations.',
        'Show actual capability and graphics diagnostics without claiming measured GPU completion or magically raising the Quest refresh rate.',
        'Settings persist locally; real physical Quest 2, handset and desktop visual acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
