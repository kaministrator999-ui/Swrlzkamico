/* SE295_CHAT_LOFT_SURFACE_NORMALS_START */
// The historical organic loft stores outward radial normals with inward
// triangle winding. Double-sided shading therefore lights its visible outer
// surface as an inside face. Correct only the plain lofts authored by Chat;
// saved descriptors and historical starter appearance remain unchanged.
const se295ChatLoftGeometryBase = geometry;
geometry = function (part) {
  const result = se295ChatLoftGeometryBase(part);
  if (part.kind !== 'loft' || !part.id?.startsWith('atelier-chat-') ||
      part.textureBinding || part.hdFinish || part.surfaceStyle || part.organicSurface ||
      !result?.index) return result;
  // Textured lofts already reverse their winding in the existing courier
  // wrapper. They bypass this branch, so no surface is reversed twice.
  const indices = result.index.array;
  for (let index = 0; index < indices.length; index += 3) {
    const next = indices[index + 1];
    indices[index + 1] = indices[index + 2];
    indices[index + 2] = next;
  }
  result.index.needsUpdate = true;
  result.computeVertexNormals();
  return result;
};
/* SE295_CHAT_LOFT_SURFACE_NORMALS_END */
