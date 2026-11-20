#!/usr/bin/env python3
"""§C 1.1.42: copy Android image bytes while picker is valid, one original-resolution Qwen pass.

Fail closed on source drift; preserve prior source and verify served HF revision.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, re, time, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
START_REV="44330852bf147887398f0ca3eabb99d66d93db4f"
UI="chat/§wyrlz/index.html"
VISION="chat_vision.py"
PATHS=(UI,VISION)
EXPECTED={UI:"24b63ba8d45699f24165ee1b04bec036d715e14176b2ccf38edb130a7841c2fb",
          VISION:"83506b87f7551de8fd61b6318adc3ef8f8143a9006716f8c3e8be15bfe689133"}
BASE="https://kamiloki-swyrlz.hf.space"
BACKUP=Path("reports/swrlz-vision-original-v1142")
MARK="swrlz-vision-original-v1142"

def sha(v):return hashlib.sha256(v).hexdigest()
def emit(event,**kwargs):print("SWRLZ_VISION_1142 "+json.dumps({"event":event,**kwargs},sort_keys=True),flush=True)
def once(text,source,replacement,tag):
 count=text.count(source)
 if count!=1:raise RuntimeError(f"SOURCE_DRIFT_{tag}: expected 1, got {count}")
 return text.replace(source,replacement,1)
def regex_once(text,pattern,replacement,tag):
 result,count=re.subn(pattern,lambda _:replacement,text,count=1,flags=re.S)
 if count!=1:raise RuntimeError(f"SOURCE_DRIFT_{tag}")
 return result

class IdParser(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):
  key=dict(attrs).get("id")
  if key:self.ids.append(key)
def ids(text):
 parser=IdParser();parser.feed(text);return parser.ids

def patch_ui(raw):
 text=raw.decode("utf-8")
 if text.count('swrlz-chat-version" content="1.1.41"')!=1:
  raise RuntimeError("Not the approved v1.1.41 live Chat source")
 if MARK in text:raise RuntimeError("Already patched")
 old_ids=ids(text)
 text=once(text,'swrlz-chat-version" content="1.1.41"',
                'swrlz-chat-version" content="1.1.42"',"version")
 old='''          <label class="vision-level-label" for="imageVisionLevelSelect">Vision
            <select id="imageVisionLevelSelect" aria-label="Vision analysis levels">
              <option value="1" selected>L1 · Fast (1 pass)</option>
              <option value="2">L2 · Multi-view (slow)</option>
              <option value="3">L3 · Compare all (slow)</option>
            </select>
          </label>'''
 new='''          <span class="vision-level-label" title="Qwen3.5-9B analyzes original image pixels; internal model tokenization may vary">Qwen 9B · Original pixels</span>'''
 text=once(text,old,new,"dropdown")
 text=once(text,'      const imageVisionLevelSelect=document.getElementById("imageVisionLevelSelect");\n',"","dropdown-binding")
 text=once(text,'          imageVisionLevelSelect.value=String(selectedImage.analysisLevels||1);\n',"","dropdown-render")
 picker_start='      imagePicker.addEventListener("change",()=>{'
 picker_end='      imageRemoveButton.addEventListener("click",()=>{removeSelectedImage();composerNotice("");});'
 original_picker='''      imagePicker.addEventListener("change",()=>{
        const file=imagePicker.files&&imagePicker.files[0];
        imagePicker.value="";
        if(!file)return;
        if(!["image/jpeg","image/png","image/webp"].includes(file.type)||file.size>8*1024*1024){
          composerNotice("Choose a JPEG, PNG, or WebP under 8 MB.",true);return;
        }
        removeSelectedImage();
        selectedImage={file,url:URL.createObjectURL(file),analysisLevels:1};
        updateImagePreview();composerNotice("");
      });
      imageVisionLevelSelect.addEventListener("change",()=>{
        if(selectedImage)selectedImage.analysisLevels=Number(imageVisionLevelSelect.value)||1;
        if(imageVisionLevelSelect.value==="3")composerNotice("L3 compares three full-image passes plus optional details; local CPU processing can take several minutes.");
        else if(imageVisionLevelSelect.value==="2")composerNotice("L2 analyzes individual views and then combines them; a five-view reference can take 6+ minutes on the local CPU.");
        else composerNotice("");
      });'''
 new_picker='''      // swrlz-vision-original-v1142: copy bytes while the Android picker
      // owns the file. Resetting the input first can invalidate its handle.
      let imagePickEpoch=0;
      imagePicker.addEventListener("change",async()=>{
        const file=imagePicker.files&&imagePicker.files[0];
        const epoch=++imagePickEpoch;
        if(!file)return;
        if(!["image/jpeg","image/png","image/webp"].includes(file.type)||
           !file.size||file.size>8*1024*1024){
          imagePicker.value="";
          composerNotice("Choose a JPEG, PNG, or WebP under 8 MB.",true);return;
        }
        composerNotice("Reading original image…");
        try{
          const buffer=await file.arrayBuffer();
          const bytes=new Uint8Array(buffer);
          if(bytes.byteLength!==file.size)throw new Error("Incomplete source file");
          const png=bytes.length>=8&&[137,80,78,71,13,10,26,10].every((v,i)=>bytes[i]===v);
          const jpeg=bytes.length>=3&&bytes[0]===255&&bytes[1]===216&&bytes[2]===255;
          const webp=bytes.length>=12&&String.fromCharCode(...bytes.subarray(0,4))==="RIFF"&&
            String.fromCharCode(...bytes.subarray(8,12))==="WEBP";
          if(!((file.type==="image/png"&&png)||(file.type==="image/jpeg"&&jpeg)||
               (file.type==="image/webp"&&webp)))
            throw new Error("Image contents do not match the chosen file type");
          if(epoch!==imagePickEpoch)return;
          const stableFile={name:file.name,type:file.type,size:bytes.length};
          const url=URL.createObjectURL(new Blob([bytes],{type:file.type}));
          removeSelectedImage();
          selectedImage={file:stableFile,bytes,url};
          updateImagePreview();composerNotice("");
        }catch(error){
          if(epoch===imagePickEpoch)
            composerNotice("Could not read this image from the device. Select it again or use a local copy.",true);
          console.warn("SWYRLZ_IMAGE_PICK_READ_FAILED",error?.name||"Error");
        }finally{if(epoch===imagePickEpoch)imagePicker.value="";}
      });'''
 text=once(text,original_picker,new_picker,"picker-copy")
 old_encoder='''      const encodeImageForVision=attachment=>new Promise((resolve,reject)=>{
        // CLIENT → SERVER: transmit original encoded file bytes unchanged.
        // Resizing and optional detail crops belong to the server only.
        // Never reconstruct the image through canvas or JPEG conversion.
        const file=attachment?.file;
        if(!file||!["image/jpeg","image/png","image/webp"].includes(file.type)||
           !file.size||file.size>8*1024*1024){
          reject(new Error("Choose a valid JPEG, PNG, or WebP under 8 MB."));return;
        }
        const reader=new FileReader();
        reader.onload=()=>{
          if(typeof reader.result==="string"&&reader.result.startsWith("data:"+file.type+";base64,"))
            resolve(reader.result);
          else reject(new Error("Unable to read the original image bytes."));
        };
        reader.onerror=()=>reject(new Error("Unable to read the original image bytes."));
        reader.onabort=()=>reject(new Error("Image file read was cancelled."));
        reader.readAsDataURL(file);
      });'''
 new_encoder='''      const encodeImageForVision=attachment=>{
        // CLIENT → SERVER: encode exact original bytes captured before picker
        // release. No FileReader reopen, canvas resize or JPEG conversion.
        const bytes=attachment?.bytes, file=attachment?.file;
        if(!(bytes instanceof Uint8Array)||!file||
           !["image/jpeg","image/png","image/webp"].includes(file.type)||
           bytes.byteLength!==file.size||!bytes.length||bytes.length>8*1024*1024)
          throw new Error("Original image data is unavailable. Select the image again.");
        const segments=[];
        for(let i=0;i<bytes.length;i+=16384)
          segments.push(String.fromCharCode(...bytes.subarray(i,i+16384)));
        return "data:"+file.type+";base64,"+btoa(segments.join(""));
      };'''
 text=once(text,old_encoder,new_encoder,"encode")
 text=once(text,'        const image=await encodeImageForVision(attachment);',
                     '        const image=encodeImageForVision(attachment);',"encode-call")
 text=once(text,'          analysisLevels:Math.max(1,Math.min(3,Number(attachment.analysisLevels)||1)),',
                     '          analysisLevels:1,',"request")
 text=once(text,'''            if(phase==="ANALYZING"&&timing?.requestedLevels){
              title.textContent="Image message · level "+Math.max(1,Number(timing.activeLevel)||1)+"/"+timing.requestedLevels;
            }''','''            if(phase==="ANALYZING")title.textContent="Image message · Qwen 9B · Original image";''',"status-label")
 text=text.replace('"Initial L1 overview · "', '"Initial Qwen observation · "')
 text=text.replace('"Initial L1 overview · analyzing additional views"','"Analyzing image"')
 if ids(text)!=[item for item in old_ids if item!="imageVisionLevelSelect"]:
  raise RuntimeError("Unexpected component ID change")
 if 'imageVisionLevelSelect' in text:raise RuntimeError("Mode selector still referenced")
 if 'Unable to read the original image bytes' in text:raise RuntimeError("Expired-file reader still present")
 if text.count(MARK)!=1:raise RuntimeError("Marker count")
 return text.encode("utf-8")

def patch_vision(raw):
 text=raw.decode("utf-8")
 if MARK in text:raise RuntimeError("Already patched")
 text=once(text,"# One image-analysis engine only. Older Space SWRLZ_VISION_MODEL settings",'''# swrlz-vision-original-v1142: original source data URL is sent to Qwen,
# not a downscaled JPEG. Internal projector tokenization remains model-owned.
# One image-analysis engine only. Older Space SWRLZ_VISION_MODEL settings''',"backend-marker")
 text=once(text,'def _run_vision_job(job_id: str, image: str, question: str, cancel_event: threading.Event, analysis_levels: int = 2) -> None:',
           'def _run_vision_job(job_id: str, image: str, question: str, cancel_event: threading.Event, analysis_levels: int = 1) -> None:',"job-default")
 text=once(text,'                      analysis_levels: int = 2) -> str:',
           '                      analysis_levels: int = 1) -> str:',"analysis-default")
 text=once(text,'''    if type(analysis_levels) is not int or analysis_levels not in (1, 2, 3):
        raise ValueError("VISION_LEVEL_INVALID")

    def check_cancel():''','''    if type(analysis_levels) is not int or analysis_levels not in (1, 2, 3):
        raise ValueError("VISION_LEVEL_INVALID")
    # Normalize legacy clients to one identical whole-image inference pass.
    analysis_levels = 1

    def check_cancel():''',"single-pass")
 text=once(text,'''        image = _prepare_image(image_url)
        check_cancel()
        report("LOADING_MODEL")''','''        # Forward exact original source pixels to the resident Qwen projector.
        # No application-level downsampling, lossy conversion or source crop.
        image = image_url
        check_cancel()
        report("LOADING_MODEL")''',"native-full-resolution")
 text=once(text,'        record(1, MODEL_INPUT_SIDE, MAX_VISION_OUTPUT_TOKENS,',
           '        record(1, max(source_meta["sourceWidth"], source_meta["sourceHeight"]), MAX_VISION_OUTPUT_TOKENS,',"report-true-source")
 text=once(text,'''            analysis_levels = payload.get("analysisLevels", 2)
            if type(analysis_levels) is not int or analysis_levels not in (1, 2, 3):
                raise ValueError("VISION_LEVEL_INVALID")''','''            requested_levels = payload.get("analysisLevels", 1)
            if type(requested_levels) is not int or requested_levels not in (1, 2, 3):
                raise ValueError("VISION_LEVEL_INVALID")
            analysis_levels = 1''',"normalize-api")
 text=once(text,'"requestedLevels": job.get("requestedLevels", 2)',
           '"requestedLevels": job.get("requestedLevels", 1)',"status-default")
 ast.parse(text,filename=VISION)
 if text.count(MARK)!=1:raise RuntimeError("Backend marker count")
 if 'VISION_MODEL_VARIANT = "qwen3.5-9b"' not in text or 'PROJECTOR_FILE = "mmproj-F16.gguf"' not in text:
  raise RuntimeError("Wrong vision engine")
 return text.encode("utf-8")

def hf():
 token=os.getenv("HF_TOKEN")
 if not token:raise RuntimeError("Space deployment token missing")
 return HfApi(token=token)

def get(client,revision):
 return {p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=revision,token=client.token)).read_bytes() for p in PATHS}

def preflight(client):
 head=client.repo_info(SPACE,repo_type="space").sha
 if head!=START_REV:raise RuntimeError("Space head drift: "+head)
 originals=get(client,head)
 hashes={p:sha(v) for p,v in originals.items()}
 if hashes!=EXPECTED:raise RuntimeError("Exact source fingerprint mismatch: "+str(hashes))
 patched={UI:patch_ui(originals[UI]),VISION:patch_vision(originals[VISION])}
 BACKUP.mkdir(parents=True,exist_ok=True)
 for name in PATHS:
  for stage,content in (("original",originals[name]),("candidate",patched[name])):
   path=BACKUP/stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
 manifest={"space":SPACE,"sourceRevision":head,"paths":list(PATHS),
           "before":hashes,"after":{p:sha(patched[p]) for p in PATHS},
           "originalModel":"twoody/Qwen3.5-9B-GGUF",
           "projector":"mmproj-F16.gguf"}
 (BACKUP/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
 emit("PREFLIGHT_OK",revision=head,hashes=manifest["after"])
 return patched

def commit(client,revision,data,message):
 response=client.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
  operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v)) for p,v in data.items()],
  commit_message=message)
 return str(response.oid or client.repo_info(SPACE,repo_type="space").sha)

def served():
 try:
  request=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?release=1142",
    headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-Original-Vision-1142"})
  with urllib.request.urlopen(request,timeout=20) as res:
   content=res.read(900000).decode("utf-8",errors="replace")
   return (res.status==200 and 'swrlz-chat-version" content="1.1.42"' in content
           and MARK in content)
 except (urllib.error.URLError,TimeoutError):return False

def verify(client,revision):
 last=None;stable=0
 for i in range(1,71):
  if client.repo_info(SPACE,repo_type="space").sha!=revision:
   raise RuntimeError("Concurrent Space update; abort")
  state=client.get_space_runtime(SPACE)
  stage=str(state.stage).upper().split(".")[-1]
  serving=str((state.raw or {}).get("sha") or "")
  ok=served() if stage=="RUNNING" and serving==revision else False
  current=(stage,serving,ok)
  if current!=last:
   emit("RUNTIME_GATE",attempt=i,stage=stage,serving=serving,served=ok)
   last=current
  if stage=="RUNTIME_ERROR":raise RuntimeError("HF runtime error")
  if stage=="RUNNING" and serving==revision and ok:
   stable+=1
   if stable>=2:
    emit("LIVE_ACCEPTED",revision=revision,version="1.1.42",path="/chat/%C2%A7wyrlz")
    return
  else:stable=0
  time.sleep(12)
 raise RuntimeError("Live revision was not accepted")

def publish(client):
 if os.getenv("SWRLZ_VISION_1142_APPROVED")!="yes":
  raise PermissionError("Explicit authorized release flag required")
 manifest=json.loads((BACKUP/"manifest.json").read_text())
 old={p:(BACKUP/"original"/p).read_bytes() for p in PATHS}
 new={p:(BACKUP/"candidate"/p).read_bytes() for p in PATHS}
 if (manifest["space"]!=SPACE or manifest["sourceRevision"]!=START_REV or
     {p:sha(v) for p,v in old.items()}!=manifest["before"] or
     {p:sha(v) for p,v in new.items()}!=manifest["after"]):
  raise RuntimeError("Tampered or stale snapshot")
 if new!={UI:patch_ui(old[UI]),VISION:patch_vision(old[VISION])}:
  raise RuntimeError("Candidate differs from source-preserving patch")
 if client.repo_info(SPACE,repo_type="space").sha!=START_REV or get(client,START_REV)!=old:
  raise RuntimeError("Live source changed after inspection")
 revision=None
 try:
  revision=commit(client,START_REV,new,"§C 1.1.42: fixed Android picker image bytes + single original-pixel Qwen 9B inference")
  emit("PUBLISHED",revision=revision)
  if get(client,revision)!=new:raise RuntimeError("Postcommit exact file mismatch")
  emit("EXACT_READBACK_PASS",revision=revision)
  verify(client,revision)
 except Exception as error:
  emit("RELEASE_REJECTED",revision=revision,reason=str(error)[:260])
  if revision and client.repo_info(SPACE,repo_type="space").sha==revision:
   rollback=commit(client,revision,old,"Rollback §C 1.1.42 to exact pre-release source")
   emit("EXACT_SOURCE_ROLLBACK",revision=rollback)
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["publish"]):raise SystemExit("Use inspect or publish")
 client=hf()
 if sys.argv[1]=="inspect":preflight(client)
 else:publish(client)
