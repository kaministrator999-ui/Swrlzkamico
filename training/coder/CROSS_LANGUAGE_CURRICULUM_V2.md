# §wyrlz Coder Academy — Cross-language Bridge v2

**State:** TEACHER-AUTHORED LESSON / JAVA+KOTLIN+TYPESCRIPT EXAMPLES LOCALLY TESTED / RUST UNVERIFIED / QWEN WEIGHTS UNCHANGED.

**Purpose:** extend the real Qwen2.5-Coder-1.5B GGUF route's source curriculum to Kotlin, Java, TypeScript and Rust. Those languages were **not implementation files in the scanned main/runtime/HF candidate branches as of 2026-10-09**. This chapter teaches transferable relationships. It does NOT install dependencies, migrate the live Chat, activate a model prefill, or train weights.

**Prerequisite:** [Project Stack & Architecture v1](PROJECT_STACK_ARCHITECTURE_V1.md). The canonical [Programming LALM Runtime Architecture](../../docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md) still owns programming behavior and independent-evaluation policy.

## 1. One contract, four languages

The educational problem: a CLIENT receives SERVER response frames. Events can be out of order, repeat sequence IDs, or belong to a different request. Isolate a given request, accept only content events, keep the first arrival for each positive sequence, sort numerically ascending, and do not mutate caller-owned input.

~~~text
CLIENT → SERVER: send(requestId, payload)
SERVER → CLIENT: event(requestId, sequence, kind, content?)
CLIENT: check request identity → content-only → first sequence wins
        → ascending order → present without mutating canonical state
~~~

These are educational standalone references, **not production Chat protocol replacements**:
- [Kotlin](examples/FrameReconciler.kt): data class, List, sequence, distinctBy, sortedBy
- [Java 21](examples/FrameReconciler.java): record, TreeMap, putIfAbsent, defensive return
- [TypeScript](examples/frame-reconciler.ts): strict tagged union, readonly, typed response
- [Rust](examples/frame_reconciler.rs): borrowed slice, lifetime, BTreeMap, Result

The real Chat has its own message schemas, request correlation, Station, persistence, stream-camera contracts and client presentation. Learn the invariant, then trace the actual owner instead of inserting this teaching helper into production.

## 2. Kotlin — null safety, data flow, and prospective Android architecture

Language principles:
- String and String? have distinct nullability. Use safe calls and explicit defaults or branching; never use nonnull assertion as a blanket repair.
- val prevents reference reassignment, not all mutation of referenced objects. Understand List vs MutableList and copying.
- Data classes represent value-like records; sealed alternatives and exhaustive when aid explicit states.
- Suspend functions, structured concurrency, cancellation and Flow belong to Kotlin's actual runtime/dependency context; do not invent coroutine dependencies in the current repo.

A **future Android client** (not installed in this repository) might use:
~~~text
Compose screen → user action → ViewModel → immutable UiState (StateFlow)
                                      ↓
                                 repository (single owner)
                                 ↙          ↘
                       Room / DataStore    network CLIENT → SERVER
                                 ↓
                          state projection → Compose UI
~~~

If an actual Android module is introduced later, inspect settings.gradle.kts, build.gradle.kts, version catalog, supported SDK, current code and locked versions *before* adding Compose, Coroutines, Hilt, Room, DataStore, network clients or Gradle plugins. Android's recommended layered architecture favors repositories, UI state, unidirectional flow and coroutine/Flow patterns, but recommendations are not proof these technologies are installed.

**Failure practice:** an old Chat stream completes after switching threads. Identify the stable thread/request identity at client/Station boundary and only project the right state. Delaying Compose recomposition is not a fix for incorrect ownership.

## 3. Java — JVM APIs and data integrity

- Java record is concise data-carrying syntax but immutability is **shallow**; copy mutable list fields if the contract requires them immutable.
- Understand Java generics, exception contracts, resource closure, equality/hashCode, collections, threading and API compatibility.
- Java 21 desktop/JVM examples are not automatically valid on every Android SDK/Java language configuration. Confirm Gradle plugin, desugaring and platform API level before transfer.
- TreeMap orders keys, whereas HashMap iteration order is unspecified. putIfAbsent preserves first-arrival behavior and differs from put.
- Completion of an executor/queue does not mean an independently verified generated answer is semantically correct.

**Failure practice:** a fix changes putIfAbsent to put and silently changes duplicate precedence. It compiles but violates the contract; test the duplicate with different text.

## 4. TypeScript — safer CLIENT → SERVER, not blind rewriting of JavaScript

