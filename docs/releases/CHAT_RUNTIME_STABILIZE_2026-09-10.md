# Chat runtime stabilization — 2026-09-10

Restore production main to the known-good Chat runtime-controller baseline after the temporary dev hot-runtime routing experiment.

- Main baseline: `e8fa96daa7958776396c11417cc04bcd0196fc1f`
- Hot Chat runtime branch: `runtime`
- Runtime Chat restore point: `64c53999aa374c589bf2692e12db57ca133ab21c`
- Purpose: keep Chat and the hot inference runtime on the same durable runtime branch and avoid the remote dev v34 loader path.
