"""Check staged creative planning against pinned §C source snapshots."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch


BRIEF = (
    "Using the reference image I've uploaded, create this little dragon as a fully editable 3D model in our Model Atelier. "
    "Study the different views so you can understand its proportions, anatomy, colors, wings, horns, scales, crystals, tail, and other features. "
    "Build it as closely to the reference as you reasonably can. You choose how to construct it using the modeling tools available to you. "
    "Check your work as you go, fix mistakes you notice, and keep improving it until you have a recognizable, detailed character."
)
GENERIC_BRIEF = (
    "From the attached sketch, build an editable desk lamp in Model Atelier. "
    "You can decide how to construct it and work in stages."
)
STAGE = "one coherent editable stage"
OPTIONAL_GEOMETRY = "without asking for optional geometry"
CONTRACT_MARKER = "Operation contract: "
SUMMARY = {"workspace": "model-atelier", "mode": "edit", "selectedId": None}
CONTRACT = {
    "version": "swrlz-forge-native-v2",
    "maximumOperations": 64,
    "operations": {"mesh.add": {"required": ["op", "kind"]}},
}


def load_module(root: Path, name: str) -> ModuleType:
    source = root / f"{name}.py"
    loaded = ModuleType(name)
    exec(compile(source.read_bytes(), str(source), "exec"), vars(loaded))
    return loaded


def planner_prompt(brain, lessons, request):
    with patch.dict(sys.modules, {"forge_modeling_lessons": lessons}):
        return brain.native_plan_system(CONTRACT, prompt=request, summary=SUMMARY)


def parsed_contract(prompt):
    _, marker, tail = prompt.partition(CONTRACT_MARKER)
    assert marker, "Native planner must still receive its versioned operation contract."
    return json.JSONDecoder().raw_decode(tail)[0]


def function_ast(root, module, function):
    source = ast.parse((root / f"{module}.py").read_bytes())
    definition = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == function)
    return ast.dump(definition)


def check_policy(before, after):
    old_brain = load_module(before, "brain_forge")
    new_brain = load_module(after, "brain_forge")
    old_lessons = load_module(before, "forge_modeling_lessons")
    new_lessons = load_module(after, "forge_modeling_lessons")

    for request in (BRIEF, GENERIC_BRIEF):
        previous = planner_prompt(old_brain, old_lessons, request)
        current = planner_prompt(new_brain, new_lessons, request)
        assert STAGE not in previous and OPTIONAL_GEOMETRY not in previous
        assert STAGE in current and OPTIONAL_GEOMETRY in current
        assert parsed_contract(previous) == parsed_contract(current) == CONTRACT
        assert "Preserve its exact requested names/text, targets and negative constraints." in current
        assert "Preserve all exact user constraints." in current
        assert "UV editing, boolean operations and arbitrary asset import remain unsupported." in current

    clarification = planner_prompt(new_brain, new_lessons, "Move the existing mesh in Model Atelier.")
    assert "If an existing target is ambiguous, unavailable, or outside the active workspace" in clarification
    assert "a required input is missing" in clarification
    assert "human explicitly requires an unsupported operation, return clarify with no operations" in clarification
    assert "A how-to/explanation/hypothetical request must never produce operations." in clarification

    old_lesson = old_lessons.select_modeling_lesson(GENERIC_BRIEF, SUMMARY, role="planner")
    new_lesson = new_lessons.select_modeling_lesson(GENERIC_BRIEF, SUMMARY, role="planner")
    assert "Plan a proportionate editable stage" not in old_lesson
    assert "Plan a proportionate editable stage" in new_lesson
    assert "Explicitly required unsupported operations must return disposition=clarify" in new_lesson
    assert "Other stage proposals may use only advertised operation types." in new_lesson

    for name in ("classify_forge_intent", "requests_new_project"):
        assert function_ast(before, "brain_forge", name) == function_ast(after, "brain_forge", name), name
    for request, expected in (
        (BRIEF, "mutation"),
        (GENERIC_BRIEF, "mutation"),
        ("How do I build a model?", "explain"),
        ("Inspect the current Model Atelier project and report the existing meshes.", "read"),
        ("I previously asked you to build a model.", "explain"),
        ("Build a model. Do not change the scene.", "explain"),
    ):
        old_intent = old_brain.classify_forge_intent(request, SUMMARY)
        new_intent = new_brain.classify_forge_intent(request, SUMMARY)
        assert old_intent == new_intent and new_intent["disposition"] == expected, request
    print("FORGE_CREATIVE_STAGES_PASS: staged geometry discretion, preserved gates and native contract")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    check_policy(args.before, args.after)
