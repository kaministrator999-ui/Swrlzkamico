(()=>{
  "use strict";
  const semanticLabel=node=>{
    const kinds=[...node.querySelectorAll(".swrlz-widget")].map(card=>String(card.dataset.widgetKind||""));
    if(node.querySelector(".weather-hero"))return "§wyrlz · Analyzing weather information…";
    if(node.querySelector(".search-widget-list"))return "§wyrlz · Analyzing search results…";
    if(kinds.some(kind=>/time|clock/.test(kind)))return "§wyrlz · Analyzing time information…";
    return "§wyrlz · Analyzing retrieved information…";
  };
  const reconcile=node=>{
    if(!(node instanceof Element)||!node.classList.contains("station-live-message"))return;
    const body=node.querySelector(".assistant-body");
    const status=node.querySelector(".station-progress");
    const trail=node.querySelector(".station-online-trail");
    const widgets=node.querySelector(".message-widget-stack");
    if(!body||!status)return;
    if(widgets){
      // Permanent visual chronology: structured evidence first, then analysis,
      // then streamed conversational prose. Never insert later prose above a
      // widget the user has already started reading.
      if(widgets.nextElementSibling!==status)status.before(widgets);
      const hasText=String(body.dataset.renderedSource||body.textContent||"").trim().length>0 && !body.hidden;
      if(!hasText)status.textContent=semanticLabel(node);
      status.hidden=hasText;
      if(trail)trail.hidden=hasText;
    }
  };
  const scan=()=>document.querySelectorAll(".station-live-message").forEach(reconcile);
  new MutationObserver(scan).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["hidden","class","data-rendered-source"]});
  document.addEventListener("DOMContentLoaded",scan,{once:true});
  scan();
})();
