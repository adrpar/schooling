/**
 * src/utils/coordinates.ts
 * Coordinate translation and snapping utilities between screen pixels and A4 sheet millimeters.
 */

export const PAGE_WIDTH_MM = 210.0;
export const PAGE_HEIGHT_MM = 297.0;

export const DEFAULT_MARGIN_MM = 10.0;

/**
 * Clamps a value between min and max bounds.
 */
export function clamp(val: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, val));
}

/**
 * Snaps a coordinate in millimeters to the nearest grid step.
 */
export function snapToGrid(valMm: number, stepMm: number = 5.0): number {
  if (stepMm <= 0) return valMm;
  return Math.round(valMm / stepMm) * stepMm;
}

/**
 * Converts screen pixel deltas (from mouse/touch events) to canvas millimeters.
 */
export function screenToCanvasMm(
  screenDeltaX: number,
  screenDeltaY: number,
  svgElement: SVGSVGElement
): { dxMm: number; dyMm: number } {
  const rect = svgElement.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) {
    return { dxMm: 0, dyMm: 0 };
  }
  const scaleFactor = PAGE_WIDTH_MM / rect.width;
  return {
    dxMm: screenDeltaX * scaleFactor,
    dyMm: screenDeltaY * scaleFactor,
  };
}

/**
 * Clamps block position (x, y) so it remains entirely within the printable A4 page bounds.
 */
export function clampBlockPosition(
  x: number,
  y: number,
  width: number,
  height: number,
  margin: number = 5.0
): { x: number; y: number } {
  const minX = margin;
  const minY = margin;
  const maxX = Math.max(minX, PAGE_WIDTH_MM - width - margin);
  const maxY = Math.max(minY, PAGE_HEIGHT_MM - height - margin);

  return {
    x: clamp(x, minX, maxX),
    y: clamp(y, minY, maxY),
  };
}

