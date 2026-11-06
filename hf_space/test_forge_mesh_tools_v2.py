"""Native curved-mesh, negotiated-limit and exact-review regressions.

These controlled tests do not load a model, contact Google or execute editor
code. The transport cases do use the real encrypted owner/lease/batch boundary.
"""
import copy
import json
import math
import unittest
from unittest.mock import Mock

from fastapi import HTTPException

import forge_embed as embed
import forge_chat_actions as actions
import forge_mesh_tools_v2 as mesh
from forge_design_preview_v1 import build_preview, should_preview
import test_forge_chat_actions as planner_fixture
import test_forge_embed as embed_fixture


CAPABILITY = {"schema": "swrlz-forge-mesh-tools-v2", "kinds":
              ["sphere", "box", "cone", "cylinder", "loft", "lathe"], "maxOperations": 64}
LOFT = {"op": "mesh.add", "kind": "loft", "name": "Bent staff branch",
        "path": [[0, 0, 0], [.1, .5, 0], [0, 1, .1]], "radii": [.06, .04, .025],
        "segments": 16, "position": [1, 0, 0], "scale": [1, 1, 1], "color": "#754b36"}
LATHE = {"op": "mesh.add", "kind": "lathe", "name": "Open hood shell",
         "profile": [[.5, 0], [.7, .8], [.05, 1.4]], "arcStart": .8,
         "arcLength": 4.7, "segments": 32, "scale": [1, 1, 1], "color": "#5d396f"}


