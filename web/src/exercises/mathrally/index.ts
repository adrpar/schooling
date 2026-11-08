/**
 * src/exercises/mathrally/index.ts
 * Plugin definition for Math Rally trail calculations.
 */

import type { ExercisePlugin } from '../types';

export const mathRallyPlugin: ExercisePlugin = {
  type: 'mathrally',
  name: 'Math Rally',
  category: 'Mental Arithmetic',
  description: 'Continuous step-by-step arithmetic calculation trail on illustrated templates.',
  defaultSize: {
    width: 180,
    height: 200,
  },
  defaultParams: {
    operators: '+-*/',
    min_value: 1,
    max_value: 100,
    template: 'Rally1.svg',
  },
};
