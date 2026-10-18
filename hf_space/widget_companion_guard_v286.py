"""v286 source-grounded companion validation for the existing swrlz-widget-v1.
No new inference, no model-text-as-code, no external reads, no new data store.
"""
from __future__ import annotations
import math
import re
from typing import Any,Iterator

KINDS={"comparison","math-graph","model-3d"}
def fmt(n):
    return str(int(n)) if math.isfinite(n) and n==int(n) else f"{n:.5g}"

def safe(v):
    return re.sub(r"[\x00-\x1f\x7f]", " ",str(v or ""))[:75].strip()

def grounded_companion(widget:dict[str,Any])->str:
    kind=widget.get("kind")
    data=widget.get("data") if isinstance(widget.get("data"),dict) else {}
    if kind=="model-3d":
        shape=safe(data.get("shape") or "shape")
        return (f"Here's the interactive 3D {shape} wireframe preview. "
                "Drag to rotate it, use + / − to zoom, and Reset to restore the starting view. "
                "This displays a primitive; it is not an exported or editable mesh.")
    if kind=="math-graph":
        series=data.get("series") or []
        if len(series)==1 and series[0].get("type")=="polynomial":
            co=series[0].get("coefficients") or []
            if len(co)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in co):
                c,b,a=co
                if a!=0:
                    x=-b/(2*a);y=a*x*x+b*x+c
                    if all(math.isfinite(v) and abs(v)<1e5 for v in (x,y)):
                        shape="upward" if a>0 else "downward"
                        details=f"The parabola opens {shape}, with vertex ({fmt(x)}, {fmt(y)})."
                        disc=b*b-4*a*c
                        if 0<=disc<=1e10:
                            root=math.sqrt(disc)
                            xs=sorted(((-b-root)/(2*a),(-b+root)/(2*a)))
                            if all(math.isfinite(v) and abs(v)<1e5 for v in xs):
                                if abs(xs[0]-xs[1])<1e-9:
                                    details+=f" It touches the x-axis at ({fmt(xs[0])}, 0)."
                                else:
                                    details+=f" It crosses the x-axis at ({fmt(xs[0])}, 0) and ({fmt(xs[1])}, 0)."
                        else:details+=" It has no real x-intercepts."
                        return ("Here's the interactive equation graph. "+details+
                                " Drag to pan; use + / − or Reset for the view.")
        return ("Your equation is plotted in the interactive graph above. "
                "Drag to pan, use + / − to zoom, or Reset to restore the view.")
    if kind=="comparison":
        lines=[]
        for metric in (data.get("metrics") or [])[:6]:
            key=metric.get("key")
            if not key:continue
            values=[(item.get("name"),(item.get("values") or {}).get(key)) for item in (data.get("items") or [])]
            if not values or any(type(v) not in (float,int) or not math.isfinite(v) for _,v in values):continue
            unit=safe(metric.get("unit"))
            display=", ".join(safe(name)+" "+fmt(v)+(f" {unit}" if unit else "") for name,v in values)
            preference=metric.get("higherIsBetter")
            ending="; preference not specified"
            if preference is True or preference is False:
                best=(max if preference else min)(v for _,v in values)
                leaders=", ".join(safe(name) for name,v in values if v==best)
                ending="; preferred: "+leaders
            lines.append(safe(metric.get("label") or key)+": "+display+ending+".")
        return ("Here's the comparison using your supplied measurements. "
                +" ".join(lines)
                +" No overall winner is assumed without a rule for weighing the different metrics.")
    return "The requested visualization is shown above."

