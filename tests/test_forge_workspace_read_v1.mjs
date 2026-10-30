/* Read-only analysis must travel through the normal authenticated Chat send. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const broker=fs.readFileSync(new URL('../chat/§wyrlz/assets/forge-embed-v1.js',import.meta.url),'utf8');
const page=fs.readFileSync(new URL('../chat/§wyrlz/index.html',import.meta.url),'utf8');
new vm.Script(broker);
const eventSection=broker.slice(broker.indexOf('if(message.type === "host.analyze")'),broker.indexOf('if(message.type === "host.visibility")'));
assert.match(eventSection,/hostVisible && isAuthenticated\(\) && document.visibilityState === "visible"/);
assert.match(eventSection,/swrlz-forge-analyze-request/);
const ui=page.slice(page.indexOf('window.addEventListener("swrlz-forge-analyze-request"'),page.indexOf('sendButton.addEventListener("click",commitDraftFromPrompt)'));
assert.match(ui,/if\(prompt.value.trim\(\)\)\{prompt.focus\(\);return;\}/);
assert.match(ui,/void commitDraftFromPrompt\(\)/);
assert.match(ui,/do not modify any objects/);
assert(!/host\.batch|editor\.apply|sceneactor\.|mesh\.|cloud\.save/.test(eventSection),'no mutation message');
console.log(JSON.stringify({ok:true,suite:'forge-workspace-read-transport',checks:7}));
