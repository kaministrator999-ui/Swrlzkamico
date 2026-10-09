"""Plan validation, graph ordering, refusal of unapproved/unsafe manifests."""
import json
from project_manifest import PlanError, parse_plan, next_ready_paths, source_sha

BACKTICK=chr(96)
def fence(data):
    return BACKTICK*3+"swrlz-project-manifest\n"+json.dumps(data)+"\n"+BACKTICK*3

ok={"schema":"swrlz-project-manifest-v1","title":"Sample App","goal":"Build a small CLI with tests",
    "files":[
        {"path":"tests/test_app.py","language":"python","purpose":"Regression tests","dependsOn":["src/app.py"]},
        {"path":"README.md","language":"markdown","purpose":"Usage","dependsOn":["src/app.py"]},
        {"path":"src/app.py","language":"python","purpose":"Implementation","dependsOn":[]},
    ]}
p=parse_plan("Here is the plan:\n"+fence(ok))
assert p["generationOrder"]==["src/app.py","tests/test_app.py","README.md"],p
assert next_ready_paths(p,[])==["src/app.py"]
assert next_ready_paths(p,["src/app.py"])==["tests/test_app.py","README.md"]
assert next_ready_paths(p,["src/app.py","tests/test_app.py"])==["README.md"]
assert next_ready_paths(p,p["generationOrder"])==[]
assert len(p["planSha256"])==64 and len(source_sha(fence(ok)))==64
assert parse_plan(fence(ok))["planSha256"]==p["planSha256"]

def rejected(obj=None, raw=None):
    try:parse_plan(fence(obj if obj is not None else ok) if raw is None else raw)
    except PlanError:return
    raise AssertionError("Invalid or untrusted plan accepted: "+str(obj or raw)[:100])

rejected(raw="Not actually a project manifest")
rejected(raw=fence(ok)+"\n"+fence(ok))
rejected(raw=BACKTICK*3+"json\n"+json.dumps(ok)+"\n"+BACKTICK*3)
rejected({**ok,"schema":"unknown"})
rejected({**ok,"files":[]})
rejected({**ok,"files":ok["files"]*12})
rejected({**ok,"files":[{**ok["files"][0],"path":"../evil.py"}]})
rejected({**ok,"files":[ok["files"][0],{**ok["files"][0],"path":"TESTS/test_app.py"}]})
rejected({**ok,"files":[{**ok["files"][2],"dependsOn":["no-such.py"]}]})
rejected({**ok,"files":[{**ok["files"][2],"dependsOn":["src/app.py"]}]})
rejected({**ok,"files":[{**ok["files"][2],"dependsOn":["README.md"]},{**ok["files"][1],"dependsOn":["src/app.py"]}]})
rejected({**ok,"files":[{**ok["files"][2],"language":None}]})
rejected({**ok,"files":[{**ok["files"][2],"purpose":"x"*221}]})
rejected({**ok,"files":[{**ok["files"][2],"dependsOn":"README.md"}]})
rejected({**ok,"files":[{**ok["files"][2],"dependsOn":["README.md","README.md"]},{**ok["files"][1],"dependsOn":[]}]})
rejected({**ok,"files":[{**ok["files"][2],"path":"src"},{**ok["files"][0],"path":"src/app.py","dependsOn":[]}]})
rejected(raw=BACKTICK*3+"swrlz-project-manifest\n"+'{"schema":"swrlz-project-manifest-v1","title":NaN}'+"\n"+BACKTICK*3)
rejected({**ok,"goal":"private"*500})
rejected({**ok,"title":"Long"*50})
print("PROJECT_MANIFEST_V189_PASS dependency graph, determinism, 19 negative cases")
