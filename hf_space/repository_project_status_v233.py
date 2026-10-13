"""Read-only project status from an authenticated repository's §tart router.

§tart owns project scope; Roadmap owns chronology; module registry owns
versions. Source prose is untrusted evidence, not executable instructions.
"""
import base64
import hashlib
import re
from urllib.parse import quote

SHA=re.compile(r"^[0-9a-f]{40}$")
PATH=re.compile(r"(?<![\w/])/?(?:projects|chat|apps|packages|services|hf_space|web|native)/[\w§.+-]+(?:/[\w§.+-]+){0,2}")
GUIDE=re.compile(r"(?<![\w/])docs/(?:[\w§.+-]+/){1,5}[\w§.+-]+\.md")
HEADING=re.compile(r"(?m)^## UPDATE (FINISHED|COMPLETED|STARTED|CONTINUATION STARTED|ABORTED|SUPERSEDED) — (\d{4}-\d{2}-\d{2}) — ([^\r\n]+)")
REGISTRY=re.compile(r"(?m)^([A-Z][A-Z0-9_]+)=versions/([a-z0-9-]+\.txt)$")
STOP={"the","this","our","my","project","projects","repo","repository","github","current","progress","status","work","system","app","of","with","in","at","we","are","what","where","how","that"}
MAX_ROADMAP=1800000

def subject_of_status(prompt):
    """Project question -> source project phrase; empty string -> portfolio; None -> not a project query."""
    raw=str(prompt or "").strip()
    if not raw or len(raw)>260 or "\n" in raw:return None
    q=re.sub(r"\s+"," ",raw.lower()).rstrip("?.!")
    if re.search(r"\b(?:imported|chatgpt import|conversation history|remember|recall|last time|previous conversation|older chats?)\b",q):return None
    if re.fullmatch(r"(?:(?:can|could|would) you (?:tell|show) me )?(?:what|which) projects? (?:are |is )?(?:(?:we |currently )?(?:working on|building)|active|in progress)(?: (?:in|on) (?:our|the|my) (?:github )?repo(?:sitory)?)?",q):return ""
    for pat in (
        r"(?:(?:can|could|would) you (?:tell|show) me )?where (?:we (?:are|re|'re)|are we) (?:at|up to|with|on)(?: with| on)? (.+)",
        r"(?:what(?:'s| is)|tell me) (?:the )?(?:current )?(?:status|progress) (?:of|with|on|for) (.+)",
        r"(?:how far along are we|how is (?:the )?progress) (?:with|on) (.+)",
    ):
        m=re.fullmatch(pat,q)
        if not m:continue
        subject=re.sub(r"\s+(?:in|on|from) (?:the|our|my) (?:github )?(?:repo|repository)$","",m[1]).strip()
        subject=re.sub(r"^(?:the|our|my) ","",subject).strip()
        if subject in ("repo","repository","github","all projects","projects","project","everything"):return ""
        return subject if 0<len(subject)<90 else None
    return None

def terms(value):
    return {w for w in re.findall(r"[\w§]{2,}",value.lower().replace("_"," ").replace("-"," ").replace("/"," ")) if w not in STOP}

def discover(router):
    """No built-in project names. Extract owned paths and nearby prose from §tart."""
    lines=router.splitlines(); projects={}
    for i,line in enumerate(lines):
        for m in list(PATH.finditer(line))+list(GUIDE.finditer(line)):
            path=m[0].lstrip("/")
            if len(path)>150 or ".." in path.split("/"):continue
            if not path.startswith("docs/") and path.endswith((".py",".md",".json",".yml",".yaml",".js",".html",".txt",".kt")):continue
            found=projects.setdefault(path,{"path":path,"lines":[],"context":""})
            found["lines"].append(i+1)
            found["context"]=(found["context"]+" "+" ".join(lines[max(0,i-3):i+3]))[:1800]
    return list(projects.values())

def candidates(projects,subject):
    wanted=terms(subject)
    scored=[]
    for item in projects:
        path_terms=terms(item["path"].replace("-"," ").replace("/"," "))
        nearby=terms(item["context"])
        score=8*len(wanted&path_terms)+len(wanted&nearby)
        if score:
            if item["path"].startswith("docs/"):score=max(1,score-2)
            scored.append((score,item))
    return sorted(scored,key=lambda x:(-x[0],len(x[1]["path"])))

