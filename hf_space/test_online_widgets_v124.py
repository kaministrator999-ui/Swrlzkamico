import json
from pathlib import Path

import online_tools
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
coding_web=classify_online_request("Search the web for the current FastAPI lifespan docs",HISTORY,{"codingTask":True},None)
assert coding_web["requested"] is True,coding_web

# Weather provider parsing without network.
orig_json_get=online_tools._json_get
calls=[]
def fake_json_get(url):
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
calls=[]
def shared_json_get(url):
    calls.append(url)
    return fake_json_get(url)
try:
    online_tools._json_get=shared_json_get
    shared_result=weather_lookup({"clientLocation":{"authorized":True,"latitude":39.1,"longitude":-94.6,"label":"Your shared location"},"locationText":"","query":"weather here"})
finally:
    online_tools._json_get=orig_json_get
assert len(calls)==1,calls
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
assert "execute_online_request" in router and '"type":"WIDGET"' in router,router[:500]
assert 'kind=="ONLINE_RESEARCH"' in station and 'kind=="WIDGET"' in station,station[:500]
assert '"widgets":[]' in station and 'clientLocation' in station,station[:500]
assert "renderWidgetStack" in chat and "weather-stats" in chat and "search-widget-list" in chat,chat[:500]
assert "navigator.geolocation" in chat and "maybeSharedWeatherLocation" in chat,chat[:500]
assert "api/online_research.py" in prepare and "swrzl_prepared_runtime/research/online_research_reasoner.py" in prepare,prepare[:500]

print("online-widgets-v124 PASS")
