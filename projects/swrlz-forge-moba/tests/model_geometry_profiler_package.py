#!/usr/bin/env python3
"""§E v11.20 profiler source-integration contract; run after built package."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',required=True);args=p.parse_args()
root=Path(__file__).resolve().parent.parent
dist=Path(args.package)
html=(dist/'index.html').read_text('utf-8')
source=(root/'runtime/model_atelier_metrics_v11_10.js').read_text('utf-8')
m=json.loads((root/'source-manifest.json').read_text('utf-8'))
assert m['patches'][-1]=='patches/v11_61_context_workbench.py'
for key in ('V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH','modelAtelierMetricsBody','modelAtelierMetricsExport',
            'function atelierGeometryStats(){','refreshModelMetrics();'):
    assert key in html,key
assert 'CPU buffers only' in html
assert 'function atelierGeometryStats(){' in source
assert 'triangles=Math.floor(count/3)' in source
assert 'floor' not in source.split('function atelierGeometryStats(){')[1].split('function refreshModelMetrics(){')[0] or 'selection helpers' in source
receipt=json.loads((dist/'SOURCE.json').read_text('utf-8'))
assert receipt['patches']==m['patches']
assert hashlib.sha256(html.encode()).hexdigest()==m['finalSha256']==receipt['finalSha256']
assert len(html.encode())==m['finalBytes']==receipt['finalBytes']
print('MODEL_GEOMETRY_PROFILER_SOURCE_PASS')
