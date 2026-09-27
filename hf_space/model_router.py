"""Explicit model routing for HF candidate; never silently substitute R39 for stock."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterator, Any

class ModelUnavailable(RuntimeError):
    def __init__(self, model_id: str, reason: str):
        self.model_id=model_id
        super().__init__(reason)

@dataclass(frozen=True)
class ModelRoute:
    model_id: str
    label: str
    available: bool
    checkpoint: str | None
    reason: str | None = None

def routes(stock_checkpoint: str | None = None) -> list[ModelRoute]:
    return [
        ModelRoute("r39","§wyrlz R39 — fixed",True,"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee"),
        ModelRoute("stock","Original HF · LiquidAI LFM2-350M Q4_K_M",False,"LiquidAI/LFM2-350M-GGUF@31cd51db1365/LFM2-350M-Q4_K_M.gguf","Identified from live Space revision bc62f0fe; additive backend integration pending"),
        ModelRoute("compare","Compare both",False,None,"Requires two verified independent inference backends"),
    ]

def dispatch(model_id: str, payload: dict[str,Any], r39_generate: Callable[[dict[str,Any]],Iterator[dict[str,Any]]]):
    if model_id=="r39":
        yield from r39_generate(payload)
        return
    route=next((x for x in routes() if x.model_id==model_id),None)
    if route is None:
        raise ModelUnavailable(model_id,"Unknown model route")
    raise ModelUnavailable(model_id,route.reason or "Model route unavailable")
