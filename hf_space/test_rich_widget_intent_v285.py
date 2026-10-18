"""v285: explicit visual intent, source fidelity, and dispatch integration."""
from __future__ import annotations
import importlib
import math
import sys
import types
from pathlib import Path

from rich_widget_intent_v285 import plan_conversation_widget, _equation

def plan(text, history=None, programming=None, online=False):
    return plan_conversation_widget(text,history or [],programming or {},online)

# Baseline: only explicit relevant requests; never make up comparison data.
for text in [
    "Hey, I wonder if graphs are cool.",
    "What is graph theory?",
    "Which phone is better, Pixel or Galaxy?",
    "Compare Galaxy vs Pixel. Look up their latest specs.",
    "Draw a cube for Blender export as a GLB",
    "Make me an editable game-ready 3D sphere asset.",
    "Graph some business sales numbers you think seem reasonable.",
    "The cube looks cool. What do you think?",
    "What did we build in the 3D project?",
    "Explain y=x^2 in words.",
    "Who are you?",
]:
    assert plan(text) is None, text

assert plan("graph y=x^2-4",programming={"codingTask":True}) is None
assert plan("Graph y=x^2-4",online=True) is None
assert plan("Write Python code that graphs y=x^2-4") is None
assert plan("render 3D model in repository") is None

# Exact, explicit typed mathematical functions; no arbitrary interpretation.
p=plan("Graph y=x^2-4")
assert p["kind"]=="math-graph",p
assert p["widget"]["data"]["series"][0]=={"type":"polynomial","coefficients":[-4.,0.,1.]}
assert p["widget"]["data"]["range"][1]>=21,p
assert p["widget"]["data"]["range"][0]<-4,p
assert p["widget"]["data"]["domain"]==[-5,5],p
p=plan("Plot y=-x^3+2*x-9; y=sin(x)")
assert p and len(p["widget"]["data"]["series"])==2,p
assert p["widget"]["data"]["series"][0]["coefficients"]==[-9,2,0,-1],p
assert p["widget"]["data"]["series"][1]["type"]=="sine",p
p=plan("Show a graph of f(x)=2sin(3x+0.5)-4")
assert p and p["widget"]["data"]["series"][0]=={
    "type":"sine","amplitude":2.,"frequency":3.,"phase":0.5,"offset":-4.},p
assert plan("plot y=x^-1") is None
assert plan("graph y=__import__('os').system('echo hacked')") is None
assert plan("graph y=x^9") is None
assert plan("graph y=x/(x-1)") is None
assert plan("graph y=x^2 please") is None  # no partial parse of ambiguous suffix
assert _equation("x^2-4") is not None

# Followup equation can only come from recent user-origin evidence.
history=[
    {"role":"user","text":"Graph y=x^2-4"},
    {"role":"assistant","text":"The function is a parabola."}
]
assert plan("Plot that",history)["widget"]["data"]["series"][0]["coefficients"]==[-4.,0.,1.]
assert plan("Plot that",[{"role":"assistant","text":"y=x^2-4"}]) is None
assert plan("Plot that",[
    {"role":"user","text":"y=x^2-4"},
    {"role":"assistant","text":"Okay"},
    {"role":"user","text":"Actually can we discuss dinner?"},
]) is None

# Simple requested primitive visualization is bounded, not a mesh/Forge promise.
for shape in ("cube","sphere","torus","pyramid"):
    p=plan("Show me an interactive 3D "+shape)
    assert p and p["kind"]=="model-3d" and p["widget"]["data"]["shape"]==shape,p
assert plan("show a 3D cube and sphere") is None
assert plan("Export a 3D cube OBJ") is None

