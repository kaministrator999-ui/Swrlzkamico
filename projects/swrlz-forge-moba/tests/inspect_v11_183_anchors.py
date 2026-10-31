from pathlib import Path
import re
s=Path('/tmp/se183-audit/index.html').read_text()
print('SE183_SCAN_BYTES',len(s))
terms=[
  r'function\s+loadProject\s*\(',r'function\s+loadStarter',r'function\s+loadTemplate',
  r'function\s+loadCloud\s*\(',r'async\s+function\s+loadCloud\s*\(',
  r'function\s+se175LoadLocal\s*\(',r'function\s+se170Refresh\s*\(',
  r'function\s+seLevelsSwitch\s*\(',r'function\s+seLevelsEnsureUI\s*\(',
  r'function\s+seLevelsRefresh\s*\(',r'function\s+applyProject',
  r'function\s+startProject',r'function\s+setStatus\s*\(',
  r'function\s+refreshStatus\s*\(',r'function\s+updateStatus',
  r'actors\s*[+.]',r'actors.*None',
  r'engine-stats-pill',r'badgeBox',r'<div class="statusbar"',
  r'\.engine-stats-pill\s*\{',r'\.badgeBox\s*\{',
  r'async\s+function\s+load',r'function\s+se175Read',
  r'function\s+loadProjectFrom',r'function\s+setProject',
]
for term in terms:
  hits=list(re.finditer(term,s,re.I))
  print('SE183_TERM',term,'COUNT',len(hits))
  for i,m in enumerate(hits[:3]):
    before=160 if 'function' not in term else 80
    after=2400 if 'function' in term else 650
    sn=s[max(0,m.start()-before):min(len(s),m.end()+after)]
    print('SE183_CONTEXT',term,'AT',m.start(),'NUM',i,repr(sn)[:3600])
print('SE183_DONE')