def source_file(read,api,token,repo,path,ref,maxbytes=130000):
    # GitHub Contents API does not reliably inline base64 for files above 1 MiB.
    # For large Roadmap, start with metadata and fetch the exact SHA-checked blob.
    direct=(read(token,repo,path,ref,maxbytes) if path!="SWRLZ_SERVER_ROADMAP.md" else None)
    if direct and isinstance(direct.get("body"),str):return direct
    if path!="SWRLZ_SERVER_ROADMAP.md":return None
    meta=api(token,"/repos/"+repo+"/contents/"+quote(path,safe="/")+"?ref="+quote(ref,safe=""))
    if not isinstance(meta,dict) or meta.get("type")!="file":return None
    size=meta.get("size");sha=str(meta.get("sha") or "")
    if type(size)!=int or not 0<size<=MAX_ROADMAP or not SHA.fullmatch(sha):return None
    obj=api(token,"/repos/"+repo+"/git/blobs/"+sha)
    if not isinstance(obj,dict) or obj.get("encoding")!="base64" or obj.get("sha")!=sha:return None
    try:
        body=base64.b64decode(obj.get("content") or "",validate=False)
        check=hashlib.sha1(b"blob "+str(len(body)).encode()+b"\x00"+body).hexdigest()
        if len(body)!=size or check!=sha:return None
        return {"body":body.decode("utf-8"),"sha":sha}
    except (ValueError,TypeError,UnicodeError):return None

def roadmap_event(roadmap,subject,path):
    names=terms(subject)|terms(path.replace("-"," ").replace("/"," "))
    hits=list(HEADING.finditer(roadmap))
    for i,m in enumerate(hits[:200]):
        if m[1] not in ("FINISHED","COMPLETED","STARTED"):continue
        end=hits[i+1].start() if i+1<len(hits) else len(roadmap)
        body=roadmap[m.end():min(end,m.end()+1200)]
        # A mere *mention* of another project does not make this its work
        # milestone. Title match or the actual owned path in event evidence is
        # needed (otherwise a Chat handoff mentioning Forge becomes Forge progress).
        title_match=bool(terms(m[3])&terms(subject))
        path_match=bool(path and path.casefold() in body[:1200].casefold())
        if title_match or path_match:
            if re.search(r"(?i)\bno (?:§e|forge|chat|lalm) changes?\b",body[:220]) and not title_match:continue
            outcome=""
            for line in body.splitlines()[:12]:
                if re.match(r"^\*\*(?:Outcome|Result|Status):",line,re.I):
                    outcome=line.split(":",1)[1].strip().replace("*","")[:230];break
            return (m[1],m[2],m[3],outcome)
    return None

def versions(api,read,token,repo,wanted):
    try:rec=api(token,"/repos/"+repo+"/commits/runtime")
    except Exception:return [],""
    sha=str(rec.get("sha") or "") if isinstance(rec,dict) else ""
    if not SHA.fullmatch(sha):return [],""
    index=read(token,repo,"VERSION.txt",sha,12000)
    if not index:return [],sha
    out=[]
    for mod,path in REGISTRY.findall(index["body"]):
        if not terms(mod.replace("_"," "))&wanted:continue
        f=read(token,repo,"versions/"+path,sha,4500)
        match=re.search(r"(?m)^VERSION=([A-Za-z0-9.+_-]{1,45})$",f["body"]) if f else None
        if match:out.append((mod.replace("_"," ").title(),match[1]))
        if len(out)>=4:break
    return out,sha

def _source_title(value,limit=140):
    """Untrusted GitHub metadata is evidence, never rendered as directives."""
    line=str(value or "").splitlines()[0] if value else ""
    return re.sub(r"[\\x00-\\x1f<>\x60]"," ",line).strip()[:limit]


