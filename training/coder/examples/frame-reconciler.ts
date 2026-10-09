// EDUCATIONAL FIXTURE ONLY — not a migration of the existing JavaScript Chat UI.
// Check: tsc --strict --target es2020 --module commonjs --noEmit frame-reconciler.ts
// Run: tsc --strict --target es2020 --module commonjs --outDir dist frame-reconciler.ts && node dist/frame-reconciler.js
type ChatEvent =
  | { readonly kind: "delta"; readonly requestId: string; readonly sequence: number; readonly text: string }
  | { readonly kind: "done"; readonly requestId: string; readonly sequence: number }
  | { readonly kind: "failed"; readonly requestId: string; readonly sequence: number; readonly reason: string };

export function orderedDeltas(events: readonly ChatEvent[], requestId: string): string[] {
  const firstBySequence = new Map<number, string>();
  for (const event of events) {
    if (event.requestId !== requestId || event.sequence <= 0) continue;
    if (event.kind === "delta" && !firstBySequence.has(event.sequence)) {
      firstBySequence.set(event.sequence, event.text);
    }
  }
  return [...firstBySequence.entries()]
    .sort(([a], [b]) => a - b)
    .map(([, text]) => text);
}
const input: readonly ChatEvent[] = [
  { kind: "delta", requestId: "thread-A", sequence: 3, text: "!" },
  { kind: "delta", requestId: "thread-B", sequence: 1, text: "leak" },
  { kind: "delta", requestId: "thread-A", sequence: 1, text: "Hi" },
  { kind: "delta", requestId: "thread-A", sequence: 2, text: " there" },
  { kind: "delta", requestId: "thread-A", sequence: 2, text: "WRONG" },
  { kind: "done", requestId: "thread-A", sequence: 4 }
];
const output = orderedDeltas(input, "thread-A");
if (JSON.stringify(output) !== JSON.stringify(["Hi", " there", "!"])) {
  throw new Error("Incorrect request isolation, ordering or deduplication");
}
if (orderedDeltas(input, "missing").length) throw new Error("Cross-request leakage");
console.log("TYPESCRIPT_FRAME_PASS");
