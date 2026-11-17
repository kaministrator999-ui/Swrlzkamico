#!/usr/bin/env python3
"""Repair Hugging Face static HTML attachment responses without changing §E.

The Space previously stored index/modeler as Git-LFS/Xet pointers. Xet GET
redirects were returning Content-Disposition: attachment, making Chrome
download the engine rather than render it. Publish these two *verified*
small HTML pages as ordinary Git blobs and protect that choice via the
Space's .gitattributes. Other media, JavaScript, and the verified source
receipt are not changed.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

REPO="kamiloki/swrlz-forge-moba"
FILES=("index.html","modeler.html")
MAX_BYTES=10_000_000

def sh(*args, cwd=None, env=None, capture=False):
    result=subprocess.run(args,cwd=cwd,env=env,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None,
                          check=True)
    return result.stdout if capture else None

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    token=os.environ.get("HF_TOKEN")
    if not token: raise SystemExit("HF_TOKEN secret is missing")
    hf=HfApi(token=token)
    actor=hf.whoami(token=token)["name"]
    with tempfile.TemporaryDirectory(prefix="swrlz-hf-html-") as temp:
        d=Path(temp)
        receipt_path=hf_hub_download(repo_id=REPO,repo_type="space",filename="SOURCE.json",token=token)
        receipt=json.loads(Path(receipt_path).read_text("utf8"))
        delivery=receipt.get("staticDelivery",{})
        manifest=json.loads((Path(__file__).resolve().parents[1]/"source-manifest.json").read_text("utf8"))
        if (delivery.get("mode")!="external-es-module" or
            receipt.get("sourceVersion")!=manifest.get("name") or
            receipt.get("finalSha256")!=manifest.get("finalSha256") or
            delivery.get("verifiedSourceSha256")!=manifest.get("finalSha256")):
            raise ValueError("Space is not the exact verified split release from the current source manifest")
        pages={}
        for path in FILES:
            file=hf_hub_download(repo_id=REPO,repo_type="space",filename=path,token=token)
            raw=Path(file).read_bytes()
            if not raw or len(raw)>=MAX_BYTES:
                raise ValueError(f"Unsafe HTML size: {path} = {len(raw)}")
            if sha(raw)!=delivery["indexSha256"]:
                raise ValueError(f"Published HTML SHA does not match sealed delivery: {path}")
            pages[path]=raw
        if pages["index.html"]!=pages["modeler.html"]:
            raise ValueError("Space routes have different HTML bodies")
        askpass=d/"askpass.sh"
        askpass.write_text(
          '#!/bin/sh\ncase "$1" in\n'
          '  *Username*) printf "%s" "$HF_GIT_USERNAME" ;;\n'
          '  *Password*) printf "%s" "$HF_TOKEN" ;;\n'
          '  *) exit 1 ;;\n'
          'esac\n',encoding="utf8")
        askpass.chmod(0o700)
        env=os.environ.copy()
        env.update(GIT_ASKPASS=str(askpass),HF_GIT_USERNAME=actor,
                   GIT_TERMINAL_PROMPT="0",GIT_LFS_SKIP_SMUDGE="1",
                   GIT_CONFIG_NOSYSTEM="0")
        remote="https://huggingface.co/spaces/"+REPO
        work=d/"space"
        sh("git","clone","--depth","1","--single-branch",
           remote,str(work),env=env)
        gitattributes=work/".gitattributes"
        existing=gitattributes.read_text("utf8") if gitattributes.exists() else ""
        if not existing.endswith("\n"):existing+="\n"
        marker="# §E static browser entrypoints are regular Git blobs, not LFS/Xet attachments."
        rules=(
          "/index.html -filter -diff -merge text\n"
          "/modeler.html -filter -diff -merge text\n"
        )
        if marker not in existing:
            gitattributes.write_text(existing+marker+"\n"+rules,"utf8")
        elif rules not in existing:
            raise ValueError("Existing §E entrypoint attributes conflict; inspect manually")
        for name,raw in pages.items():
            (work/name).write_bytes(raw)
        for name in FILES:
            attrs=sh("git","check-attr","filter","--",name,cwd=work,env=env,capture=True).decode()
            if "filter: unset" not in attrs and "filter: unspecified" not in attrs:
                raise ValueError(f"LFS filter still active for {name}: {attrs.strip()}")
        sh("git","config","user.name","§wyrl§ Engine release bot",cwd=work,env=env)
        sh("git","config","user.email","bot@users.noreply.github.com",cwd=work,env=env)
        sh("git","add",".gitattributes",*FILES,cwd=work,env=env)
        for name,raw in pages.items():
            staged=sh("git","show",":"+name,cwd=work,env=env,capture=True)
            if staged!=raw:
                raise ValueError(f"Git staged an LFS pointer instead of actual HTML: {name}")
        status=subprocess.run(["git","diff","--cached","--quiet"],cwd=work,env=env)
        if status.returncode==0:
            print("SE482_GIT_BLOBS_ALREADY_VERIFIED",flush=True);return
        if status.returncode!=1:raise ValueError("Cannot determine git staged changes")
        sh("git","commit","-m","§E: serve browser HTML as Git blobs, not Xet attachments",
           cwd=work,env=env)
        sh("git","push","origin","HEAD:main",cwd=work,env=env)
        print("SE482_HTML_GIT_BLOB_PUSH_OK",json.dumps({
            "files":{name:{"bytes":len(raw),"sha256":sha(raw)} for name,raw in pages.items()},
            "sourceSha256":receipt["finalSha256"],
            "space":REPO
        }),flush=True)

if __name__=="__main__":
    main()
