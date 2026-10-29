"""§E v11.10 additive measured-geometry inspection; preserve every older native scene."""
from pathlib import Path

def once(html,old,new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(f"v11.10 profiler expected exactly one anchor: {old[:72]!r}, found {count}")
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    code=(root/'runtime/model_atelier_metrics_v11_10.js').read_text('utf-8')
    assert 'V11_10_MEASURED_GEOMETRY_PROFILER' in code
    html=once(html,"  function refreshList(){",code+"\n  function refreshList(){")
    html=once(html,"    const current=partById(selection);\n    if(current){","    refreshModelMetrics();\n    const current=partById(selection);\n    if(current){")
    html=once(html,'<p id="modelAtelierPartCount"></p>',
        '<p id="modelAtelierPartCount"></p><details id="modelAtelierMetrics"><summary>Measured model statistics</summary><div id="modelAtelierMetricsBody" aria-live="polite"></div><button id="modelAtelierMetricsExport" type="button">Export geometry statistics JSON</button></details>')
    html=once(html,"    action('Undo',()=>historyStep(true));",
        "    action('MetricsExport',()=>download('se-model-statistics.json',JSON.stringify(atelierGeometryStats(),null,2)+'\\n','application/json'));\n    action('Undo',()=>historyStep(true));")
    styles="""\n/* §E v11.10: compact measurable model statistics, inspector-local scroll. */
#modelAtelierMetrics{border:1px solid #49647d;border-radius:7px;padding:6px;color:#dbf4fc}
#modelAtelierMetrics summary{cursor:pointer;font-size:12px;font-weight:600}
#modelAtelierMetricsBody{display:grid;gap:3px;padding:7px 0;font-size:11px}
.atelier-metric-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.atelier-metric-row strong{font-variant-numeric:tabular-nums;text-align:right}
.atelier-metric-note{font-size:10px;opacity:.8}
#modelAtelierMetricsExport{font-size:11px;min-height:30px;width:100%}
"""
    html=once(html,'/* v11.8 procedural sculpt tools:',styles+'/* v11.8 procedural sculpt tools:')
    html=once(html,'V11_9_FERRET_FIGURE_ATELIER','V11_10_MEASURED_GEOMETRY_PROFILER')
    html=html.replace('Maker v11.9','Maker v11.10').replace('MAKER v11.9','MAKER v11.10')
    html=html.replace("version:'v11.9'","version:'v11.10'")
    html=html.replace('v11.9 · figure and piñata creature atelier',
                      'v11.10 · measured geometry and figure atelier')
    return html
