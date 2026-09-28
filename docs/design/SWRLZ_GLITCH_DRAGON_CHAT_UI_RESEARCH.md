# §wyrlz Glitch Dragon Chat Interface — Research + Product Schematics

**Status:** design/research blueprint. No production UI mutation is performed by this document.

**Primary product surface:** `/chat/§wyrlz`

**Architecture anchors:** `§wyrlz_§tart.md`, `SWRLZ_CHAT_OVERVIEW.md`, `SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`, `SWRLZ_RUNTIME_HOTLOADER_GUIDE.md`, and the existing durable account/profile/chat contracts.

---

## 1. Product direction

§wyrlz should feel like a compact modern AI chat first, and a living glitch-dragon companion second.

The main conversation must remain visually calm:

```text
TOP / EDGE CHROME
  compact brand / active model / status

CENTER STAGE
  conversation only
  assistant + user messages
  streaming / tool / status cards only when active

BOTTOM
  compact composer
  attach / mode / send / stop
```

Power lives behind progressive disclosure:

```text
hamburger / dragon crest
  ├─ chats
  ├─ search
  ├─ companion
  ├─ user profile
  ├─ memory + lore
  ├─ model + generation
  ├─ appearance + motion
  ├─ privacy + data
  ├─ accessibility
  └─ advanced / diagnostics
```

The interface must not become a permanently visible cockpit. Sci-fi styling is a visual language applied to real product information.

---

## 2. Core visual system

### 2.1 Glitch dragon aesthetic

Use:

- near-black / midnight-blue stage foundation;
- cold cyan / ice-blue primary signal;
- violet-magenta secondary glitch signal;
- restrained amber for warnings;
- red only for destructive / failed state;
- thin spectral linework;
- clipped / faceted dragon-scale geometry;
- sparse particles / scan fragments only in inactive negative space;
- subtle parallax or luminous breathing around the kompanion/avatar;
- micro-glitch transitions only around state changes;
- local glow, never blanket neon bloom.

Avoid:

- decorative fake telemetry;
- unreadable all-caps body text;
- constant scanlines over messages;
- heavy chromatic aberration over text;
- motion on every surface;
- status colors used decoratively;
- radial HUDs for ordinary form controls.

### 2.2 Typography

Use two roles:

1. **Conversation typography** — highly readable system or humanist sans.
2. **Machine / dragon telemetry** — compact mono/condensed face for labels, status, model/runtime, token/context readouts.

Do not render long assistant/user prose in sci-fi display fonts.

---

## 3. Stage composition

Mapped to the canonical Chat theater model:

### Scenery

Persistent, structural:

- application root;
- conversation viewport;
- side drawer;
- composer shell;
- top-edge status strip / compact brand owner;
- background dragon environment;
- modal / sheet host.

### Starting props

Visible at open:

- §wyrlz crest / kompanion;
- active thread title;
- selected model badge;
- composer controls;
- current theme;
- compact online/ready indicator.

### Actors

Stateful participants:

- current thread;
- message list;
- user identity;
- §wyrlz identity;
- selected model;
- active attachment set;
- active tool/research execution;
- companion rapport state.

### Temporary actors / props

Bounded events:

- streaming indicator;
- tool-call / research card;
- upload progress;
- approval request;
- toast;
- regeneration / retry state;
- error notice;
- temporary dragon expression / animation.

### Closed-curtain transitions

Prepare before commit:

- full theme swap;
- compact ↔ immersive layout;
- companion avatar / dragon form change;
- major sidebar architecture changes;
- accessibility density mode;
- large responsive breakpoint reflow.

---

## 4. Main chat — compact default

### Desktop

```text
┌───────────────────────────────────────────────────────────────┐
│ crest §wyrlz    thread title          model      ○ ready   ☰ │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                    conversation column                        │
│                                                               │
│  dragon avatar  §wyrlz                                        │
│  response text                                                 │
│  [copy] [retry] [branch] [more]                               │
│                                                               │
│                                 user bubble                    │
│                                                               │
│  tool / approval / source cards appear inline only as needed   │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ +  Message §wyrlz…                 mode/model       send/stop │
└───────────────────────────────────────────────────────────────┘
```

Conversation width should stay approximately 680–780 px for normal prose. Large artifacts can expand into a temporary wide mode.

### Mobile

Keep only:

- menu / thread access;
- current thread title;
- tiny model/status affordance;
- conversation;
- one-line composer expanding upward;
- attach / send / stop.

Settings use bottom sheets / full-height drawer, not stacked dashboard panels in the chat viewport.

---

## 5. Message anatomy

### User message

