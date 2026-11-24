"""Append v11.552 UV alignment and verified account startup recovery.

Historical source/patch hashes remain immutable. The startup correction is
applied only after the complete inherited version chain has been verified.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def one(text,before,after):
    count=text.count(before)
    assert count==1,('v11.552 startup recovery anchor',count,before[:110])
    return text.replace(before,after,1)

def section(text,start,end,replacement):
    assert text.count(start)==1 and text.count(end)==1,('v11.552 section anchor',start)
    a=text.index(start);b=text.index(end,a)+len(end)
    return text[:a]+replacement+text[b:]

def apply(html):
    anchor='const se356BaseEnsurePanel=ensurePanel;'
    assert html.count(anchor)==1
    assert 'function se552Open()' not in html
    html=html.replace(anchor,(ROOT/'runtime/uv_texture_alignment_v11_552.js').read_text('utf8')+'\n'+anchor,1)
    # Replace the two isolated startup orchestrators after all historical
    # source pins were validated. They do not own OAuth or serialized projects.
    html=section(html,'/* SE476_ENGINE_ACCOUNT_START_START */',
                 '/* SE476_ENGINE_ACCOUNT_START_END */',
                 (ROOT/'runtime/engine_account_start_recovery_v11_552.js').read_text('utf8').strip())
    html=section(html,'/* SE476_ACCOUNT_BRIDGE_START */',
                 '/* SE476_ACCOUNT_BRIDGE_END */',
                 (ROOT/'runtime/engine_account_bridge_recovery_v11_552.js').read_text('utf8').strip())
    # Native local loading now emits a boolean receipt after successful
    # deserialization; a stale remembered project ID cannot masquerade as one.
    html=one(html,
        "se175LocalMessage('Loaded '+wanted.name+'.');window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('local',wanted.id);",
        "se175LocalMessage('Loaded '+wanted.name+'.');window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('local',wanted.id);return true;")
    # The older saved-default boot must release the newer gateway only after
    # the original loader completes (or fails), never while a second load runs.
    html=one(html,
        "  status('');\n }\n async function readLocal(id){",
        """  status('');
  window.dispatchEvent(new CustomEvent('swrlz:saved-default-complete',{
   detail:{source:state.source,id:state.id,success:success===true,reason}
  }));
 }
 async function readLocal(id){""")
    # Keep the actual account-project failure reason visible in startup.
    html=one(html,
        " if(opened!==true)return false;\n const receipt=cloudRefs.get(getProjectId());",
        """ if(opened!==true){
  const diagnostics=window.SWYRL_ENGINE_PROJECT_LOAD_493;
  const detail=diagnostics?.getError?.()||status?.textContent||
   'Native account project download was not confirmed.';
  return se533AccountOpenFailure(detail);
 }
 const receipt=cloudRefs.get(getProjectId());""")
    return html
