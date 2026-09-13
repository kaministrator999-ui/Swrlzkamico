# Server Runtime 2.3.112 / Web Chat 1.4.95

## Context Capacity + Thread History Integrity

This runtime event separates stored conversation history from bounded model-active context.

- Adds `web/chat_context_capacity.js`.
- Shows estimated active conversation context against the current 2,048-token conversation budget.
- Shows stored thread message count separately from active context usage.
- Reaching 100% does not delete thread messages.
- Preserves the existing outbound bound of the latest 32 eligible messages with up to 2,000 characters per message; the meter estimates the active model-facing footprint of that bounded slice.
- Adds browser-local same-thread history integrity using a shadow snapshot. If an existing thread silently loses recent messages during ordinary state churn, missing messages are restored instead of accepting the shrink.
- Explicit whole-thread deletion remains allowed.
- This event does not deploy stable server code and does not change the LALM context-window implementation itself.

The UI meter is an estimate because browser-side character-to-token conversion cannot exactly reproduce the model tokenizer. It is labeled with the approximation symbol and should be treated as capacity guidance, not exact tokenizer telemetry.
