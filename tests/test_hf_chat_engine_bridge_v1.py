"""Source-level invariants for user-initiated §E/§C auth and reference integration."""
import sys
from pathlib import Path

def check(before,after):
 old_js=(before/"chat/§wyrlz/assets/forge-embed-v1.js").read_text()
 js=(after/"chat/§wyrlz/assets/forge-embed-v1.js").read_text()
 html=(after/"chat/§wyrlz/index.html").read_text()
 assert 'surface==="engine-startup"' not in old_js
 assert 'surface==="engine-startup"' in js
 assert 'recoveryCode:value.recoveryCode' in js
 assert 'return {loginUrl:url.href,pairId:value.pairId' in js
 assert 'showRecoveryCode(value.recoveryCode)' in js  # regular §C panel remains supported
 assert 'showRecoveryCode("")' in js
 assert 'host.reference.import' in js
 assert 'isAuthenticated()||!hostVisible' in js
 assert 'new Uint8Array(bytes)' in js
 assert 'bytes.byteLength>8*1024*1024' in js
 assert 'imageModelReferenceButton' in html
 assert 'Use in §E references' in html
 assert 'SwrlzForgeEmbedV1.importReference' in html
 assert 'imageModelReferenceButton.hidden=!selectedImage||!window.SwrlzForgeEmbedV1?.embedded' in html
 assert 'visionJobId:activity.jobId' in html
 assert 'encodeImageForVision' in html and 'imageSha256' in html
 assert 'id="imagePicker" type="file"' in html
 assert 'localStorage.setItem("recovery' not in js
 print("CHAT_ENGINE_LOGIN_REFERENCE_BRIDGE_PASS")

if __name__=="__main__":check(Path(sys.argv[1]),Path(sys.argv[2]))
