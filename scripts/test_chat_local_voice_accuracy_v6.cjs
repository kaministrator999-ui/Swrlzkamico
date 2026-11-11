"use strict";
// Deterministic Vosk worker/microphone regression: complete phrase capture,
// committed-result de-duplication, soft speech and asynchronous final flush.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const js = fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/local_voice_vosk.js", "utf8");

(async () => {
  let now = 1000, nextId = 1, modelLoads = 0, finalRequests = 0;
  const timers = new Map(), recognizers = [], processors = [], tracks = [];
  function timeout(fn, ms = 0) {
    const id = nextId++;
    timers.set(id, { fn, due: now + ms });
    return id;
  }
  function advance(ms) {
    now += ms;
    for (let i = 0; i < 50; i++) {
      const due = [...timers.entries()].filter(([, t]) => t.due <= now)
        .sort((a, b) => a[1].due - b[1].due);
      if (!due.length) return;
      for (const [id, task] of due) {
        if (timers.delete(id)) task.fn();
      }
    }
    assert.fail("Timer loop did not settle");
  }
  const model = {
    KaldiRecognizer: class {
      constructor(rate) {
        assert.equal(rate, 48000);
        this.events = new Map();
        this.queuedFinal = "";
        recognizers.push(this);
      }
      on(name, fn) { this.events.set(name, fn); }
      setWords() {}
      acceptWaveform(input) { assert.ok(input.getChannelData); }
      emit(name, result) { this.events.get(name)?.({ result }); }
      retrieveFinalResult() {
        finalRequests++;
        timeout(() => this.emit("result", { text: this.queuedFinal }), 400);
      }
      remove() { this.removed = true; }
    },
    terminate() {}
  };
  const window = {
    Vosk: { async createModel() { modelLoads++; return model; } },
    dispatchEvent() {},
    AudioContext: class {
      constructor() { this.sampleRate = 48000; this.state = "running"; this.destination = {}; }
      createScriptProcessor(size) {
        assert.ok([2048, 4096].includes(size));
        const p = { onaudioprocess: null, connect() {}, disconnect() {} };
        processors.push(p);
        return p;
      }
      createMediaStreamSource() { return { connect() {}, disconnect() {} }; }
      createGain() { return { gain: { value: 1 }, connect() {}, disconnect() {} }; }
      close() { return Promise.resolve(); }
      resume() { return Promise.resolve(); }
    }
  };
  const navigator = { mediaDevices: {
    async getUserMedia({ audio }) {
      assert.equal(audio.sampleRate, undefined, "never force native input to 16 kHz");
      assert.equal(audio.autoGainControl, true);
      const track = { stopped: false, stop() { this.stopped = true; } };
      tracks.push(track);
      return { getTracks() { return [track]; } };
    }
  } };
  const FakeDate = class extends Date { static now() { return now; } };
  vm.runInNewContext(js, {
    window, navigator, Date: FakeDate, console,
    setTimeout: timeout, clearTimeout: id => timers.delete(id),
    CustomEvent: class { constructor(type, options) {
      this.type = type; this.detail = options?.detail;
    } }
  });
  async function begin(turbo) {
    const rec = new window.SwrlzLocalSpeechRecognition();
    rec.turbo = turbo;
    rec.messages = [];
    rec.errors = [];
    rec.onresult = event => {
      const entry = event.results[0];
      rec.messages.push({ final: entry.isFinal, text: entry[0].transcript });
      if (entry.isFinal) rec.stop();
    };
    rec.onerror = event => rec.errors.push(event);
    rec.start();
    for (let i = 0; i < 100 && !window.SwrlzLocalVoice.active; i++)
      await new Promise(resolve => setTimeout(resolve, 5));
    assert.ok(window.SwrlzLocalVoice.active, "Microphone unavailable");
    return rec;
  }
  function speak(frames, amplitude) {
    for (let i = 0; i < frames; i++) {
      now += 100;
      processors.at(-1).onaudioprocess({
        inputBuffer: { getChannelData() { return new Float32Array(2048).fill(amplitude); } }
      });
      advance(0);
    }
  }
  const finals = rec => rec.messages.filter(msg => msg.final);

  // Local: an ordinary Vosk phrase 'result' is not the end of the conversation.
  // A prior provisional 'hello' must not cause the committed 'hello' to vanish.
  const standard = await begin(false);
  speak(5, .012);
  recognizers.at(-1).emit("partialresult", { partial: "hello" });
  recognizers.at(-1).emit("result", { text: "hello" });
  assert.equal(finals(standard).length, 0);
  assert.equal(standard.messages.at(-1).text, "hello");
  recognizers.at(-1).emit("partialresult", { partial: "hello" }); // old queued duplicate
  assert.equal(standard.messages.at(-1).text, "hello");
  speak(10, 0); // natural pause between thoughts
  assert.equal(finals(standard).length, 0);
  speak(7, .012);
  recognizers.at(-1).emit("partialresult", { partial: "how are" });
  recognizers.at(-1).emit("result", { text: "how are" });
  assert.equal(standard.messages.at(-1).text, "hello how are");
  assert.equal(finals(standard).length, 0);
  recognizers.at(-1).queuedFinal = "you";
  speak(24, 0);
  assert.equal(finalRequests, 1, "Local must flush queued worker audio");
  assert.equal(finals(standard).length, 0, "Worker flush is asynchronous");
  advance(401); advance(551);
  assert.equal(finals(standard).length, 1);
  assert.equal(finals(standard)[0].text, "hello how are you");
  assert.equal(tracks[0].stopped, true);

  // Turbo: even one short phrase must not send a provisional incomplete answer.
  const turbo = await begin(true);
  speak(5, .0065);
  recognizers.at(-1).emit("partialresult", { partial: "hey how" });
  recognizers.at(-1).queuedFinal = "hey how are you";
  speak(20, 0);
  assert.equal(finalRequests, 2);
  assert.equal(finals(turbo).length, 0);
  advance(401); advance(551);
  assert.equal(finals(turbo)[0].text, "hey how are you");
  assert.equal(tracks[1].stopped, true);
  assert.equal(modelLoads, 1, "Local speech model remains loaded for consecutive turns");
  window.SwrlzLocalVoice.dispose();
  console.log("PASS: Local/Turbo preserve full multi-phrase speech, de-duplicate finals, detect soft speech and wait for worker flush");
})().catch(error => { console.error(error); process.exitCode = 1; });
