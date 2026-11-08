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
assert.match(html,/const visionRequestId=uid\("vision"\)/);
assert.match(html,/\.\.\.\(attachment&&activity\?\.jobId\?\{visionJobId:activity\.jobId\}:\{\}\)/);
assert.match(html,/const requestVisionDescription=async\(attachment,question,activity\)=>/);
assert.match(html,/analysisLevels:Math\.max\(1,Math\.min\(3,Number\(attachment\.analysisLevels\)\|\|2\)\),\s*visionRequestId/);
assert.match(html,/if\(result\.resumedExistingJob===true\)/);
assert.match(html,/Resumed a previously accepted upload; no new inference started/);
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
// User image message stays an attachment; model report appears once as §C's reply.
assert.ok(!html.includes("imageRegionEvidence"),"no source-crop card under the uploaded image");
assert.ok(!html.includes("user-vision-summary"),"saved model output must not expand under the image");
assert.ok(!html.includes("vision-model-report"),"no nested report-card stack");
assert.ok(!html.includes("showReferenceFindings(timing)"),"no duplicate interim observations");
assert.ok(!html.includes('const findings=document.createElement("section")'),"no interim final report");
assert.match(html,/const formatLegacyVisionReply=value=>/);
assert.match(html,/const visionFinal=legacyVision!==null/);
assert.match(html,/container\.classList\.toggle\("vision-editorial",visionFinal\)/);
assert.match(html,/originalRenderedSources\.set\(container,rawSource\)/,"Copy must retain unmodified source even when legacy vision display is reformatted");
assert.match(html,/const source=sourceContext\?sourceContext\.body:displaySource/);
assert.match(html,/vision-preview-unavailable/);

