"""v170 regression: new assistant responses anchor at their top and streaming renders are coalesced."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"chat"/"§wyrlz"/"index.html").read_text(encoding="utf-8")

assert 'responseStartAnchorRequestId' in html
assert 'const scrollResponseStart=(node,requestId)=>' in html
assert 'uiCamera("response-start-anchor"' in html
assert 'responseStartAnchorActive()' in html
assert 'if(event.isTrusted&&responseStartAnchorActive()&&distanceFromLatest()<72)responseStartAnchorRequestId=""' in html
assert 'jumpLatest.addEventListener("click",()=>scrollToLatest("smooth"))' in html

# New live responses must anchor to the response start instead of immediately
# forcing the viewport back to the newest/bottom pixel.
assert 'scrollResponseStart(node,g.requestId);' in html
assert 'renderStationGeneration(); scrollToLatest("auto");' not in html

# Token/status bursts should not force a complete DOM/markdown rerender for every
# individual NDJSON event.
assert 'const scheduleStationGenerationRender=()=>{' in html
assert 'scheduleStationGenerationRender();' in html
assert 'stationRenderFrame=requestAnimationFrame' in html

# Reserve enough live-response height for block:start anchoring on mobile.
assert '.station-live-message{scroll-margin-top:72px;min-height:calc(100dvh - var(--composer-visible-height,70px) - 86px)}' in html

print("response-start-stream-anchor-v170 PASS")