def issues(candidate:str,widget:dict[str,Any])->list[str]:
    text=str(candidate or "").strip()
    if widget.get("kind") not in KINDS:return []
    if not text:return ["missing-companion"]
    faults=[]
    if len(text)>800 or re.search(r"(^|\n)\s*(?:#{1,5}\s|[0-9]+\.\s)",text):
        faults.append("unrequested-tutorial")
    if "\x60\x60\x60" in text or re.search(r"\b(?:pip install|plt\.show\(|from mpl_toolkits|import matplotlib)\b",text,re.I):
        faults.append("unrequested-code-artifact")
    if re.search(r"(?:can't|cannot|unable to|not able to|don.t have (?:the )?(?:ability|capability))\s+(?:(?:directly|actually|really)\s+)?(?:show|display|render|graph|plot|provide)\b",text,re.I):
        faults.append("denies-visible-widget")
    if widget.get("kind")=="model-3d" and re.search(r"\b(?:blender|matplotlib|install|download a|online modeling tool)\b",text,re.I):
        faults.append("irrelevant-external-tool-substitute")
    if widget.get("kind")=="math-graph":
        series=(widget.get("data") or {}).get("series") or []
        if len(series)==1 and series[0].get("type")=="polynomial":
            co=series[0].get("coefficients") or []
            if len(co)==3 and co[-1]!=0:
                a=co[2];b=co[1];c=co[0];vertex_y=c-b*b/(4*a)
                if abs(vertex_y)>1e-8 and re.search(r"(?:touch(?:es|ing)?|intersect(?:s|ing)?|cross(?:es|ing)?)\s+(?:the\s+)?x.axis\s+at\s+(?:the\s+)?vertex",text,re.I):
                    faults.append("wrong-x-intercept")
    if widget.get("kind")=="comparison":
        data=widget.get("data") or {}
        items=data.get("items") or []
        for metric in data.get("metrics") or []:
            key=str(metric.get("key") or "")
            concept=key.casefold()
            if concept not in ("speed","weight","mass") or len(items)<2:continue
            vals=[(str(it.get("name") or ""),(it.get("values") or {}).get(key)) for it in items]
            if any(type(v) not in (float,int) for _,v in vals):continue
            best=(max if concept=="speed" else min)(v for _,v in vals)
            term="fastest|faster" if concept=="speed" else "lightest|lighter"
            for name,v in vals:
                if name and v!=best and re.search(r"\b"+re.escape(name)+r"\s+is\s+(?:the\s+)?(?:"+term+r")\b",text,re.I):
                    faults.append("reversed-comparative-claim")
        if re.search(r"\bfinal ranking\b|\boverall winner\b",text,re.I):
            faults.append("unsupported-overall-ranking")
    return list(dict.fromkeys(faults))

def guard_widget_companion(events:Iterator[dict[str,Any]],widget:dict[str,Any])->Iterator[dict[str,Any]]:
    """Delay only widget-associated visible DELTAs until acceptance.

    Periodic bounded STATUS events keep Station's cancel check responsive.
    Existing terminal events always follow final accepted or corrected prose.
    """
    chunks=[];terminal=[];chars=0;count=0
    for event in events:
        if not isinstance(event,dict):continue
        kind=event.get("type")
        if kind=="DELTA":
            part=str(event.get("text") or "")
            chars+=len(part)
            if chars<=24000:chunks.append(event)
            count+=1
            if count==1 or (count%64==0 and count<=256):
                yield {"type":"STATUS","phase":"WIDGET_COMPANION_REVIEW",
                       "reason":"Checking reply against the already prepared visual.",
                       "categories":["WIDGET","GROUNDING"]}
            continue
        if kind in ("COMPLETE","COMPLETED"):
            terminal.append(event);continue
        yield event
    candidate="".join(str(e.get("text") or "") for e in chunks)
    faults=["oversized-companion"] if chars>24000 else issues(candidate,widget)
    if faults:
        yield {"type":"STATUS","phase":"WIDGET_COMPANION_CORRECTED",
               "reason":",".join(faults[:4]),
               "categories":["WIDGET","GROUNDING","CORRECTED"]}
        yield {"type":"DELTA","text":grounded_companion(widget)}
    else:
        yield from chunks
    yield from terminal
