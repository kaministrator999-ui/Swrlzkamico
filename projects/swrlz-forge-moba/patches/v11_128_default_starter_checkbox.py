"""§E v11.128: one optional persistent default starter per browser,
with checkboxes on every native starter card and safe launch precedence."""
from pathlib import Path
import re,json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:150],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/engine_default_starter_v11_128.css').read_text(encoding='utf8')
 js=(root/'runtime/engine_default_starter_v11_128.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se128-default-starter">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # The selected starter replaces the hardcoded Dragon Den boot only when
 # there is no explicit URL project. This uses existing native starter APIs.
 marker='installPerformanceSettings();applyPerformanceSettings();if(new URLSearchParams(location.search).get(\'project\')===\'starforge-observatory\')'
 start=html.index(marker)
 end=html.index(';installAnimeStarterUI();',start)
 prior=html[start:end]
 assert prior.count('loadCanonicalGlitchDen()')==1
 html=html[:start]+'installPerformanceSettings();applyPerformanceSettings();se128LaunchStartupProject()'+html[end:]
 # The v11.127 splash should not disappear while a model starter is pending.
 html=once(html,'if(loaded&&now-first>=2600&&now-quietSince>=850)finish();',
     'if(!window.se128StartupPending&&loaded&&now-first>=2600&&now-quietSince>=850)finish();')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_127_CLOVER_SHEEP_SWURV_AND_STABLE_EDITOR_BOOT',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_128_SINGLE_DEFAULT_STARTER_AND_STABLE_BOOT')
 for old,new in [
  ('ENGINE · MAKER v11.127','ENGINE · MAKER v11.128'),
  ('v11.127 · organic sheep and steady editor boot','v11.128 · organic sheep and default starter'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.127'","window.SWRLZ_FORGE_BUILD={version:'v11.128'"),
  ('<title>§wyrl§ Engine · Maker v11.127</title>',
   '<title>§wyrl§ Engine · Maker v11.128</title>')
 ]:html=once(html,old,new)
 tag='const SE_RELEASE_NOTES='
 at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Choose one startup starter project and retain Clover Sheep and steady boot',
  date='2026-10-26',changes=[
   'The native Projects template picker now has an accessible Load this project by default checkbox beside each of its starter cards. Only one can be checked. Unchecking it restores the original Dragon Den default.',
   'The chosen starter ID is saved independently in same-browser localStorage and automatically opens on later normal launches; no project JSON, autosave or existing custom files are overwritten.',
   'An explicit ?project= deep link takes precedence without changing the saved default; existing specialized starter query handlers and native template-opening behavior are preserved.',
   'The v11.127 editor boot cover remains visible while asynchronous startup projects load and never displays the legacy empty editor shell prematurely. A bounded safety fallback still exists.',
   'Organic Clover Sheep Tag animations, sheep-centered construction, permanent routes, lower ability cooldowns, 68 assets and all earlier patches remain unchanged.'
  ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11128_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
