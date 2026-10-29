"""Prevent the opening touch from immediately dismissing the mobile numeric dialog."""
import hashlib
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:90],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    # v11.97 reveals the keypad during input pointerdown. On touch devices,
    # the same gesture's synthesized click can hit the newly shown backdrop
    # and close it before the user can interact.
    html=once(html," let selected=null,draft='';\n const coarse=",
""" let selected=null,draft='';
 // A click may activate the pad only if its press began on that control.
 // The opening press originates on the underlying model input, not this pad.
 let padPressTarget=null;
 const armPad=event=>{
  padPressTarget=event.target?.closest?.('button,[data-se-cancel]')||null;
 };
 box.addEventListener('pointerdown',armPad,true);
 if(!window.PointerEvent)box.addEventListener('touchstart',armPad,{capture:true,passive:true});
 box.addEventListener('pointercancel',()=>{padPressTarget=null;},true);
 const coarse=""")
    html=once(html,
"""  if(!b)return;
  if(b.hasAttribute('data-se-cancel')){close();return;}""",
"""  if(!b)return;
  // Ignore click-through from the same touch which first opened the pad.
  // A keyboard click is accepted only for the actually focused button.
  const pressed=padPressTarget;
  padPressTarget=null;
  // Synthetic mobile clicks may also have detail===0; do not treat
  // zero detail alone as proof of keyboard activation.
  const keyboardActivation=event.detail===0&&b.tagName==='BUTTON'&&document.activeElement===b;
  if(pressed!==b&&!keyboardActivation){
   event.preventDefault();
   event.stopPropagation();
   return;
  }
  if(b.hasAttribute('data-se-cancel')){close();return;}""")
    html=once(html,
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_97_MOBILE_VIEWPORT_FOCUS',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_98_MOBILE_NUMPAD_TOUCH_FIX')
    for a,b in [
      ('ENGINE · MAKER v11.97','ENGINE · MAKER v11.98'),
      ('v11.97 · device-width mobile model editor','v11.98 · stable mobile number pad'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.97'","window.SWRLZ_FORGE_BUILD={version:'v11.98'"),
      ('<title>§wyrl§ Engine · Maker v11.97</title>','<title>§wyrl§ Engine · Maker v11.98</title>'),
    ]:html=once(html,a,b)
    prefix='const SE_RELEASE_NOTES='
    start=html.index(prefix)+len(prefix)
    notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Stable mobile numeric editor touch activation',date='2026-10-23',changes=[
        'Fix a single tap opening and immediately dismissing the mobile numeric keypad by gating click activation on a press begun within the pad.',
        'Keypad digit, decimal, sign, Clear, Delete, Apply, backdrop Cancel, and keyboard activation retain their behaviors.',
        'Preserve the device-width viewport, 16px mobile input styling, round blank model, and all existing projects.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    raw=html.encode('utf8')
    print('SWRLZ_V1198_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
