/**
 * src/exercises/custom_svg/index.ts
 * Plugin definition for arbitrary custom SVG elements and stickers.
 */

import type { ExercisePlugin } from '../types';
import { CustomSvgInspector } from './Inspector';

export const customSvgPlugin: ExercisePlugin = {
  type: 'custom_svg',
  name: 'Custom SVG / Sticker',
  category: 'Custom & Decoration',
  description: 'Insert arbitrary SVG graphics, note boxes, reward stamps, or illustrations.',
  defaultSize: {
    width: 40,
    height: 40,
  },
  defaultParams: {
    svg_content:
      '<polygon points="25,5 32,19 47,21 36,32 39,47 25,40 11,47 14,32 3,21 18,19" fill="#facc15" stroke="#ca8a04" stroke-width="2"/>',
  },
  CustomInspector: CustomSvgInspector,
};
