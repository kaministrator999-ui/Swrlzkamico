"""§E v11.536: native startup Google code and verified Chat image references.

Keep the existing Chat origin as OAuth authority and Model Atelier as the
reference/persistence authority. No duplicate project or model import system.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIOUS='SWYRL_ENGINE_DEPLOY_MARKER: V11_535_STARTUP_SIGNIN_CODE'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_536_NATIVE_ACCOUNT_IMAGE_REFERENCE'

def one(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.536 source anchor drift',n,old[:150]))
 return s.replace(old,new,1)

def section(source,name):
 return source.split(f'/* SE536_{name}_START */',1)[1].split(f'/* SE536_{name}_END */',1)[0]

def apply(html):
 runtime=(ROOT/'runtime/engine_native_login_reference_v11_536.js').read_text('utf8')
 host=section(runtime,'HOST')
 imp=section(runtime,'IMPORT')
 # Host closure owns the bound MessagePort and popup handshakes.
 html=one(html,'function mount(){\n  if(document.getElementById(\'seChatAccountPanel\')',
          host+'\nfunction mount(){\n  if(document.getElementById(\'seChatAccountPanel\')')
 html=one(html,' signIn:()=>{openPanel();return signIn();},',
          ' signIn:()=>se536PrepareLogin(),')
 html=one(html,"  note('Copy the one-time code at the top of the secure §Chat panel, then tap Continue to Google there.');",
          "  note('Preparing the Google connection code on this §E login screen…');")
 html=one(html,"  if(type==='account.status'){\n    revoke('Account changed.');",
          "  if(type==='account.status'){\n    if(payload.authenticated===true)se536Clear();\n    revoke('Account changed.');")
 html=one(html,"  if(type==='host.context'){", """  if(type==='host.reference.import'){
    try{
      if(!ready||!se176AccountConnected||!isVisible())throw Error('Sign in and open the integrated Chat before sending a reference.');
      if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')throw Error('Switch to §E Model Studio first.');
      const importer=window.SWYRL_ENGINE_REFERENCE?.importFromChat;
      if(typeof importer!=='function')throw Error('§E Model Studio references are not ready.');
      const result=await importer(payload);
      if(result?.added!==true)throw Error('Reference import was not confirmed.');
      send('rpc.result',{ok:true,result},requestId);
    }catch(reason){send('rpc.result',{ok:false,error:String(reason?.message||reason).slice(0,180)},requestId);}
    return;
  }
  if(type==='host.context'){""")
 # Native Model Atelier adds images via its original portable reference import.
 html=one(html,'window.SWYRL_ENGINE_REFERENCE=Object.freeze({status:()=>({',
          'window.SWYRL_ENGINE_REFERENCE=Object.freeze({\n'+imp+'status:()=>({')
 # §E's own startup card now owns the code, Copy and Continue controls.
 html=one(html,'<button id="se476SignIn" type="button" class="se476-primary">Sign in with Google</button>',
          """<button id="se476SignIn" type="button" class="se476-primary">Sign in with Google</button>
   <div id="se536LoginProof" hidden role="group" aria-label="Google account connection code">
     <label class="se476-section-title" for="se536RecoveryCode">One-time connection code</label>
     <input id="se536RecoveryCode" type="text" readonly autocomplete="off" spellcheck="false" aria-label="One-time Google connection code">
     <div class="se536-login-actions">
       <button id="se536CopyCode" type="button">Copy code</button>
       <button id="se536ContinueGoogle" type="button" class="se476-primary">Continue to Google</button>
     </div>
     <p class="se476-note">Copy the code before leaving this screen. If the Google tab asks for it, paste it there. The code expires in five minutes. Signing in connects this workspace and integrated §Chat.</p>
   </div>""")
 # Disable v11.535's full Chat panel workaround. Only the native gate is shown.
 html=one(html,'#se476StartupGate:not([hidden]) ~ #seChatAccountPanel:not([hidden]){z-index:2147482460!important}',
          """#se536LoginProof[hidden]{display:none!important}
#se536LoginProof{display:grid;gap:8px;padding:10px;border-radius:10px;border:1px solid #6088a6;background:#111e33}
#se536RecoveryCode{width:100%;min-height:44px;padding:8px;text-align:center;font:800 20px/1.3 ui-monospace,monospace;letter-spacing:.07em;background:#fff;color:#14223a;border:1px solid #88bad6;border-radius:8px;user-select:all}
#se536LoginProof .se536-login-actions{display:flex;flex-wrap:wrap;gap:8px}
#se536LoginProof .se536-login-actions button{flex:1 1 130px}""")
 for before,after in [
  (PREVIOUS,MARKER),
  ('ENGINE · MAKER v11.535','ENGINE · MAKER v11.536'),
  ('v11.535 · accessible Google sign-in recovery code','v11.536 · native Google code and image references'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.535'","window.SWRLZ_FORGE_BUILD={version:'v11.536'"),
  ('<title>§wyrl§ Engine · Maker v11.535</title>','<title>§wyrl§ Engine · Maker v11.536</title>'),
 ]:html=one(html,before,after)
 previous=" source.engine='§wyrl§ Engine · Maker v11.535';source.version=11.535;"
 assert html.count(previous)==5
 html=html.replace(previous,previous.replace('11.535','11.536'))
 index=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
 notes,width=json.JSONDecoder().raw_decode(html[index:])
 notes['history']=[item for item in notes['history'] if item.get('version')!='v11.535']
 notes['history'].insert(0,{'version':'v11.535','changes':notes['changes']})
 notes.update(version='v11.536',date='2026-11-22',
    title='Native Google account code and integrated Chat image references',
    changes=[
      'The §E startup screen itself displays the short-lived Google connection proof with Copy code and Continue to Google; the full §Chat panel no longer opens for startup login.',
      'Google and account ownership remain verified by the existing §Chat-origin broker; authenticated Chat and engine share the same connected session.',
      'An image attached inside integrated Chat can be explicitly added to the active Model Studio reference library through the trusted bound Chat-to-engine channel.',
      'Native reference validation, portable save compression, four-image capacity, model history and existing project persistence remain authoritative. Qwen vision upload stays unchanged.',
      'Real Google pairing and actual phone/Quest image-import acceptance require device testing.'
    ])
 release=json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
 return html[:index]+release+html[index+width:]
