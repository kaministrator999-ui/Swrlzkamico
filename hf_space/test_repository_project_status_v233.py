"""Offline v233 owner contract: §tart-led project resolution, not a Chat keyword map."""
import base64
import hashlib
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as gh
import repository_project_status_v233 as project
import brain_programming as bp

SHA="a"*40
RUNTIME="b"*40
ROUTER="""# §wyrlz §tart — READ THIS FIRST
The main §wyrlz AI Chat/LALM application is hosted separately from Forge.
- clean-room chat lives at /chat/§wyrlz and owns conversation UI.
Specialized Forge engine entrypoint §tart_§E.md:
- projects/swrlz-forge-moba/ has its own release lane.
New hypothetical scoped project: projects/saffron-simulator/
"""
ROAD="""## UPDATE FINISHED — 2026-10-13 — v233 Chat account UI refinement
**Outcome:** Signed-in Chat source report follows existing authorized repo context; owner mobile acceptance remains pending.

## UPDATE FINISHED — 2026-10-12 — v10.5 Forge recorder
**Outcome:** Forge published editor run recorder with verified independent source receipt.

## UPDATE STARTED — 2026-10-11 — generic kernel work
"""
FORGE="# §tart §E\n\n## Current v10.6 candidate · Frostveil Maul tower defense\n\nSource is a candidate, not publication.\n"
VALUES={"§wyrlz_§tart.md":ROUTER,
        "SWRLZ_SERVER_ROADMAP.md":ROAD,
        "§tart_§E.md":FORGE,
        "VERSION.txt":"WEB_CHAT=versions/web-chat.txt\nLALM_ENGINE=versions/lalm-engine.txt\nREPOSITORY_WORK=versions/repository-work.txt\n",
        "versions/web-chat.txt":"ID=web-chat\nVERSION=1.5.119\n",
        "versions/lalm-engine.txt":"ID=lalm-engine\nVERSION=2.1.196\n",
        "versions/repository-work.txt":"VERSION=1.0.173\n"}
def api(token,path):
    assert token=="private-token" and path.startswith("/repos/owner/repo/")
    if path.endswith("/commits/main"):return {"sha":SHA}
    if path.endswith("/commits/runtime"):return {"sha":RUNTIME}
    raise AssertionError("Unexpected API "+path)

def read(token,repo,path,ref,limit=0):
    assert token=="private-token" and repo=="owner/repo" and ref in (SHA,RUNTIME)
    val=VALUES.get(path)
    return {"body":val,"sha":"c"*40} if val is not None else None

def test_project_question_recognition():
    assert project.subject_of_status("Can you tell me where we are at with the chat in the repo?")=="chat"
    assert project.subject_of_status("Where are we at with the Forge engine?")=="forge engine"
    assert project.subject_of_status("What projects are we working on in the repo?")==""
    assert project.subject_of_status("What's the current progress of the Saffron Simulator project?")=="saffron simulator project"
    assert project.subject_of_status("What did we discuss in my previous chat?") is None
    assert project.subject_of_status("What's the date span of the ChatGPT import?") is None
    assert project.subject_of_status("Please modify the Forge engine project") is None

def test_dynamic_project_discovery():
    refs=project.discover(ROUTER)
    assert any(x["path"]=="chat/§wyrlz" for x in refs)
    assert any(x["path"]=="projects/swrlz-forge-moba" for x in refs)
    assert project.candidates(refs,"chat")[0][1]["path"]=="chat/§wyrlz"
    assert project.candidates(refs,"forge engine")[0][1]["path"]=="projects/swrlz-forge-moba"
    assert project.candidates(refs,"saffron simulator")[0][1]["path"]=="projects/saffron-simulator"
    assert not project.candidates(refs,"nonexistent")

def test_cross_project_reports_use_source_not_chat_shortcut():
    rec={"token":"private-token"}
    chat=project.build_status(rec,"owner/repo","main","chat",api,read)
    forge=project.build_status(rec,"owner/repo","main","forge engine",api,read)
    alt=project.build_status(rec,"owner/repo","main","saffron simulator",api,read)
    all_projects=project.build_status(rec,"owner/repo","main","",api,read)
    assert "chat/§wyrlz" in chat and "1.5.119" in chat
    assert "Chat account UI refinement" in chat
    assert "projects/swrlz-forge-moba" in forge and "Frostveil Maul" in forge
    assert "v10.5 Forge recorder" in forge
    assert "web-chat" not in forge.lower(),"Forge can't inherit unrelated Web Chat versions"
    assert "projects/saffron-simulator" in alt
    assert "no matching entry" in alt
    assert "projects/saffron-simulator" in all_projects
    assert "not proof of currently active work" in all_projects
    assert "release" not in alt or "Source records" in alt

def test_authenticated_repo_chat_followups_and_locked_writes():
    ctx={"repo":"owner/repo","branch":"main","sourceSha":SHA,
         "directory":"","lastFile":"","kind":"directory"}
    for question in ("Can you tell me where we are at with the chat in the repo?",
                     "Where are we at with the Forge engine?",
                     "What projects are we working on in the repo?"):
        cmd=gh._implicit_repo_command(question,ctx)
        assert cmd.startswith("@GitHub project status"),cmd
        assert gh._read_stage_command(cmd)
    assert gh._implicit_repo_command("Please edit Forge project and deploy it",ctx) is None
    assert not gh._read_stage_command("@GitHub create branch feature/unsafe from main")
    assert gh.is_github_conversation("What's the status of the Forge engine in the repo?")
    assert not bp.programming_intent("Can you tell me where we are at with the chat in the repo?",[],[])["codingTask"]

def test_verified_blob_roadmap_large_fallback_and_failure():
    raw=ROAD.encode("utf8")
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    def fallback(tok,url):
        assert tok=="private-token"
        if "/contents/" in url:return {"type":"file","size":len(raw),"sha":sha}
        if "/git/blobs/" in url:return {"encoding":"base64","sha":sha,"content":base64.b64encode(raw).decode()}
        raise AssertionError(url)
    obj=project.source_file(lambda *a:None,fallback,"private-token","owner/repo",
                            "SWRLZ_SERVER_ROADMAP.md",SHA)
    assert obj["body"]==ROAD
    assert project.source_file(lambda *a:None,lambda tok,url:{"type":"file","size":99999999,"sha":sha},
                                "private-token","owner/repo","SWRLZ_SERVER_ROADMAP.md",SHA) is None

if __name__=="__main__":
    test_project_question_recognition()
    test_dynamic_project_discovery()
    test_cross_project_reports_use_source_not_chat_shortcut()
    test_authenticated_repo_chat_followups_and_locked_writes()
    test_verified_blob_roadmap_large_fallback_and_failure()
    print("v233 §tart-led project scope, source progress, privacy and immutable blob checks PASS")
