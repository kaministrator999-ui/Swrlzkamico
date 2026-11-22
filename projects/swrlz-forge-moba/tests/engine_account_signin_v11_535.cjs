'use strict';
// §E v11.535: protect the code-copy-before-Google path from regressions.
// The recovery proof is produced only by the Chat-origin iframe, never read
// by the engine host or placed into host markup, URLs or local storage.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_535_STARTUP_SIGNIN_CODE'));
assert(html.includes('signIn:()=>{openPanel();return signIn();},'),
  'Account-startup button must expose the actual Chat iframe before preparing Google');
assert(html.includes('#se476StartupGate:not([hidden]) ~ #seChatAccountPanel:not([hidden]){z-index:2147482460!important}'),
  'Chat-origin code must be visible above the startup gate');
assert(html.includes('Copy the one-time code at the top of the secure §Chat panel, then tap Continue to Google there.'),
  'Startup must explain the two-click flow');
assert(html.includes('se177Prepared={pairId:result.pairId'),
  'Preserve established two-stage secure Chat-origin sign-in');
assert(html.includes("if(se177Prepared&&Date.now()<se177Prepared.until)"),
  'Google popup must remain on the subsequent explicit gesture');
assert(html.includes('if(!frame.src)frame.src=CHAT_ORIGIN'),
  'Keep existing embedded Chat iframe, no separate credential surface');
assert(!html.includes('window.SWYRL_ENGINE_STARTUP_ACCOUNT_476=Object.freeze({\n ready:()=>ready===true,\n connected:()=>se176AccountConnected===true,\n signIn:()=>signIn(),'),
  'Startup must not invoke hidden Chat sign-in');
console.log('SE535_SIGNIN_CODE_REGRESSION_PASS');
