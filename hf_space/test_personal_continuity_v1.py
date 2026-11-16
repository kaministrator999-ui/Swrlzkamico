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
    print("personal continuity: source boundaries, precedence, scope, bounded context PASSED")


if __name__ == "__main__": run()
