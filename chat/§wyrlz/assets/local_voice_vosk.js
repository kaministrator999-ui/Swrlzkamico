/* §C experimental local streaming microphone: on-device Vosk WASM.
 * No paid speech endpoint. Microphone samples never go to §C or a hosted ASR.
 * English ~41MB model and Apache-2.0 library download only after user opts in.
 * Existing Chat send, Station streaming, and browser TTS remain authoritative.
 */
(() => {
  "use strict";
  const LIBRARY_URL = "https://cdn.jsdelivr.net/npm/vosk-browser@0.0.5/dist/vosk.js";
  const MODEL_URL = "https://huggingface.co/Andesprit/vosk-small/resolve/main/vosk-model-small-en-us-0.15.tar.gz";
  let libraryPromise = null;
  let modelPromise = null;
  let model = null;
  let microphone = null;
  let active = null;
  let generation = 0;

  const stopAudio = () => {
    const previous = microphone;
    microphone = null;
    if (!previous) return;
    previous.processor.onaudioprocess = null;
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

  const loadModel = async status => {
    if (model) return model;
    if (!modelPromise) {
      modelPromise = (async () => {
        status?.("Loading local recognition · ~41 MB model download…");
        const library = await loadLibrary();
        const loaded = await library.createModel(MODEL_URL);
        if (!loaded || typeof loaded.KaldiRecognizer !== "function") throw new Error("Local model initialization failed");
        return loaded;
      })().catch(error => { modelPromise = null; throw error; });
    }
    model = await modelPromise;
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
    const oldPromise = modelPromise;
    model = null;
    modelPromise = null;
    if (oldPromise) void oldPromise.then(m => {
      if (m && model !== m) try { m.terminate(); } catch (_) {}
    }).catch(() => {});
  };

  const start = async ({ onPartial, onFinal, onStatus, onError }) => {
    stop();
    const token = generation;
    active = token;
    try {
      const available = await loadModel(onStatus);
      if (active !== token) return;
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!navigator.mediaDevices?.getUserMedia || !AudioContextClass)
        throw new Error("Microphone audio capture is unsupported");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1, sampleRate: 16000 }
      });
      if (active !== token) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }
      let context, processor, source, silentGain, recognizer;
      try {
        context = new AudioContextClass();
        if (typeof context.createScriptProcessor !== "function")
          throw new Error("Streaming audio processor unavailable");
        recognizer = new available.KaldiRecognizer();
        recognizer.setWords?.(false);
        recognizer.on("partialresult", event => {
          if (active === token && event?.result?.partial)
            onPartial?.(String(event.result.partial));
        });
        recognizer.on("result", event => {
          const transcription = String(event?.result?.text || "").trim();
          if (active === token && transcription) onFinal?.(transcription);
        });
        processor = context.createScriptProcessor(4096, 1, 1);
        source = context.createMediaStreamSource(stream);
        silentGain = context.createGain();
        silentGain.gain.value = 0;
        processor.onaudioprocess = event => {
          if (active !== token) return;
          try { recognizer.acceptWaveform(event.inputBuffer); }
          catch (_) { onError?.("Local recognition audio processing failed"); }
        };
        // A silent destination connection keeps ScriptProcessor pumping.
        // No monitor/audio feedback through speakers.
        source.connect(processor);
        processor.connect(silentGain);
        silentGain.connect(context.destination);
        microphone = { stream, context, source, processor, silentGain, recognizer };
        if (context.state === "suspended") await context.resume();
        if (active === token) onStatus?.("Local streaming · listening on this device…");
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
      void start({
        onPartial: value => {
          if (this._running) this.onresult?.({ results: [{ isFinal: false, 0: { transcript: value } }] });
        },
        onFinal: value => {
          if (this._running) this.onresult?.({ results: [{ isFinal: true, 0: { transcript: value } }] });
        },
        onStatus: label => window.dispatchEvent(new CustomEvent("swrlz-local-voice-status", { detail: { label } })),
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
