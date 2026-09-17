# ༺𓆩𓆩§𓆪wyrlz𓆪༻ — §wyrlz Sigil System

**Status:** Canonical identity documentation  
**Established:** 2026-09-16  
**Purpose:** Preserve the visual lineage, hierarchy, and intended UI usage of the §wyrlz Unicode sigil system.

---

## 1. Identity principle

The sigil system extends the existing `§wyrlz` identity rather than replacing it.

The central discovery is:

```text
𓆩§𓆪
```

The paired marks visually bind to the `§`, making the section sign read as a winged / awakened central sigil while preserving `§` as the recognizable lineage anchor.

The system intentionally scales ornamentation with UI importance. Repeated assistant labels stay compact; major title surfaces may use the complete ceremonial mark.

---

## 2. Canonical hierarchy

### Core / fallback identity

```text
§wyrlz
```

Use when Unicode support, horizontal space, accessibility, plain-text transport, logging, identifiers, or implementation constraints make the richer marks undesirable.

### Assistant identity — compact/base mark

```text
𓆩§𓆪wyrlz
```

**Primary use:** compact assistant identity, constrained surfaces, avatars/profile labels where text is supported, and fallback where the response-name treatment would be too visually dense.

Ornamentation is concentrated around the `§`; `wyrlz` remains clean and immediately readable.

### AI response-name identity — canonical Chat response mark

```text
⌬𓆩§𓆪wyrlz⌬
```

**Primary use:** the visible AI/assistant name attached to §wyrlz responses in Chat.

The `⌬` pair adds a geometric glitch-core / computational shell around the established winged `§` identity without mutating the readable `wyrlz` name. This is the preferred response-name treatment when the available UI width and font support are sufficient.

### Assistant emblem / medium mark

```text
𓆩𓆩§𓆪wyrlz𓆪
```

**Primary use:** assistant profile headers, assistant cards, splash elements, About surfaces, larger UI identity areas.

This adds an outer enclosure without introducing the full title flourish.

### Main Chat / title identity — canonical full mark

```text
༺𓆩𓆩§𓆪wyrlz𓆪༻
```

**Primary use:** main Chat name, major product/title display, hero identity, ceremonial branding, prominent headers where sufficient space exists.

This is the canonical full §wyrlz Chat sigil.

### Send-response action sigil

```text
〘§〙
```

**Primary use:** visual glyph for the Chat composer send-response button, replacing the conventional arrow where the §wyrlz Chat design uses the sigil system.

The control deliberately collapses the identity to the `§` nucleus because a send button is a small, repeated action surface. `〘 〙` provides a compact visual enclosure while keeping the action recognizable as part of §wyrlz rather than introducing the full wordmark into the composer control.

The visible glyph does **not** replace the semantic control name. The button must retain an accessible label such as **Send message** / **Send response**, keyboard behavior, disabled/loading state semantics, focus treatment, and normal button affordances.

---

## 3. Structural grammar

The full mark is deliberately nested:

```text
༺ 𓆩 [ 𓆩§𓆪 + wyrlz ] 𓆪 ༻
```

Its hierarchy is:

1. `§` — lineage/core identity.
2. `𓆩§𓆪` — winged core sigil.
3. `⌬𓆩§𓆪wyrlz⌬` — Chat response-name / glitch-core state.
4. `𓆩𓆩§𓆪wyrlz𓆪` — assistant emblem enclosure.
5. `༺𓆩𓆩§𓆪wyrlz𓆪༻` — full Chat/title presentation.
6. `〘§〙` — action compression: the identity collapses back to its core for the send-response control.

This is not arbitrary ornament stacking. Each added or reduced layer corresponds to a distinct UI role and level of visual prominence.

---

## 4. Usage contract

| Context | Canonical form |
|---|---|
| Plain/fallback/technical | `§wyrlz` |
| Compact assistant identity | `𓆩§𓆪wyrlz` |
| AI response name in Chat | `⌬𓆩§𓆪wyrlz⌬` |
| Assistant card/profile/header | `𓆩𓆩§𓆪wyrlz𓆪` |
| Main Chat/title/hero identity | `༺𓆩𓆩§𓆪wyrlz𓆪༻` |
| Send-response button | `〘§〙` |

