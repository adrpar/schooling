/**
 * src/exercises/custom_svg/Inspector.tsx
 * Custom property editor for inserting and configuring arbitrary SVG elements.
 */

import React from 'react';
import type { ExerciseInspectorProps } from '../types';

const PRESETS = [
  {
    name: 'Star (Reward)',
    svg: '<polygon points="25,5 32,19 47,21 36,32 39,47 25,40 11,47 14,32 3,21 18,19" fill="#facc15" stroke="#ca8a04" stroke-width="2"/>',
  },
  {
    name: 'Checkmark Badge',
    svg: '<circle cx="25" cy="25" r="20" fill="#22c55e"/><path d="M16 25l6 6 12-12" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
  },
  {
    name: 'Math Grid Note Box',
    svg: '<rect x="2" y="2" width="46" height="46" rx="4" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 3"/><text x="25" y="27" font-size="7" fill="#64748b" text-anchor="middle" font-family="sans-serif">Notizen</text>',
  },
];

export const CustomSvgInspector: React.FC<ExerciseInspectorProps> = ({
  params,
  onChange,
}) => {
  const currentSvg = (params.svg_content as string) || '';

  return (
    <div className="space-y-4 text-sm">
      <div>
        <label className="block font-medium text-slate-700 mb-1">
          SVG Snippet Code
        </label>
        <textarea
          value={currentSvg}
          onChange={(e) => onChange({ ...params, svg_content: e.target.value })}
          rows={5}
          placeholder="<svg...> or <g>...</g>"
          className="w-full font-mono text-xs p-2 border border-slate-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <p className="text-xs text-slate-500 mt-1">
          Paste SVG tags (e.g. &lt;rect&gt;, &lt;path&gt;, &lt;circle&gt;).
        </p>
      </div>

      <div>
        <label className="block font-medium text-slate-700 mb-2">
          Or Choose a Preset Sticker:
        </label>
        <div className="grid grid-cols-3 gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.name}
              type="button"
              onClick={() => onChange({ ...params, svg_content: preset.svg })}
              className="p-2 border border-slate-200 rounded hover:border-blue-400 hover:bg-blue-50 transition text-center flex flex-col items-center gap-1"
            >
              <div
                className="w-8 h-8 flex items-center justify-center pointer-events-none"
                dangerouslySetInnerHTML={{
                  __html: `<svg viewBox="0 0 50 50" width="32" height="32">${preset.svg}</svg>`,
                }}
              />
              <span className="text-[11px] text-slate-600 line-clamp-1">
                {preset.name}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
