/* §C voice conversation v7: Browser Turbo recognition + natural early-phrase streaming speech; retain offline modes. */
(() => {
  "use strict";
  const mic = document.getElementById("voiceConversationButton");
  const voiceProvider = document.getElementById("voiceProviderSelect");
  const status = document.getElementById("voiceConversationStatus");
  const prompt = document.getElementById("prompt");
  const send = document.getElementById("sendButton");
  const normalMic = document.getElementById("micButton");
  const imageAttachment = document.getElementById("imageAttachment");
  const BrowserRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
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
  let speechPending = "";
  let streamedReply = "";
  let generationComplete = false;
  let speakingStarted = false;
  let speechBusy = false;
  let activeSpeech = null;
  let submittedAt = 0;
  let firstDeltaAt = 0;
  // Turbo uses browser speech recognition, not the downloaded Vosk model.
  // Keep on-device Local Turbo as a separate choice for offline use.
  const turboSelected = () => voiceProvider?.value === "turbo";
  const localTurboSelected = () => voiceProvider?.value === "local-turbo";
  const localSelected = () => voiceProvider?.value === "local" || localTurboSelected();
  const fastSpeechSelected = () => turboSelected() || localTurboSelected();

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
    if (voiceProvider) voiceProvider.disabled = enabled;
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
    window.SwrlzLocalVoice?.stop(); // Keep ready WASM model between Talk activations.
    pendingId = "";
    speechParts = [];
    speechPending = "";
    streamedReply = "";
    generationComplete = false;
    speakingStarted = false;
    speechBusy = false;
    activeSpeech = null;
    submittedAt = 0;
    firstDeltaAt = 0;
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
    voiceEpoch++; // Invalidate callbacks from a previous spoken turn.
    speechParts = [];
    speechPending = "";
    streamedReply = "";
    generationComplete = false;
    speakingStarted = false;
    speechBusy = false;
    activeSpeech = null;
    try { synth?.cancel(); } catch (_) {}
    submittedAt = Date.now();
    firstDeltaAt = 0;
    update("waiting", "Thinking · waiting for §wyrlz…");
    setPrompt(text.trim());
    // Use the canonical composer click, never a second, shadow chat transport.
    send.click();
    trace("submitted", { chars: text.trim().length });
  };

  function listen() {
    if (!enabled || recognition || phase === "waiting" || phase === "speaking") return;
    const local = localSelected();
    const Recognition = local ? window.SwrlzLocalSpeechRecognition : BrowserRecognition;
    if (!Recognition) { fail(local ? "local recognition component unavailable" : "speech recognition unavailable in this browser"); return; }
    heard = "";
    let handled = false;
    const instance = new Recognition();
    if (localTurboSelected()) instance.turbo = true;
    recognition = instance;
    // The bundled offline Vosk model is en-US; Browser input may use device locale.
    instance.lang = local ? "en-US" : (navigator.language || "en-US");
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
      if (code === "local-engine") {
        fail(String(event.detail || "local recognition unavailable").slice(0,160));
      } else if (["not-allowed", "service-not-allowed", "audio-capture", "network", "language-not-supported"].includes(code)) {
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
      update("listening", local ? (localTurboSelected() ? "Local Turbo · preparing offline recognizer…" : "Local stream · loading offline recognizer…") : (turboSelected() ? "Browser Turbo · listening…" : "Listening · speak now…"));
      instance.start();
      trace("recognition-start", { engine: local ? (localTurboSelected() ? "local-vosk-turbo" : "local-vosk") : (turboSelected() ? "browser-turbo" : "browser") });
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

  const voiceChoice = () => {
    const voices = synth?.getVoices?.() || [];
    return voices.find(v => v.lang?.toLowerCase().startsWith("en") && v.default) ||
           voices.find(v => v.lang?.toLowerCase().startsWith("en"));
  };

  const resumeAfterSpeech = () => {
    // Never reopen the microphone while generation or synthesized speech is active.
    if (!enabled || !generationComplete || speechBusy || speechParts.length || speechPending.trim()) return;
    pendingId = "";
    speakingStarted = false;
    update("listening", "Listening · your turn…");
    scheduleListen(200);
  };

  const playQueuedSpeech = () => {
    if (!enabled || !["waiting", "speaking"].includes(phase) || speechBusy) return;
    if (!speechParts.length) {
      resumeAfterSpeech();
      return;
    }
    if (!synth || typeof window.SpeechSynthesisUtterance !== "function") {
      fail("speech playback unavailable"); return;
    }
    abortRecognition();
    if (!speakingStarted) {
      speakingStarted = true;
      const latencyMs = submittedAt ? Date.now() - submittedAt : 0;
      update("speaking", (fastSpeechSelected() ? "Turbo · " : "") +
        "§wyrlz speaking" + (latencyMs ? " · first audio queued " + (latencyMs / 1000).toFixed(1) + "s" : "") +
        (generationComplete ? "" : " · still generating…"));
      trace("first-audio-queued", { streamed: !generationComplete, submitToSpeechMs: latencyMs });
    }
    const token = voiceEpoch;
    const voice = voiceChoice();
    const utterance = new SpeechSynthesisUtterance(speechParts.shift());
    utterance.lang = voice?.lang || navigator.language || "en-US";
    if (voice) utterance.voice = voice;
    utterance.rate = fastSpeechSelected() ? 1.14 : 1;
    speechBusy = true;
    activeSpeech = utterance; // Keep utterance alive until Chrome announces completion.
    utterance.onend = () => {
      if (token !== voiceEpoch || !enabled) return;
      speechBusy = false;
      activeSpeech = null;
      playQueuedSpeech();
    };
    utterance.onerror = event => {
      if (token === voiceEpoch && enabled)
        fail("playback " + String(event.error || "error"));
    };
    try { synth.speak(utterance); } catch (_) { fail("audio playback failed"); }
  };

  // Browser Turbo can begin speaking before a full sentence exists. Wait for
  // a completed word/clause instead of chopping off the model's newest token.
  // Shorter utterances reduce time-to-first-audio; preserving full words and
  // punctuation keeps the synthesized voice intelligible on Android.
  const firstTurboPhraseCut = buffer => {
    const minimum = 28;
    const preferred = 52;
    const upper = 84;
    if (buffer.length < minimum) return -1;
    const pause = /[,;:—–](?:["'”’)]*)\s+/g;
    let match;
    while ((match = pause.exec(buffer))) {
      const end = match.index + match[0].length;
      if (end >= minimum && end <= upper) return end;
    }
    if (buffer.length < preferred) return -1;
    // Consume only text through a complete word; hold a potentially
    // unfinished token until the next streamed delta arrives.
    const split = buffer.lastIndexOf(" ", preferred);
    return split >= minimum ? split + 1 : -1;
  };

  const flushSpeech = final => {
    // A partial Markdown code fence must not be spoken as executable source.
    if (!final && (speechPending.match(/```/g) || []).length % 2 !== 0) return;
    while (speechPending.trim()) {
      const sentence = /[.!?](?:["'”’)]*)\s+/.exec(speechPending);
      let cut = sentence ? sentence.index + sentence[0].length : -1;
      // Only Browser Turbo gets low-latency phrase splitting. Browser and both
      // Local profiles preserve their prior sentence/fallback boundaries.
      if (!final && turboSelected()) {
        const phrase = firstTurboPhraseCut(speechPending);
        if (phrase > 0 && (cut < 0 || phrase < cut)) cut = phrase;
      }
      const earlyPhraseLimit = fastSpeechSelected() ? 95 : 170;
      if (cut < 0 && !final && speechPending.length >= earlyPhraseLimit) {
        cut = speechPending.lastIndexOf(" ", earlyPhraseLimit);
        if (cut < (fastSpeechSelected() ? 45 : 90)) break;
      }
      if (cut < 0 && !final) break;
      const portion = cut >= 0 ? speechPending.slice(0, cut) : speechPending;
      speechPending = cut >= 0 ? speechPending.slice(cut) : "";
      speechParts.push(...chunkSpeech(portion));
      if (!final && speechParts.length >= 32) break;
    }
    playQueuedSpeech();
  };

  const receiveDelta = text => {
    if (generationComplete) return;
    const fragment = String(text || "");
    if (!fragment) return;
    if (!firstDeltaAt && submittedAt) {
      firstDeltaAt = Date.now();
      const ms = firstDeltaAt - submittedAt;
      if (phase === "waiting")
        update("waiting", "First generated text " + (ms / 1000).toFixed(1) + "s after send · preparing speech…");
      trace("first-text-delta", { submitToFirstDeltaMs: ms });
    }
    streamedReply += fragment;
    speechPending += fragment;
    // Protect the browser from unbounded buffered source in voice mode.
    if (speechPending.length > 12000) {
      fail("reply too large for streaming speech"); return;
    }
    flushSpeech(false);
  };

  const finishReply = text => {
    if (!enabled || generationComplete) return;
    const committed = String(text || "");
    // Persisted Station text is authoritative. If stream deltas arrived, use
    // only its unsent suffix; never re-speak the prefix on a terminal receipt.
    if (committed && committed.startsWith(streamedReply))
      speechPending += committed.slice(streamedReply.length);
    else if (!streamedReply && committed)
      speechPending += committed;
    generationComplete = true;
    flushSpeech(true);
    if (!speechBusy && !speechParts.length)
      resumeAfterSpeech();
  };

  mic.addEventListener("click", () => {
    if (enabled) { stop(); return; }
    const local = localSelected();
    if ((local ? !window.SwrlzLocalSpeechRecognition : !BrowserRecognition) ||
        !synth || typeof window.SpeechSynthesisUtterance !== "function") {
      fail("selected speech input/output not supported"); return;
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

  voiceProvider?.addEventListener("change", () => {
    if (enabled) return;
    window.SwrlzLocalVoice?.dispose();
    update("off", turboSelected()
      ? "Browser Turbo · browser recognition, faster reply playback. May use an online speech service. Tap Talk."
      : localTurboSelected()
        ? "Offline Local Turbo · on-device Vosk with faster playback. Tap Talk."
        : voiceProvider.value === "local"
          ? "Offline Local stream · on-device Vosk. Tap Talk."
          : "Browser speech input selected · tap Talk.");
  });

  window.addEventListener("swrlz-local-voice-status", event => {
    if (enabled && phase === "listening" && localSelected())
      update("listening", String(event.detail?.label || "Local streaming · listening…"));
  });

  window.addEventListener("swrlz-voice-turn", event => {
    if (!enabled || phase !== "waiting") return;
    if (event.detail?.phase === "sent") pendingId = String(event.detail.requestId || "");
    if (event.detail?.phase === "failed" && event.detail.requestId === pendingId) fail("chat send failed");
  });

  window.addEventListener("swrlz-voice-delta", event => {
    if (!enabled || !pendingId || !["waiting", "speaking"].includes(phase)) return;
    const { requestId, text } = event.detail || {};
    if (String(requestId || "") !== pendingId) return;
    receiveDelta(text);
  });

  window.addEventListener("swrlz-voice-state", event => {
    if (!enabled || !pendingId || !["waiting", "speaking"].includes(phase)) return;
    const { requestId, terminalType, text } = event.detail || {};
    if (String(requestId || "") !== pendingId) return;
    const terminal = String(terminalType || "").toUpperCase();
    if (terminal === "FAILED" || terminal === "CANCELLED") {
      fail("model generation " + terminal.toLowerCase());
    } else if (terminal === "COMPLETE" || terminal === "COMPLETED") {
      finishReply(text);
    }
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible" && enabled) stop("Voice paused while Chat is in the background.");
  });
  window.addEventListener("pagehide", () => {
    if (enabled) stop();
    window.SwrlzLocalVoice?.dispose(); // Full cleanup only when leaving page.
  });
  update("off", "");
})();
