#!/usr/bin/env python3
"""Request-first GitHub auth UX: exact-live CAS patch, no permission picker."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
ACTIONS="github_conversation_actions_v264.py"
HTML="chat/§wyrlz/index.html"
CONNECTION="github_connection.py"
ROOT=Path("reports/github-request-first-v1")
AUTH_MARK="swrlz-request-first-github-auth-v1"

AUTH_ACTIONS=r'''

# swrlz-request-first-github-auth-v1
# Only a provider OAuth grant can supply missing scopes; a chat approval cannot.
_swrlz_prior_create=_prepare_create
_swrlz_prior_update=_prepare_update

def _swrlz_authorization_response(user_id, thread_id, result):
    if not isinstance(result,dict):
        return result
    message=str(result.get("text") or "")
    if "GITHUB_WRITE_SCOPE_REQUIRED" not in message:
        return result
    # No pending mutation may survive an OAuth roundtrip.
    expire_interrupted(user_id,thread_id)
    result["text"]=("GitHub needs one-time write authorization for this requested "
                    "operation. Choose **Authorize GitHub** to continue through "
                    "GitHub's own consent screen, then resend your request. "
                    "No repository change was made.")
    result["widget"]={
        "contract":"swrlz-widget-v1","kind":"github-authorization",
        "title":"Authorize GitHub for requested change","provider":"GitHub",
        "data":{"authorizeUrl":"/api/github/start?access=public-write",
                "purpose":"Required once for GitHub file writes. No file is changed by authorization."}
    }
    return result

def _prepare_create(user_id,thread_id,path,content):
    return _swrlz_authorization_response(
        user_id,thread_id,_swrlz_prior_create(user_id,thread_id,path,content))

def _prepare_update(user_id,thread_id,path,content):
    return _swrlz_authorization_response(
        user_id,thread_id,_swrlz_prior_update(user_id,thread_id,path,content))
'''

HTML_PATCH=r'''}else if(widget.kind==="github-authorization"){
            const message=document.createElement("p");
            message.textContent=String(data.purpose||"GitHub authorization is required.");
            card.appendChild(message);
            const authorizeUrl=String(data.authorizeUrl||"");
            if(authorizeUrl==="/api/github/start?access=public-write"){
              const authorize=document.createElement("button");
              authorize.type="button";authorize.textContent="Authorize GitHub";
              authorize.addEventListener("click",()=>{
                if(accountUser)location.assign(authorizeUrl);
              });
              card.appendChild(authorize);
            }
          }else if(widget.kind==="github-change-review"){'''

def patch_actions(source):
    assert AUTH_MARK not in source
    assert "def _prepare_update(" in source and "def _prepare_create(" in source
    assert "def expire_interrupted(" in source
    result=source.rstrip()+"\n"+AUTH_ACTIONS+"\n"
    ast.parse(result)
    return result

def patch_html(source):
    assert 'id="swrlz-request-first-github-v1"' not in source
    marker='}else if(widget.kind==="github-change-review"){'
    assert source.count(marker)==1
    assert source.count("</head>")==1
    # Retain connection and repository selection for optional manual management,
    # but remove permission-selection controls from the visible workflow.
    styles=('<style id="swrlz-request-first-github-v1">'
            '#githubCheckOperation,#githubCheckAccess,#githubAuthorizeAccess,'
            'label[for="githubCheckOperation"]{display:none!important}'
            '</style>')
    result=source.replace("</head>",styles+"\n</head>",1)
    result=result.replace(marker,HTML_PATCH,1)
    return result

def patch_connection(source):
    assert 'swrlz-request-first-github-auth-v1' not in source
    # A user without an existing connection can connect normally, without
    # choosing a permission tier. GitHub still owns the OAuth consent screen.
    assert 'def start(request: Request, access: str = "read"):' in source
    return source.replace(
        'def start(request: Request, access: str = "read"):',
        'def start(request: Request, access: str = "read"):\n'
        '    # swrlz-request-first-github-auth-v1: default to read; escalate only\n'
        '    # when a requested write actually needs GitHub OAuth consent.',
        1)

def digest(b):return hashlib.sha256(b).hexdigest()

def prepare():
    api=HfApi()
    rev=api.repo_info(SPACE,repo_type="space").sha
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    assert {ACTIONS,HTML,CONNECTION}.issubset(files)
    before={p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev)).read_bytes()
            for p in (ACTIONS,HTML,CONNECTION)}
    after={
        ACTIONS:patch_actions(before[ACTIONS].decode()).encode(),
        HTML:patch_html(before[HTML].decode()).encode(),
        CONNECTION:patch_connection(before[CONNECTION].decode()).encode(),
    }
    return rev,before,after

def main(mode):
    if mode=="selftest":
        sample='def _prepare_update():pass\ndef _prepare_create():pass\ndef expire_interrupted():pass\n'
        assert AUTH_MARK in patch_actions(sample)
        assert "github-authorization" in patch_html('<head></head>}else if(widget.kind==="github-change-review"){')
        print("REQUEST_FIRST_PATCH_SELFTEST_PASS",flush=True);return
    if mode=="verify":
        api=HfApi()
        rev=api.repo_info(SPACE,repo_type="space").sha
        a=Path(hf_hub_download(SPACE,ACTIONS,repo_type="space",revision=rev)).read_text()
        h=Path(hf_hub_download(SPACE,HTML,repo_type="space",revision=rev)).read_text()
        assert AUTH_MARK in a and 'id="swrlz-request-first-github-v1"' in h
        print("REQUEST_FIRST_LIVE_SOURCE_VERIFIED",rev,flush=True);return
    rev,before,after=prepare()
    ROOT.mkdir(parents=True,exist_ok=True)
    for p,raw in before.items():
        (ROOT/p).parent.mkdir(parents=True,exist_ok=True)
        (ROOT/p).write_bytes(raw)
    manifest={"beforeRevision":rev,"before":{p:digest(v) for p,v in before.items()},
              "after":{p:digest(v) for p,v in after.items()}}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print("REQUEST_FIRST_PREFLIGHT",json.dumps(manifest),flush=True)
    if mode=="snapshot":return
    assert mode=="publish"
    assert os.getenv("SWRLZ_GITHUB_REQUEST_FIRST_APPROVED")=="1"
    token=os.getenv("HF_TOKEN")
    assert token,"Missing HF_TOKEN"
    api=HfApi(token=token)
    assert api.repo_info(SPACE,repo_type="space").sha==rev,"Live revision changed"
    operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw))
                for p,raw in after.items()]
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=operations,
        commit_message="feat(§C): request-first GitHub OAuth, write preview approval")
    new_rev=commit.oid
    for p,raw in after.items():
        got=Path(hf_hub_download(SPACE,p,repo_type="space",revision=new_rev,token=token)).read_bytes()
        assert got==raw,"Release readback mismatch: "+p
    print("REQUEST_FIRST_PUBLISHED",new_rev,flush=True)

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["selftest","snapshot","publish","verify"])
    main(parser.parse_args().mode)
