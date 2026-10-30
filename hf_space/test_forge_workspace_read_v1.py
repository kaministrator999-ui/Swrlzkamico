"""Authorized native workspace analysis is read-only and grounded in the active bounded snapshot."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from brain_forge import classify_forge_intent,inspection_text
PROMPT="Analyze the current §E project and workspace. Inspect its actual active level, selected object, object types, scene organization and bounded metadata findings. Suggest useful next checks and improvements. This is read-only: do not modify any objects."
assert classify_forge_intent(PROMPT)["disposition"]=="read"
snapshot={"project":{"name":"Sheep Tag","sourceStarterId":"sheep-tag"},"workspace":"scene","activeLevel":{"id":"menu","name":"Main Menu"},"selectedId":"sheep","dirty":True,"totalActors":4,"actors":[{"id":"sheep","name":"Menu sheep","type":"character"},{"id":"wolf","name":"Menu wolf","type":"character"}],"workspaceAudit":{"sampled":4,"types":[{"name":"character","count":2},{"name":"wall","count":2}],"findings":[{"code":"duplicate-name","detail":"Two inspected objects share the name Menu wall."}]}}
answer=inspection_text(snapshot)
for s in ["Sheep Tag","Main Menu","Selected:","4 scene actors","character","Menu wall","No objects were modified","metadata checks only"]:
    assert s in answer,s
for prompt in ["Analyze current §E workspace","Audit the current scene","Review the current §E project"]:
    assert classify_forge_intent(prompt)["disposition"]=="read",prompt
for prompt in ["Move the selected actor","Create a project from the Blank scene starter named exactly \"Test\""]:
    assert classify_forge_intent(prompt)["disposition"]!="read",prompt
assert "Two inspected objects" not in inspection_text({**snapshot,"workspaceAudit":{}})
assert classify_forge_intent("Review this Python source code")["disposition"]=="ordinary"
print("PASS bounded §E workspace read and audit intent")
