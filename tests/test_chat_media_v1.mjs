/* Canonical §C multimedia composer regression: no live credentials or devices. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const version=fs.readFileSync("chat/§wyrlz/VERSION.txt","utf8").trim();
assert.equal(version,"1.1.22");
assert.ok(html.includes('<meta name="swrlz-chat-version" content="'+version+'">'));
assert.ok(html.includes('const SWRLZ_CHAT_VERSION = "'+version+'";'));

for(const id of ["imagePickButton","imagePicker","imageAttachment","imageAttachmentThumbnail","imageRemoveButton","micButton","composerFeedback"]){
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id+" must exist once");
}
assert.match(html,/accept="image\/jpeg,image\/png,image\/webp"/);
assert.match(html,/imagePreviews=new Map\(\)/);
assert.match(html,/encodeImageForVision=attachment=>new Promise/);
assert.match(html,/fetch\("\/api\/lalm_station\/vision"/);
assert.match(html,/description=await requestVisionDescription\(attachment,draftText\)/);
assert.match(html,/prompt:text,threadId:activeThreadId/);
assert.match(html,/imagePreviews\.set\(userMessageId,attachment\.url\)/);
assert.match(html,/recognition\.onresult=event=>/);
assert.match(html,/prompt\.value=\(original\+separator\+transcript\)/);
assert.match(html,/prompt\.dispatchEvent\(new Event\("input",\{bubbles:true\}\)\)/);
assert.match(html,/window\.SpeechRecognition\|\|window\.webkitSpeechRecognition/);
assert.match(html,/if\(speechRecognition\)\{speechRecognition\.stop\(\);return;\}/);
assert.match(html,/if\(\(!draftText&&!attachment\)\|\|sending\)return false/);
assert.match(html,/if\(\(!prompt\.value\.trim\(\)&&!selectedImage\)\|\|sending\)return/);
assert.match(html,/if\(!sendAcknowledged\)\{prompt\.value=draftText/);
assert.match(html,/if\(attachment&&selectedImage===attachment\)/);

const inline=html.match(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/i);
assert.ok(inline,"Canonical inline Chat controller exists");
new vm.Script(inline[1],{filename:"swrlz-chat-media-inline.js"});

const station=fs.readFileSync("hf_space/station.py","utf8");
assert.match(station,/install_chat_vision\(app, _require_vision_account\)/);
assert.match(station,/startsWith\('google:'\)|startswith\('google:'\)/);
const backend=fs.readFileSync("hf_space/chat_vision.py","utf8");
assert.ok(backend.includes('MODEL_REPO = "ggml-org/SmolVLM-256M-Instruct-GGUF"'));
assert.ok(backend.includes("MTMDChatHandler"));
assert.ok(!backend.includes("SWRLZ_VISION_API_KEY"),"no paid inference credentials needed");
assert.ok(!backend.includes("router.huggingface.co"),"no paid inference provider calls");
assert.match(backend,/MAX_IMAGE_BYTES = 2_000_000/);
assert.match(backend,/imageStored": False/);
assert.match(backend,/asyncio\.to_thread\(_ask_vision_local/);
assert.match(backend,/MODEL_REVISION = "[0-9a-f]{40}"/);
console.log("Chat media v1: free local vision, composer contracts, and inline JS PASS");
