from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
station=(ROOT/"hf_space"/"station.py").read_text(encoding="utf-8")
adapter=(ROOT/"chat"/"§wyrlz"/"assets"/"widget-analysis-v128.js").read_text(encoding="utf-8")

required_camera=[
    '"schema":"swrlz-online-research-outcome-v2"',
    '"sources":bounded_sources',
    '"widgets":copy.deepcopy(online_widgets[:8])',
    '"statusTrail":copy.deepcopy((g.get("status") or [])[-128:])',
    '"responseCognition":copy.deepcopy(g.get("responseCognition") or {})',
    '"candidateAttempts":copy.deepcopy((g.get("candidateAttempts") or [])[-16:])',
    '"generationTelemetry":copy.deepcopy(g.get("generationTelemetry") or {})',
    '"contextBudget":copy.deepcopy(g.get("contextBudget") or {})',
    '"resourcePlan":copy.deepcopy(g.get("resourcePlan") or {})',
    '"finalResponse":str(text or "")[:24000]',
    '"rawPromptStored":False',
    '"historyStored":False',
    '"preciseLocationStored":False',
    '"privateReasoningStored":False',
]
for token in required_camera:
    assert token in station, token

assert 'widget-analysis-v128.js' in station
assert 'status.before(widgets)' in adapter
assert 'Analyzing weather information…' in adapter
assert 'Analyzing search results…' in adapter
assert 'Analyzing time information…' in adapter
assert 'status.hidden=hasText' in adapter
assert 'trail.hidden=hasText' in adapter
print("server-complete-online-camera-widget-order-v128 PASS")
