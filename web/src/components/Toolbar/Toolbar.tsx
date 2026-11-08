/**
 * src/components/Toolbar/Toolbar.tsx
 * Top navigation bar with action buttons for undo/redo, solution toggle, SQLite save/load, and PDF export.
 */

import React, { useState } from 'react';
import {
  Undo2,
  Redo2,
  Download,
  FileDown,
  Save,
  FolderOpen,
  CheckCircle,
  Eye,
  EyeOff,
  Loader2,
  Calculator,
} from 'lucide-react';
import type { SheetSpec, SheetSummary } from '../../types/models';
import {
  exportSheetPdf,
  listSavedSheets,
  loadSheetSpec,
  saveSheetSpec,
  deleteSheetSpec,
  renderSheetSvg,
} from '../../api/client';

interface ToolbarProps {
  sheet: SheetSpec;
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onToggleSolutions: () => void;
  onLoadSheet: (sheet: SheetSpec) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  sheet,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  onToggleSolutions,
  onLoadSheet,
}) => {
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Saved sheets modal
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [savedSheets, setSavedSheets] = useState<SheetSummary[]>([]);
  const [isLoadingList, setIsLoadingList] = useState(false);

  const handleDownloadPdf = async () => {
    try {
      setIsExportingPdf(true);
      const blob = await exportSheetPdf(sheet);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(sheet.title || 'arbeitsblatt').toLowerCase().replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Fehler beim PDF-Export: ${err}`);
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleDownloadSvg = async () => {
    try {
      const svgText = await renderSheetSvg(sheet);
      const blob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(sheet.title || 'arbeitsblatt').toLowerCase().replace(/\s+/g, '_')}.svg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Fehler beim SVG-Download: ${err}`);
    }
  };

  const handleSaveToDb = async () => {
    try {
      setIsSaving(true);
      await saveSheetSpec(sheet);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      alert(`Fehler beim Speichern: ${err}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenLoadModal = async () => {
    setShowLoadModal(true);
    setIsLoadingList(true);
    try {
      const list = await listSavedSheets();
      setSavedSheets(list);
    } catch (err) {
      alert(`Fehler beim Laden der Blätter: ${err}`);
    } finally {
      setIsLoadingList(false);
    }
  };

  const handleSelectSavedSheet = async (id: string) => {
    try {
      const loaded = await loadSheetSpec(id);
      onLoadSheet(loaded);
      setShowLoadModal(false);
    } catch (err) {
      alert(`Fehler beim Öffnen des Blatts: ${err}`);
    }
  };

  const handleDeleteSavedSheet = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!confirm('Möchtest du dieses Arbeitsblatt wirklich löschen?')) return;
    try {
      await deleteSheetSpec(id);
      setSavedSheets((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      alert(`Fehler beim Löschen: ${err}`);
    }
  };

  return (
    <>
      <header className="h-14 bg-white border-b border-slate-200 px-4 flex items-center justify-between z-10">
        {/* Left: Branding */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold shadow-sm">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-800 leading-tight">
              Rechenrally Editor
            </h1>
            <span className="text-[11px] text-slate-400">
              Multi-Exercise Sheet Composer
            </span>
          </div>
        </div>

        {/* Center: Undo/Redo & Solutions Toggle */}
        <div className="flex items-center gap-2">
          <div className="flex items-center border border-slate-200 rounded-lg p-0.5 bg-slate-50">
            <button
              type="button"
              onClick={onUndo}
              disabled={!canUndo}
              className="p-1.5 rounded hover:bg-white disabled:opacity-40 text-slate-700 transition"
              title="Rückgängig (Undo)"
            >
              <Undo2 className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={onRedo}
              disabled={!canRedo}
              className="p-1.5 rounded hover:bg-white disabled:opacity-40 text-slate-700 transition"
              title="Wiederholen (Redo)"
            >
              <Redo2 className="w-4 h-4" />
            </button>
          </div>

          <div className="h-4 w-[1px] bg-slate-200 mx-1" />

          <button
            type="button"
            onClick={onToggleSolutions}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
              sheet.show_solutions
                ? 'bg-amber-50 text-amber-800 border-amber-300'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
            }`}
          >
            {sheet.show_solutions ? (
              <>
                <Eye className="w-3.5 h-3.5 text-amber-600" />
                <span>Lösungsblatt</span>
              </>
            ) : (
              <>
                <EyeOff className="w-3.5 h-3.5 text-slate-500" />
                <span>Aufgabenblatt</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Storage & Exports */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleOpenLoadModal}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition"
          >
            <FolderOpen className="w-3.5 h-3.5 text-slate-500" />
            <span>Öffnen</span>
          </button>

          <button
            type="button"
            onClick={handleSaveToDb}
            disabled={isSaving}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition"
          >
            {isSaving ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
            ) : saveSuccess ? (
              <CheckCircle className="w-3.5 h-3.5 text-green-600" />
            ) : (
              <Save className="w-3.5 h-3.5 text-slate-500" />
            )}
            <span>{saveSuccess ? 'Gespeichert!' : 'Speichern'}</span>
          </button>

          <div className="h-4 w-[1px] bg-slate-200 mx-1" />

          <button
            type="button"
            onClick={handleDownloadSvg}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition"
            title="SVG herunterladen"
          >
            <FileDown className="w-3.5 h-3.5 text-slate-500" />
            <span>SVG</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={isExportingPdf}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-sm disabled:opacity-50"
          >
            {isExportingPdf ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Download className="w-3.5 h-3.5" />
            )}
            <span>PDF Export</span>
          </button>
        </div>
      </header>

      {/* Saved Sheets Modal */}
      {showLoadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-800">
                Gespeicherte Arbeitsblätter (SQLite)
              </h2>
              <button
                type="button"
                onClick={() => setShowLoadModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="max-h-72 overflow-y-auto space-y-2">
              {isLoadingList ? (
                <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  <span>Lade gespeicherte Blätter...</span>
                </div>
              ) : savedSheets.length === 0 ? (
                <p className="py-8 text-center text-xs text-slate-400 italic">
                  Noch keine Arbeitsblätter gespeichert.
                </p>
              ) : (
                savedSheets.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleSelectSavedSheet(item.id)}
                    className="p-3 border border-slate-200 hover:border-blue-400 rounded-lg cursor-pointer hover:bg-blue-50/50 flex items-center justify-between transition group"
                  >
                    <div>
                      <h3 className="text-xs font-semibold text-slate-800 group-hover:text-blue-600">
                        {item.title}
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        {item.block_count} Bausteine &bull; Zuletzt geändert:{' '}
                        {new Date(item.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDeleteSavedSheet(e, item.id)}
                      className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50 transition"
                      title="Löschen"
                    >
                      &times;
                    </button>
                  </div>
                ))
              )}
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowLoadModal(false)}
                className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
