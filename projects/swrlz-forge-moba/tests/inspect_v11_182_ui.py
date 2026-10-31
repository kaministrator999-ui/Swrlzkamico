from pathlib import Path
import re,json
s=Path('/tmp/se182-audit/index.html').read_text()
print('UI_AUDIT_SOURCE_CHARACTERS',len(s))
for key in ['class="topbar"','class="workspace"','id="projectHub"','id="hierarchy"','id="inspector"','class="mobile-tabs"','id="mobileDrawer"','id="modelAtelierPanel"','id="seChatAccountPanel"','id="se179VRStudio"','id="st141LevelBar"','id="engineMenubar"','id="se181XRStatus"']:
  i=s.find(key)
  print('UI_ANCHOR',key,i,repr(s[max(0,i-380):i+850])[:1400])
for key in ['.topbar{','.topbar {','.workspace{','.workspace {','.toolbar{','.toolbar {','#hierarchy{','#inspector{','#projectHub{','.project-hub{','@media(max-width:620px)','dialog{','#mobileDrawer','z-index:214748','z-index:3000']:
  matches=list(re.finditer(re.escape(key),s))
  print('UI_STYLE',key,'COUNT',len(matches))
  for m in matches[-3:]:print('UI_CSS_NEAR',m.start(),repr(s[max(0,m.start()-80):m.start()+440])[:560])
print('UI_AUDIT_END')