- TypeScript annotations are erased at runtime. Untrusted JSON must be checked at ingress; casting an external object to a type is not validation.
- Prefer strict mode, narrow unknown, use discriminated kind unions for event variants, and avoid optional-field bags where states are exclusive.
- readonly protects the type-level access path, not deep runtime immutability.
- The network response contract is owned at SERVER; a TypeScript client types the agreed envelope rather than inventing a rival event protocol.
- Model requestId/sequence, cancellation, terminal vs delta, deduplication and stream replay explicitly.
- Current Chat uses JavaScript in an HTML page. TypeScript is a **learning target**, not a request to introduce a Node bundler to production.

**Failure practice:** an object typed with an unchecked assertion compiles, then invalid server JSON crashes the UI. Add runtime shape validation and handle failures deliberately.

## 5. Rust — ownership, borrowing and native boundaries

- Resource ownership and borrowing govern valid lifetimes. String owns data; &str borrows a view; &T reads without taking ownership, &mut T has exclusive mutability constraints.
- Option represents absence and Result represents recoverable failure. Do not use unwrap as a generic production error policy.
- The Rust reference returns borrowed text whose lifetime is tied to the input slice, demonstrating that callers cannot keep dangling references after the source is gone.
- BTreeMap provides ordered keys; borrowed input is not mutated.
- The actual R39 native acceleration currently uses **C with NumPy/Python ABI**, not Rust. A Rust replacement would need explicit user authorization, profiling, FFI design, ABI tests, thread/error/panic boundaries and a proven owner; never replace C just because Rust offers safety mechanisms.
- Unsafe is not a way to silence a borrow-checker mistake.

**Failure practice:** returning a borrowed reference to a local temporary String is invalid. Return owned data or a reference demonstrably tied to the caller input.

## 6. Cross-language mapping

| Concern | Kotlin | Java | TypeScript | Rust |
|---|---|---|---|---|
| Possible absence | Nullable T? | null / Optional when appropriate | T or undefined union | Option<T> |
| Failure | exception or explicit result | exceptions | throw or tagged error | Result<T,E> |
| Data carrier | data class | record | interface / tagged union | struct / enum |
| Concurrency | coroutines and Flow (when available) | executors by runtime | Promise / async / streams | ownership + opted-in async runtime |
| Manifest if adopted | Gradle Kotlin DSL | Gradle or Maven | package.json, lock, tsconfig | Cargo.toml/Cargo.lock |
| Current project | study only | study only | study only | study only |

These examples use minimum standard-library dependencies. Framework choice follows the actual new app requirement, not the teacher's taste. Architecture ownership remains: Mask/client presentation, Station operational lifecycle, Brain semantics, canonical state store, Forge editor/render.

## 7. Validation and actual model-learning boundary

Example validation commands (isolated from the production repo):

~~~bash
kotlinc FrameReconciler.kt -include-runtime -d frame-kotlin.jar
java -jar frame-kotlin.jar

javac FrameReconciler.java
java FrameReconciler

tsc --strict --target es2020 --module commonjs --noEmit frame-reconciler.ts
tsc --strict --target es2020 --module commonjs --outDir dist frame-reconciler.ts
node dist/frame-reconciler.js

# Rust only when compiler/toolchain is available:
rustc --edition=2021 --test frame_reconciler.rs -o frame_tests
./frame_tests
~~~

**Teacher fixture evidence (2026-10-09):** Java 21 javac/java, TypeScript tsc strict plus Node 22, and Kotlin JVM 1.9 kotlinc/java each printed their corresponding FRAME_PASS marker on locally materialized equivalent source bodies. Rust compiler was not present; Rust example remains unverified until an independent compile/test. None of those executions are **Qwen-generated outputs** or evidence the hosted Chat changed.

[Public practice assignments v2](cross_language_practice_v2.json) remain UNGRADED until the actual Qwen model is asked to solve each independently and original output/test receipts are captured. Distinguish reference docs → model context ingestion → observed answers → independently tested patches → curated exact-source training records → trained checkpoint → guarded activation. Merely committing these files does not cause weight updates or automatic prompt ingestion.

## Canonical official references

- [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html)
- [Android app architecture recommendations](https://developer.android.com/topic/architecture/recommendations)
- [Java records](https://dev.java/learn/using-record-to-model-immutable-data/)
- [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [Rust ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)
- [Rust references/borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)

**Core rule:** If the real path is CLIENT → SERVER, say CLIENT → SERVER. A language name alone cannot transfer canonical ownership, activate a runtime dependency, or prove learned model competence.