### Rules

- Preserve the lowercase spelling `wyrlz` unless a separate design explicitly requires another case.
- Preserve `§` as the identity anchor.
- Use `⌬𓆩§𓆪wyrlz⌬` as the canonical AI response-name treatment when the Chat surface can render it cleanly.
- Use `𓆩§𓆪wyrlz` as the compact assistant identity and response-name fallback when space/rendering requires less ornamentation.
- Do not replace compact/repeated marks with the full title mark in every message; repeated ceremonial ornamentation creates visual noise.
- Use `〘§〙` as a visual send-action identity, never as a substitute for the control's accessible semantic label.
- Do not silently normalize the Unicode sigils into ordinary parentheses/brackets on surfaces that support the canonical characters.
- Maintain a plain `§wyrlz` fallback for systems with incomplete glyph/font support.
- UI implementation must treat these as presentation identity, not as hidden cognitive instructions or LALM behavior controls.
- Accessibility labels should use readable textual identity/action labels rather than requiring a screen reader to meaningfully pronounce ornamental Unicode.

---

## 5. Experimental / non-canonical forge variants

These remain useful design experiments but are **not** the current canonical hierarchy:

```text
꧁§꧂
꧁𓆩§𓆪꧂
༺𓆩§𓆪༻
꧁༺𓆩§wy∞lz§𓆪༻꧂
∞§∞
𓆩§∞§𓆪
```

The experimental form:

```text
꧁༺𓆩§wy∞lz§𓆪༻꧂
```

is a distinct recursive/ceremonial exploration. It mutates the wordmark itself by introducing `∞` into the name and therefore should not replace the canonical readable `wyrlz` identity without an explicit future identity decision.

---

## 6. Design rationale

The strongest property of `𓆩§𓆪wyrlz` is that the ornament reads as belonging specifically to the `§`, rather than merely framing an otherwise unchanged gamer-style name.

The response mark extends that identity with a computational shell:

```text
⌬𓆩§𓆪wyrlz⌬
```

while the send action performs the opposite transformation by compressing the system back to its nucleus:

```text
〘§〙
```

That gives the system a recognizable transformation path:

```text
§wyrlz
   ↓
𓆩§𓆪wyrlz
   ↓
⌬𓆩§𓆪wyrlz⌬    ← AI response identity
   ↓
𓆩𓆩§𓆪wyrlz𓆪
   ↓
༺𓆩𓆩§𓆪wyrlz𓆪༻

ACTION COMPRESSION
§wyrlz → § → 〘§〙 → Send
```

The identity therefore scales from minimal to ceremonial while preserving lineage, and can also collapse into a functional UI action without forcing the complete name into a tiny control.

---

## 7. Implementation note

These marks are Unicode text, not image assets. Rendering will vary by platform/font and must be visually tested on target clients before hard-coding layout assumptions. The surrounding marks may have different width, baseline, or fallback behavior across Android, browsers, desktop systems, and other clients.

For `〘§〙`, implementation should preserve the existing send button's semantic behavior and state machine. Only its visual identity changes unless a separate interaction change is explicitly designed and tested.

Where a future vector/logo asset is created, this document remains the textual source-of-truth for the intended hierarchy unless superseded by an explicitly versioned identity decision.

---

## 8. Canonical quick reference

```text
CORE
§wyrlz

COMPACT ASSISTANT
𓆩§𓆪wyrlz

AI RESPONSE NAME
⌬𓆩§𓆪wyrlz⌬

ASSISTANT EMBLEM
𓆩𓆩§𓆪wyrlz𓆪

MAIN CHAT / TITLE
༺𓆩𓆩§𓆪wyrlz𓆪༻

SEND RESPONSE
〘§〙
```

**Current canonical full sigil:** `༺𓆩𓆩§𓆪wyrlz𓆪༻`  
**Current canonical AI response sigil:** `⌬𓆩§𓆪wyrlz⌬`  
**Current canonical compact assistant sigil:** `𓆩§𓆪wyrlz`  
**Current canonical send-response sigil:** `〘§〙`
