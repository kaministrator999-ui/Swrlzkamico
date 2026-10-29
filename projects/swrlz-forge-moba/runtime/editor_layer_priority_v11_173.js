// §E v11.173: remove the Projects modal from the editor/dock stacking context.
// Reparent the original node (never clone or re-create controls/listeners).
// Its existing open/close, starter checkbox, tabs, Save/Load and cloud handlers
// all retain the same element identity and IDs.
function se173PromoteProjectDialog(){
 const hub=document.getElementById('projectHub');
 if(!hub)throw Error('SE173_PROJECT_DIALOG_MISSING');
 if(hub.parentElement!==document.body)document.body.appendChild(hub);
 return hub;
}
se173PromoteProjectDialog();