- user avatar optional;
- display name optional;
- message text;
- attachment chips;
- edit / copy / branch on long-press or hover;
- timestamp hidden by default.

### §wyrlz message

- dragon kompanion mark;
- §wyrlz identity;
- response body;
- optional source row;
- compact actions;
- optional expandable execution details.

### Streaming

Show three distinct states:

1. **Listening / accepted** — request acknowledged.
2. **Thinking / generating** — subtle kompanion animation + textual status.
3. **Acting** — explicit tool/research/action card.

Do not visually conflate model thought with tool execution.

---

## 6. Composer

Default composer stays calm.

Primary controls:

- attachment;
- textarea;
- send;
- stop while generating.

Secondary controls behind a compact affordance:

- model;
- reasoning / effort;
- research/web;
- tools;
- temporary chat / no-memory mode;
- voice when supported;
- generation preset.

Optional slash command surface:

```text
/model
/research
/memory
/lore
/temporary
/export
/settings
```

Slash commands should be discoverable, not required.

---

## 7. Navigation + drawer

### Upper block

- §wyrlz kompanion identity;
- current account;
- New Chat;
- Search chats.

### Thread block

- pinned;
- recent;
- archived;
- rename;
- duplicate/fork;
- delete;
- multi-select.

### Product block

- Companion;
- You;
- Lore & Memory;
- Models;
- Appearance;
- Settings.

### Engineering / advanced block

Hidden by default:

- runtime versions;
- diagnostics/cameras;
- route/source identity;
- export evidence;
- developer controls.

This prevents engineering receipts from competing with ordinary-user tasks.

---

## 8. Settings information architecture

### General

- language;
- enter-to-send;
- compact/comfortable density;
- open last thread;
- link behavior;
- default download/export format.

### AI / Model

- default model;
- automatic model selection;
- reasoning/effort preset;
- max response length preference;
- creativity vs precision preset;
- context/history budget;
- tool use default;
- research/web default;
- citation preference;
- code verbosity;
- streaming on/off.

Guardrails:

- advanced sampling values (temperature/top-p/etc.) remain in Advanced;
- show user-friendly presets first.

### Conversation

- default response style;
- markdown rendering;
- code block behavior;
- auto-title chats;
- suggestions/follow-ups;
- auto-scroll;
- keep composer draft per thread;
- branch/retry behavior.

### Companion — §wyrlz

User-editable companion identity:

- name;
- title;
- pronouns / grammatical presentation;
- species/form (Glitch Dragon default);
- avatar / crest;
- voice;
- speaking style;
- humor intensity;
- warmth;
- directness;
- formality;
- verbosity;
- initiative;
- emoji usage;
- mythology / lore density;
- preferred relationship framing.

**AI-owned self-lore proposal model:**

The AI may *propose* changes to its own profile/lore when a stable pattern emerges.

Proposal card:

```text
§wyrlz noticed a possible identity update

Current:
  "Glitch Dragon Kompanion"

Proposed:
  add "Archivist of the shared project lineage"

Why:
  repeated project role across 14 conversations

[Approve] [Edit] [Not now] [Never infer this category]
```

No AI self-profile mutation silently commits durable state.

### You — User profile

User-controlled:

- display name / nickname;
- pronouns if desired;
- role / work;
- communication preferences;
- recurring projects;
- expertise areas;
- learning style;
- output preferences;
- accessibility preferences;
- optional personal lore / persona layer.

Separate ordinary profile facts from creative lore.

### Lore & Memory

Four explicit stores:

1. **User Facts**
   - durable factual preferences/context.
2. **User Lore**
   - chosen narrative/persona/worldbuilding.
3. **§wyrlz Self Lore**
   - companion identity/history/traits.
4. **Shared Lore / Rapport**
   - shared callbacks, project mythology, relationship conventions.

Every durable entry includes:

- title;
- content;
- type;
- source;
- confidence;
- created/updated time;
- scope;
- who authored it;
- editable flag;
- active / paused;
- delete;
- history.

### AI-proposed memory flow

```text
conversation signal
  ↓
candidate memory / lore
  ↓
AI evaluates durability + scope
  ↓
proposal only
  ↓
user approves / edits / rejects
  ↓
durable profile state
```

The user can choose policy per category:

- Ask every time;
- Auto-save low-risk preferences;
- Never save automatically;
- Session only.

For **AI self-lore**, the default should still be proposal-first so the companion can grow without becoming self-authorizing durable identity state.

### Rapport controls

Rapport is not a single hidden score.

Expose dimensions such as:

- familiarity;
- preferred humor;
- shared vocabulary;
- callback frequency;
- user correction history;
- working-style alignment;
- creative-lore continuity.

