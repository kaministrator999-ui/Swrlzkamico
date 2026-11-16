"""§E v11.472 — preserve imported texture resolution, optional GPU downscale."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_472_FULL_RES_TEXTURES'

def once(src,old,new,label):
    count=src.count(old)
    if count!=1:raise AssertionError(('v11.472 source anchor',label,count,old[:130]))
    return src.replace(old,new,1)

def apply(html):
    for token in (
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE',
        'async function se336ImportPaint(file)',
        'part.uvPaintPNG.length <= 360000',
        'SE471_UV_FINE_FIT_START',
        'SE469_UV_SHAPE_FIT_START',
        'function se336InstallUI()',
        'function se336UpdateUI()',
        'function ensurePanel(){',
    ):assert token in html,token
    # Keep all previous validation layers; remove the outdated 360K baked PNG
    # cap. The actual import still enforces the existing 5 MB file size limit.
    html=once(html,'part.uvPaintPNG.length <= 360000',
              'part.uvPaintPNG.length <= 7000000',
              'native mesh schema source-length cap')
    html=once(html,r'^data:image\/png;base64',
              r'^data:image\/(?:png|jpeg);base64',
              'accept original PNG and JPEG data URLs')
    html=once(html,
              'Cyan guide lines are cleaned when detected; large images are resized for model saves.',
              'Importing preserves original pixels and image dimensions. Optional viewport sizes only affect GPU sampling.',
              'native guide description')
    script=(ROOT/'runtime/texture_full_resolution_v11_472.js').read_text('utf8')
    styles=(ROOT/'runtime/texture_full_resolution_v11_472.css').read_text('utf8')
    assert 'SE472_NATIVE_TEXTURE_RESOLUTION_START' in script
    assert 'SE472_NATIVE_TEXTURE_RESOLUTION_STYLES_START' in styles
    html=once(html,'  function ensurePanel(){',script+'\n  function ensurePanel(){',
              'native model studio texture extension')
    assert html.index('</head>')<html.index('<body'),'invalid HTML head'
    html=html.replace('</head>','<style id="se472TextureResolutionStyles">\n'+styles+
        '\n</style>\n</head>',1)

    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE',MARKER),
        ('ENGINE · MAKER v11.471','ENGINE · MAKER v11.472'),
        ('v11.471 · visible UV texture and project delete','v11.472 · preserve original imported textures'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.471'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.472'"),
        ('<title>§wyrl§ Engine · Maker v11.471</title>',
         '<title>§wyrl§ Engine · Maker v11.472</title>')
    ]:html=once(html,old,new,'release marker '+old[:40])
    prior=" source.engine='§wyrl§ Engine · Maker v11.471';source.version=11.471;"
    assert html.count(prior)==5,('model save provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.472';source.version=11.472;")
    key='const SE_RELEASE_NOTES='
    offset=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[offset:])
    notes['history']=[row for row in notes.get('history',[]) if row.get('version')!='v11.471']
    notes['history'].insert(0,{'version':'v11.471','changes':notes.get('changes',[])})
    notes.update(version='v11.472',date='2026-11-16',
      title='Original imported UV texture resolution with explicit display-size presets',
      changes=[
       'PNG and JPEG import preserve the exact original source bytes, dimensions and aspect ratio, with no automatic 512/384/320/256/192 resave.',
       'The existing model part schema accepts 5 MB imported original images as PNG or JPEG data URIs, instead of the legacy 360K-character lossy save workaround.',
       'The native UV Editor adds Original (default), 4096, 2048, 1024, 512, and 256 as explicit GPU viewport maximum-dimension choices, without upscaling.',
       'Changing viewport resolution keeps the imported full-resolution image in the saved model so switching back to Original restores all original detail.',
       'The UV Editor shows imported dimensions, source format/size, and effective viewport dimensions; UV fit, latitude, geometry, and original source remain independent.',
       'Color maps use sRGB, mipmaps and bounded anisotropy. Imported textures are never silently resized or stripped of cyan guide pixels.',
       'Existing saved 256px paintings remain readable, but recovering lost pixels requires reimporting the original high-resolution image.',
       'The model and account project save size limits still apply and failures report explicitly rather than altering artwork; device/VR acceptance awaits owner testing.'
      ])
    return html[:offset]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[offset+n:]