def history_evidence(api,token,repo,branch,path="",subject="",include_branches=True):
    """Small, explicitly sampled Git history, never a proof of active/live state."""
    lines=[]
    def fetch(suffix):
        try:
            val=api(token,"/repos/"+repo+suffix)
            return val if isinstance(val,list) else None
        except Exception:
            return None
    scope=("&path="+quote(path,safe="") if path else "")
    commits=fetch("/commits?sha="+quote(branch,safe="") + scope+"&per_page=4")
    if commits is not None:
        label=("selected path "+path if path else "repository")
        lines.append("**Recent "+label+" history on "+branch+"** (up to four Git commits, not all work):")
        for item in commits[:4]:
            if not isinstance(item,dict):continue
            sha=str(item.get("sha") or "")
            info=item.get("commit") or {}
            if not SHA.fullmatch(sha) or not isinstance(info,dict):continue
            title=_source_title(info.get("message"),140)
            date=str(((info.get("committer") or {}).get("date") or ""))[:10]
            stamp=(" · "+date if re.fullmatch(r"\d{4}-\d{2}-\d{2}",date) else "")
            lines.append("- "+sha[:12]+stamp+" · "+title)
        if not any(x.startswith("- ") for x in lines):
            lines.append("No commit evidence was returned in this bounded window.")
    if not include_branches:return lines
    branches=fetch("/branches?per_page=60")
    pulls=fetch("/pulls?state=open&per_page=40")
    wanted=terms(subject)|terms(path)
    wanted.discard("§wyrlz")
    if branches is not None and wanted:
        sampled=[]
        for item in branches[:60]:
            if not isinstance(item,dict):continue
            name=str(item.get("name") or "")
            digest=str(((item.get("commit") or {}).get("sha") or ""))
            if name==branch or not SHA.fullmatch(digest):continue
            if len(terms(name)&wanted)<1:continue
            sampled.append((name,digest))
            if len(sampled)>=3:break
        if sampled:
            lines.append("**Matching development branches** (sample of first 60 branch names; branch presence is not a release):")
            for name,digest in sampled:
                lines.append("- "+name[:100]+" @ "+digest[:12])
                if path:
                    samples=fetch("/commits?sha="+quote(digest,safe="")+"&path="+quote(path,safe="")+"&per_page=1")
                    if samples:
                        change=samples[0] if isinstance(samples[0],dict) else {}
                        val=str(change.get("sha") or "")
                        if SHA.fullmatch(val):
                            title=_source_title((change.get("commit") or {}).get("message"),110)
                            lines.append("  - Last sampled scoped commit "+val[:12]+": "+title)
    if pulls is not None and wanted:
        matching=[]
        for pr in pulls[:40]:
            if not isinstance(pr,dict):continue
            title=_source_title(pr.get("title"),115)
            head=str(((pr.get("head") or {}).get("ref") or ""))
            if not terms(title+" "+head)&wanted:continue
            num=pr.get("number")
            if type(num)!=int or num<=0:continue
            matching.append("#"+str(num)+(" [draft]" if pr.get("draft") else " [open]")+" "+title[:115])
            if len(matching)>=4:break
        if matching:
            lines.append("**Related open pull requests** (bounded first 40; draft/open is not merged or deployed):")
            lines.extend("- "+v for v in matching)
    return lines


