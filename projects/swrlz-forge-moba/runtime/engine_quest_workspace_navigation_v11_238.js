// §E v11.238 candidate — real Quest Browser 2D workspace chrome.
// Reparent EXISTING native controls (no clones, no new handlers) into an
// accessible popover, preserving all original element event listeners.
// This does not arrange or control Meta OS's separate browser windows.
(function se238Workspace(){
  const s={gameMoves:0,gameRestores:0,modelMoves:0,modelRestores:0,
    game:null,model:null,topObserver:null,profileObserver:null,
    transitions:0,lastError:''};
  const isQuest=()=>document.documentElement.classList.contains('se-quest-panel')&&
    document.documentElement.dataset.seDeviceProfile==='quest-browser';
  const node=(tag,cls,textContent)=>{
    const n=document.createElement(tag);n.className=cls;
    if(textContent!==undefined)n.textContent=textContent;
    return n;
  };
  function portalMove(element,parent,originals){
    if(originals.has(element))return false;
    const marker=document.createComment('§E v11.238 original control position');
    element.before(marker);
    originals.set(element,marker);
    parent.appendChild(element);
    return true;
  }
  function restore(originals){
    for(const [element,marker] of originals){
      if(marker.parentNode)marker.replaceWith(element);
    }
    originals.clear();
  }
  function makeGame(){
    const bar=document.querySelector('.app > .topbar');
    if(!bar)return;
    if(s.game?.bar===bar)return;
    const trigger=node('button','se238-game-tools-toggle','☷ Controls');
    trigger.type='button';trigger.id='se238GameToolsToggle';
    trigger.setAttribute('aria-expanded','false');
    trigger.setAttribute('aria-controls','se238GameTools');
    const drawer=node('section','se238-game-tools-drawer');
    drawer.id='se238GameTools';drawer.hidden=true;
    drawer.setAttribute('aria-label','Game Engine controls');
    const heading=node('header','se238-drawer-head');
    heading.append(node('strong','','Engine controls'));
    const close=node('button','se238-drawer-close','✕ Close');
    close.type='button';close.addEventListener('click',()=>openGame(false));
    heading.append(close);drawer.append(heading);
    const contents=node('div','se238-drawer-content');
    drawer.append(contents);
    bar.append(trigger);document.body.append(drawer);
    s.game={bar,trigger,drawer,contents,originals:new Map()};
    trigger.addEventListener('click',()=>openGame(drawer.hidden));
    if(s.topObserver)s.topObserver.disconnect();
    s.topObserver=new MutationObserver(()=>{if(isQuest())collectGame();});
    s.topObserver.observe(bar,{childList:true});
  }
  function openGame(open){
    if(!s.game)return;
    const g=s.game;
    g.drawer.hidden=!open;
    g.trigger.setAttribute('aria-expanded',String(open));
    g.trigger.classList.toggle('active',open);
    if(open)g.drawer.querySelector('.se238-drawer-close')?.focus();
    else g.trigger.focus();
  }
  function collectGame(){
    const g=s.game;if(!g)return;
    for(const element of [...g.bar.children]){
      if(element===g.trigger||element.classList.contains('se187-game-tabs'))continue;
      if(portalMove(element,g.contents,g.originals))s.gameMoves++;
    }
  }
  function makeModel(){
    const panel=document.getElementById('modelAtelierPanel');
    const head=panel?.querySelector('.atelier-head');
    const actions=head?.querySelector('.atelier-actions');
    if(!panel||!head||!actions)return;
    if(s.model?.panel===panel)return;
    const menu=node('details','se238-model-menu');
    menu.id='se238ModelActions';
    const summary=node('summary','','☷ Model actions');
    menu.append(summary);
    const contents=node('div','se238-model-menu-content');
    menu.append(contents);
    head.insertBefore(menu,actions);
    const tools=node('button','se238-model-tools-toggle','☷ Edit tools');
    tools.type='button';tools.id='se238ModelToolsToggle';
    tools.setAttribute('aria-expanded','false');
    tools.addEventListener('click',()=>{
      const open=!panel.classList.contains('se238-tool-rail-open');
      panel.classList.toggle('se238-tool-rail-open',open);
      tools.setAttribute('aria-expanded',String(open));
    });
    head.insertBefore(tools,menu);
    s.model={panel,head,actions,menu,contents,tools,originals:new Map()};
  }
  function collectModel(){
    const m=s.model;if(!m)return;
    for(const element of [...m.actions.children]){
      // Keep the real Close button permanently visible even in a small window.
      const name=(element.getAttribute('aria-label')||element.textContent||'').trim();
      if(element.tagName==='BUTTON'&&(/\bclose\b/i.test(name)||/close/i.test(element.id||'')))continue;
      if(portalMove(element,m.contents,m.originals))s.modelMoves++;
    }
  }
  function restoreGame(){
    const g=s.game;if(!g)return;
    openGame(false);
    restore(g.originals);s.gameRestores++;
  }
  function restoreModel(){
    const m=s.model;if(!m)return;
    m.menu.open=false;
    m.panel.classList.remove('se238-tool-rail-open');
    m.tools.setAttribute('aria-expanded','false');
    restore(m.originals);s.modelRestores++;
  }
  function apply(){
    s.transitions++;
    try{
      makeGame();makeModel();
      if(isQuest()){collectGame();collectModel();}
      else{restoreGame();restoreModel();}
    }catch(e){s.lastError=String(e?.message||e).slice(0,180);}
  }
  function mount(){
    apply();
    if(!s.profileObserver){
      s.profileObserver=new MutationObserver(apply);
      s.profileObserver.observe(document.documentElement,{
        attributes:true,attributeFilter:['class','data-se-device-profile']});
    }
  }
  document.addEventListener('pointerdown',event=>{
    const g=s.game,m=s.model;
    if(g&&!g.drawer.hidden&&
       !g.drawer.contains(event.target)&&!g.trigger.contains(event.target)){
      g.drawer.hidden=true;g.trigger.setAttribute('aria-expanded','false');
    }
    if(m&&m.menu.open&&!m.menu.contains(event.target))m.menu.open=false;
    if(m&&m.panel.classList.contains('se238-tool-rail-open')&&
       !m.tools.contains(event.target)&&
       !m.panel.querySelector('.atelier-tool-rail')?.contains(event.target)){
      m.panel.classList.remove('se238-tool-rail-open');
      m.tools.setAttribute('aria-expanded','false');
    }
  },{passive:true});
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    if(s.game&&!s.game.drawer.hidden)openGame(false);
    if(s.model){s.model.menu.open=false;
      s.model.panel.classList.remove('se238-tool-rail-open');
      s.model.tools.setAttribute('aria-expanded','false');}
  });
  window.SWYRL_ENGINE_QUEST_WORKSPACE_238=Object.freeze({
    diagnose:()=>({questLayoutActive:isQuest(),
      engineControlsInDrawer:s.game?.originals.size||0,
      modelActionsInMenu:s.model?.originals.size||0,
      gameDrawerOpen:!!s.game&&!s.game.drawer.hidden,
      modelActionsOpen:!!s.model?.menu.open,
      modelToolRailOpen:!!s.model?.panel.classList.contains('se238-tool-rail-open'),
      gameMoves:s.gameMoves,modelMoves:s.modelMoves,
      gameRestores:s.gameRestores,modelRestores:s.modelRestores,
      lastError:s.lastError})
  });
  if(document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
  window.addEventListener('load',apply,{once:true});
})();
