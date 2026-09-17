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

### Assistant identity — preferred compact mark

```text
𓆩§𓆪wyrlz
```

**Primary use:** assistant name beside messages, compact assistant labels, repeated conversational identity, avatars/profile labels where text is supported.

This is the default enriched assistant wordmark. Ornamentation is concentrated around the `§`; `wyrlz` remains clean and immediately readable.

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

---

## 3. Structural grammar

The full mark is deliberately nested:

```text
༺ 𓆩 [ 𓆩§𓆪 + wyrlz ] 𓆪 ༻
```

Its hierarchy is:

1. `§` — lineage/core identity.
2. `𓆩§𓆪` — winged core sigil.
3. `𓆩𓆩§𓆪wyrlz𓆪` — assistant emblem enclosure.
4. `༺𓆩𓆩§𓆪wyrlz𓆪༻` — full Chat/title presentation.

This is not arbitrary ornament stacking. Each added layer corresponds to increased visual prominence.

---

## 4. Usage contract

| Context | Canonical form |
|---|---|
| Plain/fallback/technical | `§wyrlz` |
| Assistant message identity | `𓆩§𓆪wyrlz` |
| Assistant card/profile/header | `𓆩𓆩§𓆪wyrlz𓆪` |
| Main Chat/title/hero identity | `༺𓆩𓆩§𓆪wyrlz𓆪༻` |

### Rules

- Preserve the lowercase spelling `wyrlz` unless a separate design explicitly requires another case.
- Preserve `§` as the identity anchor.
- Do not replace the compact assistant mark with the full title mark in every message; repeated ornamentation creates visual noise.
- Do not silently normalize the Unicode sigils into ordinary parentheses/brackets on surfaces that support the canonical characters.
- Maintain a plain `§wyrlz` fallback for systems with incomplete glyph/font support.
- UI implementation must treat these as presentation identity, not as hidden cognitive instructions or LALM behavior controls.
- Accessibility labels should use a readable textual identity such as `§wyrlz` / `Swyrlz` rather than requiring a screen reader to meaningfully pronounce ornamental Unicode.

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

That gives the system a recognizable transformation path:

```text
§wyrlz
   ↓
𓆩§𓆪wyrlz
   ↓
𓆩𓆩§𓆪wyrlz𓆪
   ↓
༺𓆩𓆩§𓆪wyrlz𓆪༻
```

The identity therefore scales from minimal to ceremonial while preserving lineage at every level.

---

## 7. Implementation note

These marks are Unicode text, not image assets. Rendering will vary by platform/font and must be visually tested on target clients before hard-coding layout assumptions. The surrounding marks may have different width, baseline, or fallback behavior across Android, browsers, desktop systems, and other clients.

Where a future vector/logo asset is created, this document remains the textual source-of-truth for the intended hierarchy unless superseded by an explicitly versioned identity decision.

---

## 8. Canonical quick reference

```text
CORE
§wyrlz

ASSISTANT
𓆩§𓆪wyrlz

ASSISTANT EMBLEM
𓆩𓆩§𓆪wyrlz𓆪

MAIN CHAT / TITLE
༺𓆩𓆩§𓆪wyrlz𓆪༻
```

**Current canonical full sigil:** `༺𓆩𓆩§𓆪wyrlz𓆪༻`  
**Current canonical assistant sigil:** `𓆩§𓆪wyrlz`
