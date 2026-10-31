"""Small, isolated §C conversational evaluation pilot.

Smoke mode validates the browser-context harness and intent-gate fixtures.
Live mode uses TWO separate, dedicated test-account sessions provided as secrets.
No credentials, account profiles, or full model responses are written to artifacts.
"""
from __future__ import annotations

import argparse
import ast
import asyncio
import json
import os
import re
import statistics
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

BASE = os.getenv("SWRLZ_EVAL_BASE", "https://kamiloki-swyrlz.hf.space").rstrip("/")
MODEL_ID = os.getenv("SWRLZ_EVAL_MODEL", "700m")
OUTPUT = Path("reports/chat-eval-pilot")
LIMIT_SECONDS = 150
SCENARIOS = (
    {
        "id": "python-repair",
        "user": "A",
        "prompt": (
            "A Python function named add(a, b) currently subtracts b from a. "
            "I want this EXISTING function repaired to add the two numbers. "
            "Before writing any code, briefly explain what I want you to do."
        ),
        "required": {
            "python": r"\bpython\b",
            "function": r"\badd\b",
            "repair": r"\b(fix|repair|correct|change|replace|modify)\b",
            "addition": r"\b(add|sum|addition|plus)\b",
        },
        "followup": "Now provide the corrected Python add(a, b) function, runnable, without extra dependencies.",
        "objective": "python_ast",
    },
    {
        "id": "modeler-without-game",
        "user": "B",
        "prompt": (
            "I want a 3D cube model made in the §E Modeler, without opening or creating "
            "any game project. First restate my goal and the constraint. "
            "Do not take actions in the editor yet."
        ),
        "required": {
            "modeling": r"\b(model|modeler|modeling)\b",
            "cube": r"\bcube\b",
            "game_project": r"\bgame\s+project\b",
            "avoid_project": r"\b(without|no|not|avoid|independent|separate|don't|do not)\b",
        },
        "followup": (
            "Without actually changing files, outline concrete §E Modeler operations "
            "to create and save the cube as a model independently of any game project."
        ),
        "objective": "modeler_plan_only",
    },
)


def redact_excerpt(raw: str) -> str:
    """Retain a reviewable excerpt, never an account profile or raw transcript."""
    text = str(raw or "")[:1100]
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email]", text)
    text = re.sub(r"(?i)\b(bearer|token|secret|password|api[_ -]?key)\s*[:=]\s*[^\s,;]+", r"\1=[redacted]", text)
    return text[:750]


def intent_gate(case: dict, response: str) -> dict:
    """Conservative evidence checks, NOT a claim of semantic certainty."""
    response = str(response or "")
    if case["id"] == "modeler-without-game" and re.search(
        r"\b(?:I|we)\s+(?:will|'ll)\s+(?:start|create|open|load)\s+(?:a |the )?game\s+project\b",
        response, re.I,
    ):
        return {"status": "IMPROVE_INTENT", "reason": "Explicitly proposes the forbidden game project."}
    missing = [name for name, pattern in case["required"].items() if not re.search(pattern, response, re.I)]
    if missing:
        return {
            "status": "IMPROVE_INTENT",
            "reason": "Intent evidence missing; needs human review, not a proven misunderstanding.",
            "missing": missing,
        }
    return {"status": "PASS", "reason": "Required intent evidence present; not independently proven understanding."}


def objective_gate(case: dict, response: str) -> dict:
    if case["objective"] == "python_ast":
        fenced = re.search(r"“?"+r"\x60{3}(?:python)?\s*\n([\s\S]*?)\x60{3}", response, re.I)
        code = fenced.group(1).strip() if fenced else response.strip()
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"status": "REVIEW_EXECUTION", "reason": "Code could not be parsed as Python."}
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != "add":
                continue
            if [a.arg for a in node.args.args] != ["a", "b"]:
                continue
            for item in ast.walk(node):
                if (isinstance(item, ast.Return) and isinstance(item.value, ast.BinOp)
                    and isinstance(item.value.op, ast.Add)
                    and isinstance(item.value.left, ast.Name) and item.value.left.id == "a"
                    and isinstance(item.value.right, ast.Name) and item.value.right.id == "b"):
                    return {"status": "PASS", "reason": "Expected addition operation found in parsed add(a, b)."}
        return {"status": "REVIEW_EXECUTION", "reason": "Expected add(a, b) implementation not statically verified."}
    missing = []
    for name, pattern in (
        ("geometry_operation", r"\b(mesh|geometry|primitive|vertex|vertices|face|box)\b"),
        ("model_storage", r"\b(save|export|store|persist)\b"),
    ):
        if not re.search(pattern, response, re.I):
            missing.append(name)
    return {
        "status": "PLAN_EVIDENCE_ONLY" if not missing else "REVIEW_EXECUTION",
        "reason": "Chat plan only; no §E host actions executed." if not missing else "Modeler plan evidence missing.",
        "missing": missing,
    }


