"""§wyrl§ Engine v7.5: mobile editor chrome consolidation."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.5 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_4_EDITOR_WORKSPACES":"V7_5_MOBILE_EDITOR_CHROME",
      "Maker v7.4":"Maker v7.5","MAKER v7.4":"MAKER v7.5",
      "v7.4 · EDITOR WORKSPACES":"v7.5 · MOBILE EDITOR CHROME",
      "version:'v7.4'":"version:'v7.5'",
      "version:'swyrl-engine-agent-v5.4'":"version:'swyrl-engine-agent-v5.5'",
      "engine:'§wyrl§ Engine · Maker v7.4'":"engine:'§wyrl§ Engine · Maker v7.5'",
      "version:7.4":"version:7.5",
      "editorLog('§wyrl§ Engine v7.4 initialized · editor menus · workspace launcher','ok')":"editorLog('§wyrl§ Engine v7.5 initialized · consolidated mobile editor chrome','ok')"
    }.items(): s=_once(s,a,b)

    css=r"""
.mobile-engine-trigger{display:none}
@media(max-width:720px){
 .engine-menubar{left:10px!important;right:auto!important;top:8px!important;width:auto!important;max-width:none!important;padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important;overflow:visible!important}
 .engine-menu{display:none!important}
 .mobile-engine-trigger{display:flex!important;align-items:center;gap:7px;border:1px solid #35516d;background:#0b1a2bf2;color:#e4f4ff;padding:9px 12px;border-radius:11px;font:800 12px system-ui;box-shadow:0 7px 20px #0008}
 .workspace-launcher{position:absolute!important;left:10px!important;right:10px!important;top:52px!important;bottom:auto!important;max-height:70vh!important;overflow:auto!important}
 .engine-command-deck{display:none!important}
 .engine-stats-pill{top:52px!important;bottom:auto!important;right:10px!important;max-width:58vw!important;font-size:10px!important;padding:5px 8px!important}
 .runtime-diag{bottom:96px!important}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Add one mobile entry point to the existing workspace launcher; desktop retains menus.
    marker="host.appendChild(bar);document.addEventListener('pointerdown'"
    repl="""const mobile=document.createElement('button');mobile.className='mobile-engine-trigger';mobile.innerHTML='☰ <span>§E</span>';mobile.setAttribute('aria-label','Open §E workspaces');mobile.onclick=e=>{e.stopPropagation();$('engineWorkspaces')?.classList.toggle('open')};bar.appendChild(mobile);
  host.appendChild(bar);document.addEventListener('pointerdown'"""
    s=_once(s,marker,repl)

    # The launcher is created after the bar; make the mobile trigger robust to first tap timing.
    marker2="host.appendChild(w);$('workspaceClose').onclick=()=>w.classList.remove('open');"
    repl2=marker2+"\n  mobile.onclick=e=>{e.stopPropagation();w.classList.toggle('open')};"
    s=_once(s,marker2,repl2)
    return s
