/**
 * src/exercises/addsub/index.ts
 * Plugin definition for Column-form Written Addition and Subtraction.
 */

import type { ExercisePlugin } from '../types';

export const addSubPlugin: ExercisePlugin = {
  type: 'addsub',
  name: 'Written Calculation (Add/Sub)',
  category: 'Written Arithmetic',
  description: 'Column-form written arithmetic on simulated math grid paper.',
  defaultSize: {
    width: 35,
    height: 30,
  },
  defaultParams: {
    operators: '+-',
    num_rows: 2,
    min_value: 10,
    max_value: 999,
    show_numbering: true,
  },
};

