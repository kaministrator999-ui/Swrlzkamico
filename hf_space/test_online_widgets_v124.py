import json
from pathlib import Path

import online_tools
import api.online_research as canonical_search
import model_router
from online_tools import classify_online_request, execute_online_request, weather_lookup, WIDGET_CONTRACT
from response_cognition import classify_response_cognition

HISTORY=[
    {"role":"user","content":"Tell me about Mars."},
    {"role":"assistant","content":"Mars is the fourth planet from the Sun."},
]

# Carry the v123 live failure receipt forward generically.
count_state=classify_response_cognition("Create 2 short names for a moon base.",[],{})
assert count_state["requestedCount"]==2,count_state

# Weather routing.
weather=classify_online_request("What's the weather in Kansas City, MO today?",HISTORY,{},None)
assert weather["requested"] is True and weather["kind"]=="weather",weather
assert "Kansas City" in weather["locationText"],weather
assert weather["locationRequired"] is False,weather

missing=classify_online_request("What's my weather right now?",HISTORY,{},None)
assert missing["kind"]=="weather" and missing["locationRequired"] is True,missing

shared=classify_online_request("What's the weather here?",HISTORY,{},{"authorized":True,"latitude":39.1,"longitude":-94.6,"label":"Shared"})
assert shared["clientLocation"] and shared["locationRequired"] is False,shared

# General web search routing and programming freshness restraint.
search=classify_online_request("Search online for the latest OpenAI release notes",HISTORY,{},None)
assert search["requested"] is True and search["kind"]=="search",search
fresh=classify_online_request("What is the latest stable Python release?",HISTORY,{},None)
assert fresh["requested"] is True,fresh
coding=classify_online_request("Update the current function to return JSON",HISTORY,{"codingTask":True},None)
assert coding["requested"] is False,coding
coding_weather=classify_online_request("Write JavaScript for a weather forecast card",HISTORY,{"codingTask":True},None)
assert coding_weather["requested"] is False,coding_weather
coding_web=classify_online_request("Search the web for the current FastAPI lifespan docs",HISTORY,{"codingTask":True},None)
assert coding_web["requested"] is True,coding_web
coding_fresh=classify_online_request("What changed in the latest FastAPI release?",HISTORY,{"codingTask":True},None)
assert coding_fresh["requested"] is True and coding_fresh["kind"]=="search",coding_fresh

# Weather provider parsing without network.
orig_json_get=online_tools._json_get
calls=[]
def fake_json_get(url,*args,**kwargs):
    calls.append(url)
    if "geocoding-api.open-meteo.com" in url:
        return {"results":[{"name":"Kansas City","admin1":"Missouri","country":"United States","country_code":"US","timezone":"America/Chicago","latitude":39.0997,"longitude":-94.5786}]}
    return {
        "timezone":"America/Chicago",
        "current":{
            "time":"2026-10-04T21:00","temperature_2m":72.5,"relative_humidity_2m":61,
            "apparent_temperature":72.0,"precipitation":0.0,"rain":0.0,"snowfall":0.0,
            "weather_code":1,"cloud_cover":22,"surface_pressure":1008.2,
            "wind_speed_10m":8.4,"wind_direction_10m":190,"wind_gusts_10m":15.2,
        },
        "current_units":{"temperature_2m":"°F","relative_humidity_2m":"%","apparent_temperature":"°F","precipitation":"inch","surface_pressure":"hPa","wind_speed_10m":"mp/h","wind_gusts_10m":"mp/h"},
        "daily":{
            "time":["2026-10-04","2026-10-05"],
            "weather_code":[1,61],
            "temperature_2m_max":[78,70],
            "temperature_2m_min":[58,55],
            "precipitation_sum":[0,0.12],
            "precipitation_probability_max":[5,60],
            "wind_speed_10m_max":[12,15],
            "wind_gusts_10m_max":[20,24],
            "sunrise":["2026-10-04T07:15","2026-10-05T07:16"],
            "sunset":["2026-10-04T18:56","2026-10-05T18:54"],
        },
        "daily_units":{"temperature_2m_max":"°F","temperature_2m_min":"°F","precipitation_sum":"inch","wind_speed_10m_max":"mp/h","wind_gusts_10m_max":"mp/h"},
    }

try:
    online_tools._json_get=fake_json_get
    result=weather_lookup({"locationText":"Kansas City, MO","query":"weather"})
finally:
    online_tools._json_get=orig_json_get