async def send_and_receive(context, thread_id: str, prompt: str) -> dict:
    rid = "eval-" + uuid.uuid4().hex[:16]
    assistant_id = "a-" + uuid.uuid4().hex[:16]
    payload = {
        "modelId": MODEL_ID, "threadId": thread_id, "requestId": rid,
        "messageId": "u-" + uuid.uuid4().hex[:16],
        "assistantMessageId": assistant_id, "prompt": prompt,
        "profile": "", "userProfile": "", "timeZone": "America/Chicago",
    }
    started = time.perf_counter()
    ack = await context.request.post(
        BASE + "/api/lalm_station/send", data=json.dumps(payload),
        headers={"Content-Type": "application/json"}, timeout=30000,
    )
    ack_ms = round((time.perf_counter() - started) * 1000)
    if ack.status != 202:
        raise RuntimeError("chat admission failed (HTTP " + str(ack.status) + ")")
    acknowledged = await ack.json()
    if not acknowledged.get("accepted") or acknowledged.get("requestId") != rid:
        raise RuntimeError("chat admission did not confirm this request")

    deadline = time.monotonic() + LIMIT_SECONDS
    while time.monotonic() < deadline:
        await asyncio.sleep(2)
        snapshot_response = await context.request.get(BASE + "/api/lalm_station/sync", timeout=30000)
        if snapshot_response.status != 200:
            raise RuntimeError("chat sync failed (HTTP " + str(snapshot_response.status) + ")")
        snapshot = await snapshot_response.json()
        for thread in snapshot.get("threads", []):
            if thread.get("id") != thread_id:
                continue
            for message in reversed(thread.get("messages") or []):
                meta = message.get("meta") or {}
                if (message.get("role") == "assistant"
                    and (meta.get("requestId") == rid or message.get("id") == assistant_id)
                    and message.get("text") and message.get("state") != "streaming"):
                    return {
                        "text": str(message["text"]),
                        "latency_ms": round((time.perf_counter() - started) * 1000),
                        "ack_ms": ack_ms,
                    }
    raise TimeoutError("No committed assistant response observed within the bounded timeout.")


async def live_user(browser, case: dict, session: str) -> dict:
    context = await browser.new_context()
    thread_id = "eval-" + case["id"] + "-" + uuid.uuid4().hex[:12]
    result = {"case": case["id"], "user": case["user"], "turns": [], "status": "UNTESTED"}
    try:
        await context.add_cookies([{
            "name": "swrlz_session", "value": session, "url": BASE,
            "httpOnly": True, "secure": True, "sameSite": "Lax",
        }])
        page = await context.new_page()
        start_ui = time.perf_counter()
        page_response = await page.goto(BASE + "/", wait_until="domcontentloaded", timeout=30000)
        result["chat_load_ms"] = round((time.perf_counter() - start_ui) * 1000)
        if not page_response or page_response.status != 200:
            raise RuntimeError("chat page failed to load")
        account = await context.request.get(BASE + "/api/account/me", timeout=30000)
        if account.status != 200 or not (await account.json()).get("user", {}).get("id"):
            raise RuntimeError("dedicated evaluation session not authenticated")
        first = await send_and_receive(context, thread_id, case["prompt"])
        gate = intent_gate(case, first["text"])
        result["turns"].append({
            "step": "intent", "latency_ms": first["latency_ms"], "ack_ms": first["ack_ms"],
            "evaluation": gate, "output_excerpt": redact_excerpt(first["text"]),
        })
        if gate["status"] != "PASS":
            result["status"] = "STOPPED_FOR_INTENT_IMPROVEMENT"
            return result
        second = await send_and_receive(context, thread_id, case["followup"])
        validation = objective_gate(case, second["text"])
        result["turns"].append({
            "step": "objective", "latency_ms": second["latency_ms"], "ack_ms": second["ack_ms"],
            "evaluation": validation, "output_excerpt": redact_excerpt(second["text"]),
        })
        result["status"] = validation["status"]
    except Exception as exc:
        result["status"] = "BLOCKED"
        result["error"] = type(exc).__name__ + ": " + redact_excerpt(str(exc))
    finally:
        await context.close()
    return result


