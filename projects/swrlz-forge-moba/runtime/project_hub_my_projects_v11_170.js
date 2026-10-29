// §E v11.170: account-backed My Projects tab inside the existing native starter hub.
// Runs inside the canonical Chat host closure; no new credentials or storage APIs.
let se170Pane=null,se170Status=null,se170Cards=null,se170Active='starter',se170Epoch=0;
function se170Message(message){if(se170Status)se170Status.textContent=message;}
function se170Invalidate(){
  ++se170Epoch;
  if(se170Cards)se170Cards.replaceChildren();
  se170Message('Connect your §wyrlz Chat account to browse your saved projects.');
}
function se170Select(tab){
  se170Active=tab;
  for(const name of ['starter','mine']){
    const button=document.getElementById('se170-tab-'+name);
    const pane=document.getElementById('se170-pane-'+name);
    if(!button||!pane)continue;
    button.setAttribute('aria-selected',String(name===tab));
    button.tabIndex=name===tab?0:-1;
    pane.hidden=name!==tab;
  }
  if(tab==='mine')se170Refresh();
}
async function se170Refresh(){
  if(se170Active!=='mine'||!se170Cards)return;
  const token=++se170Epoch;
  se170Cards.replaceChildren();
  if(!ready){
    if(frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
    se170Message('Connecting to your Chat account…');
    return;
  }
  se170Message('Loading your saved projects…');
  try{
    const data=await rpc('cloud.list');
    if(token!==se170Epoch||se170Active!=='mine')return;
    if(!Array.isArray(data.projects))throw Error('Invalid project list.');
    if(!data.projects.length){se170Message('No account projects saved yet. Save a project using § Chat to see it here.');return;}
    se170Message(data.projects.length+' saved project'+(data.projects.length===1?'':'s')+' · Choose Load to open one.');
    for(const project of data.projects){
      if(!bounded(project?.id,160))continue;
      const card=document.createElement('article');card.className='se170-project-card';
      const name=document.createElement('strong');name.textContent=summaryName(project.name)||'Untitled project';
      const version=document.createElement('span');version.textContent='Revision '+(Number.isInteger(project.revision)?project.revision:'unknown');
      const load=document.createElement('button');load.type='button';load.textContent='Load';load.setAttribute('aria-label','Load '+name.textContent);
      load.onclick=async()=>{
        if(cloudBusy)return;
        load.disabled=true;se170Message('Loading '+name.textContent+'…');
        try{const loaded=await loadCloud(project.id);
          if(loaded){document.getElementById('projectHub')?.classList.remove('show');se170Message('Project loaded.');}
          else se170Message('Project was not loaded; your previous workspace is preserved.');
        }finally{load.disabled=false;}
      };
      card.append(name,version,load);se170Cards.append(card);
    }
  }catch(error){
    if(token!==se170Epoch)return;
    se170Message('Could not list projects: '+summaryName(error.message)+'. Sign in using § Chat if needed.');
  }
}
function se170AccountStatus(payload){
  se170Invalidate();
  if(payload?.authenticated&&se170Active==='mine')se170Refresh();
}
function se170Install(){
  const hub=document.getElementById('projectHub'),win=hub?.querySelector('.project-window');
  const header=win?.querySelector('.project-head');
  if(!header||document.getElementById('se170-tab-mine'))return;
  const tabs=document.createElement('div');tabs.className='se170-hub-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Project library');
  const starter=document.createElement('div');starter.id='se170-pane-starter';starter.className='se170-hub-pane';starter.setAttribute('role','tabpanel');starter.setAttribute('aria-labelledby','se170-tab-starter');
  se170Pane=document.createElement('div');se170Pane.id='se170-pane-mine';se170Pane.className='se170-hub-pane';se170Pane.setAttribute('role','tabpanel');se170Pane.setAttribute('aria-labelledby','se170-tab-mine');se170Pane.hidden=true;
  for(const [name,title] of [['starter','Starter Projects'],['mine','My Projects']]){
    const button=document.createElement('button');button.type='button';button.id='se170-tab-'+name;
    button.setAttribute('role','tab');button.setAttribute('aria-controls','se170-pane-'+name);
    button.textContent=title;button.onclick=()=>se170Select(name);tabs.append(button);
  }
  // Keep every existing native starter card, checkbox, save/load action, and
  // attached event listener by moving the existing nodes, not cloning them.
  while(header.nextSibling)starter.append(header.nextSibling);
  win.append(tabs,starter,se170Pane);
  const tools=document.createElement('div');tools.className='se170-my-tools';
  const refresh=document.createElement('button');refresh.type='button';refresh.textContent='Refresh';refresh.onclick=se170Refresh;
  const signIn=document.createElement('button');signIn.type='button';signIn.textContent='Open § Chat / Sign in';signIn.onclick=()=>{
    hub.classList.remove('show');openPanel();
  };
  tools.append(refresh,signIn);
  se170Status=document.createElement('p');se170Status.id='se170-library-status';se170Status.setAttribute('role','status');se170Status.setAttribute('aria-live','polite');
  se170Cards=document.createElement('div');se170Cards.className='se170-project-list';
  se170Pane.append(tools,se170Status,se170Cards);
  se170Message('Connect your §wyrlz Chat account to browse your saved projects.');
  se170Select('starter');
}
