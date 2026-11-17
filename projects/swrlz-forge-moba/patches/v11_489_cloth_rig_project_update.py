"""§E v11.489: weighted Sorting Hat cloth rig, clip playback and selected-card model update.

All changes are additive to v11.488: no alteration to the original starter
mesh, account credentials, engine source predecessors or revision lineage.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_489_CLOTH_RIG_PROJECT_UPDATE"

def once(text,old,new,tag):
    n=text.count(old)
    if n!=1:raise AssertionError(("v11.489 anchor",tag,n,old[:120]))
    return text.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_488_ACCOUNT_PROJECT_NAMING" in html
    cloth=(ROOT/"runtime/model_atelier_cloth_rig_v11_489.js").read_text("utf8")
    card=(ROOT/"runtime/my_projects_update_model_v11_489.js").read_text("utf8")
    for k in ("se489ClothRigValidate","se489ClothSkinWeights",
              "se489SelectClip","SWYRL_ENGINE_CLOTH_RIG_489"):
        assert k in cloth,k
    for k in ("updateSelectedModel","sourceModel","se486Rev","cloud.save"):
        # The current revision helper variable is named 'revisions';
        # check the stable API rather than a legacy local alias.
        if k=="se486Rev":k="REVISIONS_486"
        assert k in card,k
    # Inside the existing Model Atelier closure after rig editor has been
    # installed; extends the original GPU SkinnedMesh pipeline.
    html=once(html,"  function refreshList(){",
      cloth+"\n  function refreshList(){",
      "native Model Atelier cloth rig")
    # Existing My Projects wrapper is already bound to each selected card;
    # add Update Model only to that selected document, never the viewport.
    html=once(html,"function se184SyncDefaultBoxes(){",
      card+"\nfunction se184SyncDefaultBoxes(){",
      "selected-card revision-safe model update")
    css="""
#projectHub .se184-card-actions [data-se489-update],
#projectHub .se184-card-actions [data-se489Update]{border-color:#95bdda}
.atelier-rig-studio .se489-clip-selector{display:grid;gap:5px;border-bottom:1px solid #3f526a;padding:5px 0 9px}
.atelier-rig-studio .se489-clip-selector[hidden]{display:none}
.atelier-rig-studio .se489-clip-selector label{display:grid;gap:4px}
.atelier-rig-studio .se489-clip-selector select{width:100%;min-height:36px;background:#20344b;color:#ebf6ff;border:1px solid #8baac4;border-radius:6px}
.atelier-rig-studio .atelier-rig-actions[hidden]{display:none!important}
"""
    html=once(html,"</head>",'<style id="se489ClothRig">'+css+'</style>\n</head>',
      "cloth rig UI")
    for old,new,tag in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_488_ACCOUNT_PROJECT_NAMING",MARKER,"marker"),
      ("ENGINE · MAKER v11.488","ENGINE · MAKER v11.489","header"),
      ("v11.488 · account-save names and model rename",
       "v11.489 · cloth rig animation and in-place account model updates","headline"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.488'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.489'","build version"),
      ("<title>§wyrl§ Engine · Maker v11.488</title>",
       "<title>§wyrl§ Engine · Maker v11.489</title>","title"),
    ):html=once(html,old,new,tag)
    old=" source.engine='§wyrl§ Engine · Maker v11.488';source.version=11.488;"
    if html.count(old)!=5:raise AssertionError(("source provenance",html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.489';source.version=11.489;")
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!="v11.488"]
    notes['history'].insert(0,{'version':'v11.488','changes':notes.get('changes',[])})
    notes.update(version='v11.489',date='2026-11-17',
      title="Animated cloth rig and same-project model updating",
      changes=[
        "A new native cloth-skin skeleton schema supports up to 48 hierarchical bones, smooth four-influence vertex weights, and multiple named editable animation clips in the existing Model Studio Rig · Pose · Animate panel.",
        "The owner-supplied one-mesh Sorting Hat now has a separate exportable rigged JSON file with eleven cloth joints and five clips: idle, talking, laughing, scowling, tip flourish. Original mesh, UV coordinates, material and painted image remain unchanged.",
        "My Projects now has Update Model on each account/on-device project card. It accepts version-bound model packages or a native project export with matching model part identity; the active scene is never switched.",
        "Cloud updates use the existing account project's ID, expected revision, atomic server compare-and-swap, and rolling eight-slot history. Original scene, editor and other project data remain intact.",
        "Local card updates similarly keep identity and create revision history; project cards never create separate imported copies.",
        "Starter templates, legacy hand rig, original v11.488 naming, VR tool controls and existing native project export remain unchanged."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
