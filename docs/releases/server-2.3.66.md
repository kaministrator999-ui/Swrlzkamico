# Server 2.3.66 — Ice Dragon adult wallpaper source repair

Date: 2026-09-11/12
Branch: `runtime`
Deployment: none
Restart: none

## Trigger evidence

The exported Ice Dragon diagnostics proved the v13 single-flight hydrator was active, but the adult wallpaper source itself remained invalid. The new trace reported `adult rawChars=7713` followed by `adult base64 length invalid after normalization (7713)`, while the companion continued to load successfully.

## Root cause

The repository asset `web/themes/ice-dragon/assets/adult-180x320.jpg.b64` was corrupted. A Base64 payload with 7713 significant characters is structurally impossible (`length % 4 == 1`), so the browser failure was upstream of CSS, DOM placement, painting, and cache behavior.

## Repair

- Recovered the exact intended adult Ice Dragon source artwork from the project/user Library (`32841.png`, 864x1536).
- Rebuilt it as an aspect-preserving 180x320 JPEG.
- Verified the rebuilt JPEG locally before encoding.
- Replaced the corrupt `.b64` payload with valid Base64 whose encoded length is divisible by four.
- Kept the v13 single-flight hydrator unchanged because its concurrency behavior was verified by the new logs.

## Failure lineage preserved

An intermediate asset replacement commit accidentally wrote a placeholder string to the adult payload path. It was detected immediately and corrected in the next commit before acceptance. This failed intermediate state remains in Git history rather than being rewritten away.

## Version authority

- Server runtime: `2.3.65` -> `2.3.66`
- Web Chat: `1.4.59` -> `1.4.60`

## Relevant lineage

- Intermediate placeholder write: `4b0ff408f68e5f2ade8c2005e255837a8c8f1014`
- Correct rebuilt adult payload: `08f9af180e8714a935a8a57c27624c0794d443ed`
- Server version authority: `6626332198a7ce61a4d4f67c79a98c2fd95a200b`
- Chat version authority: `ea16fe9fd0b6d23d9018dd21b639edbcb95adc4c`

## Acceptance gate

The live adult payload must return from the `runtime` source, normalize without error, decode as a 180x320 JPEG, and produce `adult-decode-ok` followed by `adult-painted` in the in-product theme diagnostics.
