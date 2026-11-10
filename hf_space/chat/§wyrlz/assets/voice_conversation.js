/* §C voice conversation v1: browser STT/TTS, existing Station send authority. */
(() => {
  "use strict";
  const mic = document.getElementById("voiceConversationButton");
  const status = document.getElementById("voiceConversationStatus");
  const prompt = document.getElementById("prompt");
  const send = document.getElementById("sendButton");
  const normalMic = document.getElementById("micButton");
  const imageAttachment = document.getElementById("imageAttachment");
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;
  if (!mic || !status || !prompt || !send) return;

  let enabled = false;
  let phase = "off";
  let recognition = null;
  let pendingId = "";
  let heard = "";
  let emptyAttempts = 0;
  let voiceEpoch = 0;
  let restartTimer = 0;
  let speechParts = [];

  const trace = (event, data = {}) => {
    // Strictly state-only diagnostics; never record audio, transcription or reply text.
    try {
      fetch("/api/chat?__swrlz_client_debug=1", {
        method: "POST", credentials: "same-origin", cache: "no-store", keepalive: true,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          runId: "chat-live-voice-v1", url: location.pathname,
          event: { at: new Date().toISOString(), type: "chat-live-voice", message: event,
            data: { phase, ...data } }
        })
      }).catch(() => {});
    } catch (_) {}
  };

  const update = (nextPhase, label) => {
    phase = nextPhase;
    mic.setAttribute("aria-pressed", String(enabled));
    mic.setAttribute("aria-label", enabled ? "End live voice conversation" : "Start live voice conversation");
    mic.dataset.voiceState = nextPhase;
    status.textContent = label || "";
    status.hidden = !label;
    document.body.classList.toggle("voice-session-label", Boolean(label));
    trace("state", { state: nextPhase });
  };

  const setPrompt = value => {
    prompt.value = value;
    prompt.dispatchEvent(new Event("input", { bubbles: true }));
  };

  const abortRecognition = () => {
    const current = recognition;
    recognition = null;
    if (current) {
      current.onend = null;
      current.onresult = null;
      current.onerror = null;
      try { current.abort(); } catch (_) {}
    }
  };

  const stop = (notice = "") => {
    enabled = false;
    voiceEpoch++;
    clearTimeout(restartTimer);
    abortRecognition();
    pendingId = "";
    speechParts = [];
    try { synth?.cancel(); } catch (_) {}
    update("off", notice);
  };

  const fail = reason => {
    trace("failure", { reason });
    stop("Voice stopped · " + reason + ". Tap the mic to retry.");
  };

  const scheduleListen = (delay = 200) => {
    clearTimeout(restartTimer);
    restartTimer = setTimeout(() => {
      if (enabled && document.visibilityState === "visible" && phase !== "waiting" && phase !== "speaking") listen();
    }, delay);
  };

  const submitSpeech = text => {
    if (!enabled || !text.trim()) return;
    if (send.disabled) { fail("chat is busy"); return; }
    pendingId = "";
    update("waiting", "Thinking · waiting for §wyrlz…");
    setPrompt(text.trim());
    // Use the canonical composer click, never a second, shadow chat transport.
    send.click();
    trace("submitted", { chars: text.trim().length });
  };

  function listen() {
    if (!enabled || recognition || phase === "waiting" || phase === "speaking") return;
    if (!Recognition) { fail("speech recognition unavailable in this browser"); return; }
    heard = "";
    let handled = false;
    const instance = new Recognition();
    recognition = instance;
    instance.lang = navigator.language || "en-US";
    instance.continuous = false; // Android Chrome does not honor continuous=true.
    instance.interimResults = true;
    instance.maxAlternatives = 1;
    instance.onresult = event => {
      if (!enabled || recognition !== instance) return;
      let final = "", interim = "";
      for (let i = 0; i < event.results.length; i++) {
        const text = event.results[i]?.[0]?.transcript || "";
        if (event.results[i].isFinal) final += text + " ";
        else interim += text + " ";
      }
      if (final.trim()) {
        heard = final.trim();
        setPrompt(heard);
        if (!handled) {
          handled = true;
          try { instance.stop(); } catch (_) {}
        }
      } else if (interim.trim()) setPrompt(interim.trim());
    };
    instance.onerror = event => {
      if (recognition !== instance || !enabled) return;
      const code = String(event.error || "unknown");
      if (code === "no-speech" || code === "aborted") return;
      if (["not-allowed", "service-not-allowed", "audio-capture", "network", "language-not-supported"].includes(code)) {
        fail("microphone/recognition " + code);
      } else {
        trace("recognition-error", { code });
      }
    };
    instance.onend = () => {
      if (recognition !== instance) return;
      recognition = null;
      if (!enabled || phase !== "listening") return;
      const utterance = heard.trim();
      if (utterance) {
        emptyAttempts = 0;
        submitSpeech(utterance);
      } else if (++emptyAttempts < 4) {
        setPrompt("");
        update("listening", "Listening · speak now…");
        scheduleListen(350);
      } else {
        setPrompt("");
        fail("no speech detected");
      }
    };
    try {
      update("listening", "Listening · speak now…");
      instance.start();
      trace("recognition-start");
    } catch (_) {
      recognition = null;
      fail("microphone could not start");
    }
  }

  const prepareSpeech = text => String(text || "")
    .replace(/\x60{3}[\s\S]*?\x60{3}/g, " Code block omitted. ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " image ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/\x60([^\x60]+)\x60/g, "$1")
    .replace(/https?:\/\/\S+/g, " link ")
    .replace(/[#>*_~|]/g, " ")
    .replace(/\s+/g, " ").trim();

  const chunkSpeech = raw => {
    const text = prepareSpeech(raw);
    const chunks = [];
    let part = "";
    for (const word of text.split(" ")) {
      if (!word) continue;
      if (part && part.length + word.length + 1 > 170) {
        chunks.push(part);
        part = "";
      }
      part += (part ? " " : "") + word;
    }
    if (part) chunks.push(part);
    return chunks;
  };

  const speak = reply => {
    if (!enabled || phase !== "waiting") return;
    if (!synth || typeof window.SpeechSynthesisUtterance !== "function") {
      fail("speech playback unavailable"); return;
    }
    speechParts = chunkSpeech(reply);
    if (!speechParts.length) { fail("empty reply"); return; }
    abortRecognition();
    const token = ++voiceEpoch;
    update("speaking", "§wyrlz speaking · tap mic to stop");
    const voices = synth.getVoices?.() || [];
    const voice = voices.find(v => v.lang?.toLowerCase().startsWith("en") && v.default) ||
                  voices.find(v => v.lang?.toLowerCase().startsWith("en"));
    const playNext = () => {
      if (!enabled || phase !== "speaking" || token !== voiceEpoch) return;
      if (!speechParts.length) {
        update("listening", "Listening · your turn…");
        scheduleListen(200);
        return;
      }
      const speech = new SpeechSynthesisUtterance(speechParts.shift());
      speech.lang = voice?.lang || navigator.language || "en-US";
      if (voice) speech.voice = voice;
      speech.rate = 1;
      speech.onend = playNext;
      speech.onerror = event => {
        if (token === voiceEpoch) fail("playback " + String(event.error || "error"));
      };
      try { synth.speak(speech); } catch (_) { fail("audio playback failed"); }
    };
    try { synth.cancel(); } catch (_) {}
    playNext();
    trace("speaking", { chunks: speechParts.length + 1 });
  };

  mic.addEventListener("click", () => {
    if (enabled) { stop(); return; }
    if (!Recognition || !synth || typeof window.SpeechSynthesisUtterance !== "function") {
      fail("browser speech input/output not supported"); return;
    }
    if (prompt.value.trim()) {
      update("off", "Finish or clear your typed draft before voice mode."); return;
    }
    if (normalMic?.getAttribute("aria-pressed") === "true") {
      update("off", "Stop normal dictation before starting a voice conversation."); return;
    }
    if (imageAttachment && !imageAttachment.hidden) {
      update("off", "Remove the image attachment before starting voice conversation."); return;
    }
    if (send.disabled) {
      update("off", "Finish the current reply before starting voice mode."); return;
    }
    enabled = true;
    pendingId = "";
    emptyAttempts = 0;
    listen();
  });

  window.addEventListener("swrlz-voice-turn", event => {
    if (!enabled || phase !== "waiting") return;
    if (event.detail?.phase === "sent") pendingId = String(event.detail.requestId || "");
    if (event.detail?.phase === "failed" && event.detail.requestId === pendingId) fail("chat send failed");
  });

  window.addEventListener("swrlz-voice-state", event => {
    if (!enabled || phase !== "waiting" || !pendingId) return;
    const { requestId, terminalType, text } = event.detail || {};
    if (String(requestId || "") !== pendingId) return;
    const terminal = String(terminalType || "").toUpperCase();
    if (terminal === "FAILED" || terminal === "CANCELLED") {
      fail("model generation " + terminal.toLowerCase());
    } else if ((terminal === "COMPLETE" || terminal === "COMPLETED") && String(text || "").trim()) {
      speak(text);
    }
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible" && enabled) stop("Voice paused while Chat is in the background.");
  });
  window.addEventListener("pagehide", () => { if (enabled) stop(); });
  update("off", "");
})();