assert len(calls)==2,calls
assert result["status"]=="OK",result
widget=result["widgets"][0]
assert widget["contract"]==WIDGET_CONTRACT and widget["kind"]=="weather",widget
assert widget["data"]["current"]["temperature"]==72.5,widget
assert widget["data"]["current"]["condition"]=="Mainly clear",widget
assert widget["data"]["daily"][1]["precipitationProbability"]==60,widget
assert widget["data"]["location"]["label"]=="Kansas City, Missouri, United States",widget
assert "latitude" not in json.dumps(widget).lower() and "longitude" not in json.dumps(widget).lower(),widget

# Shared-location weather must not persist exact coordinates in the widget.
shared_calls=[]
def shared_json_get(url,*args,**kwargs):
    shared_calls.append(url)
    if "geocoding-api.open-meteo.com" in url:
        raise AssertionError("Shared explicit coordinates must not invoke geocoding")
    return {
        "timezone":"America/Chicago",
        "current":{
            "time":"2026-10-04T21:00","temperature_2m":72.5,"relative_humidity_2m":61,
            "apparent_temperature":72.0,"precipitation":0.0,"rain":0.0,"snowfall":0.0,
            "weather_code":1,"cloud_cover":22,"surface_pressure":1008.2,
            "wind_speed_10m":8.4,"wind_direction_10m":190,"wind_gusts_10m":15.2,
        },
        "current_units":{"temperature_2m":"°F","relative_humidity_2m":"%","apparent_temperature":"°F","precipitation":"inch","surface_pressure":"hPa","wind_speed_10m":"mp/h","wind_gusts_10m":"mp/h"},
        "daily":{"time":[]},
        "daily_units":{},
    }
try:
    online_tools._json_get=shared_json_get
    shared_result=weather_lookup({"clientLocation":{"authorized":True,"latitude":39.1,"longitude":-94.6,"label":"Your shared location"},"locationText":"","query":"weather here"})
finally:
    online_tools._json_get=orig_json_get
assert len(shared_calls)==1,shared_calls
assert shared_result["widgets"][0]["data"]["location"]["sharedLocation"] is True,shared_result
serialized=json.dumps(shared_result["widgets"][0])
assert "39.1" not in serialized and "-94.6" not in serialized,serialized

# Search-result widget and evidence context using a deterministic research stub.
orig_research=online_tools.run_online_research
def fake_research(payload):
    return {
        "provider":"duckduckgo-html",
        "researchId":"research:test",
        "evidence":[
            {"evidenceId":"e1","title":"Official Example","url":"https://example.com/a","snippet":"Current official information.","source":"example.com","query":"example","rank":1},
            {"evidenceId":"e2","title":"Second Example","url":"https://example.org/b","snippet":"Secondary information.","source":"example.org","query":"example","rank":2},
        ],
        "errors":[],
    }
try:
    online_tools.run_online_research=fake_research
    search_result=execute_online_request({"requestId":"r1","prompt":"Search online for example","history":[]},{})
finally:
    online_tools.run_online_research=orig_research
assert search_result["kind"]=="search" and search_result["resultCount"]==2,search_result
assert search_result["widgets"][0]["kind"]=="search-results",search_result
assert search_result["sources"][0]["url"]=="https://example.com/a",search_result
assert search_result["modelContext"]["trust"]=="UNTRUSTED_EXTERNAL_EVIDENCE",search_result

# Location-required result refuses timezone inference.
need_location=execute_online_request({"requestId":"r2","prompt":"What's my weather?","history":[],"temporalContext":{"timeZone":"America/Chicago"}},{})
assert need_location["status"]=="LOCATION_REQUIRED",need_location
assert need_location["widgets"]==[],need_location
assert "timezone" in need_location["modelContext"]["message"].lower(),need_location

# Source-shape integration checks.
root=Path(__file__).resolve().parents[1]
router=(root/"hf_space/model_router.py").read_text(encoding="utf-8")
station=(root/"hf_space/station.py").read_text(encoding="utf-8")
chat=(root/"chat/§wyrlz/index.html").read_text(encoding="utf-8")
prepare=(root/"scripts/prepare_hf_space.py").read_text(encoding="utf-8")
assert "stream_online_request" in router and '"type":"WIDGET"' in router,router[:500]
assert 'kind=="ONLINE_RESEARCH"' in station and 'kind=="WIDGET"' in station,station[:500]
assert '"widgets":[]' in station and 'clientLocation' in station,station[:500]
assert "renderWidgetStack" in chat and "weather-stats" in chat and "search-widget-list" in chat,chat[:500]
assert "navigator.geolocation" in chat and "maybeSharedWeatherLocation" in chat,chat[:500]
assert "api/online_research.py" in prepare and "swrzl_prepared_runtime/research/online_research_reasoner.py" in prepare,prepare[:500]

print("online-widgets-v124 PASS")


