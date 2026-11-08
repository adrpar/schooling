/**
 * src/exercises/types.ts
 * Core contract for modular exercise plugins.
 */

import React from 'react';
import type { CatalogExerciseParam } from '../types/models';

export interface ExerciseInspectorProps {
  params: Record<string, any>;
  onChange: (updatedParams: Record<string, any>) => void;
  schemaParams?: CatalogExerciseParam[];
}

export interface ExercisePlugin {
  /** Unique key matching the backend ExerciseType enum (e.g. 'zahlenmauer') */
  type: string;

  /** Human-readable display name */
  name: string;

  /** Category for palette grouping ('Arithmetic Puzzles', 'Written Arithmetic', etc.) */
  category: string;

  /** Short description */
  description: string;

  /** Default width and height on canvas in millimeters */
  defaultSize: { width: number; height: number };

  /** Default exercise parameters */
  defaultParams: Record<string, any>;

  /** Optional icon identifier or SVG snippet */
  icon?: string;

  /**
   * Optional custom property editor component.
   * If omitted, a dynamic schema-driven form is automatically rendered.
   */
  CustomInspector?: React.FC<ExerciseInspectorProps>;
}