async def smoke(browser) -> dict:
    checks = []
    for case, good, bad in (
        (SCENARIOS[0], "I will repair the Python add function so it does addition instead of subtraction.", "I'll build a new game."),
        (SCENARIOS[1], "Make a cube in the Modeler without creating a game project.", "I will create a game project."),
    ):
        checks.append(intent_gate(case, good)["status"] == "PASS")
        checks.append(intent_gate(case, bad)["status"] == "IMPROVE_INTENT")
    checks.append(objective_gate(SCENARIOS[0], "def add(a, b):\n    return a + b")["status"] == "PASS")
    contexts = [await browser.new_context() for _ in range(2)]
    try:
        for i, ctx in enumerate(contexts):
            page = await ctx.new_page()
            await page.goto("data:text/html,<title>evaluation test</title>")
            await page.evaluate("(v) => localStorage.setItem('eval-profile', v)", "user-" + str(i))
        checks.append(
            (await contexts[0].pages[0].evaluate("localStorage.getItem('eval-profile')")) == "user-0"
            and (await contexts[1].pages[0].evaluate("localStorage.getItem('eval-profile')")) == "user-1"
        )
    finally:
        await asyncio.gather(*(ctx.close() for ctx in contexts))
    return {"checks_passed": sum(checks), "checks_total": len(checks), "two_browser_contexts_isolated": checks[-1]}


def write_report(report: dict) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# §C conversational evaluation pilot",
        "", "- Mode: **" + report["mode"] + "**",
        "- Model evaluated: **" + str(report["model_evaluated"]) + "**",
        "- Browser initialization: **" + str(report["browser_launch_ms"]) + " ms**",
        "- Total runner time: **" + str(report["runner_ms"]) + " ms**",
    ]
    if report["mode"] == "smoke":
        lines += [
            "- Harness checks: **" + str(report["smoke"]["checks_passed"]) + "/" + str(report["smoke"]["checks_total"]) + "**",
            "", "This run DOES NOT measure §C inference speed or intelligence. It only validates the pilot harness.",
        ]
    else:
        turns = [t["latency_ms"] for r in report["results"] for t in r.get("turns", [])]
        lines += [
            "- Committed AI responses: **" + str(len(turns)) + "**",
            "- Mean committed-response latency: **" + (str(round(statistics.mean(turns))) + " ms" if turns else "n/a") + "**",
            "",
            "| Case | Result | Intent | Turns |",
            "|---|---|---|---:|",
        ]
        for result in report["results"]:
            gate = (result.get("turns") or [{}])[0].get("evaluation", {}).get("status", "NOT_TESTED")
            lines.append("| " + result["case"] + " | " + result["status"] + " | " + gate + " | " + str(len(result.get("turns", []))) + " |")
        lines += ["", "Stopping on intent failure prevents unproductive follow-ups. Modeler case is a planning-only check, NOT an editor-action verification."]
    lines += ["", "One run establishes a baseline, not an improvement trend. Compare future live runs using the same scenarios and model revision."]
    (OUTPUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main(mode: str) -> int:
    if mode == "live":
        sessions = [os.getenv("SWRLZ_EVAL_SESSION_A", ""), os.getenv("SWRLZ_EVAL_SESSION_B", "")]
        if not all(sessions) or sessions[0] == sessions[1]:
            raise SystemExit("Live mode requires two DIFFERENT dedicated account session secrets.")
    run_start = time.perf_counter()
    async with async_playwright() as playwright:
        launched = time.perf_counter()
        browser = await playwright.chromium.launch(headless=True)
        launch_ms = round((time.perf_counter() - launched) * 1000)
        try:
            if mode == "smoke":
                test = await smoke(browser)
                report = {"mode": mode, "model_evaluated": False, "smoke": test}
                good = test["checks_passed"] == test["checks_total"]
            else:
                results = await asyncio.gather(*(
                    live_user(browser, case, session) for case, session in zip(SCENARIOS, sessions)
                ))
                report = {"mode": mode, "model_evaluated": True, "results": results}
                good = all(result["status"] not in ("BLOCKED", "UNTESTED") for result in results)
        finally:
            await browser.close()
    report.update({
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "browser_launch_ms": launch_ms,
        "runner_ms": round((time.perf_counter() - run_start) * 1000),
        "scenario_count": len(SCENARIOS),
        "users": 2,
    })
    write_report(report)
    print(json.dumps({
        "mode": mode, "model_evaluated": report["model_evaluated"],
        "scenario_count": 2, "runner_ms": report["runner_ms"],
        "results": [{"case": r["case"], "status": r["status"]} for r in report.get("results", [])],
        "smoke": report.get("smoke"),
    }, ensure_ascii=False))
    return 0 if good else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "live"), default="smoke")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.mode)))
