"""§E v11.488 — ask for names before first account save; allow model rename.

Uses the current v11.371 Save/Clone and v11.470 account asset methods,
leaves stable project/asset identity and v11.486 revision history unchanged.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_488_ACCOUNT_PROJECT_NAMING"

def once(text,old,new,label):
    found=text.count(old)
    if found!=1:raise AssertionError(("v11.488 source anchor",label,found,old[:150]))
    return text.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_487_CORRECT_MODEL_PROJECT_EXPORT" in html
    project=(ROOT/"runtime/account_project_naming_v11_488.js").read_text("utf8")
    asset=(ROOT/"runtime/account_asset_naming_v11_488.js").read_text("utf8")
    for token in ("se488AskProjectName","se488EnsureProjectNameForAccount",
                  "se488PreviousAccountSave"):
        assert token in project,token
    for token in ("se488NameAssetBeforeCloudSave","se488RenameActiveModel",
                  "se488InstallNameAction"):
        assert token in asset,token

    # Existing Save Project clones starters before cloud sync. Ask for the
    # account name BEFORE changing/loading that native project, not after.
    html=once(html,
      """  if(!se371HasSavedIdentity())await se371Clone(se371NewName(se371ProjectName()));
  else await se371SaveLocal();""",
      """  if(!se371HasSavedIdentity()){
    const proposal=ready&&se176AccountConnected
      ?se488AskProjectName(se488NeedsProjectName()?'':se371ProjectName())
      :se371NewName(se371ProjectName());
    if(proposal===null)throw Error('Save cancelled. Project name was not supplied.');
    await se371Clone(proposal);
  }else{
    if(ready&&se176AccountConnected&&se488NeedsProjectName()){
      const name=se488AskProjectName('');
      if(name===null)throw Error('Save cancelled. Project name was not supplied.');
      se175StampProject(getProjectId(),name,se371SourceId());
    }
    await se371SaveLocal();
  }""",
      "first account save prompts before native clone and local save")

    # The Chat account button and VR cloud actions can invoke saveCloud
    # directly, bypassing the normal project toolbar. All of them must use
    # the same naming gate and existing version-checked account save.
    html=once(html,
      "window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({",
      project+"\nwindow.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({",
      "account save naming wrapper")

    # The standalone Model Studio account save is a different versioned
    # asset path. Preserve its working.id and remote revision through rename.
    html=once(html,
      """ async function save(type,cloud){
  if(!['modeler','particles'].includes(type)||busy)return false;""",
      asset+""" async function save(type,cloud){
  if(!['modeler','particles'].includes(type)||busy)return false;""",
      "asset naming helper")
    html=once(html,
      """   const record=snapshot(type),working=se470Working.get(type);
   if(cloud){""",
      """   const record=snapshot(type),working=se470Working.get(type);
   if(cloud&&!se488NameAssetBeforeCloudSave(type,record,working))return false;
   if(cloud){""",
      "name unnamed asset before cloud account write")
    html=once(html,
      """  bar.hidden=!type;
  if(type!==lastStudio){""",
      """  bar.hidden=!type;
  const nameControl=bar.querySelector('[data-se488-name]');
  if(nameControl)nameControl.hidden=type!=='modeler';
  if(type!==lastStudio){""",
      "only show rename control inside Model Studio")
    html=once(html,
      """  se486InstallAssetActions(bar);
  refresh();""",
      """  se486InstallAssetActions(bar);
  se488InstallNameAction(bar);
  refresh();""",
      "mount model rename inside existing asset bar")

    for old,new,label in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_487_CORRECT_MODEL_PROJECT_EXPORT",MARKER,"marker"),
      ("ENGINE · MAKER v11.487","ENGINE · MAKER v11.488","header"),
      ("v11.487 · named exports for active models and saved projects",
       "v11.488 · account-save names and model rename","headline"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.487'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.488'","build metadata"),
      ("<title>§wyrl§ Engine · Maker v11.487</title>",
       "<title>§wyrl§ Engine · Maker v11.488</title>","browser title"),
    ):html=once(html,old,new,label)
    prior=" source.engine='§wyrl§ Engine · Maker v11.487';source.version=11.487;"
    if html.count(prior)!=5:raise AssertionError(("project source version",html.count(prior)))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.488';source.version=11.488;")
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[h for h in notes.get("history",[]) if h.get("version")!="v11.487"]
    notes["history"].insert(0,{"version":"v11.487","changes":notes.get("changes",[])})
    notes.update(version="v11.488",date="2026-11-17",
      title="Name account projects and models without duplicating saves",
      changes=[
        "First Save to account on a starter asks for a user-defined project name before creating the independent account-owned copy.",
        "Unnamed or generic account project names require confirmation before a cloud save, including saves initiated from the Chat account panel.",
        "Standalone Model and Particle Studio account saves ask for a model/asset name if unset or inherited from the original Prism Jester or untitled placeholder.",
        "Model Studio's existing asset toolbar gains Name Model, which renames the active model for its next in-place account revision without creating a duplicate asset.",
        "My Projects card exports remain bound to the selected project and preserve native/UV data, account IDs and rolling revision history.",
        "Canonical starter protection, saved project identities and expected-revision concurrency guards remain unchanged."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
