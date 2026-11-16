// §E v11.472 assembled source contract: full-resolution import dominates old auto-resize.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const html=fs.readFileSync(process.argv[2],'utf8');
const required=[
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE',
 'SE472_NATIVE_TEXTURE_RESOLUTION_START',
 'SE472_NATIVE_TEXTURE_RESOLUTION_STYLES_START',
 'part.uvPaintPNG.length <= 7000000',
 'se336ImportPaint=async function(file){',
 'part.uvPaintPNG=source;',
 'part.uvPaintMaxSize=0;',
 'part.uvPaintSourceW=w;part.uvPaintSourceH=h;part.uvPaintSourceBytes=file.size;',
 'const source=await se472ReadFile(file);',
 'const [w,h]=await se472DecodeDimensions(source);',
 'const size=se472DisplaySize(part)',
 'const preview=se472ApplyFiltering(new THREE.Texture())',
 'tex.anisotropy=Math.max(1,Math.min(8,limit))',
 "const select=root.querySelector('#se472DisplayResolution')",
 'id="se472DisplayResolution"',
 'Original (full resolution)',
 'Up to 4096','Up to 2048','Up to 1024','Up to 512','Up to 256',
 'source stored unmodified',
 'se356UVPreviewSchedule()',
 'checkpoint()',
 'No resizing or guide removal',
 'Texture PNG and geometry positions unchanged.',
 'SE471_UV_FINE_FIT_START',
 'SE469_UV_SHAPE_FIT_START'
];
for(const token of required)assert(html.includes(token),'Missing full-resolution contract: '+token);
assert(html.includes('image\\/'), 'Native image URI should use an escaped slash in the regex');
const legacy=html.indexOf('async function se336ImportPaint(file)');
const override=html.indexOf('se336ImportPaint=async function(file){',html.indexOf('SE472_NATIVE_TEXTURE_RESOLUTION_START'));
assert(override>legacy,'New import must override the old 512 to 192 pixel loop');
const fragment=html.slice(override,html.indexOf('const se472PriorRemovePaint=',override));
assert(!fragment.includes('canvas.toDataURL('),'Original import may not re-encode source via canvas');
assert(!fragment.includes('se336StripCyanGuide('),'Original import may not silently strip artwork');
assert(!fragment.includes('for (const size of [512, 384, 320, 256, 192])'),'Old fallback must be unreachable');
assert(fragment.includes('source.length>7_000_000'),'Explicit oversize error');
assert(fragment.includes('source=await se472ReadFile(file)'));
const sourceIndex=fragment.indexOf('const source=await se472ReadFile(file)');
const persistIndex=fragment.indexOf('part.uvPaintPNG=source;');
assert(sourceIndex>=0&&persistIndex>sourceIndex);
const materialStart=html.indexOf('material=function(part){',html.indexOf('SE472_NATIVE_TEXTURE_RESOLUTION_START'));
const materialEnd=html.indexOf('function se472ReadFile(',materialStart);
const material=html.slice(materialStart,materialEnd);
assert(material.includes('if(!selected||!size||'),'Original must be default, not optional resize');
assert(material.includes('return mat; // Always bind original pixels by default'));
assert(material.includes('preview.image=canvas;preview.needsUpdate=true'));
console.log('SE472_FULL_RES_INTEGRATION_PASS: native importer, original PNG/JPEG source, optional GPU size, inherited UV tools');
