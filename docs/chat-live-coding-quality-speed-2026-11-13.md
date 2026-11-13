# §C Qwen3.5-9B live coding quality and latency — 2026-11-13

## Scope

Read-only synthetic tests against the existing Hugging Face Space, without user chat history, private source code, model changes, hardware changes or paid services. The live readiness endpoint reported model `qwen3.5-9b`, 16 effective CPU cores, 18 decode threads, 18 batch threads, batch 2048, microbatch 1024.

Benchmark workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43523771141

Repeat-diagnostic workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43524677356

## Five-task coding quality and latency results

| Test | First visible text | Total wall time | Native first token | Measured model generation | Inputs | Unit-test results |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Python `square(n)` | 105.299s | 105.301s | 20.739s | 22.521s | 1,388 tokens | 4/4 |
| Fix existing `square(n)` | 40.971s | 40.972s | 38.479s | 40.603s | 2,567 tokens | 4/4 |
| Python `is_prime(n)` | 29.643s | 29.671s | 15.581s | 29.362s | 1,403 tokens | 11/11 |
| Python `merge_intervals(intervals)` | 61.538s | 61.566s | 41.285s | 61.250s | 2,799 tokens | 5/5 |
| JS `isPalindrome(text)` | 29.417s | 29.418s | 15.688s | 29.128s | 1,414 tokens | 6/6 |

**Total: 5/5 tasks yielded complete code passing 30/30 executable tests.** All requests were observed using the coding route and had `candidateStatus=PASS`. These are small targeted tests, not proof of general coding correctness, safety, reliability under large repositories or long-term stability.

### Exact-output simple-code repeat

The standalone `square(n)` prompt was re-run in a new synthetic session with the same Qwen3.5-9B production configuration.

- **First run:** 105.299s first text, 105.301s complete, 20.739s native first token, 22.521s generation.
- **Repeat:** **17.127s first text and total**, 15.026s native first token, 16.869s generation.
- The generated output on both runs was byte-identical, SHA-256 prefix `eb3c0e4f5122`. All 4 square-function tests passed in both runs.
- Repeat Station metrics: `queueWaitMs=2`, `stationRunMs=16885`, `endToEndMs=16887`. Therefore the repeat did not experience queue delay.
- The approximately 83-second difference between first-run wall time and reported generation duration was outside the first run's measured model-generation window, **but its exact cause was not captured**. Could be transient queueing, startup, pipeline stalls or other overhead; no unsupported root-cause assertion is made. Do not treat 105s as a consistent simple-code latency.

## Engineering observations

1. Coding output started at essentially the moment of completion for **all five cases**. Code work behaves like buffered generation/validation rather than interactive token-by-token display; this is a significant user-perceived latency difference from §C's fast casual chat.
2. The repair and interval tasks had long prompt-prefill/native-first-token times (38.5s and 41.3s). Their larger system/input contexts are a promising target for safe prompt-prefix caching and reducing redundant processing, but must not lose repair constraints or coding validation.
3. The JavaScript and prime implementations took ~29–30s each, both correct. The repeat standalone square task required ~17s.
4. Optimize measurable time-to-first-visible-text and time-to-complete separately. Do not conflate a model starting native generation with user-visible streaming.
5. For future candidate changes, require deterministic code-correctness checks, repetition across warm/cold conditions, queue and generation time telemetry, unchanged Qwen3.5 model/hardware, and explicit rollback criteria.

## Validation boundaries

The Python outputs were parsed, isolated to permitted function/import nodes, and executed with bounded runtime and edge-case assertions. The JavaScript output was syntax-checked and its function executed in a bounded VM context on test inputs. These are real execution checks, not textual keyword matching. No private code or chat was tested, and no §C production files were changed by these benchmark workflows.
