"""Scoped, source-pinned §C integration: §E startup proof and image references."""
from __future__ import annotations
import hashlib

BEFORE = {
 "chat/§wyrlz/assets/forge-embed-v1.js": "2e74d9fa9a44739963e177d366f07210efa65a01c71ae2aa125b5bf04ef3f6e2",
 "chat/§wyrlz/index.html": "79b11bcc6bb79535d8ea7cd8803eccbd9398d0536822d139385c9b8d0f16328c",
}
AFTER = {
 "chat/§wyrlz/assets/forge-embed-v1.js": "41d4dcd397d561c88984ad940847334584535fccde789e1168c0690d40463515",
 "chat/§wyrlz/index.html": "717ebe92837e2ce66a3705f6f09750f0b76a022ad309f17d19efd4043e9ca2d1",
}

def one(s, old, new):
 n=s.count(old)
 if n!=1: raise AssertionError(("scoped source anchor drift",n,old[:110]))
 return s.replace(old,new,1)

def patch_js(s):
 s=one(s,'const startPair = async () => {','const startPair = async (surface="chat") => {')
 s=one(s,'    showRecoveryCode(value.recoveryCode);\n    pairing=', '    if(surface==="engine-startup")showRecoveryCode("");else showRecoveryCode(value.recoveryCode);\n    pairing=')
 s=one(s,'return {loginUrl:url.href,pairId:value.pairId};', """return {loginUrl:url.href,pairId:value.pairId,
      ...(surface==="engine-startup"?{recoveryCode:value.recoveryCode,expiresAt:Number(value.expiresAt)*1000}:{})};""")
 s=one(s,'if(message.type === "account.signIn")result=await startPair();',
         'if(message.type === "account.signIn")result=await startPair(message.payload?.surface==="engine-startup"?"engine-startup":"chat");')
 s=one(s,'    requestSignIn(){if(port)send("account.signInRequested",{});},', """    async importReference(candidate){
      if(!embedded||!port||!isAuthenticated()||!hostVisible||document.visibilityState!=="visible")throw error("Connect §e and open its integrated Chat before importing a reference.");
      const {name,type,bytes}=candidate||{};
      if(typeof name!=="string"||!name||name.length>100||/[\\x00-\\x1f]/.test(name)||
         !["image/png","image/jpeg","image/webp"].includes(type)||
         !(bytes instanceof Uint8Array)||bytes.byteLength<12||bytes.byteLength>8*1024*1024)
        throw error("Choose a JPEG, PNG or WebP reference under 8 MB.");
      // Explicit user-initiated copy to the trusted native §e reference importer.
      // This does not add scene operations, grant a model lease or send to cloud.
      return rpc("host.reference.import",{name,type,bytes:new Uint8Array(bytes)},45000);
    },
    requestSignIn(){if(port)send("account.signInRequested",{});},""")
 return s

def patch_html(s):
 s=one(s,'<button id="imageRemoveButton" type="button" aria-label="Remove attached image">✕</button>',
   '<button id="imageModelReferenceButton" type="button" hidden>Use in §E references</button>\n          <button id="imageRemoveButton" type="button" aria-label="Remove attached image">✕</button>')
 s=one(s,'.image-attachment button{border:0;background:transparent;color:#e3faff;font-size:17px;cursor:pointer}',
   '.image-attachment button{border:0;background:transparent;color:#e3faff;font-size:17px;cursor:pointer}\n    #imageModelReferenceButton:not([hidden]){border:1px solid #78c8e4;border-radius:7px;background:#143d59;color:#e6faff;font-size:11px;min-height:34px;padding:5px 8px;white-space:normal;max-width:152px}\n    #imageModelReferenceButton[hidden]{display:none!important}')
 s=one(s,'const imageAttachmentName=document.getElementById("imageAttachmentName");',
   'const imageAttachmentName=document.getElementById("imageAttachmentName");\n      const imageModelReferenceButton=document.getElementById("imageModelReferenceButton");')
 s=one(s,'        imageAttachment.hidden=!selectedImage;\n        imageAttachmentThumbnail.removeAttribute("src");',
   '        imageAttachment.hidden=!selectedImage;\n        imageModelReferenceButton.hidden=!selectedImage||!window.SwrlzForgeEmbedV1?.embedded;\n        imageAttachmentThumbnail.removeAttribute("src");')
 s=one(s,'      imagePickButton.addEventListener("click",()=>imagePicker.click());', """      imagePickButton.addEventListener("click",()=>imagePicker.click());
      imageModelReferenceButton.addEventListener("click",async()=>{
        const attachment=selectedImage;
        if(!attachment||!window.SwrlzForgeEmbedV1?.embedded)return;
        imageModelReferenceButton.disabled=true;
        composerNotice("Adding image to the active §E Model Studio references…");
        try{
          const receipt=await window.SwrlzForgeEmbedV1.importReference({
            name:attachment.file.name,type:attachment.file.type,bytes:attachment.bytes});
          if(receipt?.added!==true)throw new Error("§E did not confirm the reference import.");
          composerNotice("Added image to §E Model Studio references. It will be saved with the model project.");
        }catch(reason){composerNotice("Reference import failed: "+String(reason?.message||reason).slice(0,180),true);}
        finally{imageModelReferenceButton.disabled=false;}
      });""")
 return s

PATCHES={"chat/§wyrlz/assets/forge-embed-v1.js":patch_js,
         "chat/§wyrlz/index.html":patch_html}
def apply(name, raw:bytes)->bytes:
 if name not in PATCHES:raise ValueError("scope")
 if hashlib.sha256(raw).hexdigest()!=BEFORE[name]:raise ValueError("unrecognized live source")
 s=PATCHES[name](raw.decode("utf8")).encode("utf8")
 if hashlib.sha256(s).hexdigest()!=AFTER[name]:raise ValueError("candidate changed unexpectedly")
 return s
