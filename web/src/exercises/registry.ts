/**
 * src/exercises/registry.ts
 * Central registration for all exercise plugins.
 * The core canvas and editor never hardcode exercise logic; everything is accessed via this registry.
 */

import type { ExercisePlugin } from './types';
import { zahlenmauerPlugin } from './zahlenmauer';
import { addSubPlugin } from './addsub';
import { mathRallyPlugin } from './mathrally';
import { customSvgPlugin } from './custom_svg';

export const exerciseRegistry: Record<string, ExercisePlugin> = {
  zahlenmauer: zahlenmauerPlugin,
  addsub: addSubPlugin,
  mathrally: mathRallyPlugin,
  custom_svg: customSvgPlugin,
};

/**
 * Register a new exercise plugin dynamically at runtime.
 */
export function registerPlugin(plugin: ExercisePlugin): void {
  exerciseRegistry[plugin.type] = plugin;
}

/**
 * Look up a plugin by its exercise type key.
 */
export function getPlugin(type: string): ExercisePlugin | undefined {
  return exerciseRegistry[type];
}

/**
 * Retrieve all registered exercise plugins.
 */
export function getAllPlugins(): ExercisePlugin[] {
  return Object.values(exerciseRegistry);
}

/**
 * Group plugins by category for easy palette display.
 */
export function getPluginsByCategory(): Record<string, ExercisePlugin[]> {
  const groups: Record<string, ExercisePlugin[]> = {};
  for (const plugin of getAllPlugins()) {
    const cat = plugin.category || 'Other';
    if (!groups[cat]) {
      groups[cat] = [];
    }
    groups[cat].push(plugin);
  }
  return groups;
}
