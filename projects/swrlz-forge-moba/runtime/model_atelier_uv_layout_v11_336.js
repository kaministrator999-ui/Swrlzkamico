// §E v11.336 UV guide extraction and mesh-bound painted PNG import.
// Model Atelier is the owner of the selected mesh and serialized model parts.
// This module is injected inside the existing ModelAtelier closure, not a second editor.
const se336BaseCheckPart = checkPart;
checkPart = function(part) {
  if (!se336BaseCheckPart(part)) return false;
  if (part.uvPaintPNG === undefined) return true;
  return typeof part.uvPaintPNG === 'string' &&
    part.uvPaintPNG.length <= 360000 &&
    /^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(part.uvPaintPNG);
};

const se336BaseMaterial = material;
material = function(part) {
  const result = se336BaseMaterial(part);
  if (typeof part.uvPaintPNG !== 'string' || !part.uvPaintPNG) return result;
  // A UV texture is color data. Do not multiply it by the part's old tint.
  const texture = new THREE.TextureLoader().load(part.uvPaintPNG);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = true; // Canvas PNG top edge corresponds to UV v=1.
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  result.map = texture;
  result.color.set('#ffffff');
  result.userData.se336PaintTexture = true;
  result.needsUpdate = true;
  return result;
};
const se336BaseWipe = wipeModel;
wipeModel = function() {
  if (modelRoot) for (const mesh of modelRoot.children) {
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const mat of mats) if (mat?.userData?.se336PaintTexture) mat.map?.dispose();
  }
  return se336BaseWipe.apply(this, arguments);
};

