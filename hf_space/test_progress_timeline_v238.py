"""v238: timestamps and display of factual, bounded assistant activity."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import progress_timeline_v238 as progress


def test_observation_timestamps_are_not_invented():
    incoming = [
        {"phase": "QUEUED", "reason": "Accepted by Workstation", "atUnixMs": 1000},
        {"phase": "GITHUB_PERMISSION_CHECK", "reason": "Verifying access"},
        {"phase": "GITHUB_TOOL_COMPLETE", "reason": "Verified read"},
    ]
    progress.mark_new(incoming, 1, at_unix_ms=2500)
    assert incoming[0]["atUnixMs"] == 1000
    assert incoming[1]["atUnixMs"] == 2500
    assert incoming[2]["atUnixMs"] == 2500
    progress.mark_new(incoming, 1, at_unix_ms=9900)
    assert incoming[1]["atUnixMs"] == 2500
    result = progress.project(incoming, accepted_at=1000, request_id="request-42")
    assert result["schema"] == "swrlz-chat-activity-timeline-v1"
    assert result["acceptedAtUnixMs"] == 1000
    assert len(result["events"]) == 3
    assert result["events"][2]["atUnixMs"] == 2500
    assert result["events"][1]["phase"] == "GITHUB_PERMISSION_CHECK"
    assert result["requestId"] == "request-42"
    unstamped = progress.project([{"phase": "PAGE_FETCH_STARTED"}])
    assert unstamped["events"][0]["atUnixMs"] is None


def test_redaction_and_bounded_log():
    rows = [{"phase": "QUEUED", "reason": "Begin", "atUnixMs": 1000}]
    for i in range(98):
        rows.append({"phase": "GITHUB_TOOL_STARTED" if i % 2 else "GITHUB_TOOL_COMPLETE",
                     "reason": "Read file " + str(i),
                     "atUnixMs": 1100 + i * 8})
    rows += [
        {"phase": "GITHUB_SOURCE", "reason": "Bearer super-secret-value; https://example.org/a?token=x", "atUnixMs": 3000},
        {"phase": "PAGE_FETCH_STARTED", "reason": "lat 39.091232, -94.098921", "atUnixMs": 3001},
        {"phase": "GENERATION_TELEMETRY", "reason": "engine raw diagnostic", "atUnixMs": 3002},
        {"phase": "INVALID/PHASE", "reason": "not a valid event", "atUnixMs": 3003},
    ]
    data = progress.project(rows, accepted_at=1000)
    assert len(data["events"]) == 64
    assert data["omittedCount"] > 0
    assert data["events"][0]["phase"] == "QUEUED"
    assert data["events"][-1]["phase"] == "PAGE_FETCH_STARTED"
    assert "super-secret-value" not in str(data)
    assert "https://example.org" not in str(data)
    assert "39.091232" not in str(data)
    assert "GENERATION_TELEMETRY" not in str(data)


def test_dedup_and_privacy_contract():
    src = [{"phase": "QUEUED", "reason": "started", "atUnixMs": 1000},
           {"phase": "QUEUED", "reason": "started", "atUnixMs": 2000},
           {"phase": "GITHUB_TOOL_COMPLETE", "reason": "source checked", "atUnixMs": 3000}]
    result = progress.project(src)
    assert len(result["events"]) == 2
    assert result["events"][0]["atUnixMs"] == 1000
    assert "rawPrompt" not in str(result)
    assert "privateReasoning" not in str(result)


def test_station_and_chat_ui_contracts():
    station = (ROOT / "station.py").read_text(encoding="utf-8")
    html = (ROOT.parent / "chat" / "§wyrlz" / "index.html").read_text(encoding="utf-8")
    assert '"atUnixMs":item.get("atUnixMs")' in station
    assert 'progress_timeline_v238.mark_new(g["status"],prior_progress_count)' in station
    assert '"progressTrace":progress_timeline_v238.project(' in station
    assert '"progressTrace":progress_timeline_v238.project(g.get("status"),g.get("acceptedAtUnixMs"),request_id)' in station
    assert 'renderActivityTimelineV238(node,msg?.meta?.progressTrace' in html
    assert 'renderActivityTimelineV238(node,g.status||[]' in html
    assert 'atUnixMs:Number(event.atUnixMs||0)||null' in html
    assert 'aria-label","Response activity timeline"' in html
    assert "Copy activity log" in html
    assert "no private reasoning" in html
    assert "No GitHub mutation" not in str(progress.project([]))  # no false actions
    assert "pct" not in progress.project([]).keys()


if __name__ == "__main__":
    test_observation_timestamps_are_not_invented()
    test_redaction_and_bounded_log()
    test_dedup_and_privacy_contract()
    test_station_and_chat_ui_contracts()
    print("v238 timestamped activity trace contract PASS")
