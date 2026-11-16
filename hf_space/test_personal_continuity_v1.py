"""Synthetic cross-thread adaptation test. Never includes real imported conversations."""
from personal_continuity_v1 import compose, archive_signals, signal, MAX_CONTEXT, latest_imported_signals


def msg(text, at, role="user"):
    return {"role":role,"text":text,"createdAt":at, "id":str(at)}


def thread(tid, messages, created=0):
    return {"id":tid,"title":"Chat quality coding and response tests", "createdAt":created,
            "updatedAt":created, "messages":messages}


def run():
    older = msg("I prefer short answers when you respond.", 1700000000)
    newest = msg("I prefer detailed answers when you respond.", 1750000000)
    assert signal(older,"chatgpt-import","id")["slot"] == "answer_length"
    assert signal(msg("I prefer short answers.",1750000000,"assistant"),"chatgpt-import","id") is None
    assert signal(msg("My password is peach and I prefer detailed replies.",1750000000),"native-§c","id") is None
    docs = [{"continuitySignals":archive_signals([older, newest],"chatgpt-1")}]
    native = [thread("current",[msg("Current prompt",1780000000)]),
              thread("other",[msg("Please always verify GitHub source and run tests before changing code.",1770000000),
                              msg("We fixed the response selection and stopped code being output as music.",1770000001)],1770000001)]
    value = compose("Can we improve the coding and response tests?",native,docs,"current")
    assert "detailed answers" in value and "short answers" not in value, value
    assert "verify GitHub" in value, value
    assert "RELATED NATIVE" in value, value
    assert "Current prompt" not in value
    unrelated = thread("unrelated", [msg("I visited my grandparents and planted flowers yesterday.",1770000002)],1770000002)
    assert "RELATED NATIVE" not in compose("Improve coding response tests", [unrelated], [], "current")
    assert "PRIVATE ACCOUNT HISTORICAL USER EVIDENCE" in value
    assert len(value) <= MAX_CONTEXT
    assert compose("hi",[],[]) == ""
    assert not archive_signals([msg("I prefer detailed answers",1750000000,"assistant")],"chatgpt")
    native_newer=[thread("native",[msg("I prefer very brief responses when you answer.",1780000000)],1780000000)]
    out=compose("How can I do this?",native_newer,docs)
    assert "very brief" in out and "detailed answers" not in out, out
    out=compose("Can you write a rap?",[],[{"continuitySignals":archive_signals([msg("When you write rap lyrics, I prefer verses with intricate wordplay.",1700000000)],"a")}])
    assert "intricate wordplay" in out,out
    assert compose("hi",[],[{"continuitySignals":archive_signals([msg("When you write rap lyrics, I prefer verses with intricate wordplay.",1700000000)],"a")}]) == ""
    # Reject a forged future date instead of silently ranking it as recent.
    assert signal(msg("I prefer long answers.", 2000000000), "chatgpt-import", "a") is None
    assert "RELATED NATIVE" not in compose("Improve code and tests",[
        thread("future",[msg("We improved code and tests.",2000000000)],2000000000)],[])
    # Large imports are compressed once into one newest signal per topic.
    older_import = archive_signals([msg("I prefer short answers when you respond.",1700000000)],"old")
    newer_import = archive_signals([msg("I prefer detailed answers when you respond.",1750000000)],"new")
    large_docs = [{"continuitySignals":older_import} for _ in range(1800)]
    large_docs.append({"continuitySignals":newer_import})
    compact = latest_imported_signals(large_docs)
    assert len(compact) == 1 and "detailed answers" in compact[0]["text"],compact
    assert "short answers" not in compose("Please explain our project",[],[{"continuitySignals":compact}])
    # A preference about lyrics must never silently govern code reviews.
    scoped = [
        msg("I prefer short answers when writing rap lyrics.", 1750000100),
        msg("I prefer detailed answers when coding.", 1750000200),
    ]
    scoped_docs = [{"continuitySignals":archive_signals(scoped, "scoped-import")}]
    creative = compose("Write a rap song with verses", [], scoped_docs)
    coding = compose("Can you review this code?", [], scoped_docs)
    assert "short answers" in creative and "detailed answers" not in creative, creative
    assert "detailed answers" in coding and "short answers" not in coding, coding
    # Same slot in different scopes must survive in archive, unlike v1.
    assert len(scoped_docs[0]["continuitySignals"]) == 2
    # A one-off instruction is not a durable preference.
    assert signal(msg("Just this time, give me a short answer.", 1780000200), "native-§c", "a") is None
    general_docs = [{"continuitySignals":archive_signals(
        [msg("I prefer detailed answers when you respond.", 1750000200)], "g")}]
    assert "detailed answers" not in compose("Give me a short answer today for this one.", [], general_docs)
    assert "detailed answers" not in compose("I prefer brief replies for this response.", [], general_docs)
    assert "detailed answers" in compose("Explain the implications of this proposal.", [], general_docs)
    # Explicit withdrawals in later native history suppress older imports.
    withdrawn = [thread("later",[msg("Forget my preference for detailed answers.",1780000300)],1780000300)]
    assert "detailed answers" not in compose("Explain all of this.", withdrawn, general_docs)
    # No personal secrets, contact details, child-specific or quoted third-party
    # material in an unsolicited historical continuity hint.
    assert signal(msg("I prefer fast answers. My email is user@example.org.",1750000000),"native-§c","a") is None
    assert signal(msg("I prefer detailed answers when asking about my child.",1750000000),"native-§c","a") is None
    assert signal(msg("The assistant said I prefer detailed answers.",1750000000),"native-§c","a") is None
    assert "grandparents" not in compose("Improve our code tests",[
        thread("sensitive",[msg("My child visited grandparents and improved code tests.",1750000000)],1750000000)],[])
    # The most recent huge thread should not exhaust the cross-thread scan.
    many = [thread("huge",[msg("Ordinary unrelated text.",1760000000+i) for i in range(1600)],1750000100),
            thread("older",[msg("Please always verify source and GitHub tests before committing code.",1740000000)],1740000000)]
    fair = compose("Improve GitHub source tests", many, [])
    assert "verify source" in fair, fair
    assert len(fair) <= MAX_CONTEXT
    # A generic greeting should not incur an archive-wide prompt injection.
    assert compose("hi", many, scoped_docs) == ""

    print("personal continuity: source boundaries, precedence, scope, bounded context PASSED")


if __name__ == "__main__": run()
