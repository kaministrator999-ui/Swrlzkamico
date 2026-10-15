import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const html=fs.readFileSync(path.join(root,"chat/§wyrlz/index.html"),"utf8");
const station=fs.readFileSync(path.join(root,"hf_space/station.py"),"utf8");
const css=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/assistant-fullwidth-v261.css"),"utf8");
const dashboard=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-work-summary-v260.css"),"utf8");
function expectRule(selector,checks){
  const start=css.indexOf(selector);
  assert(start>=0, "Missing full-width layout rule "+selector);
  const open=css.indexOf("{",start);
  assert(open>start && open-start<900,"No bounded CSS declaration for "+selector);
  const end=css.indexOf("}",open);
  assert(end>open,"Unclosed CSS selector "+selector);
  const text=css.slice(open,end);
  for(const check of checks) assert(text.includes(check),selector+" missing "+check);
}
assert(html.includes(".message-list{width:min(var(--conversation-width),100%)"),
  "The base chat markup changed: reconcile new full-width sheet with layout");
assert(html.includes(".message-widget-stack{margin:9px 0 4px 38px"),
  "The old 38px widget indent has moved; update regression");
assert(station.includes("github-work-summary-v260.css"),"Keep existing GitHub stats widget CSS");
const oldIdx=station.indexOf("github-work-summary-v260.css");
const newIdx=station.indexOf("assistant-fullwidth-v261.css");
assert(newIdx>oldIdx && newIdx>0,"v261 stylesheet must follow the earlier dashboard style");
assert(station.includes("source=source.replace('</head>',css+'</head>',1)"),
  "Full-width CSS needs to load with canonical Chat head");
expectRule(".chat-viewport",["padding-left:","padding-right:","safe-area-inset-left","safe-area-inset-right"]);
expectRule(".chat-viewport .message-list",["width:100%!important","max-width:none!important","margin-inline:0!important"]);
expectRule(".message-list>.assistant-message,\n.message-list>.station-live-message",["width:100%!important","align-self:stretch"]);
expectRule(".assistant-message .assistant-body,\n.station-live-message .assistant-body",["width:100%!important","margin-left:0!important","margin-right:0!important","box-sizing:border-box!important"]);
expectRule(".assistant-message .message-widget-stack,\n.station-live-message .message-widget-stack",["width:100%!important","margin:8px 0 4px!important"]);
expectRule(".assistant-message .message-evidence,\n.station-live-message .message-evidence",["margin-left:0!important","max-width:100%!important"]);
expectRule(".swrlz-widget.github-work",["background:transparent","border:0"]);
expectRule(".swrlz-widget.github-work>.widget-head",["display:none"]);
assert(css.includes(".assistant-message .station-activity,"),"Live work/activity should align");
assert(css.includes(".assistant-message .station-progress,"),"Status strip should align");
assert(css.includes(".assistant-message .station-online-trail,"),"External tool trail should align");
assert(css.includes(".assistant-message .assistant-actions,"),"Copy/action strip should align");
assert(css.includes("min-width:0"),"Responsive children need constrained shrink");
assert(css.includes("@media(max-width:600px)"),"Phone layout must be covered");
assert(css.includes("@media(min-width:1200px)"),"Wide viewport readability must be covered");
assert(!css.includes(".user-bubble{"),"User messages are distinct: do not modify their bubble positioning");
assert(!css.includes(".user-message{"),"User messages are distinct: do not modify their positioning");
assert(!css.includes("overflow:hidden"),"Do not clip large assistant visualizations");
assert(dashboard.includes(".github-work-dashboard"),"Existing dashboard intact");
console.log("v261 full-width AI content and widget layout contract PASS");