# Canonical bounded provider chain: an empty DDG HTML response must fall through
# to DDG Lite and accept only validated public result links.
provider_calls=[]
orig_search_html=canonical_search._search_html
def fake_search_html(url):
    provider_calls.append(url)
    if "html.duckduckgo.com" in url:
        return 200,"<html><body>No classed results</body></html>",42
    if "lite.duckduckgo.com" in url:
        return 200,(
            "<html><body>"
            "<a class='result-link' href='https://example.com/docs'>Example Docs</a>"
            "<td class='result-snippet'>Useful current documentation.</td>"
            "</body></html>"
        ),180
    raise AssertionError("Bing fallback should not run after DDG Lite succeeds")
try:
    canonical_search._search_html=fake_search_html
    fallback_results=canonical_search._ddg_search("example docs")
finally:
    canonical_search._search_html=orig_search_html
assert len(provider_calls)==2,provider_calls
assert fallback_results and fallback_results[0]["url"]=="https://example.com/docs",fallback_results
assert fallback_results[0]["title"]=="Example Docs",fallback_results
assert canonical_search._provider()=="bounded-web-search-chain-v1"

print("online-search-provider-fallback-v124 PASS")


# Retrieval is model-agnostic: every selectable inference route receives the same
# bounded online evidence after one router-level retrieval.
captures={}
orig_stream=model_router.stream_online_request
def fake_online_stream(payload,intent):
    yield {"type":"progress","event":{"contract":"swrlz-online-trace-v1","phase":"SEARCH_PROVIDER_VISIT","provider":"test-provider","site":"example.com","url":"https://example.com/","activity":"Searching provider"}}
    yield {"type":"result","result":{
        "contract":"swrlz-hf-online-capability-v1",
        "kind":"search",
        "status":"OK",
        "provider":"test-provider",
        "resultCount":1,
        "sources":[{"title":"Example","url":"https://example.com","provider":"example.com"}],
        "widgets":[{"contract":"swrlz-widget-v1","kind":"search-results","version":1,"title":"Example","provider":"test-provider","data":{"query":"example","results":[]}}],
        "modelContext":{"contractId":"test-online-context","trust":"UNTRUSTED_EXTERNAL_EVIDENCE","instructionAuthority":False,"evidence":[{"title":"Example","url":"https://example.com","snippet":"Fresh evidence."}]},
    }}
def capture(name):
    def generate(payload):
        captures[name]=payload
        yield {"type":"DELTA","text":"ok"}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    return generate
try:
    model_router.stream_online_request=fake_online_stream
    generators={name:capture(name) for name in ("r39","stock","700m","coder")}
    for model_id in ("r39","stock","700m","coder"):
        list(model_router.dispatch(
            model_id,
            {"requestId":"route-"+model_id,"prompt":"Search online for example documentation","history":[]},
            generators["r39"],
            generators["stock"],
            generators["700m"],
            generators["coder"],
        ))
finally:
    model_router.stream_online_request=orig_stream

for model_id in ("stock","700m","coder"):
    assert (captures[model_id].get("onlineContext") or {}).get("contractId")=="test-online-context",(model_id,captures[model_id])
assert captures["r39"].get("onlineContextEmbeddedForR39") is True,captures["r39"]
assert "§WYRLZ ONLINE EXTERNAL EVIDENCE" in captures["r39"].get("prompt",""),captures["r39"]

stock_source=(root/"hf_space/original_engine.py").read_text(encoding="utf-8")
large_source=(root/"hf_space/lfm2_700m_engine.py").read_text(encoding="utf-8")
coder_source=(root/"hf_space/qwen_coder_engine.py").read_text(encoding="utf-8")
app_source=(root/"hf_space/app.py").read_text(encoding="utf-8")
assert "ONLINE EXTERNAL EVIDENCE (bounded server retrieval" in stock_source
assert "ONLINE EXTERNAL EVIDENCE (bounded server retrieval" in large_source
assert "ONLINE EXTERNAL EVIDENCE (bounded server retrieval" in coder_source
assert "_r39_online_payload" in router and "onlineContextEmbeddedForR39" in router
assert "load as large_load" in app_source
assert '(("700m",large_load),("coder",coder_load),("stock",original_load),("r39",engine))' in app_source

print("all-model-online-context-v124 PASS")


# Real-time observability contract: provider/site events are emitted without query strings,
# then Station/Chat have source hooks to persist and render them.
trace_events=[]
canonical_search.set_trace_sink(trace_events.append)
provider_calls=[]
orig_search_html=canonical_search._search_html
def traced_search_html(url):
    provider_calls.append(url)
    if "html.duckduckgo.com" in url:
        return 200,"<html><body>No classed results</body></html>",42
    return 200,(
        "<html><body>"
        "<a class='result-link' href='https://example.com/docs?secret=query'>Example Docs</a>"
        "<td class='result-snippet'>Useful current documentation.</td>"
        "</body></html>"
    ),180
