"""Synthetic cross-thread adaptation test. Never includes real imported conversations."""
from personal_continuity_v1 import compose, archive_signals, signal, MAX_CONTEXT


def msg(text, at, role="user"):
    return {"role":role,"text":text,"createdAt":at, "id":str(at)}


def thread(tid, messages, created=0):
    return {"id":tid,"title":"Chat quality coding and response tests", "createdAt":created,
            "updatedAt":created, "messages":messages}


def run():
    older = msg("I prefer short answers when you respond.", 1700000000)
    newest = msg("I prefer detailed answers when you respond.", 1800000000)
    assert signal(older,"chatgpt-import","id")["slot"] == "answer_length"
    assert signal(msg("I prefer short answers.",1800000000,"assistant"),"chatgpt-import","id") is None
    assert signal(msg("My password is peach and I prefer detailed replies.",1800000000),"native-§c","id") is None
    docs = [{"continuitySignals":archive_signals([older, newest],"chatgpt-1")}]
    native = [thread("current",[msg("Current prompt",1900000000)]),
              thread("other",[msg("Please always verify GitHub source and run tests before changing code.",1850000000),
                              msg("We fixed the response selection and stopped code being output as music.",1850000001)],1850000001)]
    value = compose("Can we improve the coding and response tests?",native,docs,"current")
    assert "detailed answers" in value and "short answers" not in value, value
    assert "verify GitHub" in value, value
    assert "RELATED PRIOR NATIVE" in value, value
    assert "Current prompt" not in value
    unrelated = thread("unrelated", [msg("I visited my grandparents and planted flowers yesterday.",1850000002)],1850000002)
    assert "RELATED PRIOR NATIVE" not in compose("Improve coding response tests", [unrelated], [], "current")
    assert "EXPLICIT PAST USER" in value
    assert len(value) <= MAX_CONTEXT
    assert compose("hi",[],[]) == ""
    assert not archive_signals([msg("I prefer detailed answers",1800000000,"assistant")],"chatgpt")
    native_newer=[thread("native",[msg("I prefer very brief responses when you answer.",1900000000)],1900000000)]
    out=compose("How can I do this?",native_newer,docs)
    assert "very brief" in out and "detailed answers" not in out, out
    out=compose("Can you write a rap?",[],[{"continuitySignals":archive_signals([msg("When you write rap lyrics, I prefer verses with intricate wordplay.",1700000000)],"a")}])
    assert "intricate wordplay" in out,out
    assert compose("hi",[],[{"continuitySignals":archive_signals([msg("When you write rap lyrics, I prefer verses with intricate wordplay.",1700000000)],"a")}]) == ""
    # A preference about lyrics must never silently govern code reviews.
    scoped = [
        msg("I prefer short answers when writing rap lyrics.", 1800000100),
        msg("I prefer detailed answers when coding.", 1800000200),
    ]
    scoped_docs = [{"continuitySignals":archive_signals(scoped, "scoped-import")}]
    creative = compose("Write a rap song with verses", [], scoped_docs)
    coding = compose("Can you review this code?", [], scoped_docs)
    assert "short answers" in creative and "detailed answers" not in creative, creative
    assert "detailed answers" in coding and "short answers" not in coding, coding
    # Same slot in different scopes must survive in archive, unlike v1.
    assert len(scoped_docs[0]["continuitySignals"]) == 2
    # A one-off instruction is not a durable preference.
    assert signal(msg("Just this time, give me a short answer.", 1900000200), "native-§c", "a") is None
    general_docs = [{"continuitySignals":archive_signals(
        [msg("I prefer detailed answers when you respond.", 1800000200)], "g")}]
    assert "detailed answers" not in compose("Give me a short answer today for this one.", [], general_docs)
    assert "detailed answers" not in compose("I prefer brief replies for this response.", [], general_docs)
    assert "detailed answers" in compose("Explain the implications of this proposal.", [], general_docs)
    # Explicit withdrawals in later native history suppress older imports.
    withdrawn = [thread("later",[msg("Forget my preference for detailed answers.",1900000300)],1900000300)]
    assert "detailed answers" not in compose("Explain all of this.", withdrawn, general_docs)
    # No personal secrets, contact details, child-specific or quoted third-party
    # material in an unsolicited historical continuity hint.
    assert signal(msg("I prefer fast answers. My email is user@example.org.",1800000000),"native-§c","a") is None
    assert signal(msg("I prefer detailed answers when asking about my child.",1800000000),"native-§c","a") is None
    assert signal(msg("The assistant said I prefer detailed answers.",1800000000),"native-§c","a") is None
    assert "grandparents" not in compose("Improve our code tests",[
        thread("sensitive",[msg("My child visited grandparents and improved code tests.",1800000000)],1800000000)],[])
    # The most recent huge thread should not exhaust the cross-thread scan.
    many = [thread("huge",[msg("Ordinary unrelated text.",1799999999+i) for i in range(1600)],1800000100),
            thread("older",[msg("Please always verify source and GitHub tests before committing code.",1790000000)],1790000000)]
    fair = compose("Improve GitHub source tests", many, [])
    assert "verify source" in fair, fair
    assert len(fair) <= MAX_CONTEXT
    # A generic greeting should not incur an archive-wide prompt injection.
    assert compose("hi", many, scoped_docs) == ""

    print("personal continuity: source boundaries, precedence, scope, bounded context PASSED")


if __name__ == "__main__": run()
