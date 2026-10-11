"""Synthetic/no-private-data tests for authenticated ChatGPT archive import."""
import io
import json
import re
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.resolve()))
(Path(__file__).parent / "chat/§wyrlz/assets").mkdir(parents=True, exist_ok=True)
import github_connection as gh
import chatgpt_archive as archive
import chatgpt_upload_session as upload_session
import chatgpt_import_job as import_job
import station

ALICE = "google:alice123456789"
BOB = "google:bob987654321"


def make_redis():
    values, indexes = {}, {}
    def command(_cfg, method, *args):
        if method == "GET":
            return values.get(args[0])
        if method == "SET":
            key, value, *options = args
            if "NX" in options and key in values:
                return None
            values[key] = value
            return "OK"
        if method == "EVAL" and args[0] == import_job._UNLOCK:
            script, count, key, token = args
            assert count == "1"
            if values.get(key) == token:
                del values[key]
                return 1
            return 0
        if method == "EVAL":
            script, count, key, expected, new_json = args
            assert script == archive._CAS and count == "1"
            old = values.get(key)
            actual = json.loads(old)["revision"] if old is not None else 0
            if actual != int(expected):
                return 0
            values[key] = new_json
            return 1
        if method == "ZADD":
            key, score, ident = args
            group = indexes.setdefault(key, {})
            was_new = ident not in group
            group[ident] = float(score)
            return int(was_new)
        if method == "DEL":
            deleted = 0
            for key in args:
                if key in values:
                    del values[key]
                    deleted += 1
            return deleted
        if method == "ZREM":
            key, *ids = args
            group = indexes.setdefault(key, {})
            removed = 0
            for ident in ids:
                if ident in group:
                    del group[ident]
                    removed += 1
            return removed
        if method == "ZCARD":
            return len(indexes.get(args[0], {}))
        if method == "ZREVRANGE":
            key, start, end = args
            items = sorted(indexes.get(key, {}), key=lambda s: (-indexes[key][s], s))
            return items[int(start):int(end)+1]
        raise AssertionError("unexpected Redis verb: "+method)
    return values, indexes, command


def make_thread(cid="test-thread-0001", count=2, updated=1000, title="Synthetic title"):
    mapping = {"root": {"id": "root", "parent": None, "message": None}}
    last = "root"
    for i in range(count):
        mid = "test-message-%04d" % i
        mapping[mid] = {
            "id": mid, "parent": last,
            "message": {"id": mid, "author": {"role": "user" if i % 2 == 0 else "assistant"},
                        "create_time": 100+i, "content": {"content_type": "text",
                        "parts": ["Fixture text only "+str(i)]}}}
        last = mid
    return {"id": cid, "conversation_id": cid, "title": title,
            "create_time": 100, "update_time": updated,
            "current_node": last, "mapping": mapping}


def make_zip(threads, filename="conversations-000.json"):
    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(filename, json.dumps(threads))
    return raw.getvalue()


