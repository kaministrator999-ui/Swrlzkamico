# §E v11.535 — Reach the existing Google sign-in recovery code

## Observed problem
The first-paint §E account startup gate (v11.476) obscures the embedded
§Chat panel. Google sign-in from that gate called the existing sign-in
handler, which in v11.177 deliberately prepares a short-lived one-time
pairing proof inside the Chat iframe *before* opening Google. The code
therefore existed but was not visible or copyable at startup.

## Targeted correction
- The startup Sign in with Google button first opens the **existing**
  §Chat panel, then invokes its original Chat-origin two-stage login.
- While the startup gate is open, the Chat panel is allowed above it.
  The regular editor stacking order is untouched once the gate exits.
- The code remains displayed/copyable in the secure Chat-origin iframe;
  the parent engine reads no secret, never renders a duplicate proof and
  does not transmit it in an URL, clipboard call, host message or storage.
- First interaction: prepare the code and allow it to be copied. Second
  interaction: **Continue to Google** in the Chat panel opens the same
  first-party login page and preserves existing pairing/PKCE checks.
- Existing cloud project revisions, local projects, startup recovery,
  Google ownership and native project loaders are not modified.

## Verification and user acceptance
- Assemble all ordered patches and pin the new HTML length/SHA.
- Run inline-JavaScript parse, the targeted account-code regression test,
  and previous mesh/account persistence tests.
- On a phone and Meta Quest browser, launch signed-out §E and tap the
  startup Sign in with Google button. The Chat-origin code must be visible
  before Google opens, with a working Copy code action.
- Tap Continue to Google, complete Google verification, and confirm the
  account badge and cloud project list in §E. Also verify offline/local
  continuation and normal editor panel stacking.
- Physical device and actual Google account acceptance must be reported
  separately from source and simulated browser checks.

This is a focused recovery of the existing v11.177 login contract;
there is no second OAuth implementation or new account data store.
