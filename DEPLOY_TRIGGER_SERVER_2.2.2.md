# Server 2.2.3 production deployment trigger

This file is intentionally changed only after the Server 2.2.3 repair batch is complete so the Vercel ignored-build gate admits one production build for the finished `main` tree.

Expected server version after deployment: `2.2.3`

Repair scope:
- Correct fp16 subnormal conversion in the compiled R39 native kernels. The previous exponent calculation produced exactly half-scale values for subnormal fp16 quantization scales.
- Add native/reference regression coverage using explicit subnormal quantization scales so the 1/2-scale bug cannot silently return.
- Preserve Hot R39 2.1.20 deep selection/prefill/decode diagnostics for production validation after the native extension rebuild.

Final trigger lineage includes native fix `16543ccc`, regression verifier `70f0f009`, and Server 2.2.3 entrypoint `e6e56eaf`.
