# Forge terminal validation feedback

The live Model Atelier trial reached `FORGE_INVALID_LOFT_PROFILE` after one correction and previously reached `FORGE_UNREQUESTED_NATIVE_ACTION`. The typed failures occurred before the server could register any editor changes. The chat reply gave generic connection advice for both paths.

`forge_chat_actions.py` selects fixed copy in the terminal validation branch. Invalid lofts report the bounded diagnostic category and suggest retrying one part at a time. Rejected scope asks the user to specify the part and action. The ordinary chat reply and terminal `FAILED` event carry the same message. The activity log retains the typed code. The message draws only on fixed copy and bounded reason keys.

The terminal branch runs after the planner's one correction and before preview staging or editor registration. Whether §C can create a valid curved mesh after correcting an invalid proposal requires a live modeling retest.

`tests/test_forge_validation_messages.py` compares the exact source before and after the change. It exercises four loft reasons, unknown and absent diagnostics, rejected scope, an unchanged unrelated validation rejection, an unchanged inference transport failure, and identical events for a successful correction. Terminal failure assertions confirm no preview or native batch registered.
