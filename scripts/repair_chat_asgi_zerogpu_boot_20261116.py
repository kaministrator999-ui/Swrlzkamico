#!/usr/bin/env python3
"""§C read-preserving repair: disable manual ZeroGPU scan incompatible with ASGI-mounted Gradio.
Must only run via approved, revision-pinned GitHub workflow. No hardware, files, accounts or model changes.
"""
import ast
import hashlib
import json
import os
import time
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
TARGET="kamiloki/Swyrlz"
EXPECTED_SHA="37209db8fc5b1ff16fc1ee15d5f18d5f25b6ab51"
OLD='    _report_zerogpu_startup()\n    _warm_backends()'
NEW='    # The ASGI-mounted /probe Blocks callbacks do not form the root Gradio\'s\n    # launch-time ZeroGPU registry. Do not manually invoke its scanner.\n    # Uvicorn still initializes the same native Station app and model warmup.\n    _warm_backends()'
def checked(api):
    obj=api.space_info(TARGET)
    stage=getattr(getattr(obj,"runtime",None),"stage",None)
    assert obj.sha==EXPECTED_SHA,("SPACE_REVISION_CHANGED",obj.sha)
    assert str(stage) in ("RUNTIME_ERROR","SpaceStage.RUNTIME_ERROR"),("SPACE_STATE_CHANGED",str(stage))
    return obj
def main():
    assert os.environ.get("SWRLZ_CHAT_REPAIR_APPROVED")=="yes","No owner approval supplied"
    token=os.environ.get("HF_TOKEN")
    assert token,"Missing existing HF_TOKEN; do not deploy"
    api=HfApi(token=token)
    checked(api)
    source=Path(hf_hub_download(TARGET,"app.py",repo_type="space",revision=EXPECTED_SHA,token=token)).read_text("utf8")
    assert source.count(OLD)==1,"Exact startup anchor drift"
    assert "app=gr.mount_gradio_app(station_app,demo,path=\"/probe\",ssr_mode=False)" in source
    assert "app=gr.mount_gradio_app(app,legacy[\"demo\"],path=\"/legacy\",ssr_mode=False)" in source
    assert "@spaces.GPU(duration=1)" in source and "_zg_button.click(fn=_zerogpu_registration_probe" in source
    assert "uvicorn.run(app,host=\"0.0.0.0\"" in source
    next_source=source.replace(OLD,NEW,1)
    ast.parse(next_source)
    before=hashlib.sha256(source.encode()).hexdigest()
    after=hashlib.sha256(next_source.encode()).hexdigest()
    print("SECHAT_BOOT_PREPARED="+json.dumps({"space":TARGET,"expectedSha":EXPECTED_SHA,"oldBytes":len(source.encode()),
      "newBytes":len(next_source.encode()),"oldDigest":before,"newDigest":after,"patchCount":1,
      "hardwareChanged":False,"secretsChanged":False,"modelChanged":False},sort_keys=True),flush=True)
    checked(api)
    result=api.create_commit(repo_id=TARGET,repo_type="space",
      operations=[CommitOperationAdd(path_in_repo="app.py",path_or_fileobj=next_source.encode("utf8"))],
      commit_message="§C: skip invalid manual ZeroGPU probe scan for mounted ASGI startup",
      parent_commit=EXPECTED_SHA)
    print("SECHAT_BOOT_COMMIT="+json.dumps({"oldSha":EXPECTED_SHA,"newSha":getattr(result,"oid",None),
      "file":"app.py","oldDigest":before,"newDigest":after},sort_keys=True),flush=True)
if __name__=="__main__":main()
