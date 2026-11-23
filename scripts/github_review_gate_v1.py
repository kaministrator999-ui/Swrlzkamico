"""Server-side, single-use review gate for GitHub create/edit operations."""
from dataclasses import dataclass
import hashlib, hmac, re, secrets, threading, time

class ReviewError(ValueError): pass

@dataclass(frozen=True)
class Proposal:
    ticket: str
    actor: str
    thread: str
    repo: str
    branch: str
    path: str
    operation: str
    content: str
    sha256: str
    expected_sha: str | None
    issued: float

    def public(self):
        return dict(ticket=self.ticket,repo=self.repo,branch=self.branch,
                    path=self.path,operation=self.operation,content=self.content,
                    sha256=self.sha256,expectedBlobSha=self.expected_sha)

class ReviewGate:
    def __init__(self, ttl=300, clock=time.monotonic):
        self.ttl, self.clock = ttl, clock
        self.lock, self.pending = threading.Lock(), {}

    def prepare(self, *, actor, thread, repo, branch, path, operation, content, expected_sha=None):
        if not all(isinstance(v,str) and v.strip() for v in (actor,thread,repo,branch,path)):
            raise ReviewError("Missing authenticated scope")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo):
            raise ReviewError("Invalid repository")
        if branch.startswith("-") or ".." in branch or any(c in branch for c in " ~^:?*[\\"):
            raise ReviewError("Invalid branch")
        if (path.startswith("/") or "\\" in path or len(path)>500
            or any(p in ("",".","..") or any(ord(c)<32 for c in p) for p in path.split("/"))
            or path==".git" or path.startswith(".git/")):
            raise ReviewError("Unsafe path")
        if operation not in ("CREATE_FILE","UPDATE_FILE"):
            raise ReviewError("Unsupported operation")
        if not isinstance(content,str) or len(content.encode("utf-8"))>262144:
            raise ReviewError("Invalid content")
        if operation=="CREATE_FILE" and expected_sha is not None:
            raise ReviewError("Create must not overwrite")
        if operation=="UPDATE_FILE" and (not isinstance(expected_sha,str) or not re.fullmatch(r"[a-f0-9]{40}",expected_sha)):
            raise ReviewError("Update requires original blob SHA")
        with self.lock:
            now=self.clock()
            self.pending={k:v for k,v in self.pending.items()
                          if now-v.issued<self.ttl and (v.actor,v.thread)!=(actor,thread)}
            ticket=secrets.token_urlsafe(32)
            p=Proposal(ticket,actor,thread,repo,branch,path,operation,content,
                       hashlib.sha256(content.encode("utf-8")).hexdigest(),expected_sha,now)
            self.pending[ticket]=p
            return p

    def decide(self, *, ticket, actor, thread, approved):
        if type(approved) is not bool or not all(isinstance(v,str) for v in (ticket,actor,thread)):
            raise ReviewError("Invalid decision")
        with self.lock:
            p=self.pending.get(ticket)
            if not p or not hmac.compare_digest(p.actor,actor) or not hmac.compare_digest(p.thread,thread):
                raise ReviewError("Unauthorized or stale proposal")
            del self.pending[ticket]
            if self.clock()-p.issued>=self.ttl:
                raise ReviewError("Expired proposal")
            return p if approved else None

def apply_approved(p, github):
    """Caller authenticates GitHub adapter; get_file returns None or {sha,content}."""
    old=github.get_file(p.repo,p.branch,p.path)
    if p.operation=="CREATE_FILE":
        if old is not None: raise ReviewError("File already exists")
        github.create_file(p.repo,p.branch,p.path,p.content)
    elif p.operation=="UPDATE_FILE":
        if old is None or old["sha"]!=p.expected_sha:
            raise ReviewError("Source changed since preview")
        github.update_file(p.repo,p.branch,p.path,p.content,p.expected_sha)
    else: raise ReviewError("Unsupported operation")
    current=github.get_file(p.repo,p.branch,p.path)
    if not current or hashlib.sha256(current["content"].encode()).hexdigest()!=p.sha256:
        raise ReviewError("GitHub readback failed")
    return dict(verified=True,repo=p.repo,branch=p.branch,path=p.path,
                operation=p.operation,sha256=p.sha256)
