"""Owner opt-in, invalidation and source isolation checks (synthetic account data)."""
from unittest.mock import patch
import chatgpt_account_memory as memory
from personal_continuity_v1 import archive_signals

ALICE="google:continuity-alice"
BOB="google:continuity-bob"
old={"role":"user","text":"I prefer detailed answers when explaining projects.",
     "createdAt":1700000000}
docs=[{"continuitySignals":archive_signals([old],"old-imported-chat")}]
native=[{"id":"other","title":"My projects","messages":[
    {"role":"user","text":"Please always verify source and tests for my projects.",
     "createdAt":1800000000}]}]
state={ALICE:{"state":"ready","docs":docs,"done":1,"total":1}}

with patch.object(memory,"enabled",side_effect=lambda owner: owner==ALICE), \
     patch.object(memory,"_STATE",state), \
     patch.object(memory,"warm") as warm:
    assert memory.interaction_context(BOB,"Can we explain projects?",native)==""
    warm.assert_not_called()
    output=memory.interaction_context(ALICE,"Explain and test my projects",native)
    assert "detailed answers" in output and "verify source" in output,output
    assert memory.interaction_context(BOB,"test my projects",native)==""


def invalidate_during_compose(prompt,threads,imported,active):
    memory._EPOCH[ALICE]+=1
    return "SHOULD_NOT_LEAK"

with patch.object(memory,"enabled",return_value=True), \
     patch.object(memory,"_STATE",state), \
     patch.object(memory.continuity,"compose",side_effect=invalidate_during_compose):
    assert memory.interaction_context(ALICE,"test",native)==""

print("opt-in continuity, distinct account isolation, invalidation PASS")
