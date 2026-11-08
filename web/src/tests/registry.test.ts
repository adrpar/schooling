import { describe, it, expect } from 'vitest';
import {
  exerciseRegistry,
  getPlugin,
  getAllPlugins,
  getPluginsByCategory,
  registerPlugin,
} from '../exercises/registry';
import type { ExercisePlugin } from '../exercises/types';

describe('Exercise Plugin Registry', () => {
  it('registers all core plugins', () => {
    expect(exerciseRegistry['zahlenmauer']).toBeDefined();
    expect(exerciseRegistry['addsub']).toBeDefined();
    expect(exerciseRegistry['mathrally']).toBeDefined();
    expect(exerciseRegistry['custom_svg']).toBeDefined();
  });

  it('retrieves plugin by type', () => {
    const zm = getPlugin('zahlenmauer');
    expect(zm).toBeDefined();
    expect(zm?.name).toBe('Zahlenmauer');
    expect(zm?.defaultSize.width).toBeGreaterThan(0);
    expect(zm?.defaultSize.height).toBeGreaterThan(0);
    expect(zm?.defaultParams.base_size).toBe(4);
  });

  it('retrieves all registered plugins', () => {
    const all = getAllPlugins();
    expect(all.length).toBeGreaterThanOrEqual(4);
  });

  it('groups plugins by category', () => {
    const categories = getPluginsByCategory();
    expect(categories['Arithmetic Puzzles']).toBeDefined();
    expect(categories['Written Arithmetic']).toBeDefined();
    expect(categories['Custom & Decoration']).toBeDefined();
  });

  it('allows dynamic registration of custom plugins', () => {
    const testPlugin: ExercisePlugin = {
      type: 'fraction_clock',
      name: 'Fraction Clock',
      category: 'Geometry',
      description: 'Clock face for teaching fractions.',
      defaultSize: { width: 40, height: 40 },
      defaultParams: { slices: 4 },
    };

    registerPlugin(testPlugin);
    const retrieved = getPlugin('fraction_clock');
    expect(retrieved).toBeDefined();
    expect(retrieved?.name).toBe('Fraction Clock');
  });
});
