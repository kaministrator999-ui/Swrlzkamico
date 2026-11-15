# §C Stop → Send terminal reconciliation

This patch is a one-file follow-up to the already deployed Stop/Continue/webpage-quality release.

## Source inspection

The current live Station already writes `activeGeneration.terminal=true` and `terminalType="CANCELLED"` after acknowledging a cancellation and actually exiting its generation worker. The Chat UI already has correct desired button states in `syncStationControls`: running -> Stop visible, Send hidden; terminal -> Stop hidden, Send enabled. However, the live `renderStationGeneration` exits early if the assistant response was saved/committed and did not call `syncStationControls`. The matching `settleStationGeneration` also did not immediately refresh controls after clearing `stationAcknowledgedRequest`. Those render paths could leave the stale Stop button on screen.

## Correction

- When Station supplies a matching terminal receipt (`CANCELLED`, `COMPLETE`, `COMPLETED`, or `FAILED`), the settlement function runs `syncStationControls` immediately after removing the acknowledged request.
- When a saved response causes `renderStationGeneration` to return early, it also reconciles the composer.
- Do NOT switch to Send upon `CANCEL_REQUESTED` alone: native decode must actually terminate. Do NOT hide Stop after a network error with no cancellation receipt.
- Only the live `chat/§wyrlz/index.html` is updated. Exact source parent revision and hash are checked; previous bytes are backed up for rollback.

Source tests execute the actual live `syncStationControls` function across actively running, cancellation pending, confirmed cancelled, completed, failed, pre-ack sending, and fully idle states, and parse all inline Chat JavaScript. Mobile visual acceptance remains user-side.
