# Server Runtime 2.3.41

## Modules
- Server Runtime: 2.3.41
- Web Chat: 1.4.36
- LALM Engine: 2.1.25 (unchanged)

## Change
The generated Ice Dragon juvenile companion and adult guardian artwork no longer uses nested JPEG-inside-SVG wrappers. Android Chrome rendered the juvenile brand asset as a broken-image glyph. The generated JPEGs are now stored as browser-safe base64 text assets and hydrated at runtime by `ice-dragon-art-loader.js`, which assigns data-URI CSS variables for the companion badge/avatar and adult Chat background.

The Chat boot reveal now waits up to 700 ms for Ice Dragon art hydration when Ice Dragon is the saved theme. The existing global 1.8-second boot fail-open remains in place, preventing a failed art load from trapping the interface behind the hydration surface.

## Verification state
- Runtime source and manifest updated.
- Browser screenshot acceptance pending after refresh.
- LALM behavior unchanged.

## Deployment
- Vercel deployment: none required (runtime-hot change).
- Server restart: none required.

## Relevant lineage
- Companion base64 asset: `3e3db01d20249ef5f8185e3c538fdce72d332d9a`
- Adult base64 asset: `32a8b0a71cb2d55ddb54347701db45a7d891e932`
- Art CSS transport fix: `ca95bde2da1a9cac0c747d49d4ba3a902e9324cc`
- Art hydration loader: `ce7f10fe1ae249aabe76be722cac24bf3f597e24`
- Runtime manifest wiring: `ad3eca059519a13b8fcb27e6af0e00f3d9d70403`
- Boot reveal integration: `8b0ac2a7b6ffec2023a12d3572e97606c9ba07eb`
- Server version authority: `0fedb8501f6e6aadebcc003d9625d8b0dd29608f`
- Chat version authority: `44182cfb8cec58f687c0d47547a27df3df6502ec`
