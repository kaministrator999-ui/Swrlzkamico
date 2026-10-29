// Dismissal is scoped to this exact version, never to future releases.
function engineReleaseNotesInstall(){
 if($('seReleaseNotesDialog'))return;
 const data=SE_RELEASE_NOTES,key='swyrl:release-notes:hidden:'+data.version;
 const suppressed=()=>{try{return localStorage.getItem(key)==='true';}catch{return false;}};
 const dialog=document.createElement('dialog');dialog.id='seReleaseNotesDialog';dialog.setAttribute('aria-labelledby','seReleaseNotesTitle');
 dialog.innerHTML='<header><small>§WYRLZ ENGINE · UPDATE</small><h2 id="seReleaseNotesTitle"></h2><p id="seReleaseNotesSubtitle"></p></header><section><ul id="seReleaseNotesLatest"></ul><details id="seReleaseNotesHistory"><summary>Previous updates</summary><div></div></details></section><footer><label><input type="checkbox" id="seReleaseNotesHide"> Don’t show again for this update</label><button type="button" id="seReleaseNotesClose">Continue</button></footer>';
 document.body.append(dialog);$('seReleaseNotesTitle').textContent='What’s new in '+data.version;$('seReleaseNotesSubtitle').textContent=data.title+' · '+data.date;
 function list(parent,items){for(const text of items){const li=document.createElement('li');li.textContent=text;parent.append(li);}}
 list($('seReleaseNotesLatest'),data.changes);
 const history=$('seReleaseNotesHistory');history.querySelector('summary').textContent='All previous updates · '+(data.history.length+1)+' versions';
 for(const release of [...data.history,data.base]){const details=document.createElement('details'),summary=document.createElement('summary'),ul=document.createElement('ul');summary.textContent=release.version+' · '+release.changes[0].split('. ')[0];details.append(summary,ul);list(ul,release.changes);history.querySelector('div').append(details);}
 const open=()=>{$('seReleaseNotesHide').checked=suppressed();if(!dialog.open)dialog.showModal();};
 $('seReleaseNotesClose').onclick=()=>dialog.close();dialog.addEventListener('close',()=>{try{if($('seReleaseNotesHide').checked)localStorage.setItem(key,'true');else localStorage.removeItem(key);}catch{}});
 const button=document.createElement('button');button.id='seReleaseNotesOpen';button.type='button';button.textContent='Updates · '+data.version;button.setAttribute('aria-haspopup','dialog');button.onclick=open;(document.querySelector('footer.status')||document.body).append(button);
 if(!suppressed())open();
}
queueMicrotask(engineReleaseNotesInstall);