try:
    canonical_search._search_html=traced_search_html
    traced_results=canonical_search._ddg_search("sensitive user query")
finally:
    canonical_search._search_html=orig_search_html
    canonical_search.clear_trace_sink()
assert traced_results,traced_results
assert any(item.get("phase")=="SEARCH_PROVIDER_VISIT" and item.get("site")=="html.duckduckgo.com" for item in trace_events),trace_events
assert any(item.get("phase")=="SEARCH_PROVIDER_VISIT" and item.get("site")=="lite.duckduckgo.com" for item in trace_events),trace_events
for item in trace_events:
    assert "sensitive user query" not in json.dumps(item),item
    if item.get("url"):
        assert "?" not in item["url"],item

weather_trace=[]
def traced_weather_json(url,*args,**kwargs):
    progress=args[0] if args and callable(args[0]) else kwargs.get("progress")
    phase=kwargs.get("phase","WEATHER_PROVIDER_VISIT")
    activity=kwargs.get("activity","Fetching weather data")
    online_tools._progress(progress,phase,provider=online_tools.WEATHER_PROVIDER,url=url,activity=activity)
    if "geocoding-api.open-meteo.com" in url:
        online_tools._progress(progress,phase.replace("_VISIT","_COMPLETE"),provider=online_tools.WEATHER_PROVIDER,url=url,activity="Weather provider response received",httpStatus=200)
        return {"results":[{"name":"Kansas City","admin1":"Missouri","country":"United States","country_code":"US","timezone":"America/Chicago","latitude":39.0997,"longitude":-94.5786}]}
    online_tools._progress(progress,phase.replace("_VISIT","_COMPLETE"),provider=online_tools.WEATHER_PROVIDER,url=url,activity="Weather provider response received",httpStatus=200)
    return {
        "timezone":"America/Chicago",
        "current":{"time":"2026-10-04T21:00","temperature_2m":72.5,"relative_humidity_2m":61,"apparent_temperature":72.0,"precipitation":0.0,"rain":0.0,"snowfall":0.0,"weather_code":1,"cloud_cover":22,"surface_pressure":1008.2,"wind_speed_10m":8.4,"wind_direction_10m":190,"wind_gusts_10m":15.2},
        "current_units":{"temperature_2m":"°F","relative_humidity_2m":"%","apparent_temperature":"°F","precipitation":"inch","surface_pressure":"hPa","wind_speed_10m":"mp/h","wind_gusts_10m":"mp/h"},
        "daily":{"time":[]},"daily_units":{},
    }
orig_json_get=online_tools._json_get
try:
    online_tools._json_get=traced_weather_json
    weather_lookup({"locationText":"Kansas City, MO","query":"weather"},weather_trace.append)
finally:
    online_tools._json_get=orig_json_get
assert any(item.get("phase")=="WEATHER_GEOCODE_VISIT" and item.get("site")=="geocoding-api.open-meteo.com" for item in weather_trace),weather_trace
assert any(item.get("phase")=="WEATHER_FORECAST_VISIT" and item.get("site")=="api.open-meteo.com" for item in weather_trace),weather_trace
assert all("?" not in str(item.get("url") or "") for item in weather_trace),weather_trace

station_source=(root/"hf_space/station.py").read_text(encoding="utf-8")
assert '"ONLINE_RESEARCH_TRACE":("online-research","online-research-trace.json"' in station_source
assert '"ONLINE_RESEARCH_OUTCOME":("online-research","online-research-outcome.json"' in station_source
assert 'kind=="ONLINE_TRACE"' in station_source
assert '"onlineTrace":[]' in station_source
assert '"site":str(item.get("site") or "")' in station_source
assert "runtime-diagnostics/online-research/" in station_source
assert '"requestedModelId"' in station_source and '"selectedModelId"' in station_source
assert 'kind=="ROUTE"' in station_source
assert "SEARCH_PROVIDER_VISIT" in chat and "SEARCH_PROVIDER_RESULTS" in chat and "PAGE_FETCH_STARTED" in chat and "WEATHER_FORECAST_VISIT" in chat
assert 'site:String(event.site||"")' in chat
assert 'activityDetail=activitySite||activityProvider' in chat
assert "station-online-trail" in chat and "station-online-event" in chat
assert "safeHttpUrl(item.url)" in chat

print("online-trace-observability-v125 PASS")