function se336SelectedMesh() {
  const part = partById(selection);
  const mesh = modelRoot?.children.find(x => x.isMesh && x.userData.atelierId === selection);
  return part && mesh ? {part, mesh} : null;
}
function se336UVLayout(mesh, canvas) {
  const g = mesh.geometry, uv = g?.getAttribute('uv');
  const position = g?.getAttribute('position'), index = g?.getIndex();
  if (!uv || !position || uv.count !== position.count)
    throw Error('This mesh has no complete UV coordinates. Create UVs before exporting.');
  const triangles = Math.floor((index?.count || position.count) / 3);
  if (!triangles || triangles > 180000)
    throw Error('UV mesh has no faces or exceeds the 180,000 triangle preview limit.');
  const ctx = canvas.getContext('2d');
  if (!ctx) throw Error('2D UV canvas unavailable.');
  const size = canvas.width;
  ctx.clearRect(0, 0, size, size);
  // Export a transparent guide: artists put this over a separate paint layer.
  // Do NOT export a baked white background or a screenshot of the 3D view.
  ctx.strokeStyle = '#21e6ec';
  ctx.lineWidth = Math.max(1, size / 512);
  ctx.lineJoin = 'round';
  const eps = 0.00001;
  for (let i = 0; i < triangles * 3; i += 3) {
    const pts = [];
    for (let j = 0; j < 3; j++) {
      const k = index ? index.getX(i + j) : i + j;
      const u = uv.getX(k), v = uv.getY(k);
      if (!Number.isFinite(u) || !Number.isFinite(v) ||
          u < -eps || u > 1 + eps || v < -eps || v > 1 + eps)
        throw Error('UV coordinates outside 0–1 need an atlas/repack before PNG extraction.');
      pts.push([Math.max(0, Math.min(1, u)) * size,
                (1 - Math.max(0, Math.min(1, v))) * size]);
    }
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    ctx.lineTo(pts[1][0], pts[1][1]);
    ctx.lineTo(pts[2][0], pts[2][1]);
    ctx.closePath();
    ctx.stroke();
  }
  return {triangles, vertices:uv.count};
}
function se336SaveCanvas(canvas, name) {
  const link = document.createElement('a');
  link.href = canvas.toDataURL('image/png');
  link.download = name.replace(/[^a-z0-9_.-]+/gi, '-').slice(0, 85);
  document.body.append(link);
  link.click();
  link.remove();
}
function se336ExportGuide() {
  try {
    const target = se336SelectedMesh();
    if (!target) throw Error('Select a model mesh first.');
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1024;
    const result = se336UVLayout(target.mesh, canvas);
    se336SaveCanvas(canvas, target.part.name + '-uv-guide.png');
    status('Exported true UV guide: ' + result.triangles + ' faces, ' +
      result.vertices + ' UV vertices. Paint on a separate layer; hide the guide before exporting your artwork.');
  } catch (error) { status('UV guide: ' + error.message, true); }
}
async function se336ImportPaint(file) {
  const original = se336SelectedMesh();
  if (!original || !file) { status('Select a model mesh first.', true); return; }
  if (!['image/png', 'image/jpeg'].includes(file.type) || file.size > 5000000) {
    status('Import a PNG/JPEG image up to 5 MB.', true); return;
  }
  const {part, mesh} = original, id = part.id;
  const probe = document.createElement('canvas');
  probe.width = probe.height = 512;
  try {
    // An import must target valid actual UVs; never silently project geometry.
    se336UVLayout(mesh, probe);
    const url = URL.createObjectURL(file), image = new Image();
    try {
      await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = () => reject(Error('Unable to decode texture.'));
        image.src = url;
      });
      if (image.naturalWidth > 4096 || image.naturalHeight > 4096 ||
          !image.naturalWidth || !image.naturalHeight)
        throw Error('Texture image dimensions are unsupported.');
      // The model stores texture PNGs in JSON. Keep the native save-size cap,
      // but reduce resolution when a detailed import would otherwise be rejected.
      let png = null, storedSize = 0;
      for (const size of [512, 384, 320, 256, 192]) {
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = size;
        const context = canvas.getContext('2d');
        if (!context) throw Error('2D texture canvas unavailable.');
        context.drawImage(image, 0, 0, size, size);
        const candidate = canvas.toDataURL('image/png');
        if (candidate.length <= 360000) {
          png = candidate; storedSize = size; break;
        }
      }
      if (!png)
        throw Error('Painted PNG exceeds the model save limit even at 192px. Simplify the artwork.');
      if (selection !== id || partById(id) !== part)
        throw Error('Selected mesh changed while the image was loading. Try again.');
      const before = part.uvPaintPNG;
      part.uvPaintPNG = png;
      const valid = checkPart(part);
      part.uvPaintPNG = before;
      if (!valid) throw Error('The native mesh schema rejected this texture.');
      checkpoint();
      part.uvPaintPNG = png;
      signalEdited();
      select(id);
      status('Painted PNG applied to ' + part.name + ' using its existing UV coordinates (' + storedSize + 'px saved texture). Save Project to keep it.');
    } finally { URL.revokeObjectURL(url); }
  } catch (error) { status('Texture import: ' + error.message, true); }
}
function se336RemovePaint() {
  const part = partById(selection);
  if (!part?.uvPaintPNG) return;
  checkpoint();
  delete part.uvPaintPNG;
  signalEdited();
  select(part.id);
  status('Removed UV texture from this mesh. Undo restores it.');
}
function se336UpdateUI() {
  const root = document.getElementById('modelAtelierUVLayout');
  if (!root) return;
  const target = se336SelectedMesh();
  root.querySelector('#se336UVName').textContent =
    target ? target.part.name : 'Select a mesh to extract its UV guide.';
  root.querySelector('#se336UVHasPaint').textContent =
    target?.part.uvPaintPNG ? 'Mapped PNG saved on selected mesh.' :
      'No imported painted texture on selected mesh.';
  for (const button of root.querySelectorAll('button'))
    button.disabled = !target || (button.id === 'se336UVRemove' && !target.part.uvPaintPNG);
}
function se336InstallUI() {
  if (!panel || document.getElementById('modelAtelierUVLayout')) return;
  const inspector = panel.querySelector('.atelier-inspector');
  if (!inspector) return;
  const root = document.createElement('section');
  root.id = 'modelAtelierUVLayout';
  root.className = 'se336-uv-layout';
  root.innerHTML =
    '<h3>🎨 UV Layout · image guide</h3>' +
    '<p id="se336UVName"></p>' +
    '<p class="se336-uv-hint">Export the actual mesh UV wireframe as a transparent 1024px PNG. Paint beneath that guide in an image editor, then import the artwork as PNG/JPEG (up to 5 MB). Large textures are resized to fit the model save format.</p>' +
    '<div class="se336-uv-actions"><button id="se336UVExport" type="button">Export UV guide PNG</button>' +
    '<button id="se336UVImport" type="button">Import painted PNG</button>' +
    '<button id="se336UVRemove" type="button">Remove texture</button></div>' +
    '<input id="se336UVFile" type="file" accept="image/png,image/jpeg" hidden>' +
    '<p id="se336UVHasPaint" class="se336-uv-hint"></p>';
  inspector.append(root);
  root.querySelector('#se336UVExport').addEventListener('click', se336ExportGuide);
  root.querySelector('#se336UVImport').addEventListener('click', () =>
    root.querySelector('#se336UVFile').click());
  root.querySelector('#se336UVRemove').addEventListener('click', se336RemovePaint);
  root.querySelector('#se336UVFile').addEventListener('change', async event => {
    const file = event.target.files?.[0];
    await se336ImportPaint(file);
    event.target.value = '';
  });
  se336UpdateUI();
}
const se336BaseEnsurePanel = ensurePanel;
ensurePanel = function() {
  const result = se336BaseEnsurePanel.apply(this, arguments);
  se336InstallUI();
  return result;
};
const se336BaseRefreshInspector = refreshInspector;
refreshInspector = function() {
  const result = se336BaseRefreshInspector.apply(this, arguments);
  se336UpdateUI();
  return result;
};
