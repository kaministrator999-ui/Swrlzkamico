"""Exercise pinned Chat source with a controlled native authority and receipt."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from html.parser import HTMLParser
from importlib import import_module
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


REQUEST = "Make the existing stem more curved."
LEASE = "1" * 32
RESHAPE = {"op": "mesh.reshape", "id": "stem", "kind": "loft",
           "path": [[0, 0, 0], [0.4, 0.6, 0], [0.3, 1, 0]], "radii": [0.3, 0.2, 0.1], "segments": 12}
SOURCE = {"id": "stem", "name": "Green stem", "kind": "box", "position": [1, 2, 3],
          "rotation": [0.3, -0.2, 0.8], "scale": [0.5, 1.1, 0.7], "color": "#297b45", "material": "matte"}
CAP = {"schema": "swrlz-forge-mesh-shape-edit-v1", "kinds": ["sphere", "box", "cone", "cylinder", "loft"],
       "editableIds": ["stem"]}
SUMMARY = {"projectId": "fixture-project", "project": {"name": "Fixture"}, "epoch": 4, "mode": "edit",
           "workspace": "model-atelier", "meshes": [SOURCE, {**SOURCE, "id": "other", "name": "Other part"}],
           "meshShapeEdit": CAP}


def stub(name, **attrs):
    module = ModuleType(name)
    vars(module).update(attrs)
    return module


@contextmanager
def pinned_sources(root):
    dependencies = {
        "account_chat_store": stub("account_chat_store"),
        "github_connection": stub("github_connection"),
        "forge_modeling_lessons": stub("forge_modeling_lessons", select_modeling_lesson=lambda *args, **kwargs: ""),
    }
    optional = {
        "forge_workspace_insights_v1": {"build_insight": lambda *args: ("Scene inspection.", {})},
        "forge_studio_commands_v1": {"STUDIO_SCHEMA": {}, "STUDIO_LABELS": {}, "PARTICLE_PRESETS": (),
                                     "validate_studio_operation": None, "StudioCommandError": ValueError},
        "progress_timeline_v238": {"forge_failure_fields": lambda code, _: {"code": code}},
    }
    dependencies.update({name: stub(name, **attrs) for name, attrs in optional.items()
                         if not (root / f"{name}.py").exists()})
    with patch.dict(sys.modules, dependencies), patch.object(sys, "path", [str(root), *sys.path]):
        yield SimpleNamespace(**{key: import_module(name) for key, name in {
            "brain": "brain_forge", "shape": "forge_mesh_tools_v2", "actions": "forge_chat_actions",
            "preview": "forge_design_preview_v1", "embed": "forge_embed",
        }.items()})


class ControlledAuthority:
    """Replace storage and caller authentication while running the real Forge guards."""
    def __init__(self, embed, summary):
        self.embed = embed
        self.records = {}
        expires_at = embed._now() + 900
        self.session = {"key": "test-session", "user": {"id": "test-owner"},
                        "expiresAt": expires_at, "record": {"expiresAt": expires_at}}
        self.set_host(summary, LEASE)

    def set_host(self, summary, lease_id):
        stored, context_hash = self.embed._safe_json(summary)
        self.lease = {"sessionKey": self.session["key"], "owner": self.session["user"]["id"],
                      "leaseId": lease_id, "threadId": "fixture-thread", "projectId": stored["projectId"],
                      "context": stored, "contextHash": context_hash,
                      "parentOrigin": "https://example.invalid", "hostId": "fixture-host", "channelId": "fixture-channel"}
        self.records[self.embed._key("lease", lease_id)] = self.lease
        self.records[self.session["key"]] = self.session

    def read(self, key):
        record = self.records.get(key)
        return deepcopy(record), json.dumps(record, sort_keys=True) if record is not None else None

    def live_lease(self, lease_id):
        if lease_id != self.lease["leaseId"]:
            self.embed._error(409, "FORGE_LEASE_REVOKED")
        return (*self.read(self.embed._key("lease", lease_id)), *self.read(self.session["key"]))

    def transaction(self, expected, writes=(), deletes=()):
        if any(self.read(key)[1] != raw for key, raw in expected):
            return False
        for key, record, _ttl in writes:
            self.records[key] = deepcopy(record)
        for key in deletes:
            self.records.pop(key, None)
        return True

    @contextmanager
    def wiring(self):
        with patch.multiple(self.embed, _read_key=self.read, _live_lease=self.live_lease, _txn=self.transaction,
                            require_embed=lambda _request: self.session):
            yield self

    def generation(self, identity):
        return self.embed.authorize_generation(None, self.lease["leaseId"], self.lease["threadId"], identity)

    def all_records(self, kind):
        return [data for data in self.records.values() if data.get("kind") == kind]


def reject(code, call):
    try:
        call()
    except Exception as error:
        assert getattr(error, "code", getattr(error, "detail", None)) == code, error
    else:
        raise AssertionError(f"Expected rejection {code}")


def check_schema(modules):
    brain, shape, actions = modules.brain, modules.shape, modules.actions
    for prompt in (REQUEST, "Please refine the shape of the stem.", "Round the selected part.",
                   "Apply in §e now: reshape the existing stem."):
        assert brain.classify_forge_intent(prompt, SUMMARY)["reason"] == "explicit-current-mesh-reshape", prompt
    replacement = "Remove the existing mesh and make a rounded replacement."
    assert brain.classify_forge_intent(replacement, SUMMARY)["reason"] == "explicit-current-native-edit"
    for prompt in ('"Reshape the existing stem."', "Don't reshape the existing stem.", "How can I reshape the stem?",
                   "Make a rounder sphere in Model Atelier.", "Change the stem color.", replacement,
                   "Make the existing mesh rounder by removing it and adding a replacement."):
        assert not brain.requests_mesh_reshape(prompt), prompt
    assert not brain.requests_mesh_reshape("\n```text\nReshape the stem now\n```"), "Fences cannot authorize edits."
    assert shape.mesh_shape_edit(SUMMARY) == CAP
    for cap in ({**CAP, "extra": 1}, {**CAP, "kinds": ["loft"]}, {**CAP, "editableIds": ["offscreen"]},
                {**CAP, "editableIds": ["stem", "stem"]}):
        assert shape.mesh_shape_edit({**SUMMARY, "meshShapeEdit": cap}) is None
    assert shape.mesh_shape_edit({**SUMMARY, "workspace": "scene"}) is None
    contract = actions.operation_contract(SUMMARY, reshape_only=True)
    assert contract["maximumOperations"] == 1 and contract["meshShapeEdit"] == CAP
    schema = actions.native_plan_response_format(SUMMARY, reshape_only=True)["schema"]
    operations = schema["oneOf"][0]["properties"]["operations"]
    assert operations["maxItems"] == 1
    for variant in operations["items"]["oneOf"]:
        props = variant["properties"]
        assert props["op"]["const"] == "mesh.reshape" and props["id"]["enum"] == ["stem"]
        assert set(variant["required"]) == (set(RESHAPE) if props["kind"]["const"] == "loft" else {"op", "id", "kind"})
    assert "mesh.reshape" not in json.dumps(actions.native_plan_response_format(SUMMARY))
    assert "mesh.reshape" not in json.dumps(actions.native_plan_response_format({**SUMMARY, "meshShapeEdit": None}, reshape_only=True))


def check_preview_claim(modules):
    actions, embed = modules.actions, modules.embed
    with ControlledAuthority(embed, SUMMARY).wiring() as authority:
        context = authority.generation("generation-preview")
        assert context.model_context()["meshShapeEdit"] == CAP
        assert embed._safe_json(SUMMARY)[1] == context._context_hash
        assert actions.validate_operations(context, [RESHAPE]) == [RESHAPE]
        for operations, code in (
            ([{**RESHAPE, "id": "missing"}], "FORGE_NATIVE_TARGET_NOT_IN_SNAPSHOT"),
            ([{**RESHAPE, "id": "other"}], "FORGE_MESH_RESHAPE_TARGET_UNAVAILABLE"),
            ([RESHAPE, {"op": "mesh.select", "id": "stem"}], "FORGE_MESH_RESHAPE_REQUIRES_SINGLE_OPERATION"),
            ([{**RESHAPE, "kind": "lathe"}], "FORGE_NATIVE_KIND_NOT_ALLOWED"),
            ([{**RESHAPE, "kind": "box"}], "FORGE_UNSUPPORTED_SHAPE_FIELD"),
            ([{**RESHAPE, "rotation": [0, 0, 0]}], "FORGE_INVALID_NATIVE_OPERATION_FIELDS"),
            ([{k: v for k, v in RESHAPE.items() if k != "segments"}], "FORGE_INVALID_MESH_SEGMENTS"),
            ([{**RESHAPE, "radii": [0.1, 0.1]}], "FORGE_INVALID_LOFT_PROFILE"),
        ):
            reject(code, lambda: actions.validate_operations(context, operations))
        reject("FORGE_DESIGN_RESHAPE_APPROVAL_REQUIRED", lambda: embed.create_batch(context, [RESHAPE]))
        reject("FORGE_UNREQUESTED_NATIVE_ACTION", lambda: actions._validate_requested_actions("Move the stem.", [RESHAPE]))
        reject("FORGE_UNREQUESTED_NATIVE_ACTION", lambda: actions._validate_requested_actions(
            REQUEST, [{"op": "mesh.add", "kind": "sphere"}], reshape_only=True))

        def infer(messages, _budget):
            assert "Propose exactly one in-place geometry edit" in messages[0]["content"]
            return json.dumps({"disposition": "apply", "operations": [RESHAPE]}), {"finishReason": "stop"}

        events = list(actions.generate_events({"prompt": "Apply in §e now: " + REQUEST}, context, generate_plan=infer))
        assert events[-1]["forgeStatus"] == "DESIGN_PREVIEW", events
        assert not authority.all_records("batch")
        data = next(event["widget"]["data"] for event in events if event["type"] == "WIDGET")
        step = data["steps"][0]
        assert data["schema"] == "swrlz-forge-design-preview-v2"
        assert step["name"] == SOURCE["name"] and step["kind"] == "loft" and step["target"] == "stem"
        for attribute in ("position", "rotation", "scale", "color", "material"):
            assert step[attribute] == SOURCE[attribute]
        assert step["fields"] == {key: value for key, value in RESHAPE.items() if key != "op"}
        assert data["planDigest"] == embed._design_digest([RESHAPE])
        assert authority.all_records("design-proposal")[0]["operations"] == [RESHAPE]

        image_context = authority.generation("generation-image")
        image = {"observation": data["followup"]}
        def clarify(_messages, _budget):
            return json.dumps({"disposition": "clarify", "operations": [], "question": "Which edit?"}), {"finishReason": "stop"}

        list(actions.generate_events({"prompt": data["followup"], "verifiedForgeImage": image}, image_context,
                                     generate_plan=clarify))
        assert not authority.all_records("batch") and authority.all_records("design-proposal")[0]["state"] == "offered"
        authority.set_host(SUMMARY, "2" * 32)
        approval = authority.generation("generation-approve")

        def wait(_context, batch_id, timeout):
            [batch] = authority.all_records("batch")
            assert batch["leaseId"] == approval.lease_id and batch["operations"] == [RESHAPE]
            assert batch["designPlanDigest"] == data["planDigest"]
            return {"batchId": batch_id, "status": "finished", "allSucceeded": True,
                    "receipts": [{"op": "mesh.reshape", "id": "stem", "kind": "loft", "ok": True, "changed": True}]}

        approved = list(actions.generate_events({"prompt": data["followup"]}, approval, wait_batch=wait))
        assert approved[-1]["forgeStatus"] == "APPLIED" and approved[-1]["appliedCount"] == 1
        assert authority.all_records("design-proposal")[0]["state"] == "claimed"
        replay = authority.generation("generation-replay")
        reject("FORGE_DESIGN_EXPIRED_OR_USED", lambda: embed.claim_design_proposal(replay, data["proposalId"]))
        assert len(authority.all_records("batch")) == 1


def check_stale_and_fallback(modules):
    actions, embed = modules.actions, modules.embed
    with ControlledAuthority(embed, SUMMARY).wiring() as authority:
        start = authority.generation("stale-preview")
        staged = embed.create_design_proposal(start, [RESHAPE])
        authority.set_host({**SUMMARY, "epoch": 5}, "3" * 32)
        next_context = authority.generation("stale-approval")
        reject("FORGE_DESIGN_CONTEXT_MISMATCH", lambda: embed.claim_design_proposal(next_context, staged["proposalId"]))
        assert not authority.all_records("batch")

    with ControlledAuthority(embed, {**SUMMARY, "meshShapeEdit": {**CAP, "unknown": True}}).wiring() as authority:
        context = authority.generation("legacy-host")
        assert "meshShapeEdit" not in context.model_context()
        assert context._summary["meshShapeEdit"]["unknown"] is True
        events = list(actions.generate_events({"prompt": REQUEST}, context))
        assert events[-1]["code"] == "FORGE_NO_CURRENT_NATIVE_EDIT" and not authority.all_records("batch")
        reject("FORGE_MESH_RESHAPE_TARGET_UNAVAILABLE", lambda: actions.validate_operations(context, [RESHAPE]))
        replacement = [{"op": "mesh.remove", "id": "stem"}, {"op": "mesh.add", "kind": "sphere"}]
        assert actions.validate_operations(context, replacement) == replacement
        actions._validate_requested_actions("Remove the existing mesh and make a rounded replacement.", replacement)


def check_reshape_receipts(modules):
    actions, embed = modules.actions, modules.embed
    receipt = {"op": "mesh.reshape", "id": "stem", "kind": "loft", "ok": True, "changed": False}
    for native_receipt, expected in ((receipt, "NO_CHANGE"), ({**receipt, "id": "other"}, "FAILED"),
                                      ({**receipt, "kind": "box"}, "FAILED")):
        with ControlledAuthority(embed, SUMMARY).wiring() as authority:
            context = authority.generation("fixture-offer")
            staged = embed.create_design_proposal(context, [RESHAPE])
            context = authority.generation("fixture-claim")

            def wait(_context, batch_id, timeout):
                return {"batchId": batch_id, "status": "finished", "allSucceeded": True, "receipts": [native_receipt]}

            events = list(actions.generate_events({"prompt": "Approve §e design preview " + staged["proposalId"]},
                                                  context, wait_batch=wait))
            assert events[-1]["forgeStatus"] == expected, events
            if expected == "NO_CHANGE":
                assert events[-1]["appliedCount"] == 0
            else:
                assert events[-1]["code"] == "FORGE_MESH_RESHAPE_RECEIPT_INVALID"


class ScriptSource(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        self.inside = tag == "script" and not dict(attrs).get("src")

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.scripts.append(data)


def check_widget_syntax(after):
    parser = ScriptSource()
    parser.feed((after / "chat/§wyrlz/index.html").read_text(encoding="utf-8"))
    widget, = [text for text in parser.scripts if 'widget.kind==="forge-design-preview"' in text]
    assert 'step.op==="mesh.reshape"?step.rotation:' in widget
    assert 'v.op!=="mesh.reshape"||validVector(v.rotation)' in widget
    subprocess.run(["node", "--check"], input=widget, text=True, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    with pinned_sources(args.before.resolve()) as before:
        assert "mesh.reshape" not in before.actions._SCHEMA
    with pinned_sources(args.after.resolve()) as after:
        check_schema(after)
        check_preview_claim(after)
        check_stale_and_fallback(after)
        check_reshape_receipts(after)
    check_widget_syntax(args.after)
    print("FORGE_MESH_RESHAPE_PASS: eligible intent, frozen preview, live context matching, and one exact claim")
