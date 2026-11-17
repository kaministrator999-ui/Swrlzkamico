"""§E v11.495 — compact reversible history, smaller model update transfer."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_495_FAST_REVISION_TRANSFER'
def once(html,old,new,label):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.495',label,n,old[:110]))
 return html.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_494_MODEL_UPDATE_LIFECYCLE' in html
 js=(ROOT/'runtime/model_revision_shared_texture_v11_495.js').read_text('utf8')
 assert 'se495TexturePool' in js
 html=once(html,'const se494TrustedLoadCache=new Map();',
  js+'\nconst se494TrustedLoadCache=new Map();','install versioned codec in trusted host')
 # Original revision actions were compiled earlier and captured the old codec.
 # Use the dynamic wrapper when a user opens/recovers previous snapshots.
 for old,new in (
  ('se486Rev.history(document)','window.SWYRL_ENGINE_REVISIONS_495.history(document)'),
  ('se486Rev.unpack(item)','window.SWYRL_ENGINE_REVISIONS_495.unpack(item)'),
  ('se486AssetRev.history(doc)','window.SWYRL_ENGINE_REVISIONS_495.history(doc)'),
  ('se486AssetRev.unpack(item)','window.SWYRL_ENGINE_REVISIONS_495.unpack(item)')
 ):html=once(html,old,new,'legacy revision restoration')
 html=once(html,
  'const archived=(await revisions.prepare(doc,next,version,max)).payload;',
  'const archived=(await window.SWYRL_ENGINE_REVISIONS_495.prepare(doc,next,version,max,onProgress)).payload;',
  'model card archive uses shared texture history')
 html=once(html,
  "   onProgress('Saving '+String(metadata.name||record.name)+' · expected revision '+version+'…');",
  "   onProgress('Uploading '+(bytes.byteLength/1048576).toFixed(1)+' MiB to §C account · expected revision '+version+'…');",
  'display actual transfer size')
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_494_MODEL_UPDATE_LIFECYCLE',MARKER),
  ('ENGINE · MAKER v11.494','ENGINE · MAKER v11.495'),
  ('v11.494 · staged model updates and immediate reopen','v11.495 · faster model updates with compact revision history'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.494'","window.SWRLZ_FORGE_BUILD={version:'v11.495'"),
  ('<title>§wyrl§ Engine · Maker v11.494</title>','<title>§wyrl§ Engine · Maker v11.495</title>')
 ):html=once(html,old,new,'runtime identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.494';source.version=11.494;"
 if html.count(old)!=5:raise AssertionError(('v11.495 provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.495';source.version=11.495;")
 at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.494']
 notes['history'].insert(0,{'version':'v11.494','changes':notes.get('changes',[])})
 notes.update(version='v11.495',date='2026-11-17',
  title='Compacted revision history for faster in-place model saves',
  changes=[
   'Model revisions no longer store separate large copies of an unchanged embedded UV PNG; archived full scenes share a lossless texture pool in the same native account record.',
   'The first eligible save migrates older full gzip+base64 snapshots to compact snapshots before sending them, preserving the last seven historic account revisions and the current revision.',
   'The normal Revision History UI transparently reconstructs each prior full model and texture, including versions with different painted images.',
   'My Projects Save progress shows the true encoded transfer size in MiB, rather than hiding tens of megabytes under a generic Saving message.',
   'Existing validated project identity, mesh, rig, animation, original ZIP updates, conditional account writes and normal project reopening remain intact.',
   'A one-time migration can spend time unpacking old snapshots, but subsequent cloud transfers carry far fewer duplicated texture bytes. Actual network performance depends on §C storage.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