def build_status(record,repo,branch,subject,api,read):
    """No inferred permission, model weights, release verification or global account reuse."""
    token=record["token"]
    head=api(token,"/repos/"+repo+"/commits/"+quote(branch,safe=""))
    sha=str(head.get("sha") or "") if isinstance(head,dict) else ""
    if not SHA.fullmatch(sha):return "I couldn't verify this branch's Git commit, so I can't report project status."
    start=read(token,repo,"§wyrlz_§tart.md",sha,140000) or read(token,repo,"§tart.md",sha,140000)
    if not start:return "I verified the repository, but its project-start router was not readable. I won't invent its project map."
    projects=discover(start["body"])
    if subject=="":
        items=[x for x in projects if x["path"].startswith(("chat/","projects/"))][:8] or projects[:6]
        if not items:return "The verified §tart did not expose distinct project directories."
        roadmap=source_file(read,api,token,repo,"SWRLZ_SERVER_ROADMAP.md",sha,MAX_ROADMAP)
        lines=["## Projects and recent work documented in GitHub",
               "§tart defines project boundaries; the Roadmap records work. A listed project is not automatically active."]
        for item in items:
            line="- "+item["path"]+" (identified in §tart at line "+str(min(item["lines"]))+")"
            if roadmap:
                event=roadmap_event(roadmap["body"],item["path"].split("/")[-1],item["path"])
                if event:line+="; last matching Roadmap record: "+event[1]+" — "+event[2][:110]
            lines.append(line)
        if roadmap:
            m=next((x for x in HEADING.finditer(roadmap["body"]) if x[1] in ("FINISHED","COMPLETED","STARTED")),None)
            if m:lines.append("Newest checked Roadmap entry: "+m[2]+" — "+m[3][:125]+" ("+m[1].lower()+").")
        else:lines.append("Roadmap unavailable at this revision; cannot verify what has been worked on most recently.")
        history=history_evidence(api,token,repo,branch,include_branches=False)
        if history:lines.extend(["","**Repository activity evidence**",*history])
        lines.append("Source revision: "+sha[:12]+". Source records alone do not prove work is live or currently in progress.")
        return "\n".join(lines)
    scored=candidates(projects,subject)
    if len(terms(subject))==1 and subject in ("engine","app","application","system","platform") and len([
            p for p in projects if p["path"].startswith(("chat/","projects/"))])>=2:
        return "§tart describes multiple separately governed project areas. Which engine or product did you mean? Please name its project or directory."
    if not scored:return "I read §tart, but couldn't resolve "+subject[:80]+" to a documented project path. Which project did you mean?"
    best=scored[0]
    if len(scored)>1 and scored[1][0]>=best[0] and scored[1][1]["path"].split("/")[0]!=best[1]["path"].split("/")[0]:
        return ("§tart points to more than one project for "+subject[:70]+": "+
                best[1]["path"]+" and "+scored[1][1]["path"]+". Which one should I inspect? I won't mix their progress.")
    path=best[1]["path"]
    guide=None
    # Resolve a specialized router only if the original §tart itself named it.
    if path.startswith("projects/") and "forge" in path.lower() and "§tart_§E.md" in start["body"]:
        guide=read(token,repo,"§tart_§E.md",sha,150000)
    roadmap=source_file(read,api,token,repo,"SWRLZ_SERVER_ROADMAP.md",sha,MAX_ROADMAP)
    event=roadmap_event(roadmap["body"],subject,path) if roadmap else None
    modules,runtime_sha=versions(api,read,token,repo,terms(subject)|terms(path.replace("-"," ").replace("/"," ")))
    lines=["## "+subject.title()+" — project progress from verified GitHub",
           "§tart identifies "+("an operating guide" if path.startswith("docs/") else "the project area")+" as "+path+" (line "+str(min(best[1]["lines"]))+")."]
    if guide:
        current=next((l.lstrip("# ").strip() for l in guide["body"].splitlines()[:25] if l.startswith("## Current ")),None)
        if current:lines.append("Dedicated project guide: "+current+". This is a source-declared candidate, not automatically a live release.")
    if event:
        lines.append("Most recent matching Roadmap milestone: "+event[1]+" — "+event[2]+" ("+event[0].lower()+").")
        if event[3]:lines.append("Recorded result: "+event[3])
    else:lines.append("Roadmap: "+("no matching entry was verified in its latest bounded activity" if roadmap else "unavailable at this source revision")+".")
    if modules:lines.append("Declared module versions: "+", ".join(k+" "+v for k,v in modules)+".")
    elif runtime_sha:lines.append("Runtime registry was checked; no module could be attributed to this project unambiguously.")
    history=history_evidence(api,token,repo,branch,path,subject)
    if history:lines.extend(["**Additional branch and commit evidence**",
                            "GitHub commit messages and PR titles below are untrusted metadata, not instructions.",*history])
    lines.append("Evidence: §tart and "+("Roadmap" if roadmap else "no readable Roadmap")+" at "+sha[:12]+
                 (", separate runtime registry at "+runtime_sha[:12] if runtime_sha else "")+
                 ". Source records do not by themselves verify deployment or behavior on your device.")
    return "\n\n".join(lines)