def run():
    values, indexes, fake = make_redis()
    config = {"fernet": Fernet.generate_key().decode(), "redis": "https://redis.test",
              "redis_token": "test-secret", "client": "", "secret": "", "callback": ""}
    with mock.patch.object(gh, "_settings", return_value=config), mock.patch.object(gh, "_redis", side_effect=fake):
        initial = archive.normalize(make_thread())
        assert len(initial["messages"]) == 2
        a = archive.upsert(ALICE, initial)
        assert a == {"created": True, "updated": False, "skipped": False, "addedMessages": 2}
        assert archive.upsert(ALICE, initial)["skipped"]
        revised = archive.normalize(make_thread(count=3, updated=2000, title="Updated title"))
        changed = archive.upsert(ALICE, revised)
        assert changed["updated"] and changed["addedMessages"] == 1
        assert len(archive.read_archive(ALICE, revised["id"])["messages"]) == 3
        assert archive.read_archive(ALICE, revised["id"])["title"] == "Updated title"
        older = archive.normalize(make_thread(updated=500, title="Outdated title"))
        assert archive.upsert(ALICE, older)["skipped"]
        assert archive.read_archive(ALICE, revised["id"])["title"] == "Updated title"
        assert len(archive.read_archive(ALICE, revised["id"])["messages"]) == 3
        assert archive.list_archive(ALICE)["total"] == 1
        assert archive.list_archive(BOB)["total"] == 0
        try:
            archive.read_archive(BOB, revised["id"])
            raise AssertionError("Cross-account imported thread unexpectedly visible")
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 404
        assert "Fixture text only" not in str(values) and "test-secret" not in str(values)
        # Archive deletion never changes another user's account.
        archive.upsert(BOB, initial)
        assert archive.delete_archive(ALICE, initial["id"]) == {"deleted": 1}
        assert archive.list_archive(ALICE)["total"] == 0
        assert archive.list_archive(BOB)["total"] == 1
        assert archive.delete_all_archive(BOB) == {"deleted": 1}
        assert archive.list_archive(BOB)["total"] == 0
        # Regenerated branches do not blindly duplicate messages on losing paths.
        branch = make_thread(count=3)
        branch["mapping"]["alternative-message-9999"] = {
            "id": "alternative-message-9999", "parent": "test-message-0001",
            "message": {"id": "alternative-message-9999", "author": {"role": "assistant"},
                        "create_time": 200, "content": {"content_type": "text", "parts": ["Alternate"]}}}
        assert len(archive.normalize(branch)["messages"]) == 3
        assert not archive.normalize(make_thread(count=0))["messages"]
        # Genuine archive subsets can contain empty/non-text conversations; report skip.
        with tempfile.NamedTemporaryFile(suffix=".zip") as z:
            z.write(make_zip([make_thread("batch-item-0001", 2),
                              make_thread("batch-item-0002", 0)]))
            z.flush()
            result = list(archive.import_archive(z.name, ALICE))[-1]
            assert result["type"] == "COMPLETE"
            assert result["created"] == 1 and result["unsupported"] == 1
            assert result["addedMessages"] == 2
            again = list(archive.import_archive(z.name, ALICE))[-1]
            assert again["created"] == 0 and again["skipped"] == 1
        with tempfile.NamedTemporaryFile(suffix=".zip") as z:
            z.write(make_zip([make_thread()], filename="../../conversations-000.json"))
            z.flush()
            try:
                list(archive.import_archive(z.name, ALICE))
                raise AssertionError("ZIP traversal should not have a recognized entry")
            except Exception as exc:
                assert getattr(exc, "status_code", None) == 400
        with tempfile.NamedTemporaryFile(suffix=".zip") as z:
            z.write(b"not zip")
            z.flush()
            try:
                list(archive.import_archive(z.name, ALICE))
                raise AssertionError("Invalid ZIP should reject")
            except Exception as exc:
                assert getattr(exc, "status_code", None) == 400
        assert re.fullmatch(archive.ENTRY, "conversations-024.json")
        assert re.fullmatch(archive.ENTRY, "conversations.json")
        assert not re.fullmatch(archive.ENTRY, "../conversations.json")
        # Endpoints deny anonymous caller before they read upload bytes.
        with mock.patch.object(station, "_account_session", return_value=(None, None)):
            client = TestClient(station.app)
            response = client.post("/api/chatgpt_archive/import", content=make_zip([make_thread()]),
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1", "Content-Type": "application/zip"})
            assert response.status_code == 401
            assert client.get("/api/chatgpt_archive/list").status_code == 401
        # Server-verification succeeds for real owner; no body-based owner override.
        with mock.patch.object(station, "_account_session", return_value=("cookie", {"id": ALICE})):
            client = TestClient(station.app)
            body = make_zip([make_thread("test-thread-0003")])
            bad = client.post("/api/chatgpt_archive/import", content=body,
                headers={"Origin": "https://evil.invalid", "X-Swrlz-Import": "1", "Content-Type": "application/zip"})
            assert bad.status_code == 403
            response = client.post("/api/chatgpt_archive/import", content=body,
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1", "Content-Type": "application/zip"})
            assert response.status_code == 200, response.text
            events = [json.loads(x) for x in response.text.splitlines()]
            assert events[-1]["type"] == "COMPLETE"
            assert events[-1]["created"] == 1
            assert client.get("/api/chatgpt_archive/list").json()["total"] == 2
            assert client.delete("/api/chatgpt_archive",
                headers={"Origin": "https://evil.invalid", "X-Swrlz-Import": "1"}).status_code == 403
            good_delete = client.delete("/api/chatgpt_archive",
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"})
            assert good_delete.status_code == 200 and good_delete.json()["deleted"] == 2
            assert client.get("/api/chatgpt_archive/list").json()["total"] == 0
            # Large-file-safe protocol exercises INIT → offset-locked CHUNKS → COMPLETE.
            zipped = make_zip([make_thread("test-thread-0004", 4)])
            start = client.post("/api/chatgpt_archive/init",
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"},
                json={"size": len(zipped)})
            assert start.status_code == 200, start.text
            transfer = start.json()
            token = transfer["uploadId"]
            assert transfer["chunkSize"] == 2*1024*1024
            wrong = client.post("/api/chatgpt_archive/chunk/" + token + "?offset=1",
                content=zipped[:16], headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"})
            assert wrong.status_code == 409
            split = len(zipped)//2
            assert client.get("/api/chatgpt_archive/upload/" + token).json()["received"] == 0
            for start_offset, chunk in ((0,zipped[:split]),(split,zipped[split:])):
                sent = client.post("/api/chatgpt_archive/chunk/" + token + "?offset=" + str(start_offset),
                    content=chunk, headers={"Origin": "http://testserver",
                                            "X-Swrlz-Import": "1"})
                assert sent.status_code == 200, sent.text
            # Interrupted network acknowledgements must not append duplicate bytes.
            duplicate = client.post("/api/chatgpt_archive/chunk/" + token + "?offset=0",
                content=zipped[:split], headers={"Origin": "http://testserver",
                                                  "X-Swrlz-Import": "1"})
            assert duplicate.status_code == 200
            assert duplicate.json()["received"] == len(zipped)
            with mock.patch.object(station, "_account_session", return_value=("other", {"id": BOB})):
                assert client.get("/api/chatgpt_archive/upload/" + token).status_code == 404
                assert client.get("/api/chatgpt_archive/status").json()["storedTotal"] == 0

            completed = client.post("/api/chatgpt_archive/complete/" + token,
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"})
            assert completed.status_code == 202
            assert completed.json()["state"] == "running"
            # HTTP response is already closed: import continues in its own thread.
            for attempt in range(150):
                observed = client.get("/api/chatgpt_archive/status").json()
                if observed["state"] != "running":
                    break
                time.sleep(.02)
            assert observed["state"] == "complete", observed
            assert observed["created"] == 1 and observed["addedMessages"] == 4
            assert observed["storedTotal"] == 1
            assert archive.list_archive(ALICE)["total"] == 1
            # Same conversation from an older ZIP: no duplicate.
            old = archive.normalize(make_thread("test-thread-0004", 2, 500))
            assert archive.upsert(ALICE, old)["skipped"]
            assert len(archive.read_archive(ALICE, old["id"])["messages"]) == 4
            # A different user cannot finish someone else's upload token.
            transfer2 = client.post("/api/chatgpt_archive/init",
                headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"},
                json={"size": len(zipped)}).json()
            with mock.patch.object(station, "_account_session", return_value=("other", {"id": BOB})):
                denied = client.post("/api/chatgpt_archive/chunk/" + transfer2["uploadId"] + "?offset=0",
                    content=zipped, headers={"Origin": "http://testserver", "X-Swrlz-Import": "1"})
                assert denied.status_code == 404
            # Cleanup of test session only.
            upload_session.begin(ALICE, 12)
        html = Path("chat/§wyrlz/assets/chatgpt-archive-import-v1.js").read_text(encoding="utf-8")
        source = Path("hf_space/station.py").read_text(encoding="utf-8")
        prepare = Path("scripts/prepare_hf_space.py").read_text(encoding="utf-8")
        assert "chatgpt-archive-import-v1.js" in source and "chatgpt-archive-import-v1.js" in prepare
        for marker in ("ChatGPT imports", "/api/chatgpt_archive/status", "/api/chatgpt_archive/upload/", "/api/chatgpt_archive/init",
                       "/api/chatgpt_archive/chunk/", "/api/chatgpt_archive/complete/",
                       "X-Swrlz-Import", "unsupported", "addedMessages"):
            assert marker in html, marker
        assert "SWRLZ_GITHUB_ENCRYPTION_KEY" not in html
    print("ChatGPT import v203: detached owner-scoped jobs, persisted progress, resume and archive integrity PASS")


if __name__ == "__main__":
    run()
