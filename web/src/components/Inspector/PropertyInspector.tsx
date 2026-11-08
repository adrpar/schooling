/**
 * src/components/Inspector/PropertyInspector.tsx
 * Property sidebar for editing selected block parameters or worksheet global headers.
 */

import React from 'react';
import { Trash2, Copy, FileText, Sliders } from 'lucide-react';
import type { CatalogExerciseItem, ExerciseBlockSpec, HeaderSpec } from '../../types/models';
import { getPlugin } from '../../exercises/registry';

interface PropertyInspectorProps {
  selectedBlock: ExerciseBlockSpec | null;
  catalog: CatalogExerciseItem[];
  header: HeaderSpec;
  onUpdateHeader: (updates: Partial<HeaderSpec>) => void;
  onUpdateBlock: (id: string, updates: Partial<ExerciseBlockSpec>) => void;
  onUpdateParams: (id: string, params: Record<string, any>) => void;
  onDeleteBlock: (id: string) => void;
  onDuplicateBlock: (id: string) => void;
}

export const PropertyInspector: React.FC<PropertyInspectorProps> = ({
  selectedBlock,
  catalog,
  header,
  onUpdateHeader,
  onUpdateBlock,
  onUpdateParams,
  onDeleteBlock,
  onDuplicateBlock,
}) => {
  if (!selectedBlock) {
    return (
      <aside className="w-80 bg-white border-l border-slate-200 flex flex-col h-full">
        <div className="p-4 border-b border-slate-200 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
            Blatt-Eigenschaften
          </h2>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto flex-1 text-sm">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Haupttitel
            </label>
            <input
              type="text"
              value={header.title || ''}
              onChange={(e) => onUpdateHeader({ title: e.target.value })}
              className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Untertitel / Klasse
            </label>
            <input
              type="text"
              value={header.subtitle || ''}
              onChange={(e) => onUpdateHeader({ subtitle: e.target.value })}
              className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="pt-2 border-t border-slate-100 space-y-3">
            <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={header.show_name_field ?? true}
                onChange={(e) => onUpdateHeader({ show_name_field: e.target.checked })}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>Zeile &bdquo;Name: _________&ldquo; anzeigen</span>
            </label>

            <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={header.show_date_field ?? true}
                onChange={(e) => onUpdateHeader({ show_date_field: e.target.checked })}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>Zeile &bdquo;Datum: _________&ldquo; anzeigen</span>
            </label>
          </div>

          <div className="pt-6 text-xs text-slate-400">
            Wähle einen Baustein auf dem Arbeitsblatt aus, um seine mathematischen Parameter und Position anzupassen.
          </div>
        </div>
      </aside>
    );
  }

  const plugin = getPlugin(selectedBlock.type);
  const catalogItem = catalog.find((c) => c.type === selectedBlock.type);
  const schemaParams = catalogItem?.params || [];
  const currentParams = selectedBlock.params || {};

  const handleParamChange = (key: string, value: any) => {
    onUpdateParams(selectedBlock.id!, { [key]: value });
  };

  return (
    <aside className="w-80 bg-white border-l border-slate-200 flex flex-col h-full">
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800">
            {plugin?.name || selectedBlock.type}
          </h2>
        </div>
        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
          {selectedBlock.type}
        </span>
      </div>

      <div className="p-4 space-y-5 overflow-y-auto flex-1 text-sm">
        {/* Geometry / Position */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Position &amp; Größe (mm)
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[11px] font-medium text-slate-500">X (mm)</label>
              <input
                type="number"
                value={Math.round(selectedBlock.x)}
                onChange={(e) =>
                  onUpdateBlock(selectedBlock.id!, { x: Number(e.target.value) })
                }
                className="w-full px-2 py-1 border border-slate-300 rounded text-xs"
              />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-slate-500">Y (mm)</label>
              <input
                type="number"
                value={Math.round(selectedBlock.y)}
                onChange={(e) =>
                  onUpdateBlock(selectedBlock.id!, { y: Number(e.target.value) })
                }
                className="w-full px-2 py-1 border border-slate-300 rounded text-xs"
              />
            </div>
          </div>
        </div>

        {/* Dynamic Exercise Parameters */}
        <div className="border-t border-slate-100 pt-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
            Aufgaben-Parameter
          </h3>

          {plugin?.CustomInspector ? (
            <plugin.CustomInspector
              params={currentParams}
              onChange={(newParams) => onUpdateParams(selectedBlock.id!, newParams)}
              schemaParams={schemaParams}
            />
          ) : schemaParams.length > 0 ? (
            <div className="space-y-3">
              {schemaParams.map((param) => {
                const val = currentParams[param.name] ?? param.default;
                return (
                  <div key={param.name}>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {param.label}
                    </label>

                    {param.type === 'select' ? (
                      <select
                        value={String(val ?? '')}
                        onChange={(e) => handleParamChange(param.name, e.target.value)}
                        className="w-full px-2 py-1.5 border border-slate-300 rounded text-xs focus:ring-2 focus:ring-blue-500"
                      >
                        {param.options?.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                    ) : param.type === 'bool' ? (
                      <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={Boolean(val)}
                          onChange={(e) => handleParamChange(param.name, e.target.checked)}
                          className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Aktivieren</span>
                      </label>
                    ) : param.type === 'int' ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min={param.min}
                          max={param.max}
                          value={Number(val ?? 0)}
                          onChange={(e) =>
                            handleParamChange(param.name, parseInt(e.target.value, 10))
                          }
                          className="w-full px-2 py-1 border border-slate-300 rounded text-xs focus:ring-2 focus:ring-blue-500"
                        />
                        {param.min !== undefined && param.max !== undefined && (
                          <span className="text-[10px] text-slate-400 whitespace-nowrap">
                            ({param.min}–{param.max})
                          </span>
                        )}
                      </div>
                    ) : (
                      <input
                        type="text"
                        value={String(val ?? '')}
                        onChange={(e) => handleParamChange(param.name, e.target.value)}
                        className="w-full px-2 py-1 border border-slate-300 rounded text-xs focus:ring-2 focus:ring-blue-500"
                      />
                    )}

                    {param.help && (
                      <p className="text-[10px] text-slate-400 mt-0.5">{param.help}</p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">Keine anpassbaren Parameter.</p>
          )}
        </div>

        {/* Actions */}
        <div className="border-t border-slate-100 pt-4 space-y-2">
          <button
            type="button"
            onClick={() => onDuplicateBlock(selectedBlock.id!)}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 border border-slate-300 rounded hover:bg-slate-50 transition"
          >
            <Copy className="w-3.5 h-3.5" />
            <span>Baustein duplizieren</span>
          </button>
          <button
            type="button"
            onClick={() => onDeleteBlock(selectedBlock.id!)}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded hover:bg-red-50 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Baustein löschen</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
