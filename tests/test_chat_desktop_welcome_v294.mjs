/* v294 desktop Dragon Den welcome panel: production-source CSS and lifecycle regression.
 * No account, network, mocks of user data, or GitHub permissions.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const version=fs.readFileSync("chat/§wyrlz/VERSION.txt","utf8").trim();
assert.match(version,/^\d+\.\d+\.\d+$/,"Read the authoritative Chat surface version instead of pinning v294 forever");
assert.ok(html.includes('<meta name="swrlz-chat-version" content="'+version+'">'));
assert.ok(html.includes('const SWRLZ_CHAT_VERSION = "'+version+'";'));
assert.match(html,/\.first-run-welcome\{margin:auto 0;/,"Original mobile layout owner retained");
assert.match(html,/@media \(min-width:761px\)\s*\{\s*\.first-run-welcome\s*\{[\s\S]*?width:min\(100%,560px\);[\s\S]*?margin:auto;/,
  "Desktop welcome has bounded centered width");
assert.match(html,/\.first-run-hint\s*\{\s*margin-top:17px;\s*padding-top:12px;\s*border-top:/,
  "Desktop hint has a visual separator");
assert.match(html,/body\.a11y-reduced-transparency \.first-run-welcome/,
  "Accessibility transparency preference must be honored");
assert.match(html,/const renderFirstRunWelcome = \(\) => \{[\s\S]*?if\(chatThreads\.length\|\|!draftThread\)return;/,
  "Welcome remains first-conversation-only");
assert.match(html,/card\.append\(kicker,title,copy,hint\);messageList\.appendChild\(card\);/,
  "Existing welcome contents and insertion preserved");
assert.equal((html.match(/\/\* v294: the first-conversation greeting/g)||[]).length,1);
console.log("v294 Dragon Den desktop welcome source and mobile-preservation checks passed");
