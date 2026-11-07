/* Canonical §C multimedia composer regression: no live credentials or devices. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const version=fs.readFileSync("chat/§wyrlz/VERSION.txt","utf8").trim();
assert.equal(version,"1.1.28");
assert.ok(html.includes('<meta name="swrlz-chat-version" content="'+version+'">'));
assert.ok(html.includes('const SWRLZ_CHAT_VERSION = "'+version+'";'));

for(const id of ["imagePickButton","imagePicker","imageAttachment","imageAttachmentThumbnail","imageRemoveButton","micButton","composerFeedback"]){
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id+" must exist once");
}
assert.match(html,/accept="image\/jpeg,image\/png,image\/webp"/);
assert.match(html,/imagePreviews=new Map\(\)/);
assert.match(html,/encodeImageForVision=attachment=>new Promise/);
assert.match(html,/fetch\("\/api\/lalm_station\/vision"/);
assert.match(html,/description=await requestVisionDescription\(attachment,draftText,activity\)/);
assert.match(html,/const startVisionActivity=\(attachment,question\)=>/);
assert.match(html,/activity\.jobId=String\(result\.jobId\)/);
assert.match(html,/cancel\.textContent="Cancel analysis"/);
assert.match(html,/\/api\/lalm_station\/vision\/cancel/);
assert.match(html,/\["FAILED","CANCELLED"\]\.includes\(state\?\.phase\)/);
assert.match(html,/body:JSON\.stringify\(\{jobId\}\)/);
assert.match(html,/queued behind the local image worker/);
assert.match(html,/const visionSleep=\(ms,signal\)=>/);
assert.match(html,/\/api\/lalm_station\/vision\/status\?jobId=/);
assert.match(html,/const regionDetail=\(state\.phase==="ANALYZING"&&state\.activeRegion&&/);
assert.match(html,/state\.activeRegion!=="Whole-scene synthesis"/);
assert.match(html,/activity\.update\(state\.phase\|\|"QUEUED",regionDetail,\{/);
assert.match(html,/spatialRegionRecords:state\.spatialRegionRecords/);
assert.match(html,/activeVisionModel:state\.activeVisionModel/);
assert.match(html,/visionModelLoaded:state\.visionModelLoaded/);
assert.match(html,/Loaded local vision model:/);
assert.match(html,/spatialRegionFailures:state\.spatialRegionFailures/);
assert.match(html,/integratedOutcome:state\.integratedOutcome/);
assert.match(html,/elapsedSeconds:state\.elapsedSeconds/);
assert.match(html,/phaseElapsedSeconds:state\.phaseElapsedSeconds/);
assert.match(html,/const durationText=seconds=>/);
assert.match(html,/activity\.interval=setInterval\(\(\)=>activity\.tick\(\),1000\)/);
assert.match(html,/activity\.stopClock\(\);activity\.root\.remove\(\)/);
assert.match(html,/state\?\.code==="VISION_JOB_NOT_FOUND"/);
assert.match(html,/jobId=await acceptJob\(\)/);
assert.match(html,/Connection interrupted\. Reconnecting to the same image job automatically/);
assert.match(html,/The local CPU queue is full\. Retrying automatically/);
assert.ok(!html.includes("Date.now()-started>6*60*1000"),"never abort still-running CPU image at six minutes");
assert.ok(!html.includes("Press Send again to resume checking"),"no manual resend required for continued polling");
assert.match(html,/activity\.update\("SENDING"\)/);
assert.match(html,/activity\.update\("RESPONDING"\)/);
assert.match(html,/activity\.update\(activity\.abort\.signal\.aborted\?"STOPPED":"ERROR",detail\)/);
assert.ok(!html.includes("Analyzing image…"),"no opaque composer-only image operation");
assert.match(html,/prompt:text,threadId:submission\.threadId/);
assert.match(html,/imagePreviews\.set\(userMessageId,attachment\.url\)/);
assert.match(html,/recognition\.onresult=event=>/);
assert.match(html,/prompt\.value=\(original\+separator\+transcript\)/);
assert.match(html,/prompt\.dispatchEvent\(new Event\("input",\{bubbles:true\}\)\)/);
assert.match(html,/window\.SpeechRecognition\|\|window\.webkitSpeechRecognition/);
assert.match(html,/if\(speechRecognition\)\{speechRecognition\.stop\(\);return;\}/);
assert.match(html,/if\(\(!draftText&&!attachment\)\|\|stationBusy\(\)\)return false/);
assert.match(html,/if\(\(!prompt\.value\.trim\(\)&&!selectedImage\)\|\|stationBusy\(\)\)return/);
assert.match(html,/const restorePendingVisionDraft=\(\)=>/);
assert.match(html,/if\(provisionalThread&&provisionalMessageId\)/);
assert.match(html,/m\.id!==provisionalMessageId/);
assert.match(html,/if\(originalDraft&&!imageThreadCreated&&restoreDraft\)\{/);
assert.match(html,/activity\.onAccepted=async\(\)=>/);
assert.match(html,/await activity\.onAccepted\?\.\(\)/);
assert.match(html,/if\(originalDraft&&draftThread\)\{/);
assert.match(html,/const saved=await mutateChat\(\[/);
assert.match(html,/\{type:"UPSERT_THREAD",threadId:id,title,pinned:false,createdAt:now\}/);
assert.match(html,/\{type:"SET_CURRENT_THREAD",threadId:id\}/);
assert.match(html,/imageThreadCreated=true/);
assert.match(html,/activity\.originDraft=false;activity\.originThreadId=id/);
assert.match(html,/messageList\.appendChild\(activity\.root\)/);
assert.match(html,/if\(!chatThreads\.some\(t=>t\.id===id\)\)\{/);
assert.match(html,/const newImageThread=imageThreadCreated&&!draftThread&&activeThreadId===imageThreadId/);
assert.match(html,/if\(originalDraft&&!imageThreadCreated&&restoreDraft\)/);
assert.match(html,/activity\.onAccepted\?\.\(\)/);
assert.match(html,/if\(prompt\.value\.trim\(\)===draftText\)prompt\.value=""/);
assert.match(html,/if\(selectedImage===attachment\)selectedImage=null/);
assert.match(html,/if\(!selectedImage\)\{selectedImage=attachment;updateImagePreview\(\);\}/);
assert.match(html,/if\(!sendAcknowledged\)\{[\s\S]*?restorePendingVisionDraft\(\)/);
assert.match(html,/if\(activity\.threadAccepted\)return/);
assert.match(html,/integratedObservation:state\.integratedObservation/);
assert.match(html,/observed==="FUSION_PREFILL"/);
const stagedIndex=html.indexOf("visionDraftHeld=true;\n            if(prompt.value.trim()===draftText)");
const inferenceIndex=html.indexOf("description=await requestVisionDescription(attachment,draftText,activity)");
assert.ok(stagedIndex>=0&&inferenceIndex>stagedIndex,
  "image and prompt move into visible pending card before uploading/inferring");
assert.match(html,/const restorePendingVisionDraft=\(\)=>/);
assert.match(html,/const encodeImageForVision=attachment=>new Promise/);
assert.match(html,/const reader=new FileReader\(\)/);
assert.match(html,/reader\.readAsDataURL\(file\)/);
assert.match(html,/image=await encodeImageForVision\(attachment\)/);
assert.ok(!html.includes("canvas.toDataURL"),"client must not recompress source before upload");
assert.ok(!html.includes("img.naturalWidth*scale"),"client must not downscale source before upload");
assert.match(html,/originalBytesPreserved:state\.originalBytesPreserved/);
assert.match(html,/sourceWidth:state\.sourceWidth/);
assert.match(html,/sourceHeight:state\.sourceHeight/);
assert.match(html,/Original received by server/);
for(const id of ["imageVisionLevelSelect"]){
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1);
}
assert.match(html,/analysisLevels:Math\.max\(1,Math\.min\(3,Number\(attachment\.analysisLevels\)\|\|2\)\)/);
assert.match(html,/option value="1"/);
assert.match(html,/option value="2" selected/);
assert.match(html,/option value="3"/);
assert.match(html,/observed==="LEVEL3_PREFILL"/);
assert.match(html,/observed==="LEVEL3_DECODING"/);
assert.match(html,/showLevels\(records,selected\)/);
assert.match(html,/levelRecords:state\.levelRecords/);

assert.ok(!html.includes("1600/Math.max(img.naturalWidth"),"do not encode unused pixels at 1600px");
assert.match(html,/if\(attachment\)\{[\s\S]*?imagePreviews\.set\(userMessageId,attachment\.url\)/);

const inline=html.match(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/i);
assert.ok(inline,"Canonical inline Chat controller exists");
new vm.Script(inline[1],{filename:"swrlz-chat-media-inline.js"});

const station=fs.readFileSync("hf_space/station.py","utf8");
assert.match(station,/install_chat_vision\(app, _require_vision_account\)/);
assert.match(station,/startsWith\('google:'\)|startswith\('google:'\)/);
const backend=fs.readFileSync("hf_space/chat_vision.py","utf8");
assert.match(backend,/phaseElapsedSeconds/);
assert.match(backend,/elapsedSeconds/);
assert.match(backend,/max_tokens=tokens/);
assert.match(backend,/generate\(image, prompt, MAX_VISION_OUTPUT_TOKENS\)/);
assert.ok(backend.includes('DETAIL_RETRY_SIDE = 768'));
assert.ok(backend.includes('DETAIL_RETRY_TOKENS = 224'));
assert.match(backend,/MAX_BODY_BYTES = 12_000_000/);
assert.match(backend,/MAX_IMAGE_BYTES = 8 \* 1024 \* 1024/);
assert.match(backend,/focus_center=True/);
assert.match(backend,/def _source_image_metadata\(/);
assert.match(html,/observed==="DETAIL_RETRY"/);
assert.match(html,/observed==="DETAIL_PREFILL"/);
assert.match(html,/observed==="DETAIL_DECODING"/);
assert.match(backend,/WATCH_LEASE_SECONDS = 20 \* 60/);
assert.match(html,/if\(event\.type==="HEARTBEAT"\)continue/);
assert.match(html,/document\.addEventListener\("resume",keepStationHydrated\)/);
assert.match(station,/next_heartbeat=time\.monotonic\(\)\+15\.0/);
assert.match(backend,/def _cancel_unwatched_jobs\(/);
assert.match(backend,/def cancel_vision\(/);
assert.match(backend,/stream=True/);
assert.match(backend,/raise VisionCancelled\(\)/);
// The image analyzer has only Qwen3-VL, with no legacy alternate backend.
assert.ok(backend.includes('MODEL_REPO = "Qwen/Qwen3-VL-4B-Instruct-GGUF"'));
assert.ok(backend.includes('VISION_MODEL_VARIANT = "qwen3-vl-4b"'));
assert.ok(!backend.includes("MTMDChatHandler"));
assert.ok(!backend.includes("ggml-org/SmolVLM"));
assert.ok(!backend.includes("SWRLZ_VISION_API_KEY"),"no paid inference credentials needed");
assert.ok(!backend.includes("router.huggingface.co"),"no paid inference provider calls");
assert.match(backend,/MAX_IMAGE_PIXELS = 16_000_000/);
assert.match(backend,/def _run_vision_job\(/);
assert.match(backend,/def _detail_regions\(/);
assert.match(backend,/spatialRegionRecords/);
assert.match(backend,/referenceProgress/);
assert.match(html,/vision-reference-findings/);
assert.match(html,/showReferenceFindings\(timing\)/);
assert.match(html,/referenceProgress:state\.referenceProgress/);
assert.match(html,/Final modeling description/);
assert.match(html,/Read full observation/);
assert.match(html,/vision-reference-more/);
// The final image analysis is rendered into a semantic visual reference,
// using ONLY the model's own text: no fabricated view counts or 3D geometry.
assert.match(html,/const buildVisionReferenceReport=raw=>/);
assert.match(html,/vision-report-grid/);
assert.match(html,/vision-report-view/);
assert.match(html,/vision-report-crops/);
assert.match(html,/vision-report-raw/);
assert.match(html,/imageText\.slice\(imageStart\+VISION_START\.length,-VISION_END\.length\)/);
assert.match(html,/const visual=buildVisionReferenceReport\(originalText\)/);
assert.match(html,/visionReportOpenState\.get\(stateKey\):true/);
assert.match(html,/\.user-vision-plain\{white-space:pre-wrap/);
assert.ok(!html.includes("crop.innerHTML="),"model observations must never be rendered as untrusted HTML");

const visualStart=html.indexOf("const visionReportOpenState=new Map();");
const visualEnd=html.indexOf("let visionActivity=null;",visualStart);
assert.ok(visualStart>0&&visualEnd>visualStart,"extract the actual inline report builder");
const element=(tag)=>({
  tag,className:"",textContent:"",dataset:{},children:[],attrs:{},
  append(...children){this.children.push(...children);},
  setAttribute(key,value){this.attrs[key]=value;}
});
const renderReport=vm.runInNewContext(
  html.slice(visualStart,visualEnd)+"\n buildVisionReferenceReport",
  {document:{createElement:element}}
);
const fixture=[
  "Character reference · local model observation (accuracy unverified)",
  "Subject and views: One mage shown in front, left side, right side, back, and top.",
  "Silhouette and anatomy: Chibi proportions and two white braids.",
  "Clothing and surface detail: Purple robe with gold embroidery.",
  "Props and small features: One purple crystal-topped staff.",
  "Visibility limits: Some surfaces are obscured; do not infer invisible geometry.",
  "",
  "Focused image details (unverified source-crop observations):",
  "- Upper-left figure detail: White braids and a crystal staff.",
  "- Central outfit and prop detail: Robe trim and a pouch."
].join("\n");
const report=renderReport(fixture);
assert.equal(report.className,"vision-report");
const reportHead=report.children.find(x=>x.className==="vision-report-head");
const angleStrip=reportHead.children.find(x=>x.className==="vision-report-views");
assert.deepEqual(Array.from(angleStrip.children,x=>x.textContent),
  ["Front","Left side","Right side","Back","Top"]);
const reportGrid=report.children.find(x=>x.className==="vision-report-grid");
assert.equal(reportGrid.children.length,5);
assert.deepEqual(Array.from(reportGrid.children,x=>x.dataset.kind),
  ["subject","anatomy","materials","props","limits"]);
assert.equal(reportGrid.children[3].children[1].textContent,"One purple crystal-topped staff.");
const cropGroup=report.children.find(x=>x.className==="vision-report-crops");
assert.equal(cropGroup.children.length,3,"two actual crop records and one summary");
const sourcePanel=report.children.find(x=>x.className==="vision-report-raw");
assert.equal(sourcePanel.children[1].textContent,fixture,"raw model text remains inspectable");
assert.equal(renderReport("A cat sitting on a table."),null,
  "simple image results keep their ordinary text layout");
// The image analysis card must not trap touch scrolling in a nested 72dvh
// scrollport; swiping anywhere on it scrolls the single chat viewport.
assert.match(html,/\.vision-work-card\{[^}]*max-height:none;overflow:visible;touch-action:pan-y/s);
assert.ok(!html.includes('max-height:72dvh;overflow-y:auto;overscroll-behavior:contain'),"no nested image-card scroll trap");
// Both an in-progress attachment and the committed chat image get the same
// keyboard/Android-tappable expanded image preview, with native Escape close.
assert.match(html,/const openVisionImagePreview=\(imageUrl/);
assert.match(html,/dialog\.showModal\(\);close\.focus\(\)/);
assert.match(html,/dialog\.addEventListener\("close",\(\)=>dialog\.remove\(\)/);
assert.match(html,/previewButton\.addEventListener\("click",\(\)=>openVisionImagePreview\(attachment\.url/);
assert.match(html,/expand\.addEventListener\("click",\(\)=>openVisionImagePreview\(previewURL/);
assert.match(html,/vision-image-dialog-close/);
// Zoom must preserve the pixel selected by the user's tap, not start at (0,0).
assert.match(html,/const fractionX=Math\.max\(0,Math\.min\(1,\(event\.clientX-before\.left\)\/before\.width\)\)/);
assert.match(html,/const fractionY=Math\.max\(0,Math\.min\(1,\(event\.clientY-before\.top\)\/before\.height\)\)/);
assert.match(html,/dialog\.scrollLeft\+=after\.left\+fractionX\*after\.width-event\.clientX/);
assert.match(html,/dialog\.scrollTop\+=after\.top\+fractionY\*after\.height-event\.clientY/);
assert.match(html,/image\.style\.height=image\.naturalHeight\+"px"/);
assert.match(backend,/proposals = proposals\[:2\]/);
assert.match(backend,/about 80 to 120 words/);
assert.match(backend,/Focused image details/);
assert.ok(!backend.includes('"\\n\\nSource observations:\\n"'),"final response must not repeat the whole raw overview");
assert.ok(!html.includes('Checking for contradictions'),"internal inference consistency checks stay hidden");
assert.match(backend,/def vision_status\(/);
assert.match(backend,/threading\.Thread\(/);
assert.match(backend,/ACTIVE_PHASES/);
assert.match(backend,/retryAfterSeconds/);
assert.match(backend,/\@app\.get\("\/api\/lalm_station\/vision\/status"/);
assert.match(backend,/MODEL_REVISION = "[0-9a-f]{40}"/);
console.log("Chat media v1: local vision job progress, chat composer, and inline JS PASS");
