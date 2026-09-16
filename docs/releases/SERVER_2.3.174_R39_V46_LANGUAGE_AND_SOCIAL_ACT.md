# Server 2.3.174 — R39 v46 language preference + social-act repetition

**Server Runtime:** 2.3.174  
**LALM Engine:** 2.1.57 / `2.1.57-hot-social-act-language-preference-v46`  
**Web Chat:** 1.5.35  
**Runtime page manifest:** 103  
**Deployment:** NONE  
**Restart:** NONE

## Purpose

Add an explicit user-controlled profanity preference to Chat settings and improve the Brain's repetition reasoning so surface wording changes inside a greeting/check-in sequence no longer reset contextual recognition.

## Architecture

- Mask: stores and relays the factual language preference only. Default is `clean`; explicit opt-in is `allowed`.
- Brain: owns contextual language choice and greeting/check-in interpretation.
- Server/body: unchanged.
- The setting permits profanity when enabled; it does not command or force profanity.
- Clean is fail-closed/default when preference metadata is absent or malformed.

## LALM behavior

R39 v46 preserves v45 exact repetition evidence and adds a separate bounded conversational-act signal for common greeting/check-in forms such as hello/hey/hi, good morning/afternoon/evening/night, what's up/going on, and how-are-you/how-is-it-going variants. It tracks contiguous user greeting/check-in acts through canonical history while retaining the original surface text.

This is intentionally scoped. It is not a claim of arbitrary semantic equivalence across all prompts. Non-social turns continue through the prior inference path.

For the normal inference path, the explicit language preference is introduced inside the Brain's input context as a user language-style constraint. Social fast paths remain clean by default and do not force profanity when permission is enabled.

## Chat behavior

`web/chat_language_preferences_v1.js` adds a Language style control inside the existing Chat settings dialog:

- Clean language — default.
- Profanity allowed — explicit permission for contextual use.

The preference is stored locally and attached as factual `userPreferences.profanity` metadata to protocol-v2 Chat turn requests. It is not treated as Chat-side cognition.

## Lineage

Baseline authorities before mutation and again at version assignment boundary:
- Server Runtime 2.3.173
- LALM Engine 2.1.56 / v45
- Web Chat 1.5.34
- VERSION.txt registry format 2

Relevant commits:
- Chat language preference relay: `4c80bafa7091259aef9081831ed2690d0801d1b9`
- R39 v46 source: `4bc9eda49bd5953345467ab6174e54b4faed79fa`
- Hot loader: `17a78f51a70054e0a00d4e2336d13ac273b78e5f`
- Runtime page manifest 103: `70a0c9a36d7cbf7d03c98da92691fb0f1aa6ad17`
- Hot inference manifest: `88e4f55a6814f8055177a8b47e8065c6c9d25348`
- Server authority: `14c3ac7a9529934d4526b07a645ae774701f9237`
- LALM authority: `677ad5a260464516bdf2109b1f9cccf878a4c5ea`
- Web Chat authority: `9d40e599e3c715d3664d891075aab8b076f930f6`

## Verification state

Repository/source and authority verification required after this receipt. Live runtime acceptance requires confirming manifest 103, R39 v46 engine inspection/cameras, clean default preference relay, explicit allowed preference relay, and a mixed-surface greeting sequence. No Vercel deployment or restart was requested or performed.
