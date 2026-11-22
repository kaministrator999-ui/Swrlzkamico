"""§E v11.538 — native immersive sculpt performance, hover envelope, starter handoff."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_537_ROBOTIC_HUMANOID_MANNEQUIN'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_538_IMMERSIVE_SCULPT_LOAD'

def once(s, before, after, label):
    n=s.count(before)
    if n!=1: raise AssertionError(('se538',label,n,before[:90]))
    return s.replace(before,after,1)

def section(s, start, end, func):
    a=s.index(start);b=s.index(end,a+len(start))
    return s[:a]+func(s[a:b])+s[b:]

def apply(html):
    assert OLD in html and 'SE531_QUEST_MENU_GIZMO_ACCOUNT_END' in html
    runtime=(ROOT/'runtime/model_vr_sculpt_preview_v11_538.js').read_text('utf8')
    assert 'SE538_IMMERSIVE_SCULPT_REPAIR_END' in runtime
    html=once(html,'/* SE531_QUEST_MENU_GIZMO_ACCOUNT_END */',
        '/* SE531_QUEST_MENU_GIZMO_ACCOUNT_END */\n'+runtime,
        'single native XR runtime layer')

    def optimize(s):
        old="""    const a = g.preview.attributes.position;
    let affected = 0, changed = false;
    for (let i = 0; i < a.count; i++) {
      const xyz = [a.getX(i), a.getY(i), a.getZ(i)];
      if (g.maskWeights) for (let k = 0; k < 3; k++) xyz[k] = previous[i * 3 + k] + (xyz[k] - previous[i * 3 + k]) * g.maskWeights[i];
      for (let k = 0; k < 3; k++) xyz[k] = Math.min(g.before[i * 3 + k] + .49999, Math.max(g.before[i * 3 + k] - .49999, xyz[k]));
      a.setXYZ(i, ...xyz);
      if (xyz.some((n, k) => Math.abs(n - g.before[i * 3 + k]) > 1e-7)) { affected++; changed = true; }
    }
"""
        new="""    // SE538: typed-array in-place mask/clamp, no per-vertex arrays,
    // spreading or closures in the high-frequency immersive sculpt path.
    const a = g.preview.attributes.position, raw = a.array, base = g.before;
    const weights = g.maskWeights;
    let affected = 0, changed = false;
    for (let i = 0, j = 0; i < a.count; i++, j += 3) {
      let x = raw[j], y = raw[j + 1], z = raw[j + 2];
      if (weights) {
        const w = weights[i];
        x = previous[j] + (x - previous[j]) * w;
        y = previous[j + 1] + (y - previous[j + 1]) * w;
        z = previous[j + 2] + (z - previous[j + 2]) * w;
      }
      x = Math.min(base[j] + .49999, Math.max(base[j] - .49999, x));
      y = Math.min(base[j + 1] + .49999, Math.max(base[j + 1] - .49999, y));
      z = Math.min(base[j + 2] + .49999, Math.max(base[j + 2] - .49999, z));
      raw[j] = x; raw[j + 1] = y; raw[j + 2] = z;
      if (Math.abs(x - base[j]) > 1e-7 ||
          Math.abs(y - base[j + 1]) > 1e-7 ||
          Math.abs(z - base[j + 2]) > 1e-7) { affected++; changed = true; }
    }
"""
        s=once(s,old,new,'stroke typed-array update')
        old="""    for (let i = 0; i < a.count; i++) {
      const delta = [a.getX(i), a.getY(i), a.getZ(i)].map((n, k) => n - g.before[i * 3 + k]);
      if (delta.every(n => Math.abs(n) <= 1e-7)) continue;
      indices.push(i); moves.push(delta); if (indices.length === 256) flush();
    }
"""
        new="""    // SE538: avoid 20K+ short-lived arrays while committing sparse edits.
    const raw = a.array, base = g.before;
    for (let i = 0, j = 0; i < a.count; i++, j += 3) {
      const dx = raw[j] - base[j], dy = raw[j + 1] - base[j + 1],
        dz = raw[j + 2] - base[j + 2];
      if (Math.abs(dx) <= 1e-7 && Math.abs(dy) <= 1e-7 &&
          Math.abs(dz) <= 1e-7) continue;
      indices.push(i); moves.push([dx,dy,dz]);
      if (indices.length === 256) flush();
    }
"""
        return once(s,old,new,'sparse commit typed array')
    html=section(html,'/* SE350_MODEL_VR_SURFACE_START',
         '/* SE350_MODEL_VR_SURFACE_END',optimize)

    def register(s):
        # Previous starter cards were registered in the 2D UI but not the
        # authenticated immersive library's independent native starter index.
        start=s.index('const se175StarterKinds={')
        stop=s.index('};',start)
        block=s[start:stop]
        extra=[]
        for key,name in [('sorting-hat','Sorting Hat'),
          ('sorting-hat-sculpted','Sculpted Sorting Hat'),
          ('smooth-witch-hat','Smooth Witch Hat'),
          ('robotic-humanoid-mannequin','Robotic Humanoid Mannequin')]:
            if "'"+key+"':" not in block:
                extra.append(" '"+key+"':['"+name+"','model-atelier','model-atelier']")
        if extra:
            s=s[:stop].rstrip()+",\n"+",\n".join(extra)+"\n"+s[stop:]
        return s
    html=section(html,'const se175StarterKinds={',
      '// Starter definitions keep their native canonical identity',register)

    for before,after in (
      (OLD,MARKER),
      ('ENGINE · MAKER v11.537','ENGINE · MAKER v11.538'),
      ('v11.537 · robotic humanoid T-pose mannequin',
       'v11.538 · responsive immersive sculpt and VR project loading'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.537'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.538'"),
      ('<title>§wyrl§ Engine · Maker v11.537</title>',
       '<title>§wyrl§ Engine · Maker v11.538</title>'),
    ):
        html=once(html,before,after,'release identity')
    before=" source.engine='§wyrl§ Engine · Maker v11.537';source.version=11.537;"
    assert html.count(before)==5,('v538 project provenance',html.count(before))
    html=html.replace(before,
      " source.engine='§wyrl§ Engine · Maker v11.538';source.version=11.538;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[])
                      if x.get('version')!='v11.537']
    notes['history'].insert(0,{'version':'v11.537',
       'changes':notes.get('changes',[])})
    notes.update(version='v11.538',date='2026-11-22',
      title='Responsive immersive sculpt and project loading',
      changes=[
       'Replace the flat immersive sculpt ring with a pooled translucent strength dome, pointer selector and capped real-mesh falloff wire overlay. No stored geometry is changed on hover.',
       'Limit expensive precise sculpt sampling to approximately 30Hz with accumulated time, remove per-vertex allocations in hot update and sparse commit loops, and expose non-production timing counters.',
       'Crop blank space from existing grouped VR Sculpt parameter UI, preserve original native action targets and left-hand menu architecture.',
       'Keep the WebXR session alive while native project switching temporarily releases the borrowed model root, and register the existing Sorting Hat, Sculpted Sorting Hat, Smooth Witch Hat and humanoid starters in the VR project library.',
       'Retain model source, UV/paint, native sketch/rig/project undo and cloud ownership; physical Meta Quest performance acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(',',':')).replace('</',r'<\/')+html[at+n:]
