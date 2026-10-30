/* Opener-less browser-tab recovery is always bound to an original Chat-origin pair. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const page=fs.readFileSync(new URL('../chat/§wyrlz/forge-connect.html',import.meta.url),'utf8');
const broker=fs.readFileSync(new URL('../chat/§wyrlz/assets/forge-embed-v1.js',import.meta.url),'utf8');
const js=page.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert(js,'popup script exists');new vm.Script(js);new vm.Script(broker);
assert.match(page,/id="recoveryCode"/);
assert.match(page,/id="checkAccount"/);
assert.match(js,/if\(!\/\^\[a-f0-9\]\{32\}\$\/\.test\(pairId\)\)/,'standalone-tab popup no longer rejects missing opener');
assert.match(js,/recoveryCode:code\(\)/,'recovery proof required when opener is unavailable');
assert.match(js,/!user\|\|complete\|\|\(!bound&&!codeReady\(\)\)/,'unverified account and missing proof cannot approve');
assert.match(broker,/showRecoveryCode\(value\.recoveryCode\)/,'original iframe displays separate proof');
assert.match(broker,/showRecoveryCode\(""\)/,'proof clears after account connection');
assert(!/const code=.*value\.pairId/.test(broker),'proof must not be derived from public pair ID');
console.log(JSON.stringify({ok:true,suite:'forge-popup-mobile-recovery',checks:9}));
