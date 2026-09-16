(() => {
  "use strict";
  const form = document.querySelector("#composer");
  const tools = document.querySelector(".composer-left");
  const route = document.querySelector("#route");
  if (!form || !tools || !route || document.querySelector("#onlineResearch")) return;

  const style = document.createElement("style");
  style.textContent = `
    .online-research-toggle{display:inline-flex;align-items:center;gap:7px;height:34px;padding:0 10px;border:1px solid var(--line);border-radius:10px;color:var(--secondary);background:rgba(12,21,39,.72);font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap;user-select:none}
    .online-research-toggle:has(input:checked){border-color:rgba(56,232,255,.42);background:rgba(56,232,255,.08);color:var(--text)}
    .online-research-toggle input{width:14px;height:14px;margin:0;accent-color:var(--cyan)}
    @media(max-width:640px){.online-research-toggle{padding:0 8px}.online-research-toggle .online-research-label{display:none}}
  `;
  document.head.append(style);

  const label = document.createElement("label");
  label.className = "online-research-toggle";
  label.title = "Ask the §wyrlz Brain to use authorized online evidence and show research progress when the server has a retrieval capability.";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.id = "onlineResearch";
  checkbox.checked = true;
  checkbox.setAttribute("aria-label", "Use online research");
  const glyph = document.createElement("span"); glyph.textContent = "⌕";
  const text = document.createElement("span"); text.className = "online-research-label"; text.textContent = "Online";
  label.append(checkbox, glyph, text);
  route.insertAdjacentElement("afterend", label);

  const baseValues = ["AUTO", "LALM"];
  for (const base of baseValues) {
    const option = document.createElement("option");
    option.value = `${base}+ONLINE`;
    option.textContent = base === "AUTO" ? "AUTO · SERVER" : "LALM · DIRECT";
    option.hidden = true;
    route.append(option);
  }

  let baseRoute = baseValues.includes(route.value) ? route.value : "AUTO";
  const apply = () => { route.value = checkbox.checked ? `${baseRoute}+ONLINE` : baseRoute; };
  checkbox.addEventListener("change", apply);
  route.addEventListener("change", () => {
    const raw = String(route.value || "AUTO");
    baseRoute = raw.replace(/\+ONLINE$/, "");
    if (!baseValues.includes(baseRoute)) baseRoute = "AUTO";
    apply();
  });

  const phaseLabels = {
    RESEARCH_PLANNING: "Structuring online research",
    RESEARCH_CAPABILITY: "Checking online research capability",
    RESEARCH_QUERY: "Building focused search queries",
    RESEARCH_DISCOVERY: "Discovering candidate sources",
    RESEARCH_VERIFYING: "Verifying evidence",
    RESEARCH_COMPARING: "Comparing evidence",
    RESEARCH_SYNTHESIS: "Synthesizing verified findings"
  };
  // No cognition is performed here. Existing stream phases remain server/Brain-authored;
  // this table only gives research phases readable Mask labels when they arrive.
  window.SWRLZ_RESEARCH_PHASE_LABELS = Object.freeze(phaseLabels);

  // Camera/debug instrumentation may read this explicit user control as evidence.
  const emit = () => {
    try {
      window.dispatchEvent(new CustomEvent("swrlz:online-research-toggle", {detail:{enabled:checkbox.checked, profileId:route.value}}));
    } catch (_) {}
  };
  checkbox.addEventListener("change", emit);
  apply();
  emit();
})();
