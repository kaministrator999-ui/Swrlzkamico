"""Typed native §E plans with server authorization and receipt-bound answers.

The inference model proposes JSON. This module never executes generated code or
native methods. The separate active §E host takes canonical operations and
returns real native receipts through its own short-lived credential.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any, Callable, Iterator

from brain_forge import classify_forge_intent, current_command_text, inspection_text, native_plan_system, requests_new_project, _literal

MAX_OPERATIONS = 16
MAX_PLAN_BYTES = 24576
PLAN_TOKENS = 3072
MATERIALS = ("matte", "silk", "gloss", "metal", "emissive")
MESH_KINDS = ("sphere", "box", "cone", "cylinder")
ACTOR_PREFABS = ("wall", "rock", "bush", "crystal", "pedestal")
_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
_HEX = re.compile(r"^[0-9a-f]{32}$")
_MESH_ATTRIBUTES = {"name", "position", "rotation", "scale", "color", "material"}
_VECTORS = {"position", "rotation", "scale"}
_SCHEMA = {
    "project.create": ({"op", "starterId", "name"}, {"op", "starterId", "name"}),
    "mesh.add": ({"op", "kind"}, _MESH_ATTRIBUTES | {"op", "kind"}),
    "mesh.set": ({"op", "id"}, _MESH_ATTRIBUTES | {"op", "id"}),
    "mesh.select": ({"op", "id"}, {"op", "id"}),
    "mesh.duplicate": ({"op", "id"}, {"op", "id"}),
    "mesh.remove": ({"op", "id"}, {"op", "id"}),
    "sceneactor.add": ({"op", "prefab"}, {"op", "prefab", "name", "position"}),
    "sceneactor.transform": ({"op", "id"}, {"op", "id", "position", "rotation", "scale"}),
    "sceneactor.select": ({"op", "id"}, {"op", "id"}),
    "sceneactor.rename": ({"op", "id", "name"}, {"op", "id", "name"}),
    "editor.undo": ({"op"}, {"op"}),
    "editor.redo": ({"op"}, {"op"}),
}
_LABELS = {"project.create": "create separate project", "mesh.add": "add mesh", "mesh.set": "edit mesh", "mesh.select": "select mesh",
           "mesh.duplicate": "duplicate mesh", "mesh.remove": "remove mesh",
           "sceneactor.add": "add scene actor", "sceneactor.transform": "transform scene actor",
           "sceneactor.select": "select scene actor", "sceneactor.rename": "rename scene actor",
           "editor.undo": "undo", "editor.redo": "redo"}


class ForgePlanError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def operation_contract() -> dict[str, Any]:
    """Small versioned model contract backed by the fixed native host adapter."""
    return {
        "version": "swrlz-forge-native-v2", "maximumOperations": MAX_OPERATIONS,
        "workspaceRules": {"model-atelier": "mesh.*, project.create and available editor.undo/redo",
                           "scene": "sceneactor.*, project.create and available editor.undo/redo"},
        "operations": {name: {"required": sorted(required), "optional": sorted(allowed - required)}
                       for name, (required, allowed) in _SCHEMA.items()},
        "meshKinds": list(MESH_KINDS), "sceneActorPrefabs": list(ACTOR_PREFABS),
        "materials": list(MATERIALS), "name": "1–100 literal characters",
        "color": "#RRGGBB", "vectors": "arrays [x,y,z], three finite numbers",
        "positionAndRotation": "each component between -100 and 100; rotations in radians",
        "scale": "each component greater than .005 and at most 20",
        "targets": "only exact IDs in the original current workspace summary",
        "mesh.set": "at least one supplied attribute; geometry kind cannot be changed",
        "sceneactor.transform": "at least one supplied transform",
        "undoRedo": "single-operation batch only, and only when corresponding canUndo/canRedo is true",
        "project.create": "single-operation batch only; starterId must be advertised in current context.starters; "
                          "name must be the exact user-requested name; creates a new independent project, never overwrites a starter; "
                          "reconnect to the new active project before further edits",
    }


def native_plan_response_format() -> dict[str, Any]:
    """Constrain JSON transport, not semantic correctness or execution success."""
    vector = {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
    fields = {"id": {"type": "string"}, "name": {"type": "string"}, "starterId": {"type": "string"},
              "position": vector, "rotation": vector, "scale": vector,
              "color": {"type": "string"}, "material": {"enum": list(MATERIALS)},
              "kind": {"enum": list(MESH_KINDS)}, "prefab": {"enum": list(ACTOR_PREFABS)}}
    variants = []
    for name, (required, allowed) in _SCHEMA.items():
        properties = {"op": {"const": name}, **{key: fields[key] for key in sorted(allowed - {"op"})}}
        variants.append({"type": "object", "properties": properties, "required": sorted(required),
                         "additionalProperties": False})
    schema = {"oneOf": [
        {"type": "object", "properties": {"disposition": {"const": "apply"},
         "operations": {"type": "array", "items": {"oneOf": variants}, "minItems": 1, "maxItems": MAX_OPERATIONS}},
         "required": ["disposition", "operations"], "additionalProperties": False},
        {"type": "object", "properties": {"disposition": {"const": "clarify"},
         "operations": {"type": "array", "maxItems": 0}, "question": {"type": "string"}},
         "required": ["disposition", "operations", "question"], "additionalProperties": False},
    ]}
    return {"type": "json_object", "schema": schema}


def _name(value: Any) -> str:
    if (not isinstance(value, str) or not 1 <= len(value) <= 100 or not value.strip()
            or any(ord(char) < 32 or 0x7f <= ord(char) <= 0x9f for char in value)):
        raise ForgePlanError("FORGE_INVALID_LITERAL_NAME")
    try:
        value.encode("utf-8", "strict")
    except UnicodeError as exc:
        raise ForgePlanError("FORGE_INVALID_LITERAL_NAME") from exc
    return value  # Never normalize spelling, whitespace, case or punctuation.


def _vector(value: Any, *, scale: bool = False) -> list[int | float]:
    def finite(number):
        try:
            return type(number) in (int, float) and math.isfinite(number)
        except (OverflowError, ValueError):
            return False
    if (not isinstance(value, list) or len(value) != 3
            or any(not finite(n) for n in value)):
        raise ForgePlanError("FORGE_INVALID_NATIVE_VECTOR")
    if any(not (.005 < n <= 20) if scale else not (-100 <= n <= 100) for n in value):
        raise ForgePlanError("FORGE_NATIVE_VECTOR_OUT_OF_BOUNDS")
    return list(value)


def _summary(context) -> dict[str, Any]:
    # This validation remains mandatory even for callers supplying a custom model
    # or batch callback. A JSON-shaped object is never a native capability.
    from forge_embed import revalidate
    revalidate(context, require_snapshot=True)
    summary = context.model_context()
    if (not isinstance(summary, dict) or summary.get("projectId") != context.project_id
            or type(summary.get("epoch")) is not int or summary["epoch"] < 0
            or summary.get("workspace") not in ("scene", "model-atelier")
            or summary.get("mode") not in ("edit", "play")):
        raise ForgePlanError("FORGE_NATIVE_SUMMARY_INVALID")
    return summary


def validate_operations(context, operations: Any) -> list[dict[str, Any]]:
    """Independently validate the complete batch against server-bound snapshot.

    Called both after model decoding and by ``forge_embed.create_batch``. All
    fields are fail-closed. No plan can add APIs, target invisible IDs, change
    workspace or grant another project/account access.
    """
    summary = _summary(context)
    if summary["mode"] != "edit":
        raise ForgePlanError("FORGE_NATIVE_EDITOR_MODE_REQUIRED")
    if (not isinstance(operations, list) or not 1 <= len(operations) <= MAX_OPERATIONS
            or any(not isinstance(op, dict) for op in operations)):
        raise ForgePlanError("FORGE_INVALID_NATIVE_OPERATION_COUNT")
    workspace = summary["workspace"]
    entries = summary.get("meshes" if workspace == "model-atelier" else "actors")
    if not isinstance(entries, list) or len(entries) > 48:
        raise ForgePlanError("FORGE_NATIVE_SUMMARY_INVALID")
    ids = {item.get("id") for item in entries if isinstance(item, dict) and isinstance(item.get("id"), str)}
    canonical = []
    for proposed in operations:
        name = proposed.get("op")
        if not isinstance(name, str) or name not in _SCHEMA:
            raise ForgePlanError("FORGE_NATIVE_OPERATION_NOT_ALLOWED")
        required, allowed = _SCHEMA[name]
        if not required <= set(proposed) or not set(proposed) <= allowed:
            raise ForgePlanError("FORGE_INVALID_NATIVE_OPERATION_FIELDS")
        if name == "project.create":
            starters = summary.get("starters")
            if (len(operations) != 1 or not isinstance(starters, list) or not 1 <= len(starters) <= 16
                    or any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
                           or not re.fullmatch(r"[a-z][a-z0-9-]{0,79}", item["id"]) for item in starters)
                    or len({item["id"] for item in starters}) != len(starters)
                    or not isinstance(proposed.get("starterId"), str)
                    or proposed["starterId"] not in {item["id"] for item in starters}):
                raise ForgePlanError("FORGE_PROJECT_STARTER_UNAVAILABLE")
        if name.startswith("mesh.") and workspace != "model-atelier":
            raise ForgePlanError("FORGE_NATIVE_WORKSPACE_MISMATCH")
        if name.startswith("sceneactor.") and workspace != "scene":
            raise ForgePlanError("FORGE_NATIVE_WORKSPACE_MISMATCH")
        if name.startswith("editor."):
            flag = "canUndo" if name == "editor.undo" else "canRedo"
            if len(operations) != 1 or summary.get(flag) is not True:
                raise ForgePlanError("FORGE_NATIVE_HISTORY_UNAVAILABLE")
        if "id" in proposed and (not isinstance(proposed["id"], str) or proposed["id"] not in ids):
            raise ForgePlanError("FORGE_NATIVE_TARGET_NOT_IN_SNAPSHOT")
        if name == "mesh.set" and not (set(proposed) & _MESH_ATTRIBUTES):
            raise ForgePlanError("FORGE_NATIVE_EMPTY_CHANGE")
        if name == "sceneactor.transform" and not (set(proposed) & _VECTORS):
            raise ForgePlanError("FORGE_NATIVE_EMPTY_CHANGE")
        op = dict(proposed)
        if "kind" in op and op["kind"] not in MESH_KINDS:
            raise ForgePlanError("FORGE_NATIVE_KIND_NOT_ALLOWED")
        if "prefab" in op and op["prefab"] not in ACTOR_PREFABS:
            raise ForgePlanError("FORGE_NATIVE_PREFAB_NOT_ALLOWED")
        if "material" in op and op["material"] not in MATERIALS:
            raise ForgePlanError("FORGE_NATIVE_MATERIAL_NOT_ALLOWED")
        if "name" in op:
            op["name"] = _name(op["name"])
        if "color" in op and (not isinstance(op["color"], str) or not _COLOR.fullmatch(op["color"])):
            raise ForgePlanError("FORGE_NATIVE_COLOR_INVALID")
        for field in _VECTORS & set(op):
            op[field] = _vector(op[field], scale=field == "scale")
        canonical.append(op)
    if len(json.dumps(canonical, ensure_ascii=False, allow_nan=False).encode()) > MAX_PLAN_BYTES:
        raise ForgePlanError("FORGE_NATIVE_PLAN_TOO_LARGE")
    return canonical


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ForgePlanError("FORGE_PLAN_DUPLICATE_FIELD")
        result[key] = value
    return result


def _bad_constant(_value):
    raise ForgePlanError("FORGE_PLAN_NONFINITE_VALUE")


def decode_plan(text: Any, observation: Any) -> dict[str, Any]:
    if not isinstance(observation, dict) or observation.get("finishReason") != "stop":
        raise ForgePlanError("FORGE_PLAN_INCOMPLETE_GENERATION")
    if not isinstance(text, str) or not text or len(text.encode("utf-8")) > MAX_PLAN_BYTES:
        raise ForgePlanError("FORGE_PLAN_INVALID_LENGTH")
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_bad_constant)
    except (ValueError, RecursionError) as exc:
        raise ForgePlanError("FORGE_PLAN_INVALID_JSON") from exc
    if not isinstance(value, dict) or value.get("disposition") not in ("apply", "clarify"):
        raise ForgePlanError("FORGE_PLAN_INVALID_DISPOSITION")
    expected = {"disposition", "operations"} | ({"question"} if value["disposition"] == "clarify" else set())
    if set(value) != expected or not isinstance(value.get("operations"), list):
        raise ForgePlanError("FORGE_PLAN_INVALID_FIELDS")
    if value["disposition"] == "clarify":
        question = value.get("question")
        if (value["operations"] or not isinstance(question, str) or not question.strip()
                or len(question) > 500 or any(ord(char) < 32 for char in question)
                or re.search(r"\b(?:sfe1|sfh1|sfp1|sfr1)_|https?://|```", question)):
            raise ForgePlanError("FORGE_PLAN_INVALID_CLARIFICATION")
    return value


def _validate_requested_actions(prompt: str, operations: list[dict[str, Any]]) -> None:
    """A generated plan cannot introduce delete/history/duplicate instructions.

    This guard does not claim to prove all semantic correctness. It adds an
    independent floor for these action classes using only the original current
    human request; scene names, quoted literals and model prose cannot grant it.
    """
    command = current_command_text(prompt)
    explicit = {"mesh.remove": r"\b(?:remove|delete)\b",
                "mesh.duplicate": r"\b(?:duplicate|copy)\b",
                "editor.undo": r"\bundo\b", "editor.redo": r"\bredo\b"}
    for op in operations:
        if (op["op"] == "project.create") != requests_new_project(prompt):
            raise ForgePlanError("FORGE_UNREQUESTED_NATIVE_ACTION")
        if op["op"] == "project.create":
            literal = re.search(r'\b(?:called|named)(?:\s+exactly)?\s+(?:"([^"\n]*)"|“([^”\n]*)”|\x27([^\x27\n]*)\x27)', prompt, re.I)
            if literal and op["name"] != next(value for value in literal.groups() if value is not None):
                raise ForgePlanError("FORGE_PROJECT_LITERAL_NAME_MISMATCH")
        pattern = explicit.get(op["op"])
        if pattern and not re.search(pattern, command, re.I):
            raise ForgePlanError("FORGE_UNREQUESTED_NATIVE_ACTION")


def explicit_project_plan(prompt: str, summary: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve a complete literal command against the current native catalog.

    No fuzzy/default starter, generated name, history replay or authority comes
    from this parser. Ambiguous or incomplete wording stays with the constrained
    planner. Authorization, complete validation and host receipts remain required.
    """
    if not requests_new_project(prompt):
        return None
    actions = re.findall(r"\b(?:add|create|make|build|start|set\s+up|insert|place|move|rotate|scale|resize|rename|recolor|colour|color|change|set|select|duplicate|copy|remove|delete|undo|redo|turn)\b",
                         current_command_text(prompt), re.I)
    if len(actions) != 1:
        return None
    literal = re.search(r'\b(?:called|named)(?:\s+exactly)?\s+(?:"([^"\n]*)"|“([^”\n]*)”|\x27([^\x27\n]*)\x27)', prompt, re.I)
    starters = summary.get("starters")
    if not literal or not isinstance(starters, list) or not 1 <= len(starters) <= 16:
        return None
    if not re.fullmatch(r"[.!?]*", prompt[literal.end():].strip()):
        return None
    name = next(value for value in literal.groups() if value is not None)
    # Only the current command outside its literal project name may select a
    # starter. A project named "blank-scene" cannot select that starter itself.
    command = prompt[:literal.start()] + " LITERAL_NAME " + prompt[literal.end():]
    matches = set()
    remainder = command
    for item in starters:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            return None
        for label in (item["id"], item.get("name")):
            if not isinstance(label, str) or not label.strip():
                continue
            words = re.split(r"\s+", label.strip())
            pattern = r"(?<![\w-])" + r"\s+".join(re.escape(word) for word in words) + r"(?![\w-])"
            if re.search(pattern, command, re.I):
                matches.add(item["id"])
                remainder = re.sub(pattern, " STARTER ", remainder, flags=re.I)
    if len(matches) != 1:
        return None
    # Every remaining word must belong to the creation/selection grammar.
    # Requested contents such as "with two boxes" require a richer plan or
    # clarification, rather than silently reducing the request to a blank copy.
    if re.sub(r"\b(?:create|make|build|start|set|up|me|us|a|an|another|brand|new|blank|empty|independent|3d|scene|model|game|project|from|with|using|the|starter|called|named|exactly|literal_name)\b|[\s.!?\"'“”]", "", remainder, flags=re.I):
        return None
    return {"disposition": "apply", "operations": [{"op": "project.create", "starterId": matches.pop(), "name": name}]}


