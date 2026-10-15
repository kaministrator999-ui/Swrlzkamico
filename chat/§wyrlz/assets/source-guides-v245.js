/* §wyrlz v245 — read-only, source-preserving mobile GitHub guide cards.
   Presentation only. No GitHub credentials, requests, writes or automatic sends. */
(function (root) {
  "use strict";
  const GUIDE_CONTRACT = "swrlz-source-guide-v1";
  const definitions = [
    {
      id: "workflow",
      heading: "## GitHub workflow guide · source-only",
      title: "GitHub workflow guide",
      description: "Find and inspect existing GitHub Actions workflows.",
      commands: [
        {label:"Browse workflows", value:"@GitHub files .github/workflows", caption:"See the workflow filenames in this repository.", ready:true},
        {label:"Read a workflow", value:"@GitHub read file .github/workflows/NAME.yml", caption:"Replace NAME.yml with a filename from the list.", ready:false}
      ],
      boundary:"Read-only source inspection. Workflow runs and deployments need separate verified permissions and cannot be started here."
    },
    {
      id: "engine",
      heading: "## §E engine guide · GitHub Stage 1 (read only)",
      title: "Forge engine guide",
      description: "Inspect the actual §E engine source and its separate project rules.",
      commands: [
        {label:"Browse engine files", value:"@GitHub files projects/swrlz-forge-moba", caption:"Inspect the Forge source tree.", ready:true},
        {label:"Read engine §tart", value:"@GitHub read file §tart_§E.md", caption:"Read the separate Forge startup authority.", ready:true}
      ],
      boundary:"Engine planning, cloning, reviews, commits and deployment remain unavailable in this GitHub Stage 1."
    },
    {
      id: "engine-pack",
      heading: "## §E atomic starter-pack guide · GitHub Stage 1 (read only)",
      title: "Forge starter packs",
      description: "Inspect native scene packages and their provenance descriptors.",
      commands: [
        {label:"Browse starter packs", value:"@GitHub files projects/swrlz-forge-moba/starter-packs", caption:"Inspect existing starter-pack files.", ready:true},
        {label:"Read a pack file", value:"@GitHub read file PATH", caption:"Replace PATH with the exact existing file path.", ready:false}
      ],
      boundary:"This guide cannot create, verify by tool, approve, commit or deploy a pack."
    }
  ];
  const isExactGuide = (source, heading) =>
    source === heading || source.startsWith(heading + "\n");
  const classify = value => {
    const source=String(value||"").replace(/\r\n?/g,"\n");
    const def=definitions.find(item=>isExactGuide(source,item.heading));
    if(!def || source.length>12000)return null;
    // Never invent source-side commands. A future server revision may remove one.
    const commands=def.commands.filter(item=>source.includes(item.value));
    if(!commands.length)return null;
    return {
      contract: GUIDE_CONTRACT, kind:def.id, title:def.title,
      description:def.description, commands:commands.map(item=>({...item})),
      boundary:def.boundary, source
    };
  };
  const element = (tag, className, text) => {
    const node=document.createElement(tag);
    if(className)node.className=className;
    if(text!==undefined)node.textContent=String(text);
    return node;
  };
  const render = (container, value, options={}) => {
    if(!container || typeof document==="undefined")return false;
    const data=classify(value);
    if(!data)return false;
    const card=element("section","source-guide");
    card.dataset.guideKind=data.kind;
    card.setAttribute("aria-label",data.title);
    const head=element("div","source-guide-head");
    const identity=element("div","source-guide-kicker","GITHUB  ·  GUIDE");
    const badge=element("span","source-guide-badge","READ ONLY");
    head.append(identity,badge);
    const title=element("h3","source-guide-title",data.title);
    const description=element("p","source-guide-description",data.description);
    const actions=element("div","source-guide-commands");
    for(const item of data.commands){
      const row=element("div","source-guide-command");
      const body=element("div","source-guide-command-body");
      const label=element("div","source-guide-command-title",item.label);
      const code=element("code","source-guide-command-code",item.value);
      const caption=element("div","source-guide-command-caption",item.caption);
      body.append(label,code,caption);
      const button=element("button","source-guide-command-button",item.ready?"Insert":"Copy");
      button.type="button";
      button.setAttribute("aria-label",(item.ready?"Insert command: ":"Copy template: ")+item.value);
      button.addEventListener("click",async()=>{
        if(item.ready && typeof options.preparePrompt==="function"){
          options.preparePrompt(item.value); // Inserts into composer; NEVER sends.
          return;
        }
        try{
          await navigator.clipboard.writeText(item.value);
          button.textContent="Copied";
        }catch(_){
          button.textContent="Unavailable";
        }
      });
      row.append(body,button);actions.appendChild(row);
    }
    const limit=element("p","source-guide-boundary",data.boundary);
    const details=element("details","source-guide-original");
    const summary=element("summary","","Full original answer and restrictions");
    const raw=element("pre","source-guide-raw",data.source);
    details.append(summary,raw);
    card.append(head,title,description,actions,limit,details);
    container.appendChild(card);
    return true;
  };
  const api=Object.freeze({classify,render});
  root.SwrlzSourceGuidesV245=api;
  if(typeof module!=="undefined" && module.exports)module.exports=api;
})(typeof window!=="undefined"?window:globalThis);