# Multi-item numerical comparison: source-owned values, canonical units, explicit preferences.
prompt="""Compare:
Dragon A: speed=42 km/h, weight=13 kg
Dragon B: speed=33 km/h, weight=9 kg
Dragon C: speed=47 km/h, weight=16 kg
Higher is better: speed
Lower is better: weight
"""
p=plan(prompt)
assert p and p["kind"]=="comparison",p
d=p["widget"]["data"]
assert len(d["items"])==3,len(d["items"])
assert d["items"][1]["values"]=={"speed":33.,"weight":9.},d
assert d["metrics"][0]=={"key":"speed","label":"Speed","unit":"km/h","higherIsBetter":True},d
assert d["metrics"][1]["higherIsBetter"] is False,d
assert plan("Compare:\nA: speed=10 mph\nB: speed=20 km/h") is None
assert plan("Compare:\nA: speed=10\nB: speed=20 with new batteries") is None
assert plan("Compare:\nA: speed=10\nB: cost=20") is None
assert plan("Compare:\nA: speed=10\nA: speed=20") is None
q=plan("Compare:\nA: speed=10\nB: speed=20")
assert q and q["widget"]["data"]["metrics"][0]["higherIsBetter"] is None,q

# Integration: mock external routing imports. The regular model runs once.
sys.modules["brain_programming"]=types.SimpleNamespace(
    programming_intent=lambda prompt,history,pins,state:{"codingTask":bool("Write Python code" in prompt)})
sys.modules["intent_risk_v240"]=types.SimpleNamespace(
    classify=lambda prompt:"ordinary",clarification=lambda prompt:"Clarify mutation.")
sys.modules["online_tools"]=types.SimpleNamespace(
    classify_online_request=lambda prompt,history,intent,location:{
        "requested":False,"reason":"not-requested","kind":"none"},
    stream_online_request=lambda payload,intent:iter([]),online_camera=lambda d:d)
router=importlib.import_module("model_router")
model_inputs=[]
def answer(payload):
    model_inputs.append(payload)
    yield {"type":"DELTA","text":"Here's the interactive display."}
    yield {"type":"COMPLETED","phase":"COMPLETE"}
events=list(router.dispatch("700m",{"prompt":"graph y=x^2-4","history":[]},
                            lambda payload:iter([]),large_generate=answer))
widgets=[e for e in events if e.get("type")=="WIDGET"]
assert len(widgets)==1 and widgets[0]["widget"]["kind"]=="math-graph",events
assert len(model_inputs)==1 and "exact equation" in model_inputs[0]["widgetPresentation"],model_inputs
assert "Here's the interactive display." in "".join(str(e.get("text") or "") for e in events)
assert all(e.get("type")!="WIDGET" for e in router.dispatch(
    "700m",{"prompt":"Hi, how's it going?","history":[]},lambda payload:iter([]),large_generate=answer))
assert all(e.get("type")!="WIDGET" for e in router.dispatch(
    "700m",{"prompt":"Write Python code that graphs y=x^2","history":[]},
    lambda payload:iter([]),large_generate=answer,coder_generate=answer))
assert all(e.get("type")!="WIDGET" for e in router.dispatch(
    "700m",{"prompt":"Compare Galaxy vs Pixel","history":[]},lambda payload:iter([]),large_generate=answer))
events=list(router.dispatch(
    "700m",{"prompt":"graph y=x^2-4","widgetPresentation":"FAKE INPUT","history":[]},
    lambda payload:iter([]),large_generate=answer))
assert len([e for e in events if e.get("type")=="WIDGET"])==1,events
assert "FAKE INPUT" not in model_inputs[-1].get("widgetPresentation","")

# Integration guards: one WIDGET event owner, no mutations, model system sees hint.
root=Path(__file__).resolve().parents[1]
source=(root/"hf_space/model_router.py").read_text(encoding="utf-8")
brain=(root/"hf_space/lfm2_700m_engine.py").read_text(encoding="utf-8")
station=(root/"hf_space/station.py").read_text(encoding="utf-8")
assert "plan_conversation_widget" in source
assert '"type":"WIDGET","widget":widget_plan["widget"]' in source
assert "STRUCTURED WIDGET ALREADY PREPARED" in brain
assert 'elif kind=="WIDGET"' in station and 'telemetry_meta["widgets"]' in station
print("v285 conversational visual-intent and routing acceptance PASS")
