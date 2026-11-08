import { describe, it, expect } from 'vitest';
import {
  clamp,
  snapToGrid,
  clampBlockPosition,
  PAGE_WIDTH_MM,
  PAGE_HEIGHT_MM,
} from '../utils/coordinates';

describe('Coordinates & Snapping', () => {
  it('clamps numbers within min and max', () => {
    expect(clamp(5, 10, 20)).toBe(10);
    expect(clamp(25, 10, 20)).toBe(20);
    expect(clamp(15, 10, 20)).toBe(15);
  });

  it('snaps values to specified mm grid step', () => {
    expect(snapToGrid(12.3, 5.0)).toBe(10.0);
    expect(snapToGrid(13.5, 5.0)).toBe(15.0);
    expect(snapToGrid(10.0, 5.0)).toBe(10.0);
    expect(snapToGrid(12.1, 2.5)).toBe(12.5);
  });

  it('clamps block position so it does not exceed A4 boundaries', () => {
    const width = 50;
    const height = 40;
    const margin = 5;

    // Inside bounds: stays unchanged
    const inside = clampBlockPosition(50, 50, width, height, margin);
    expect(inside.x).toBe(50);
    expect(inside.y).toBe(50);

    // Negative / off top-left: clamped to margin
    const offTopLeft = clampBlockPosition(-20, -10, width, height, margin);
    expect(offTopLeft.x).toBe(margin);
    expect(offTopLeft.y).toBe(margin);

    // Off bottom-right: clamped to page size minus dimensions minus margin
    const offBottomRight = clampBlockPosition(300, 400, width, height, margin);
    expect(offBottomRight.x).toBe(PAGE_WIDTH_MM - width - margin);
    expect(offBottomRight.y).toBe(PAGE_HEIGHT_MM - height - margin);
  });
});

