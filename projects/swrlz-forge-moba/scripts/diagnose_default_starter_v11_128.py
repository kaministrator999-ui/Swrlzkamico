"""Diagnose actual starter-project picker and boot restore from sealed HTML."""
from pathlib import Path
import re
s=Path('/tmp/se127-base/index.html').read_text()
for token in ['function createProjectFromTemplate(', 'function showProjectTemplates(', 'Project Templates','projectTemplates','projectHub','function loadProject(', 'function restore','localStorage.getItem', 'function initializeHistory(',"'DOMContentLoaded'",'window.addEventListener(\'load\'','function boot(']:
 print('SE128_TOKEN',repr(token),s.count(token),flush=True)
 for match in list(re.finditer(re.escape(token),s))[:3]:
  p=match.start();print('SE128_CONTEXT',repr(token),'offset',p,repr(s[max(0,p-1100):p+3300]),flush=True)
