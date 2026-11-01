"""§E v11.197 — remove meadow texture moiré, stabilize team fog
and remove per-frame full status snapshots in the flat Sheep Tag camera.

Append-only; preserve every prior patch, independent game and save data.
"""
from pathlib import Path
import json

def once(s,a,b):
    found=s.count(a)
    if found!=1:raise AssertionError(('v11.197 anchor',a[:180],found))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    # The original meadow texture draws a repeated 1-pixel grid every 30.72 px.
    # At Quest's oblique/low-resolution view it creates moire and temporal
    # crawling even after the independent fog depth-buffer fix v11.196.
    html=once(html,
      "    c.strokeStyle='#d6ddb817';c.lineWidth=1;\n"
      "    for(let p=512%30.72;p<1024;p+=30.72){c.beginPath();c.moveTo(p,0);c.lineTo(p,1024);c.stroke();c.beginPath();c.moveTo(0,p);c.lineTo(1024,p);c.stroke();}",
      "    // No subpixel repeating grid: fine alternating lines shimmer when the meadow is minified.")
    html=once(html,
      "const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;\n"
      "    const ground=new THREE.Mesh(new THREE.PlaneGeometry(80,80)",
      "const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;"
      "texture.minFilter=THREE.LinearMipmapLinearFilter;texture.magFilter=THREE.LinearFilter;"
      "texture.generateMipmaps=true;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());\n"
      "    const ground=new THREE.Mesh(new THREE.PlaneGeometry(80,80)")
    # New starters use the 4K original Wildwood texture, not the older 1024
    # meadow canvas. Prefilter its 1px grass details to 2048 only on Quest,
    # before WebGL uploads. Keep full-resolution original source untouched.
    html=once(html,
      "stWildwoodGroundTexture=new THREE.TextureLoader().load('assets/sheep-tag/moonbell-wildwood-ground-4k.jpg');",
      """stWildwoodGroundTexture=new THREE.TextureLoader().load('assets/sheep-tag/moonbell-wildwood-ground-4k.jpg',function(texture){
   if(!/(?:OculusBrowser|Quest)/i.test(navigator.userAgent||''))return;
   const source=texture.image;
   if(!source||!(source.naturalWidth||source.width)||(source.naturalWidth||source.width)<=2048)return;
   const canvas=document.createElement('canvas');canvas.width=canvas.height=2048;
   const ctx=canvas.getContext('2d');
   if(!ctx)return;
   ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
   ctx.drawImage(source,0,0,canvas.width,canvas.height);
   texture.image=canvas;texture.needsUpdate=true;
   texture.userData.se197QuestDownsampled=true;
  });""")
    html=once(html,
      "stWildwoodGroundTexture.colorSpace=THREE.SRGBColorSpace;",
      "stWildwoodGroundTexture.colorSpace=THREE.SRGBColorSpace;"
      "stWildwoodGroundTexture.minFilter=THREE.LinearMipmapLinearFilter;"
      "stWildwoodGroundTexture.magFilter=THREE.LinearFilter;"
      "stWildwoodGroundTexture.generateMipmaps=true;")
    js=(root/'runtime/sheep_visual_stability_v11_197.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_196_SHEEP_FOG_RADIAL_CAMERA_RECOVERY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_197_MEADOW_FOG_CAMERA_STABILITY'),
      ('ENGINE · MAKER v11.196','ENGINE · MAKER v11.197'),
      ('v11.196 · Sheep Tag fog and Quest menu/camera recovery',
       'v11.197 · Sheep Tag meadow and fog rendering stabilization'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.196'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.197'"),
      ('<title>§wyrl§ Engine · Maker v11.196</title>',
       '<title>§wyrl§ Engine · Maker v11.197</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag texture aliasing, multiplayer fog paint and browser performance follow-up',
      date='2026-10-31',changes=[
      'Remove the old 1024px meadow periodic crosshatch and explicitly mipmap both that surface and the actual 4K Moonbell Wildwood starter texture; on Quest Browser prefilter Wildwood to a 2048px texture before GPU upload without altering its original art or desktop resolution.',
      'Prevent the solo translucent fog painter from overwriting the independent LAN/team fog visual layer between remote world frames. LAN team visibility computation and orders remain untouched.',
      'Replace the normal Sheep Tag camera per-frame stStatus serialization with direct controlled/selected native actor position tracking, while keeping the native camera angle, zoom, WASD pan and selection rings.',
      'Preserve v11.196 anchored legible Quest radial, one-time camera positioning, screen captures, previous map/editor/project versions, other game starters, modeler and §C. Quest 2 long-run stereo performance still needs hardware acceptance.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