def _generate_plan(messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any]]:
    # Lazy import keeps routing/tests lightweight and uses the existing pinned
    # artifact, load function and lock. No second model/default/hardware lane.
    import qwen_coder_engine as coder
    from programming_telemetry import buffered_chat_completion
    with coder._lock:
        model = coder.load()
        actual, _, _, budget = coder._fit_messages(model, messages[0]["content"], [], messages[1]["content"], max_tokens)
        return buffered_chat_completion(_ConstrainedPlanModel(model), actual, budget, .1)


class _ConstrainedPlanModel:
    """Use the existing buffering/termination observer with native JSON grammar."""
    def __init__(self, model):
        self.model = model

    def create_chat_completion(self, **kwargs):
        return self.model.create_chat_completion(**kwargs, response_format=native_plan_response_format())


def _failure(message: str, code: str, *, partial=False) -> Iterator[dict[str, Any]]:
    yield {"type": "DELTA", "text": message}
    yield {"type": "FAILED", "phase": "FORGE_PARTIAL" if partial else "FORGE_FAILED",
           "reason": message, "code": code, "forgeStatus": "PARTIAL" if partial else "FAILED"}


def generate_events(payload: dict[str, Any], context, register_batch: Callable | None = None,
                    wait_batch: Callable | None = None, generate_plan: Callable | None = None) -> Iterator[dict[str, Any]]:
    """Generate one bounded proposal, then answer only from actual host receipts.

    ``generate_plan(messages,max_tokens)`` is an injectable trusted inference
    callback for controlled tests. It is never read from the public payload.
    ``register_batch(context,operations)`` returns a public batch ID;
    ``wait_batch(context,batchId,timeout=30)`` returns server-held receipts.
    """
    from forge_embed import create_batch, wait_batch as await_batch, revalidate
    register = register_batch or create_batch
    wait = wait_batch or await_batch
    infer = generate_plan or _generate_plan
    try:
        summary = _summary(context)
        prompt = payload.get("prompt") if isinstance(payload, dict) else None
        intent = classify_forge_intent(prompt, summary)
        if intent["disposition"] == "read":
            yield {"type": "DELTA", "text": inspection_text(summary)}
            yield {"type": "COMPLETED", "phase": "COMPLETE", "forgeStatus": "INSPECTED"}
            return
        if intent["disposition"] != "mutation":
            yield from _failure("Please specify the change you want made in the current §e workspace.", "FORGE_NO_CURRENT_NATIVE_EDIT")
            return
        if summary["mode"] != "edit":
            yield from _failure("Switch §e to Edit mode before requesting editor changes.", "FORGE_NATIVE_EDITOR_MODE_REQUIRED")
            return
        if requests_new_project(prompt) and not summary.get("starters"):
            yield from _failure("This §e version does not provide Chat project creation. Refresh the editor after the update, then retry. Your current project was not changed.",
                                "FORGE_PROJECT_STARTER_UNAVAILABLE")
            return
        yield {"type": "STATUS", "phase": "FORGE_PLANNING", "reason": "Planning the requested native editor change.",
               "categories": ["FORGE", "NATIVE_EDITOR"]}
        user_data = json.dumps({"currentUserRequest": prompt, "nativeContextData": summary},
                               ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        messages = [{"role": "system", "content": native_plan_system(operation_contract())},
                    {"role": "user", "content": user_data}]
        plan = explicit_project_plan(prompt, summary)
        if plan is None:
            text, observation = infer(messages, PLAN_TOKENS)
            plan = decode_plan(text, observation)
        # An inference delay cannot turn a closed/changed editor into authority.
        revalidate(context, require_snapshot=True)
        if plan["disposition"] == "clarify":
            yield {"type": "DELTA", "text": plan["question"]}
            yield {"type": "COMPLETED", "phase": "COMPLETE", "forgeStatus": "CLARIFICATION"}
            return
        operations = validate_operations(context, plan["operations"])
        _validate_requested_actions(prompt, operations)
        batch_id = register(context, operations)
        if not isinstance(batch_id, str) or not _HEX.fullmatch(batch_id):
            raise ForgePlanError("FORGE_INVALID_BATCH_RECEIPT")
        # Only public correlations cross the ordinary Chat stream. Host tokens,
        # operation bodies, receipt nonces and account credentials never do.
        yield {"type": "FORGE_BATCH_READY", "batchId": batch_id, **context.public_binding()}
        result = wait(context, batch_id, timeout=30)
        if not isinstance(result, dict) or result.get("batchId") != batch_id:
            raise ForgePlanError("FORGE_INVALID_EXECUTION_RECEIPT")
        receipts = result.get("receipts")
        if (result.get("status") != "finished" or not isinstance(receipts, list)
                or len(receipts) != len(operations)
                or any(not isinstance(receipt, dict) or type(receipt.get("ok")) is not bool for receipt in receipts)):
            yield from _failure("§e did not confirm this edit. The editor may have closed, changed or disconnected; inspect it before retrying.",
                                "FORGE_EXECUTION_UNCONFIRMED")
            return
        succeeded = sum(receipt["ok"] for receipt in receipts)
        if type(result.get("allSucceeded")) is not bool or result["allSucceeded"] != (succeeded == len(operations)):
            yield from _failure("§e returned inconsistent execution receipts. Inspect the editor before retrying.",
                                "FORGE_EXECUTION_RECEIPTS_INCONSISTENT")
            return
        if succeeded == len(operations) and result.get("allSucceeded") is True:
            if operations[0]["op"] == "project.create":
                receipt = receipts[0]
                if (receipt.get("op") != "project.create" or receipt.get("name") != operations[0]["name"]
                        or receipt.get("starterId") != operations[0]["starterId"]
                        or not isinstance(receipt.get("projectId"), str)
                        or not _HEX.fullmatch(receipt["projectId"]) or receipt["projectId"] == context.project_id):
                    yield from _failure("§e did not confirm the new project identity. Inspect the editor before continuing.",
                                        "FORGE_PROJECT_RECEIPT_INVALID")
                    return
                yield {"type": "DELTA", "text": "§e opened " + _literal(receipt["name"]) +
                       " as a new project copied from starter " + _literal(receipt["starterId"]) +
                       ". The bundled starter is preserved. Your next message will use the new project's current context."}
                yield {"type": "COMPLETED", "phase": "COMPLETE", "forgeStatus": "APPLIED",
                       "operationCount": 1, "appliedCount": 1}
                return
            labels = list(dict.fromkeys(_LABELS[op["op"]] for op in operations))
            yield {"type": "DELTA", "text": f"§e confirmed {succeeded} native editor operation{'s' if succeeded != 1 else ''}: " + ", ".join(labels) + "."}
            yield {"type": "COMPLETED", "phase": "COMPLETE", "forgeStatus": "APPLIED",
                   "operationCount": len(operations), "appliedCount": succeeded}
        elif succeeded:
            yield from _failure(f"§e confirmed {succeeded} of {len(operations)} operations. The remaining edits were not applied. Inspect the editor before continuing; native Undo remains available.",
                                "FORGE_EXECUTION_PARTIAL", partial=True)
        else:
            yield from _failure("§e rejected the requested operations. No successful editor change was confirmed.", "FORGE_EXECUTION_REJECTED")
    except Exception as exc:
        # Never expose arbitrary exception strings, model output or private
        # context in diagnostics. Exact reasons remain bounded constant codes.
        code = exc.code if isinstance(exc, ForgePlanError) else "FORGE_REQUEST_UNAVAILABLE"
        yield from _failure("The §e edit could not be verified. Check that the Chat panel is connected to the current editor, then retry with an explicit target.", code)
