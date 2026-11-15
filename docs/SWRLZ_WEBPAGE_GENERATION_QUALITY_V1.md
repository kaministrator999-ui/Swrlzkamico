# §C HTML generation quality contract — 2026-11-14

## Triggering evidence

A user requested a general "cool HTML webpage". The generated Neon Horizon
page rendered but had agency-template filler ("Project Alpha", "Project Beta",
"Project Gamma"), a contact/send-message affordance without demonstrated
submission behavior, unstyled secondary sections, and top navigation that
overflowed a narrow Android viewport. A separate long-code example displayed
`<html>…</html>` yet the generation pipeline kept "Code repairing" active
and prompted a "Continue code" turn. The latter has already been addressed by
the source-verified HTML fence/completion patch deployed in §C revision
`b5fee5d3d123d4af498326f18b2a71f993e6baf1`.

## Implemented additive change

`scripts/hf_webpage_quality_policy_v1.py` patches the **actual** live
`qwen_coder_engine.py` in Hugging Face, source-pinned to the verified
revision before publication. This has no relation to Vercel or the older
`api/durable_redis_store.py` route.

- For requests classified as a delivered **web-page** artifact, the model
  gets a concise scope-specific contract before generating its first token,
  including complete visual treatment of all sections, responsive 320–390 px
  layouts, accessible controls, functional in-page interactions, and honest
  handling of forms without a server endpoint.
- Broad creative requests prefer one cohesive interactive experience rather
  than fictitious multi-studio/agency marketing templates.
- Specific customer/brand/site requests preserve the stated content and
  requirements, without inventing business facts.
- The same policy is carried into the pre-existing compact repair path, so a
  subsequent correction cannot silently discard these requirements.
- Bounded structural checks expose nonfatal diagnostic **risk codes** for:
  missing viewport metadata, form without a visible submit handler or target,
  generic fictitious Project Alpha/Beta/Gamma placeholders, and `href="#"`
  dead-end links. These are *heuristic warnings*, not a proof of failure.
- The candidate's original PASS/REJECT outcome and existing code-fence
  completion logic remain authoritative. The warnings **do not trigger**
  another model retry, which would reintroduce the costly "continue code"
  deadlock.

## Tests

`scripts/test_hf_webpage_quality_policy_v1.py` checks broad vs.
site-specific scoping, narrow phone/responsive/interactivity wording,
synthetic inert vs. working forms, placeholder project diagnostics, Python
syntax/patch anchors, and preserved status logic. It does not claim a live
browser visual regression, or that every generated webpage will pass a true
runtime usability test.

## Safety and follow-up

The release touches one `qwen_coder_engine.py` source file, never model
weights, Aiven credentials, Redis account records, Station routes, or §E.
The GitHub workflow takes an exact backup, compiles and tests the patch,
refuses unexpected source changes, checks running Stage/account and native
Valkey after publication, and restores the previous file on failed
acceptance when safe.

A genuine interactive browser evaluation should still run on new model
outputs, including viewport widths 320/390/768/desktop and clicks on all
visible controls, with any defects fed back into source-grounded improvement.
Generation quality is not guaranteed by prompt policy alone.