assert.ok(!html.includes("Read full observation"),"interim caption must not repeat as expanded raw text");
assert.ok(!html.includes("Raw model output · 1 level"),"no duplicate raw output panel in live progress");
const legacyStart=html.indexOf("      const formatLegacyVisionReply=value=>{");
const legacyEnd=html.indexOf("      const renderAssistantContent=",legacyStart);
assert.ok(legacyStart>=0&&legacyEnd>legacyStart,"formatter is available");
const legacyFormatter=new Function(html.slice(legacyStart,legacyEnd)+"return formatLegacyVisionReply;")();
const screenshotCaption=[
  "Local image analyzer's description (not directly inspected by §C):",
  "",
  "Character reference · local model observation (accuracy unverified)",
  "",
  "Subject and views: Front, left side, right side, back and top views of Little Crystal Mage.",
  "Silhouette and anatomy: White braided hair and purple eyes. Feet are clad in brown boots with fur trim at top.",
  "Clothing and surface detail: Purple hooded robe with gold trim. Robe has layered geometry with visible folds and creases. Boots are brown with fur trim at top. No buckles or hidden fastenings.",
  "Props and small features: Staff with purple crystal. Staff is held by right hand in front view, left hand in side views.",
  "Visibility limits: Top view shows the hood. No occlusion is implied for the staff or other features.",
  "",
  "Focused image details (unverified source-crop observations):",
  "- Upper-left figure detail: Two identical figures; left hand gripping a staff."
].join("\n");
const readable=legacyFormatter(screenshotCaption);
assert.match(readable,/^## Image analysis/);
assert.ok(readable.includes("Staff with purple crystal"),"retain verified-as-text visual detail");
assert.ok(!readable.includes("right hand in front"),"reject conflicting handedness");
assert.ok(!readable.includes("left hand in side"),"reject conflicting handedness");
assert.ok(!readable.includes("No occlusion is implied"),"discard unjustified absolutes");
assert.ok(!readable.includes("No buckles or hidden fastenings"),"discard categorical absence");
assert.ok(!readable.includes("layered geometry"),"do not claim source mesh topology");
assert.ok(readable.includes("appears layered, with folds and creases"),"state observable layering cautiously");
assert.equal((readable.match(/\bboots?\b/gi)||[]).length,1,"boots once under clothing, not again under anatomy");
assert.ok(!readable.includes("Two identical figures"),"raw crop notes stay out of final response");

// A newer live mage caption repeated belt, braid, eyes, pouch and hood
// in multiple sections. Keep the most informative claim in its own section.
const repeatedMage=[
  "Local image analyzer's description (not directly inspected by §C):",
  "",
  "Character reference · local model observation (accuracy unverified)",
  "",
  "Subject and views: Front, left side, right side, back, and top views of a single Little Crystal Mage.",
  "Silhouette and anatomy: Silver-white hair in two braids; purple eyes; wears a hooded robe with cape; stands on two legs; holds a staff in the right hand; left hand rests on a satchel in front view; back view shows full cape and staff beside the figure; top view shows hood shape and staff position.",
  "Clothing and surface detail: Purple hooded robe with gold trim; star, moon, leaf and magic symbols; fur-lined boots; belt with buckle; satchel with leaf emblem; robe has layered geometry with visible seams and folds.",
  "Props and small features: Staff topped with glowing purple crystal; satchel with brown leather and leaf emblem; belt with buckle; hood with star and moon motifs; hair in two braids; eyes purple; no other visible accessories.",
  "Visibility limits: Back view shows the robe and staff; top view shows hood and staff; no occlusion is implied for all views; no hidden parts are visible.",
  "",
  "Focused image details (unverified source-crop observations):",
  "- Upper-left figure detail: Two identical figures in purple robes; right side view shows left hand gripping a staff."
].join("\n");
const newReadable=legacyFormatter(repeatedMage);
assert.ok(newReadable.includes("Staff topped with glowing purple crystal"),"keep richest staff description");
assert.equal((newReadable.match(/belt with buckle/g)||[]).length,1,"do not repeat belt");
assert.equal((newReadable.match(/hair in two braids/g)||[]).length,1,"do not repeat hair inventory");
assert.ok(!newReadable.includes("eyes purple"),"eyes already under appearance");
assert.ok(newReadable.includes("hood with star and moon motifs"),"preserve a distinct location-specific ornament detail");
assert.ok(newReadable.includes("satchel with brown leather and leaf emblem"),"keep richer satchel detail");
assert.ok(!newReadable.includes("satchel with leaf emblem;"),"suppress weaker satchel inventory");
assert.ok(!newReadable.includes("holds a staff in the right hand"),"no confident conflicting staff-hand assignment");
assert.ok(newReadable.includes("top view shows hood shape and staff position"),"preserve unique angle observation");
assert.ok(!newReadable.includes("layered geometry"),"no inferred mesh topology");
assert.ok(!newReadable.includes("no occlusion"),"no unsupported universal visibility");
assert.ok(!newReadable.includes("Two identical figures"),"crop evidence remains diagnostic, not repeated answer");


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
const router=fs.readFileSync("hf_space/model_router.py","utf8");
const capacity=fs.readFileSync("hf_space/runtime_capacity.py","utf8");
assert.match(capacity,/class ResponseResourceMeter:/);
assert.match(capacity,/isolatedModelAttribution/);
assert.match(capacity,/cgroupCpuUsageUsecDelta/);
assert.match(capacity,/memoryPeakSampledBytes/);
assert.match(station,/responseResourceUsage/);
assert.match(station,/visionResourceUsage/);
assert.match(station,/vision_job_resource_receipt/);
assert.match(backend,/VISION_RESPONSE_RESOURCE_USAGE/);
assert.match(backend,/resourceUsage/);
assert.match(backend,/vision_job_resource_receipt/);
assert.match(backend,/configuredEngineThreadBudget/);
assert.match(backend,/resumedExistingJob/);
assert.match(router,/def _format_direct_vision_report\(/);
assert.match(router,/return _format_direct_vision_report\(description\)/);
assert.match(router,/## Image analysis/);
assert.match(router,/Focused image details/);
assert.ok(!router.includes("Raw\\n    # crop evidence"),"no invalid escaped newline in source router");
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
assert.match(backend,/with_boxes=True/);
assert.match(backend,/coordinateSpace": "exif-corrected-source-normalized"/);
assert.match(backend,/RAW_CROP_MARKER/);
assert.match(backend,/vision_request_id = payload\.get\("visionRequestId", ""\)/);
assert.match(backend,/VISION_REQUEST_ID_INVALID/);
assert.match(backend,/resumedExistingJob/);
assert.match(backend,/bool\(vision_request_id\) and job\["phase"\] == "COMPLETE"/);
assert.match(backend,/Shape and proportions:/);
assert.match(backend,/Materials and markings:/);
assert.match(backend,/referenceProgress/);
assert.match(html,/referenceProgress:state\.referenceProgress/);
assert.match(backend,/spatialRegionRecords/);
assert.match(html,/\.assistant-body\.vision-editorial/);
assert.ok(!html.includes("vision-reference-findings"),"raw reports remain in JSON export, not chat cards");
// The image analysis card must not trap touch scrolling in a nested 72dvh
// scrollport; swiping anywhere on it scrolls the single chat viewport.
assert.match(html,/\.vision-work-card\{[^}]*max-height:none;overflow:visible;touch-action:pan-y/s);
assert.ok(!html.includes('max-height:72dvh;overflow-y:auto;overscroll-behavior:contain'),"no nested image-card scroll trap");
// Both an in-progress attachment and the committed chat image get the same
// keyboard/Android-tappable expanded image preview, with native Escape close.
assert.match(html,/const openVisionImagePreview=\(imageUrl/);
assert.match(html,/const formatLegacyVisionReply=value=>/);
assert.match(html,/const displaySource=legacyVision\|\|rawSource/);
assert.match(html,/const source=sourceContext\?sourceContext\.body:displaySource/);
assert.match(html,/\.assistant-body\.vision-editorial/);
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
assert.match(backend,/proposals = proposals\[:7\] if layout_panels else proposals\[:2\]/);
assert.match(backend,/from vision_sheet_layout import discover_view_panels/);
assert.match(backend,/regionKind/);
assert.match(backend,/evidence_notes = "\\n"\.join\(evidence_lines\)\[:2400\]/);
assert.match(backend,/about 80 to 120 words/);
assert.match(backend,/RAW_CROP_MARKER/);
assert.ok(!backend.includes('"\\n\\nSource observations:\\n"'),"final response must not repeat the whole raw overview");
assert.ok(!html.includes('Checking for contradictions'),"internal inference consistency checks stay hidden");
assert.match(backend,/def vision_status\(/);
assert.match(backend,/threading\.Thread\(/);
assert.match(backend,/ACTIVE_PHASES/);
assert.match(backend,/retryAfterSeconds/);
assert.match(backend,/\@app\.get\("\/api\/lalm_station\/vision\/status"/);
assert.match(backend,/MODEL_REVISION = "[0-9a-f]{40}"/);
console.log("Chat media v1: local vision job progress, chat composer, and inline JS PASS");
