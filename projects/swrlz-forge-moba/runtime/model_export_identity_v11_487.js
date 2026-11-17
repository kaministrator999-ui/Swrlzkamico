/* §E v11.487 — filenames follow the active model, never the original Prism Jester starter.
   Installed inside ModelAtelier's existing closure by the source patch. */
function se487ExportDisplayName(){
  const ws=window.SWYRL_ENGINE_WORKSPACES;
  const scratch=ws?.modelerActive?.()===true && ws?.usingScratch?.()===true;
  const active=model();
  const raw=scratch
    ?(active?.name||active?.title)
    :(currentProject?.projectName||currentProject?.name||active?.name||active?.title);
  return String(raw||'Untitled Model').trim().slice(0,100)||'Untitled Model';
}
function se487ExportStem(){
  // Filename-only normalization: do not rename the persisted project or model.
  const stem=se487ExportDisplayName().normalize('NFKC')
    .replace(/[^\p{L}\p{N}_-]+/gu,'-').replace(/^-+|-+$/g,'').slice(0,90);
  return stem||'untitled-model';
}
function se487ExportOBJName(){
  return se487ExportStem().replace(/[^A-Za-z0-9_]/g,'_');
}
