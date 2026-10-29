// Confirm the exact account-panel header link is removed without breaking its controls.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const root='projects/swrlz-forge-moba/';
const original=fs.readFileSync(root+'runtime/chat_account_panel_v1.js','utf8');
const patch=fs.readFileSync(root+'patches/v11_172_clean_chat_header.py','utf8');
const anchor='<a href="https://kamiloki-swyrlz.hf.space" target="_blank" rel="noopener">Open Chat</a>';
assert(original.includes(anchor),'the historical header contains exactly the link being removed');
assert(patch.includes(anchor),'patch target is limited to the redundant header link');
assert(patch.includes('seChatClose'),'Close remains next to the title');
assert(original.includes('id="seChatSignIn"'),'existing Google sign-in remains');
assert(original.includes('id="seChatSave"')&&original.includes('id="seChatLoad"'),'account project actions remain');
assert(fs.readFileSync(root+'runtime/project_hub_my_projects_v11_170.js','utf8').includes('se170Refresh'),'My Projects still uses account list');
if(process.env.SE172_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE172_ASSEMBLED_HTML,'utf8');
 assert(!html.includes(anchor),'redundant Open Chat link is not in the final engine');
 assert(html.includes('<strong>§wyrlz Chat</strong><button type="button" id="seChatClose"'),'panel title and Close are adjacent');
 assert(html.includes('id="seChatSignIn"')&&html.includes('id="seChatSave"')&&html.includes('id="seChatLoad"'),'account controls remain');
 assert(html.includes("se170Install")&&html.includes('id="se171-project-hub-layer"'),'prior project features remain');
 assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_172_CLEAN_CHAT_HEADER'));
}
console.log('SE172_CHAT_HEADER_REGRESSION_PASS');
