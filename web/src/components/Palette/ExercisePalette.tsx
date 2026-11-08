/**
 * src/components/Palette/ExercisePalette.tsx
 * Sidebar showing available exercise types with live graphical thumbnails.
 */

import React, { useState, useEffect } from 'react';
import { Plus, Grid, Layers, Sparkles, Image as ImageIcon } from 'lucide-react';
import { getPluginsByCategory } from '../../exercises/registry';
import type { ExercisePlugin } from '../../exercises/types';
import type { ExerciseType } from '../../types/models';
import { getBlockPreview } from '../../api/client';

interface ExercisePaletteProps {
  onAddBlock: (type: string) => void;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  'Arithmetic Puzzles': <Layers className="w-4 h-4 text-purple-600" />,
  'Written Arithmetic': <Grid className="w-4 h-4 text-blue-600" />,
  'Mental Arithmetic': <Sparkles className="w-4 h-4 text-amber-600" />,
  'Custom & Decoration': <ImageIcon className="w-4 h-4 text-emerald-600" />,
};

export const ExercisePalette: React.FC<ExercisePaletteProps> = ({ onAddBlock }) => {
  const groupedPlugins = getPluginsByCategory();
  const [thumbnails, setThumbnails] = useState<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;

    const loadThumbnails = async () => {
      const thumbs: Record<string, string> = {};
      const allPlugins = Object.values(groupedPlugins).flat();

      for (const plugin of allPlugins) {
        try {
          const res = await getBlockPreview({
            type: plugin.type as ExerciseType,
            params: plugin.defaultParams || {},
            show_solution: false,
          });
          thumbs[plugin.type] = `data:image/svg+xml;utf8,${encodeURIComponent(res.svg)}`;
        } catch {
          // Ignore preview failure for offline or custom items
        }
      }

      if (!cancelled) {
        setThumbnails(thumbs);
      }
    };

    loadThumbnails();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <aside className="w-72 bg-white border-r border-slate-200 flex flex-col h-full select-none">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
          Aufgaben-Bausteine
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Klicke auf einen Baustein, um ihn auf dem Blatt zu platzieren.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-5">
        {Object.entries(groupedPlugins).map(([category, plugins]) => (
          <div key={category} className="space-y-2">
            <div className="flex items-center gap-1.5 px-1 text-xs font-semibold text-slate-500">
              {CATEGORY_ICONS[category] || <Grid className="w-4 h-4" />}
              <span>{category}</span>
            </div>

            <div className="space-y-2">
              {plugins.map((plugin: ExercisePlugin) => (
                <div
                  key={plugin.type}
                  className="group p-3 rounded-lg border border-slate-200 hover:border-blue-400 hover:shadow-sm bg-white hover:bg-slate-50/50 transition cursor-pointer flex flex-col justify-between"
                  onClick={() => onAddBlock(plugin.type)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition">
                        {plugin.name}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                        {plugin.description}
                      </p>
                    </div>
                    <button
                      type="button"
                      aria-label={`Add ${plugin.name}`}
                      className="p-1 rounded bg-slate-100 group-hover:bg-blue-600 group-hover:text-white text-slate-600 transition shrink-0"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Graphical Preview Thumbnail */}
                  {thumbnails[plugin.type] && (
                    <div className="mt-2.5 p-2 bg-slate-50 rounded border border-slate-100 flex items-center justify-center max-h-20 overflow-hidden">
                      <img
                        src={thumbnails[plugin.type]}
                        alt={plugin.name}
                        className="max-h-16 max-w-full object-contain pointer-events-none"
                      />
                    </div>
                  )}

                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                    <span>
                      {plugin.defaultSize.width} &times; {plugin.defaultSize.height} mm
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};