Allow reset/pause per dimension.

Never imply emotional dependency or exclusivity.

### Privacy & Data

- memory enabled;
- lore enabled;
- chat history;
- temporary chat default;
- export;
- delete data;
- retention;
- connected services;
- local-only / server-backed mode when available;
- whether conversation data may be used for profile proposals.

### Appearance

- theme: Glitch Dragon / Ice Dragon / Void / High Contrast / Minimal;
- accent;
- background art intensity;
- glass/transparency;
- particles;
- scan/glitch intensity;
- message density;
- avatar size;
- composer compactness;
- code theme;
- font scale.

### Motion

Independent controls:

- full / reduced / off;
- kompanion breathing;
- idle particles;
- response arrival;
- glitch transitions;
- background parallax;
- typing / generation pulse.

Honor OS `prefers-reduced-motion` by default.

### Accessibility

- contrast mode;
- text scale;
- reduced transparency;
- reduced motion;
- screen-reader streaming announcements;
- keyboard shortcuts;
- focus visibility;
- dyslexia-friendly font option;
- sound/haptic toggles.

### Advanced

- generation sampling;
- context window strategy;
- profile injection budget;
- memory retrieval budget;
- debug source identity;
- camera mode;
- export trace;
- feature flags.

---

## 9. Profile and lore architecture

The repository already has a durable account profile shape:

```text
UserProfileRecord
  display_name
  preferences
  model_preferences
  ui_preferences
```

Do not create a competing user profile store.

Extend the existing profile authority intentionally.

Recommended evolution:

```text
preferences
  ├─ communication
  ├─ output
  ├─ stable_user_facts
  ├─ user_lore
  └─ rapport_preferences

model_preferences
  ├─ default_model
  ├─ effort
  ├─ response_length
  ├─ tools
  └─ context_policy

ui_preferences
  ├─ theme
  ├─ density
  ├─ motion
  ├─ accessibility
  └─ composer

companion_profile
  ├─ identity
  ├─ style
  ├─ self_lore
  └─ version

shared_rapport
  ├─ vocabulary
  ├─ callbacks
  ├─ interaction_preferences
  └─ approved_shared_lore
```

If `companion_profile` and `shared_rapport` become independently versioned durable structures, establish them through architecture reconciliation rather than hiding them inside arbitrary UI state.

---

## 10. AI-driven configuration contract

### Allowed without approval

Ephemeral/session presentation adjustments:

- temporary response verbosity inside a conversation;
- collapsing irrelevant execution details;
- choosing a transient expression animation;
- temporary tool-status presentation;
- recommending a setting.

### Approval required before durable mutation

- user profile facts;
- user lore;
- companion self-lore;
- rapport rules;
- default model;
- privacy;
- retention;
- enabled tools;
- UI accessibility settings;
- notification behavior.

### Proposed mutation envelope

```json
{
  "proposalId": "...",
  "target": "user_profile | companion_profile | shared_rapport | ui_preferences | model_preferences",
  "operation": "add | update | remove",
  "path": "...",
  "currentValue": null,
  "proposedValue": "...",
  "reason": "...",
  "scope": "global | project | thread",
  "confidence": 0.0,
  "requiresApproval": true
}
```

The UI owns approval. The AI cannot bypass it by writing directly to durable profile state.

---

## 11. Glitch dragon motion language

Motion should communicate state.

### Idle

- slow 6–10 s luminance breathing;
- tiny particle drift;
- optional eye/crest pulse;
- no layout movement.

### User typing

- kompanion subtly wakes;
- crest brightens;
- particles converge slightly.

### Request accepted

- one short ring/scale pulse around avatar;
- 120–220 ms.

### Thinking

- low-frequency breathing;
- small rotating glyph fragment or scale pattern;
- no indefinite spinner if textual progress exists.

### Tool / research

- thin data-path line or segmented arc appears near the tool card;
- status-specific color.

### Response begins

- first token causes one subtle glitch-resolve animation;
- subsequent tokens render normally.

### Error

- one controlled fracture/glitch;
- then stable error card;
- do not strobe.

### Approval request

- dragon crest + card edge pulse slowly until resolved;
- no intrusive modal unless the action is consequential.

---

## 12. Sci-fi interaction motifs that are actually useful

Use:

- segmented edge progress for generation;
- dragon-scale clipped corners for panels;
- rune/glyph markers for profile/lore categories;
- signal bars for model/runtime status;
- restrained scan reveal for opening a drawer;
- constellation-style relationship map only in the dedicated Lore/Rapport screen.

Do not use:

