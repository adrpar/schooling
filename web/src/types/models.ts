/**
 * src/types/models.ts
 * Type-safe models mapped directly from the OpenAPI generated schema.
 */

import type { components } from '../api/generated/schema';

export type SheetSpec = components['schemas']['SheetSpec'];
export type ExerciseBlockSpec = components['schemas']['ExerciseBlockSpec'];
export type ExerciseType = components['schemas']['ExerciseType'];
export type HeaderSpec = components['schemas']['HeaderSpec'];
export type CatalogExerciseItem = components['schemas']['CatalogExerciseItem'];
export type CatalogExerciseParam = components['schemas']['CatalogExerciseParam'];
export type BlockPreviewRequest = components['schemas']['BlockPreviewRequest'];
export type BlockPreviewResponse = components['schemas']['BlockPreviewResponse'];
export type SheetSummary = components['schemas']['SheetSummary'];

export interface CanvasPoint {
  x: number;
  y: number;
}

export interface CanvasDimensions {
  width: number;
  height: number;
}
