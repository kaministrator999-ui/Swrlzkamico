# Server Runtime 2.3.43

## Modules
- Server Runtime: 2.3.43
- Web Chat: 1.4.38
- LALM Engine: 2.1.25 (unchanged)

## Change
Ice Dragon adult guardian artwork is now applied directly to the live `.messages` chamber after runtime art hydration instead of relying only on inherited CSS variables and stylesheet background precedence. The baby companion remains used for the sidebar brand, welcome orb, and assistant avatars. Theme switching clears or reapplies the direct chamber background safely.

## Verification state
- Runtime source updated.
- Live browser visual acceptance pending.
- LALM engine unchanged.

## Deployment
- Vercel deployment: none required (runtime-hot change).
- Server restart: none required.

## Lineage
- Adult background loader fix commit: 7bcde3dbf95d63a467462431d1b78bd3763a16df
- Server Runtime version commit: e0d703645d9e4130e07463fc3c75c637e765493b
- Web Chat version commit: ba341549ca20aa8ba465735db4e4fb0098523b85