- circular knobs for model selection;
- radar maps for chat history;
- animated waveform for static text;
- fake coordinates;
- constant terminal logs in user view.

---

## 13. Tool / agent action cards

When §wyrlz performs work:

```text
┌ Search web — 6 sources
│ researching chat-interface accessibility patterns
│ [show details] [stop]
└
```

For consequential actions:

```text
┌ Approval required
│ §wyrlz wants to update your default response style:
│ Concise → Adaptive
│ [Approve] [Edit] [Decline]
└
```

Keep tool internals collapsed unless the user opens them.

---

## 14. First-run onboarding

Maximum 4–5 small stages:

1. Choose display name.
2. Choose §wyrlz appearance / voice / vibe.
3. Pick response style.
4. Choose memory/lore policy.
5. Optional import / sign-in / skip.

Do not force users through detailed model knobs before first chat.

---

## 15. Empty / new chat state

Avoid a dashboard.

Show:

- kompanion;
- compact greeting;
- 3–4 starter actions;
- composer.

Example starter actions:

- Ask anything
- Build something
- Research
- Configure §wyrlz

Once the first message is sent, starter UI disappears completely.

---

## 16. Search and history

Global chat search:

- semantic + exact text;
- filter by date;
- model;
- attachments;
- project;
- pinned;
- lore-relevant chats.

Search opens as a focused overlay/drawer, not permanent chat chrome.

---

## 17. Artifacts / large outputs

For code, long documents, diagrams, and reports:

- inline preview card;
- expand into right-side work surface on desktop;
- full-screen sheet on mobile;
- conversation remains available;
- closing artifact returns to same scroll location.

Do not widen every normal response because artifacts exist.

---

## 18. Performance budget

The visual identity must not damage first-token/chat responsiveness.

Rules:

- no WebGL requirement for baseline chat;
- decorative particles use bounded CSS/canvas budget and suspend in background tabs;
- background image optimized/responsive;
- avoid blur stacks on every message;
- limit `backdrop-filter` surfaces;
- animations use transform/opacity;
- no layout-changing typing animation;
- large settings/lore views lazy-load;
- diagnostics never execute just because their panel is hidden.

---

## 19. Accessibility acceptance

Must pass:

- keyboard-only operation;
- visible focus;
- semantic landmarks;
- screen-reader labels;
- polite streaming announcements;
- body-text AA contrast;
- reduced-motion;
- zoom/text scaling;
- mobile keyboard does not cover composer/latest response;
- no meaning encoded only by glow/color.

---

## 20. Recommended implementation tiers

### Tier A — visual foundation

- tokenized theme variables;
- compact top edge;
- drawer visual refresh;
- composer refinement;
- message action polish;
- reduced-motion baseline.

### Tier B — settings shell

- settings route/sheet;
- General;
- AI/Model;
- Appearance;
- Motion;
- Accessibility;
- Privacy.

### Tier C — profile + lore UI

- You;
- §wyrlz;
- Lore & Memory;
- inspect/edit/delete;
- scope + provenance;
- proposal inbox.

### Tier D — approval protocol

- durable setting/profile proposal schema;
- approve/edit/decline;
- audit/history;
- per-category auto-save policy.

### Tier E — rapport

- shared vocabulary/callback management;
- approved rapport state;
- project/thread scope;
- reset/pause.

### Tier F — companion animation state machine

- idle;
- listen;
- accepted;
- thinking;
- acting;
- responding;
- approval;
- error;
- reduced-motion equivalents.

### Tier G — artifacts + agent cards

- tool/action cards;
- side work surface;
- approval cards;
- source/evidence expansion.

---

## 21. Acceptance criteria

A successful §wyrlz Glitch Dragon Chat should satisfy all of these:

- the main chat feels simpler than the settings system;
- a first-time user can send a message without understanding any advanced setting;
- the dragon aesthetic is obvious without reducing readability;
- every animation has a state purpose;
- user profile, user lore, AI lore, and shared rapport are distinct concepts;
- durable AI/user profile changes are inspectable and reversible;
- AI-originated durable changes require the configured approval policy;
- the existing account/profile authority is reused rather than duplicated;
- engineering/runtime diagnostics remain available but backstage;
- mobile remains a first-class layout;
- reduced-motion/high-contrast use remains fully functional;
- Chat/LALM performance measurements do not regress due to visual decoration.

---

## 22. Product principle

**The stage stays simple. The dragon gets deep.**

Conversation is the foreground.
Settings are backstage.
Lore is inspectable continuity.
Rapport is shared state, not hidden magic.
The AI may notice and propose growth, but the user remains sovereign over durable changes.
