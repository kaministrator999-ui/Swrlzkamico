"""v286 live-Android regression: prepared widgets succeeded but 700M prose contradicted them."""
from __future__ import annotations
import importlib
import sys
import types
from rich_widget_intent_v285 import plan_conversation_widget
from widget_companion_guard_v286 import grounded_companion,issues,guard_widget_companion

def prepared(text):
    p=plan_conversation_widget(text,[],{"codingTask":False},False)
    assert p and p["widget"],text
    return p["widget"]

torus=prepared("Show me an interactive 3D torus")
graph=prepared("Graph y=x²−4")
compare=prepared("""Compare:
Dragon A: speed=42 km/h, weight=13 kg
Dragon B: speed=33 km/h, weight=9 kg
Higher is better: speed
Lower is better: weight""")

# Live export (86) failure behaviors, expressed as nonprivate condensed regressions.
torus_bad=("Certainly! While I can't directly display 3D models in this chat interface, "
           "use Blender or Matplotlib instead.\n\n"
           "\x60\x60\x60python\nimport matplotlib.pyplot as plt\nplt.show()\n\x60\x60\x60")
graph_bad=("The graph of y=x^2-4 has vertex (0,-4). "
           "The parabola touches the x-axis at the vertex.")
compare_bad=("Dragon A is faster (42 km/h). Dragon B is lighter (9 kg). "
             "This comparison highlights that while Dragon B is faster, "
             "Dragon A is more efficient in terms of weight, making it a better choice. "
             "Final Ranking: Speed, Weight.")

assert "denies-visible-widget" in issues(torus_bad,torus)
assert "wrong-x-intercept" in issues(graph_bad,graph)
assert "reversed-comparative-claim" in issues(compare_bad,compare)
assert "unrequested-code-artifact" in issues(torus_bad,torus)

def events(text):
    return iter([{"type":"STATUS","phase":"GENERATING"},
                 {"type":"DELTA","text":text[:20]},
                 {"type":"DELTA","text":text[20:]},
                 {"type":"CANDIDATE_VALIDATION","validation":{"status":"PASS"}},
                 {"type":"COMPLETED","phase":"COMPLETE"}])

def guarded(widget,text):
    output=list(guard_widget_companion(events(text),widget))
    answer="".join(e.get("text","") for e in output if e.get("type")=="DELTA")
    phases=[e.get("phase") for e in output if e.get("type")=="STATUS"]
    assert output[-1]["type"]=="COMPLETED",output[-3:]
    return answer,phases,output

ans,phases,_=guarded(torus,torus_bad)
assert "interactive 3D torus" in ans and "Drag" in ans,ans
assert "can't directly display" not in ans and "matplotlib" not in ans.lower(),ans
assert "WIDGET_COMPANION_CORRECTED" in phases
ans,_,_=guarded(graph,graph_bad)
assert "(-2, 0)" in ans and "(2, 0)" in ans,ans
assert "vertex (0, -4)" in ans,ans
ans,_,_=guarded(compare,compare_bad)
assert "Speed: Dragon A 42 km/h, Dragon B 33 km/h; preferred: Dragon A." in ans,ans
assert "Weight: Dragon A 13 kg, Dragon B 9 kg; preferred: Dragon B." in ans,ans
assert "No overall winner" in ans
assert "Dragon B is faster" not in ans,ans

for widget,text in [
 (torus,"I've displayed your 3D torus wireframe. Rotate it by dragging the canvas."),
 (graph,"Here is the graph of y=x²−4, with vertex (0,-4)."),
 (compare,"Dragon A leads in speed, while Dragon B is lighter. The choice depends on priorities.")
]:
    ans,phases,_=guarded(widget,text)
    assert ans==text,(widget["kind"],ans)
    assert "WIDGET_COMPANION_CORRECTED" not in phases

assert not issues("Here's the interactive widget.",torus)
assert not issues("Graph displayed.",graph)
assert not issues("The measurements are above.",compare)

# The existing model router remains the only WIDGET compiler; no prose execution.
sys.modules["brain_programming"]=types.SimpleNamespace(
    programming_intent=lambda prompt,history,pins,state:{"codingTask":"Write Python code" in prompt})
sys.modules["intent_risk_v240"]=types.SimpleNamespace(
    classify=lambda prompt:"ordinary",clarification=lambda prompt:"Clarify.")
sys.modules["online_tools"]=types.SimpleNamespace(
    classify_online_request=lambda prompt,history,intent,loc:{
        "requested":False,"reason":"none","kind":"none"},
    stream_online_request=lambda payload,intent:iter([]),online_camera=lambda d:d)
router=importlib.import_module("model_router")
seen=[]
def model(payload):
    seen.append(payload)
    yield from events(torus_bad)
r=list(router.dispatch("700m",{"prompt":"Show me an interactive 3D torus","history":[]},
                       lambda payload:iter([]),large_generate=model))
assert len([x for x in r if x.get("type")=="WIDGET"])==1
assert "can't directly display" not in "".join(x.get("text","") for x in r if x.get("type")=="DELTA")
assert any(x.get("phase")=="WIDGET_COMPANION_CORRECTED" for x in r)
assert len(seen)==1,"Do not add second model attempt"

r=list(router.dispatch("700m",{"prompt":"How's your day?","history":[]},
                       lambda payload:iter([]),large_generate=model))
assert len([x for x in r if x.get("type")=="WIDGET"])==0
assert "".join(x.get("text","") for x in r if x.get("type")=="DELTA")==torus_bad
assert not any(x.get("phase")=="WIDGET_COMPANION_CORRECTED" for x in r)
print("v286 source-grounded companion acceptance PASS")
