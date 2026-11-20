#!/usr/bin/env python3
"""No model load or personal data: regression for §C 1.1.43 image streaming."""
from __future__ import annotations
import base64, io, importlib.util, sys, threading, time, types
from pathlib import Path
from PIL import Image

ROOT=Path("reports/swrlz-image-live-stream-1143/candidate")
def run():
 brain=types.ModuleType("brain_programming")
 called=[]
 def classifier(text,history,pins,prior):
  called.append((text,len(history),len(pins),bool(prior)))
  return {"codingTask":"source code" in text.lower() or "write code" in text.lower()}
 brain.programming_intent=classifier
 sys.modules["brain_programming"]=brain
 cfg=types.ModuleType("coder_model_config")
 cfg.MODEL_LABEL="Qwen coder";cfg.MODEL_CHECKPOINT="none"
 sys.modules["coder_model_config"]=cfg
 risk=types.ModuleType("intent_risk_v240")
 risk.classify=lambda text:"ordinary";risk.clarification=lambda text:"clarify"
 sys.modules["intent_risk_v240"]=risk
 online=types.ModuleType("online_tools");online_questions=[]
 def online_classifier(text,*_):
  online_questions.append(text);return {"requested":False,"kind":"none","reason":"none"}
 online.classify_online_request=online_classifier
 online.stream_online_request=lambda *_:iter([])
 online.online_camera=lambda *_:None
 sys.modules["online_tools"]=online
 widgets=types.ModuleType("rich_widget_intent_v285");widgets.plan_conversation_widget=lambda *_:None
 sys.modules["rich_widget_intent_v285"]=widgets
 guard=types.ModuleType("widget_companion_guard_v286");guard.guard_widget_companion=lambda source,widget:source
 sys.modules["widget_companion_guard_v286"]=guard
 spec=importlib.util.spec_from_file_location("image_model_router",ROOT/"model_router.py")
 router=importlib.util.module_from_spec(spec);sys.modules[spec.name]=router;spec.loader.exec_module(router)
 question="What's this image look like to you?"
 description="The hat appears inside a source code editor; project files surround it."
 request=question+router._VISION_START+description+router._VISION_END
 events=list(router.dispatch("700m",{"prompt":request,
     "history":[{"role":"assistant","text":chr(96)*3+"python\nprint(1)\n"+chr(96)*3}],
     "pinnedContext":[{"artifactType":"code"}],
     "priorProgrammingState":{"codingTask":True}},None,
     large_generate=lambda _:iter([{"type":"DELTA","text":"WRONG SECOND PASS"}])))
 assert events[0]["type"]=="PROGRAMMING_INTENT" and events[0]["intent"]["codingTask"] is False
 assert all(e.get("type")!="ROUTE" for e in events)
 assert any(e.get("type")=="DELTA" and "hat" in e.get("text","").lower() for e in events)
 assert not any("WRONG SECOND PASS" in e.get("text","") for e in events)
 assert online_questions==[question] and all("source code" not in q for q,*_ in called)
 code_req="Write code to recreate this image"+router._VISION_START+"orange hat"+router._VISION_END
 code_events=list(router.dispatch("700m",{"prompt":code_req,"history":[],"pinnedContext":[]},None,
     large_generate=lambda _:iter([{"type":"DELTA","text":"WRONG MODEL"}]),
     coder_generate=lambda _:iter([{"type":"DELTA","text":"CODER EXPECTED"}])))
 assert code_events[0]["intent"]["codingTask"] is True
 assert any(e.get("type")=="ROUTE" for e in code_events)
 assert any(e.get("text")=="CODER EXPECTED" for e in code_events)
 capacity=types.ModuleType("runtime_capacity")
 class Meter:
  def finish(self):return {}
 capacity.ResponseResourceMeter=Meter
 sys.modules["runtime_capacity"]=capacity
 native=types.ModuleType("qwen35_single_runtime")
 native.DECODE_THREADS=18;native.BATCH_THREADS=16;native.PARALLEL_REQUESTS=1
 sys.modules["qwen35_single_runtime"]=native
 spec=importlib.util.spec_from_file_location("image_chat_vision",ROOT/"chat_vision.py")
 vision=importlib.util.module_from_spec(spec);sys.modules[spec.name]=vision;spec.loader.exec_module(vision)
 raw=io.BytesIO()
 Image.new("RGB",(1080,2388),(14,44,68)).save(raw,format="PNG")
 img="data:image/png;base64,"+base64.b64encode(raw.getvalue()).decode()
 parts=["A glowing"," orange pointed"," wizard hat."]
 inputs=[]
 class Model:
  def create_chat_completion(self,*,messages,max_tokens,temperature,stream):
   inputs.append(messages[0]["content"][1]["image_url"]["url"])
   for word in parts:
    time.sleep(.12)
    yield {"choices":[{"delta":{"content":word}}]}
 vision._load_local_model=lambda:Model()
 snapshots=[];phases=[]
 answer=vision._ask_vision_local(img,question,
    report_phase=lambda phase,**kw:phases.append((phase,kw)),
    analysis_levels=3,on_partial=snapshots.append)
 assert answer=="".join(parts)
 assert inputs==[img] and len(snapshots)>=2
 assert snapshots[0]==parts[0] and snapshots[-1]==answer
 assert any(x.get("sourceWidth")==1080 and x.get("sourceHeight")==2388 for _,x in phases)
 key="a"*32;now=time.monotonic()
 vision._jobs[key]={"id":key,"owner":"google:tester","phase":"ANALYZING",
     "createdAt":now,"updatedAt":now,"phaseStartedAt":now,
     "lastPolledAt":now,"cancelEvent":threading.Event()}
 vision._set_vision_partial(key,"Visible Qwen words")
 assert vision._jobs[key]["partialDescription"]=="Visible Qwen words"
 vision._set_job_phase(key,"COMPLETE",description="Visible Qwen words")
 vision._set_vision_partial(key,"Not mutable after finish")
 assert vision._jobs[key]["partialDescription"]=="Visible Qwen words"
 print("SWRLZ_IMAGE_STREAM_1143_REGRESSION_PASS",flush=True)
if __name__=="__main__":run()
