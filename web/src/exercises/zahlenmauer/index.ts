/**
 * src/exercises/zahlenmauer/index.ts
 * Plugin definition for Addition Pyramids (Zahlenmauer).
 */

import type { ExercisePlugin } from '../types';

export const zahlenmauerPlugin: ExercisePlugin = {
  type: 'zahlenmauer',
  name: 'Zahlenmauer',
  category: 'Arithmetic Puzzles',
  description: 'Addition pyramid where each brick is the sum of the two bricks below it.',
  defaultSize: {
    width: 70,
    height: 45,
  },
  defaultParams: {
    base_size: 4,
    difficulty: 'medium',
    min_value: 1,
    max_value: 100,
    show_numbering: true,
  },
};

