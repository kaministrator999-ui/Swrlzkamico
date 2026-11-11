/* §C local streaming microphone v6: preserve all spoken phrases, capture soft speech and flush both Local/Turbo turns.
 * No paid speech endpoint. Microphone samples never go to §C or a hosted ASR.
 * English ~41MB model and Apache-2.0 library download only after user opts in.
 * Existing Chat send, Station streaming, and browser TTS remain authoritative.
 */
(() => {
  "use strict";
  const LIBRARY_URL = "https://cdn.jsdelivr.net/npm/vosk-browser@0.0.5/dist/vosk.js";
  const MODEL_URL = "https://huggingface.co/Andesprit/vosk-small/resolve/main/vosk-model-small-en-us-0.15.tar.gz";
  const MODEL_CACHE = "swrlz-vosk-en-015-v1";
  // Vosk's native final event depends on enough trailing silence. On Android
  // a partial transcript can remain forever without a terminal event.
  // A brief pause is not the end of the user's message. Both input profiles
  // retain words from multiple Vosk phrase results and flush the worker once.
  const QUIET_FINAL_MS = 2300;
  const TURBO_QUIET_FINAL_MS = 1900;
  let libraryPromise = null;
  let modelPromise = null;
  let model = null;
  let modelEpoch = 0;
  let microphone = null;
  let active = null;
  let generation = 0;

  const stopAudio = () => {
    const previous = microphone;
    microphone = null;
    if (!previous) return;
    previous.processor.onaudioprocess = null;
    if (previous.watchdog) clearTimeout(previous.watchdog);
    if (previous.finalizeTimeout) clearTimeout(previous.finalizeTimeout);
    if (previous.finalizeSettle) clearTimeout(previous.finalizeSettle);
    try { previous.processor.disconnect(); } catch (_) {}
    try { previous.source.disconnect(); } catch (_) {}
    try { previous.silentGain.disconnect(); } catch (_) {}
    for (const track of previous.stream.getTracks()) track.stop();
    void previous.context.close().catch(() => {});
    try { previous.recognizer.remove(); } catch (_) {}
  };

  const loadLibrary = () => {
    if (window.Vosk?.createModel) return Promise.resolve(window.Vosk);
    if (libraryPromise) return libraryPromise;
    libraryPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = LIBRARY_URL;
      script.async = true;
      script.crossOrigin = "anonymous";
      script.onload = () => window.Vosk?.createModel ? resolve(window.Vosk) : reject(new Error("Vosk WASM library unavailable"));
      script.onerror = () => reject(new Error("Vosk library download blocked"));
      document.head.appendChild(script);
    }).catch(error => { libraryPromise = null; throw error; });
    return libraryPromise;
  };

  const archiveSource = async status => {
    // CacheStorage preserves the ~41 MB compressed model across page reloads.
    // Browsers may evict it under storage pressure; never require persistence.
    if (!window.caches || !window.URL?.createObjectURL)
      return { url: MODEL_URL, revoke: () => {} };
    let cache = null;
    try { cache = await window.caches.open(MODEL_CACHE); } catch (_) {}
    if (!cache) return { url: MODEL_URL, revoke: () => {} };
    let response = null;
    try { response = await cache.match(MODEL_URL); } catch (_) {}
    if (response) {
      status?.("Opening cached local speech model…");
    } else {
      status?.("Downloading local speech model · first use ~41 MB…");
      response = await fetch(MODEL_URL, { mode: "cors", credentials: "omit" });
      if (!response.ok || response.type === "opaque")
        throw new Error("Local speech model download failed");
      // A cache-write failure must not waste the successfully fetched model.
      try { await cache.put(MODEL_URL, response.clone()); } catch (_) {}
    }
    const blob = await response.blob();
    if (blob.size < 35_000_000 || blob.size > 50_000_000)
      throw new Error("Local speech model archive was incomplete");
    const url = window.URL.createObjectURL(blob);
    return { url, revoke: () => window.URL.revokeObjectURL(url) };
  };

  const loadModel = async status => {
    if (model) return model;
    const epoch = modelEpoch;
    if (!modelPromise) {
      modelPromise = (async () => {
        status?.("Preparing on-device speech recognition…");
        const library = await loadLibrary();
        const archive = await archiveSource(status);
        try {
          status?.("Initializing cached local speech engine…");
          const loaded = await library.createModel(archive.url);
          if (!loaded || typeof loaded.KaldiRecognizer !== "function")
            throw new Error("Local model initialization failed");
          return loaded;
        } finally {
          archive.revoke();
        }
      })().catch(error => { modelPromise = null; throw error; });
    }
    const loaded = await modelPromise;
    if (epoch !== modelEpoch) return null;
    model = loaded;
    return model;
  };

  const stop = () => {
    generation++;
    active = null;
    stopAudio();
  };

  const dispose = () => {
    stop();
    // If model initialization is still underway, terminate it when it resolves.
    ++modelEpoch;
    const oldPromise = modelPromise;
    model = null;
    modelPromise = null;
    if (oldPromise) void oldPromise.then(m => {
      try { m?.terminate?.(); } catch (_) {}
    }).catch(() => {});
  };

  const start = async ({ onPartial, onFinal, onStatus, onError, turbo = false }) => {
    stop();
    const token = generation;
    active = token;
    try {
      const available = await loadModel(onStatus);
      if (active !== token || !available) return;
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!navigator.mediaDevices?.getUserMedia || !AudioContextClass)
        throw new Error("Microphone audio capture is unsupported");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: false,
        // Let Android capture at its natural rate for BOTH local modes.
        // The decoder receives the actual AudioContext.sampleRate below;
        // forcing 16 kHz here can add unnecessary resampling and distort words.
        audio: { echoCancellation: true, noiseSuppression: true,
                 autoGainControl: true, channelCount: 1 }
      });
      if (active !== token) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }
      let context, processor, source, silentGain, recognizer;
      try {
        // Avoid the forced 16kHz resampling path: on the Moto it reduces
        // recognition quality. Use the native Web Audio rate, same as Local.
        // Turbo still has smaller buffers and an adaptive turn endpointer.
        if (turbo) {
          try { context = new AudioContextClass({ latencyHint: "interactive" }); }
          catch (_) { context = new AudioContextClass(); }
        } else {
          context = new AudioContextClass();
        }
        if (typeof context.createScriptProcessor !== "function")
          throw new Error("Streaming audio processor unavailable");
        // Vosk-browser 0.0.5 MUST receive the actual Web Audio sample rate.
        // Android can use 48 kHz even if getUserMedia requested 16 kHz.
        // Omitting this argument leaves the WASM recognizer uninitialized:
        // mic RMS still works, but the worker never produces words.
        const sampleRate = Number(context.sampleRate);
        if (!Number.isFinite(sampleRate) || sampleRate < 8000 || sampleRate > 192000)
          throw new Error("Browser did not provide a valid microphone sample rate");
        recognizer = new available.KaldiRecognizer(sampleRate);
        recognizer.setWords?.(false);
        let latestPartial = "";
        let lastPartialAt = 0;
        let lastLoudAt = 0;
        let firstLoudAt = 0;
        let loudFrames = 0;
        let frames = 0;
        let emitted = false;
        let reportedInput = false;
        let reportedStall = false;
        const committedSegments = [];
        let lastSegmentAt = 0;
        let finalRequested = false;
        let finalResultSeen = false;
        let finalResultAvailable = false;
        let finalSettleTimer = 0;
        let finalDeadlineTimer = 0;
        let lastAudioAt = 0;
        const quietWindowMs = turbo ? TURBO_QUIET_FINAL_MS : QUIET_FINAL_MS;
        const fullTranscript = () => [...committedSegments, latestPartial]
          .filter(Boolean).join(" ").trim();
        const finishUtterance = text => {
          const words = String(text || "").trim();
          if (active !== token || emitted || !words) return;
          emitted = true;
          if (finalSettleTimer) clearTimeout(finalSettleTimer);
          if (finalDeadlineTimer) clearTimeout(finalDeadlineTimer);
          onFinal?.(words); // Talk calls recognizer.stop() and canonical send.
        };
        const finalFallback = () => {
          if (active !== token || emitted) return;
          const words = fullTranscript();
          if (finalResultSeen && words) {
            finishUtterance(words);
          } else if (!finalResultAvailable && words) {
            // A legacy Vosk build has no explicit final flush. Preserve the
            // previous fallback for that specific compatibility case.
            finishUtterance(words);
          } else {
            // A partial is provisional. Never silently send "hello how"
            // while the final worker response is missing or empty.
            onError?.("Final transcription unavailable; review the visible words or use Browser input");
          }
        };
        const settleFinal = () => {
          if (!finalRequested || active !== token || emitted) return;
          if (finalSettleTimer) clearTimeout(finalSettleTimer);
          // Vosk's WASM worker returns asynchronously. Give the last result
          // room to arrive after queued partials and phrase-boundary results.
          finalSettleTimer = setTimeout(() => {
            if (active === token && !emitted && finalResultSeen)
              finalFallback();
          }, 550);
          if (microphone) microphone.finalizeSettle = finalSettleTimer;
        };
        const requestFinal = () => {
          if (finalRequested || emitted || active !== token) return;
          finalRequested = true;
          onStatus?.("Speech finished · completing local transcription…");
          // Vosk accepts audio on a Web Worker: do not submit the most recent
          // partial before already-queued audio has been decoded and flushed.
          if (typeof recognizer.retrieveFinalResult === "function") {
            try {
              recognizer.retrieveFinalResult();
              finalResultAvailable = true;
            } catch (_) {
              finalResultAvailable = false;
            }
          }
          finalDeadlineTimer = setTimeout(finalFallback, 2600);
          if (microphone) microphone.finalizeTimeout = finalDeadlineTimer;
        };
        recognizer.on("partialresult", event => {
          if (active !== token || emitted) return;
          const partial = String(event?.result?.partial || "").trim();
          if (partial) {
            if (partial !== latestPartial) lastPartialAt = Date.now();
            // A queued partial may repeat a phrase that has already been
            // committed. Do not display it twice or append it to the next turn.
            const prior = committedSegments.join(" ").trim().toLowerCase();
            latestPartial = prior && (partial.toLowerCase() === prior ||
              prior.endsWith(" " + partial.toLowerCase())) ? "" : partial;
            onPartial?.(fullTranscript());
          }
        });
        recognizer.on("result", event => {
          if (active !== token || emitted) return;
          const transcription = String(event?.result?.text || "").trim();
          // A Vosk "result" ends a decoder phrase, not the user's turn.
          // This applies to BOTH local profiles: never auto-send on first result.
          if (transcription) {
            // Compare only with COMMITTED results, never provisional partials.
            // The old equality check cleared a matching partial WITHOUT saving
            // its finalized text, silently dropping the first spoken words.
            const committed = committedSegments.join(" ").trim();
            const lowerCommitted = committed.toLowerCase();
            const lowerResult = transcription.toLowerCase();
            if (lowerCommitted && (lowerResult === lowerCommitted ||
                lowerCommitted.endsWith(" " + lowerResult))) {
              // The worker repeated an already committed phrase.
            } else if (lowerCommitted && lowerResult.startsWith(lowerCommitted + " ")) {
              // The worker returned a more complete replacement transcript.
              committedSegments.length = 0;
              committedSegments.push(transcription);
            } else {
              // First final phrase or genuinely new phrase.
              committedSegments.push(transcription);
            }
            latestPartial = "";
            lastSegmentAt = Date.now();
            onPartial?.(fullTranscript());
          }
          if (finalRequested) {
            finalResultSeen = true;
            settleFinal();
          }
        });
        processor = context.createScriptProcessor(turbo ? 2048 : 4096, 1, 1);
        source = context.createMediaStreamSource(stream);
        silentGain = context.createGain();
        silentGain.gain.value = 0;
        processor.onaudioprocess = event => {
          if (active !== token || emitted) return;
          const input = event?.inputBuffer;
          if (!input?.getChannelData) {
            onError?.("Microphone supplied no audio buffer");
            return;
          }
          const pcm = input.getChannelData(0);
          if (!pcm?.length) return;
          frames++;
          const now = Date.now();
          lastAudioAt = now;
          // Lightweight energy-based end-of-utterance detection. The audio
          // remains local; only an RMS number is observed, never persisted.
          let power = 0, count = 0;
          for (let i = 0; i < pcm.length; i += 32) {
            power += pcm[i] * pcm[i];
            count++;
          }
          const rms = Math.sqrt(power / Math.max(1, count));
          // A lower Turbo voice threshold catches softer speech, while the
          // longer silence gate avoids mistaking a quick pause for a full turn.
          if (rms >= (turbo ? 0.007 : 0.012)) {
            if (!firstLoudAt) firstLoudAt = now;
            lastLoudAt = now;
            loudFrames++;
          }
          if (!reportedInput && frames >= 3) {
            reportedInput = true;
            onStatus?.("Local microphone audio received · listening…");
          }
          // After final flush is requested, no further chunks can be queued:
          // otherwise the worker may finalize before processing new audio.
          if (!finalRequested) {
            try { recognizer.acceptWaveform(input); }
            catch (_) { onError?.("Local speech decoder rejected microphone audio"); return; }
          }
          if (active !== token || emitted) return;
          // Soft speech can produce Vosk words below a fixed RMS threshold.
          // Recognized-word activity keeps the turn alive even if the mic's
          // loud-frame detector missed it. Never close on a stale partial
          // while new words may still be arriving from the worker.
          const lastSpeechAt = Math.max(lastLoudAt, lastPartialAt, lastSegmentAt);
          const hasSpeech = loudFrames >= 3 || Boolean(fullTranscript());
          const quiet = hasSpeech && lastSpeechAt && now - lastSpeechAt >= quietWindowMs;
          if (quiet && !finalRequested &&
              (!lastSegmentAt || now - lastSegmentAt >= 350))
            requestFinal();
          if (frames >= 65 && !latestPartial && !committedSegments.length && !reportedStall) {
            reportedStall = true;
            onStatus?.("Microphone audio confirmed · waiting for local transcript…");
          } else if (firstLoudAt && loudFrames >= 8 &&
                     now - firstLoudAt >= 15000 && !fullTranscript()) {
            onError?.("Microphone audio reached Vosk, but no words were recognized");
          }
        };
        // A silent destination connection keeps ScriptProcessor pumping.
        // No monitor/audio feedback through speakers.
        source.connect(processor);
        processor.connect(silentGain);
        silentGain.connect(context.destination);
        microphone = { stream, context, source, processor, silentGain, recognizer,
                       watchdog: 0, finalizeTimeout: 0, finalizeSettle: 0 };
        if (context.state === "suspended") await context.resume();
        if (active === token) {
          onStatus?.((turbo ? "Turbo " : "Vosk ") + sampleRate + " Hz · checking microphone audio…");
          microphone.watchdog = setTimeout(() => {
            if (active === token && !frames)
              onError?.("Mic opened, but browser delivered no audio frames");
          }, 5000);
        }
      } catch (error) {
        processor?.disconnect?.();
        source?.disconnect?.();
        silentGain?.disconnect?.();
        stream.getTracks().forEach(track => track.stop());
        try { recognizer?.remove?.(); } catch (_) {}
        if (context) void context.close().catch(() => {});
        throw error;
      }
    } catch (error) {
      if (active === token) {
        stop();
        onError?.(String(error?.message || "Local speech recognition unavailable"));
      }
    }
  };

  class LocalVoskRecognition {
    constructor() {
      this.lang = "en-US";
      this.continuous = false;
      this.interimResults = true;
      this.maxAlternatives = 1;
      this.turbo = false;
      this.onresult = null;
      this.onerror = null;
      this.onend = null;
      this._running = false;
    }
    start() {
      if (this._running) return;
      this._running = true;
      // Native SpeechRecognition-shaped adapter: retain canonical Talk turn
      // lifecycle and finish one utterance before sending to LALM Station.
      // Local stream begins asynchronously while the model downloads.
      void start({
        turbo: this.turbo === true,
        onPartial: value => {
          if (this._running) this.onresult?.({ results: [{ isFinal: false, 0: { transcript: value } }] });
        },
        onFinal: value => {
          if (this._running) this.onresult?.({ results: [{ isFinal: true, 0: { transcript: value } }] });
        },
        onStatus: label => { if (this._running) window.dispatchEvent(new CustomEvent("swrlz-local-voice-status", { detail: { label } })); },
        onError: reason => {
          if (!this._running) return;
          this.onerror?.({ error: "local-engine", detail: reason });
          this.abort();
        }
      });
    }
    stop() {
      if (!this._running) return;
      this._running = false;
      stop();
      this.onend?.();
    }
    abort() {
      this._running = false;
      stop();
    }
  }

  window.SwrlzLocalVoice = Object.freeze({ dispose, stop, get active() { return Boolean(microphone); } });
  window.SwrlzLocalSpeechRecognition = LocalVoskRecognition;
})();
