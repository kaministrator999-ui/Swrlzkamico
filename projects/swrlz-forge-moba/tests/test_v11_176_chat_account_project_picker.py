"""Focused v11.176 text/behavior contract after actual ordered engine build."""
import sys
from pathlib import Path
import re
p=Path(sys.argv[1])
source=p.read_text(encoding="utf-8")
expected=[
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_176_CHAT_ACCOUNT_PROJECT_PICKER',
 "se176AccountState(payload);",
 "se176Install();",
 "se176PaintPicker();",
 "se176LoadSelection",
 "se176RefreshProjects",
 "se176NativeName",
 'id="seChatProjects"',
 'seChatSignIn',
 'Saved to Google account',
 'On this device',
 'Editing now · '
]
for item in expected:assert item in source,item
assert source.count("se176Install();")>=1
assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_175_CHAT_PROJECT_WORKFLOW" not in source
assert "se176AccountState({authenticated:false});" in source
assert "se176RefreshProjects();return;" in source
assert "selectedProject.startsWith('cloud:')" in source
assert "return await se175LoadLocal()" not in source
print("PASS §E v11.176 account and project picker build contract",len(source.encode("utf-8")))