class MeshPlannerTest(unittest.TestCase):
    def setUp(self):
        self.fixture = planner_fixture.PlannerTest("runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.summary = self.fixture.summary
        self.summary["meshTools"] = copy.deepcopy(CAPABILITY)
        self.context = self.fixture.context

    def invalid(self, operation, code=None):
        with self.assertRaises(actions.ForgePlanError) as raised:
            actions.validate_operations(self.context, [operation])
        if code:
            self.assertEqual(raised.exception.code, code)

    def test_capability_is_exact_copied_and_cannot_promote_an_old_host(self):
        self.assertEqual(mesh.operation_limit(self.summary), 64)
        cap = mesh.mesh_tools(self.summary)
        cap["kinds"].append("javascript")
        self.assertEqual(self.summary["meshTools"], CAPABILITY)
        malformed = [None, {}, {**CAPABILITY, "schema": "swrlz-forge-mesh-tools-v3"},
                     {**CAPABILITY, "maxOperations": True}, {**CAPABILITY, "maxOperations": 63},
                     {**CAPABILITY, "maxOperations": 65}, {**CAPABILITY, "eval": True},
                     {**CAPABILITY, "kinds": CAPABILITY["kinds"][:-1]},
                     {**CAPABILITY, "kinds": CAPABILITY["kinds"] + ["sphere"]}]
        for cap in malformed:
            with self.subTest(cap=cap):
                self.assertIsNone(mesh.mesh_tools({"meshTools": cap}))
                self.assertEqual(mesh.operation_limit({"meshTools": cap}), 16)

    def test_model_summary_sanitizes_capability_without_rewriting_host_snapshot(self):
        original = copy.deepcopy(self.summary)
        exposed = self.context.model_context()
        self.assertEqual(exposed["meshTools"], CAPABILITY)
        exposed["meshTools"]["kinds"].append("eval")
        self.assertEqual(self.summary, original)
        self.summary["meshTools"]["injected"] = "untrusted instruction"
        self.assertNotIn("meshTools", self.context.model_context())
        self.assertIn("injected", self.summary["meshTools"])
        self.assertEqual(self.context._context_hash, "context-hash")

    def test_complete_batch_limit_is_negotiated_and_never_silently_truncated(self):
        operations = [{"op": "mesh.add", "kind": "sphere", "name": f"Part {i}"} for i in range(64)]
        self.assertEqual(actions.validate_operations(self.context, operations), operations)
        with self.assertRaises(actions.ForgePlanError):
            actions.validate_operations(self.context, operations + [operations[0]])
        del self.summary["meshTools"]
        self.assertEqual(len(actions.validate_operations(self.context, operations[:16])), 16)
        with self.assertRaises(actions.ForgePlanError):
            actions.validate_operations(self.context, operations[:17])
        self.invalid(copy.deepcopy(LOFT), "FORGE_NATIVE_KIND_NOT_ALLOWED")
        self.invalid({"op": "editor.frame"}, "FORGE_MESH_TOOLS_UNAVAILABLE")

    def test_loft_accepts_exact_boundary_geometry_and_preserves_values(self):
        op = copy.deepcopy(LOFT)
        op.update(path=[[-100 + i, 100, -100] for i in range(40)],
                  radii=[.00025] + [5] * 39, segments=64)
        self.assertEqual(actions.validate_operations(self.context, [op]), [op])
        # Coincident nonadjacent points are legitimate; only adjacent points
        # would make a native path segment degenerate.
        loop = {**LOFT, "path": [[0, 0, 0], [1, 0, 0], [0, 0, 0]]}
        self.assertEqual(actions.validate_operations(self.context, [loop]), [loop])

    def test_loft_rejects_invalid_native_segments_profiles_and_wrong_fields(self):
        bad_fields = [
            {"path": [[0, 0, 0]]},
            {"path": [[i, 0, 0] for i in range(41)], "radii": [.1] * 41},
            {"path": [[0, 0], [1, 0]]}, {"path": [[0, 0, 0], [0, 0, 0]]},
            {"path": [[0, 0, 0], [1e-7, 0, 0]]},
            {"path": [[0, 0, 0], [100.0001, 0, 0]], "radii": [.1, .1]},
            {"path": [[0, 0, 0], [True, 0, 0]], "radii": [.1, .1]},
            {"path": [[0, 0, 0], [math.nan, 0, 0]], "radii": [.1, .1]},
            {"radii": [.1]}, {"radii": [0, .1, .1]}, {"radii": [.000249, .1, .1]},
            {"radii": [5.001, .1, .1]}, {"radii": [True, .1, .1]},
            {"radii": [math.inf, .1, .1]}, {"segments": 7}, {"segments": 65},
            {"segments": 8.5}, {"segments": True}, {"profile": [[0, 0], [1, 1]]},
            {"arcStart": 0}, {"arcLength": 1},
        ]
        for fields in bad_fields:
            with self.subTest(fields=fields):
                self.invalid({**copy.deepcopy(LOFT), **fields})

    def test_lathe_accepts_axis_caps_and_both_exact_arc_limits(self):
        for start, length in ((-math.tau, .05), (math.tau, math.tau)):
            op = {**LATHE, "profile": [[0, -100], [5, 0], [0, 100]],
                  "arcStart": start, "arcLength": length, "segments": 8}
            self.assertEqual(actions.validate_operations(self.context, [op]), [op])
        many = {**LATHE, "profile": [[5, i] for i in range(24)], "segments": 64}
        self.assertEqual(actions.validate_operations(self.context, [many]), [many])

    def test_lathe_rejects_degenerate_nonfinite_and_out_of_range_geometry(self):
        bad_fields = [
            {"profile": [[1, 0]]}, {"profile": [[1, i] for i in range(25)]},
            {"profile": [[1, 0, 0], [1, 1, 0]]}, {"profile": [[0, 0], [0, 1]]},
            {"profile": [[1, 0], [1, 0]]}, {"profile": [[1, 0], [1, 1e-7]]},
            {"profile": [[-0.001, 0], [1, 1]]}, {"profile": [[5.001, 0], [1, 1]]},
            {"profile": [[1, -100.001], [1, 1]]}, {"profile": [[True, 0], [1, 1]]},
            {"profile": [[1, 0], [1, math.inf]]}, {"arcStart": -math.tau - .0001},
            {"arcStart": math.tau + .0001}, {"arcStart": True}, {"arcStart": math.nan},
            {"arcLength": .04999}, {"arcLength": math.tau + .0001}, {"arcLength": True},
            {"segments": False}, {"segments": 65}, {"path": [[0, 0, 0], [1, 1, 1]]},
            {"radii": [.1, .1]},
        ]
        for fields in bad_fields:
            with self.subTest(fields=fields):
                self.invalid({**copy.deepcopy(LATHE), **fields})

    def test_primitive_and_mesh_set_cannot_smuggle_geometry(self):
        for field, value in {"path": [[0, 0, 0], [1, 1, 1]], "radii": [.1, .1],
                             "profile": [[0, 0], [1, 1]], "segments": 16,
                             "arcStart": 0, "arcLength": 1}.items():
            with self.subTest(field=field):
                self.invalid({"op": "mesh.add", "kind": "sphere", field: value},
                             "FORGE_UNSUPPORTED_SHAPE_FIELD")
                self.invalid({"op": "mesh.set", "id": "mesh-1", field: value},
                             "FORGE_INVALID_NATIVE_OPERATION_FIELDS")

    def test_frame_is_typed_workspace_scoped_and_can_finish_a_mesh_batch(self):
        for view in ("front", "back", "left", "right", "three", "hero", "top", "bottom"):
            ops = [copy.deepcopy(LOFT), {"op": "editor.frame", "view": view}]
            self.assertEqual(actions.validate_operations(self.context, ops), ops)
        self.assertEqual(actions.validate_operations(self.context, [{"op": "editor.frame"}]), [{"op": "editor.frame"}])
        for view in ("three-quarter", "perspective", 4, None, [], True):
            self.invalid({"op": "editor.frame", "view": view}, "FORGE_INVALID_FRAME_VIEW")
        self.summary["workspace"] = "scene"
        self.invalid({"op": "editor.frame"}, "FORGE_MESH_TOOLS_UNAVAILABLE")

    def test_json_grammar_uses_only_current_workspace_and_host_capabilities(self):
        def grammar():
            result = actions.native_plan_response_format(self.summary)["schema"]["oneOf"][0]
            return result["properties"]["operations"]
        current = grammar()
        variants = current["items"]["oneOf"]
        self.assertEqual(current["maxItems"], 64)
        names = {v["properties"]["op"]["const"] for v in variants}
        self.assertIn("editor.frame", names)
        self.assertNotIn("sceneactor.add", names)
        self.assertNotIn("particle.create", names)
        self.assertNotIn("project.create", names)
        self.assertNotIn("editor.redo", names)
        adds = [v for v in variants if v["properties"]["op"]["const"] == "mesh.add"]
        kinds = {v["properties"]["kind"]["const"]: v for v in adds}
        self.assertEqual(set(kinds), set(CAPABILITY["kinds"]))
        self.assertTrue({"path", "radii"} <= set(kinds["loft"]["required"]))
        self.assertIn("profile", kinds["lathe"]["required"])
        self.assertNotIn("path", kinds["sphere"]["properties"])
        del self.summary["meshTools"]
        old = grammar()
        self.assertEqual(old["maxItems"], 16)
        self.assertNotIn('"const": "loft"', json.dumps(old))
        self.assertNotIn('"const": "lathe"', json.dumps(old))
        self.assertNotIn('"const": "editor.frame"', json.dumps(old))

    def test_extended_preview_contains_all_64_steps_and_exact_geometry(self):
        operations = [{"op": "mesh.add", "kind": "sphere", "name": f"Part {i}",
                       "position": [i, 0, 0], "rotation": [0, .5, 0]} for i in range(61)]
        operations += [copy.deepcopy(LOFT), copy.deepcopy(LATHE), {"op": "editor.frame", "view": "front"}]
        _, widget = build_preview(self.summary, operations, "Design a character model", planner_fixture.PREVIEW_META)
        data = widget["data"]
        self.assertEqual(data["schema"], "swrlz-forge-design-preview-v2")
        self.assertEqual(data["operationCount"], 64)
        self.assertEqual(len(data["steps"]), 64)
        self.assertEqual([s["index"] for s in data["steps"]], list(range(1, 65)))
        self.assertEqual([s["fields"] for s in data["steps"]], [{k: v for k, v in op.items() if k != "op"} for op in operations])
        self.assertEqual(data["planDigest"], planner_fixture.PLAN_DIGEST)
        self.assertEqual(data["followup"], "Approve §e design preview " + planner_fixture.PROPOSAL)

    def test_extended_preview_cannot_be_sent_to_cached_v1_or_bypassed_by_apply(self):
        plans = [[copy.deepcopy(LOFT)], [copy.deepcopy(LATHE)], [{"op": "editor.frame"}],
                 [{"op": "mesh.add", "kind": "box"} for _ in range(17)]]
        for operations in plans:
            with self.subTest(operations=operations):
                self.assertTrue(should_preview("Apply in §e now: make the model", operations))
                _, widget = build_preview(self.summary, operations, "Build model", planner_fixture.PREVIEW_META)
                self.assertEqual(widget["data"]["schema"], "swrlz-forge-design-preview-v2")
        _, old = build_preview(self.summary, [{"op": "mesh.add", "kind": "box"}], "Build box", planner_fixture.PREVIEW_META)
        self.assertEqual(old["data"]["schema"], "swrlz-forge-design-preview-v1")

    def test_one_concrete_typed_repair_precedes_read_only_exact_preview(self):
        invalid = {**LOFT, "radii": [.1]}
        infer = Mock(side_effect=[(json.dumps({"disposition": "apply", "operations": [invalid]}), {"finishReason": "stop"}),
                                  (json.dumps({"disposition": "apply", "operations": [LOFT]}), {"finishReason": "stop"})])
        events = self.fixture.run_events(prompt="Design a bent staff model in §E", operations=[LOFT], infer=infer)
        self.assertEqual(infer.call_count, 2)
        self.assertEqual([c.args[1] for c in infer.call_args_list], [12000, 12000])
        repair = json.loads(infer.call_args.args[0][1]["content"])
        self.assertEqual(repair["typedValidationFailure"], "FORGE_INVALID_LOFT_PROFILE")
        self.assertEqual(repair["currentUserRequest"], "Design a bent staff model in §E")
        self.assertTrue(any(e.get("phase") == "FORGE_REPAIRING" for e in events))
        self.assertEqual(events[-1]["forgeStatus"], "DESIGN_PREVIEW")
        self.assertEqual(self.fixture.stage.call_args.args[1], [LOFT])
        self.assertFalse(self.fixture.register.called)
        self.assertFalse(self.fixture.wait.called)

    def test_repair_is_bounded_and_never_runs_an_invalid_plan(self):
        invalid = {"op": "mesh.add", "kind": "loft", "path": [], "radii": []}
        infer = Mock(return_value=(json.dumps({"disposition": "apply", "operations": [invalid]}), {"finishReason": "stop"}))
        events = self.fixture.run_events(prompt="Design a staff model in §E", infer=infer)
        self.assertEqual(infer.call_count, 2)
        self.assertEqual(events[-1]["type"], "FAILED")
        self.assertFalse(self.fixture.stage.called)
        self.assertFalse(self.fixture.register.called)
        self.assertFalse(self.fixture.wait.called)

    def test_incomplete_json_or_revoked_snapshot_does_not_trigger_a_repair(self):
        for text, finish in (("{", "stop"), (json.dumps({"disposition": "apply", "operations": [LOFT]}), "length")):
            with self.subTest(finish=finish):
                infer = Mock(return_value=(text, {"finishReason": finish}))
                events = self.fixture.run_events(prompt="Design a staff model in §E", infer=infer)
                self.assertEqual(infer.call_count, 1)
                self.assertEqual(events[-1]["type"], "FAILED")
                self.assertFalse(self.fixture.stage.called)
                self.assertFalse(self.fixture.register.called)
        def revoke(_messages, _budget):
            self.fixture.live = False
            return json.dumps({"disposition": "apply", "operations": [{**LOFT, "radii": []}]}), {"finishReason": "stop"}
        infer = Mock(side_effect=revoke)
        events = self.fixture.run_events(prompt="Design a staff model in §E", infer=infer)
        self.assertEqual(infer.call_count, 1)
        self.assertEqual(events[-1]["type"], "FAILED")
        self.assertFalse(self.fixture.stage.called)
        self.assertFalse(self.fixture.register.called)


class MeshBatchBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.fixture = embed_fixture.ForgeEmbedTest("runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def connected(self, capability=True):
        summary = {**copy.deepcopy(embed_fixture.CONTEXT), "workspace": "model-atelier"}
        if capability:
            summary["meshTools"] = copy.deepcopy(CAPABILITY)
        token, _ = self.fixture.pair()
        lease, _ = self.fixture.activate(token, context=summary)
        context = embed.authorize_generation(self.fixture.request(token), lease["leaseId"], embed_fixture.THREAD, "mesh-generation")
        return token, lease, context, summary

    def test_real_boundary_transports_64_exact_operations_and_remaining_budget(self):
        _, lease, context, _ = self.connected()
        operations = [{"op": "mesh.add", "kind": "box", "name": f"Part {i}"} for i in range(63)] + [LOFT]
        batch_id = embed.create_batch(context, operations)
        self.fixture.clock += 2.25
        taken = self.fixture.take(lease, batch_id)
        self.assertEqual(taken.status_code, 200, taken.text)
        body = taken.json()
        self.assertEqual(body["operations"], operations)
        self.assertEqual(body["applicationWindowMs"], 22750)
        self.assertEqual(type(body["applicationWindowMs"]), int)
        self.assertEqual(body["preconditions"]["context"]["meshTools"], CAPABILITY)
        self.assertEqual(self.fixture.take(lease, batch_id).status_code, 409)

    def test_expired_application_window_rejects_delayed_take_even_with_live_lease(self):
        _, lease, context, summary = self.connected()
        batch_id = embed.create_batch(context, [LOFT])
        self.fixture.clock += 18
        refreshed = self.fixture.post("/api/forge/embed/host/heartbeat", {
            "leaseId": lease["leaseId"], "visible": True, "hostId": embed_fixture.HOST,
            "channelId": embed_fixture.CHANNEL, "threadId": embed_fixture.THREAD,
            "projectId": embed_fixture.PROJECT, "context": summary},
            host_token=lease["hostToken"], origin=embed_fixture.PARENT)
        self.assertEqual(refreshed.status_code, 200, refreshed.text)
        self.fixture.clock += 6.01
        taken = self.fixture.take(lease, batch_id)
        self.assertEqual(taken.status_code, 409, taken.text)
        self.assertIn("FORGE_BATCH_APPLICATION_EXPIRED", taken.text)

    def test_real_boundary_rejects_unnegotiated_expanded_batch_before_storage_write(self):
        _, _, context, _ = self.connected(False)
        before = dict(self.fixture.redis.values)
        with self.assertRaises((HTTPException, actions.ForgePlanError)):
            embed.create_batch(context, [{"op": "mesh.add", "kind": "sphere"} for _ in range(17)])
        self.assertEqual(self.fixture.redis.values, before)

    def test_frozen_64_step_approval_is_exact_and_consumed_once(self):
        token, lease, context, _ = self.connected()
        operations = [{"op": "mesh.add", "kind": "sphere", "name": f"Part {i}"} for i in range(62)] + [copy.deepcopy(LOFT), copy.deepcopy(LATHE)]
        proposal = embed.create_design_proposal(context, operations)
        operations[-1]["profile"][0][0] = .4
        # The encrypted record owns a deep copy of every geometry number.
        frozen, _ = embed._read("design", proposal["proposalId"])
        self.assertEqual(frozen["operations"][-1]["profile"][0][0], .5)
        next_context = embed.authorize_generation(self.fixture.request(token), lease["leaseId"], embed_fixture.THREAD, "approve-mesh-generation")
        batch_id, exact, digest = embed.claim_design_proposal(next_context, proposal["proposalId"])
        self.assertEqual(len(exact), 64)
        self.assertEqual(exact[-1]["profile"][0][0], .5)
        self.assertEqual(digest, proposal["planDigest"])
        taken = self.fixture.take(lease, batch_id)
        self.assertEqual(taken.status_code, 200, taken.text)
        self.assertEqual(taken.json()["operations"], exact)
        with self.assertRaises(HTTPException):
            embed.claim_design_proposal(next_context, proposal["proposalId"])


if __name__ == "__main__":
    unittest.main()
