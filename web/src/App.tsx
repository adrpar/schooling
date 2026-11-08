/**
 * src/App.tsx
 * Main application shell wiring Toolbar, Palette, A4 Canvas, and Property Inspector together.
 */

import React, { useState, useEffect } from 'react';
import type { CatalogExerciseItem, SheetSpec } from './types/models';
import { getCatalog } from './api/client';
import { useSheetState } from './hooks/useSheetState';
import { Toolbar } from './components/Toolbar/Toolbar';
import { ExercisePalette } from './components/Palette/ExercisePalette';
import { A4Canvas } from './components/Canvas/A4Canvas';
import { PropertyInspector } from './components/Inspector/PropertyInspector';

const INITIAL_DEMO_SHEET: SheetSpec = {
  id: 'demo-sheet-1',
  title: 'Mathe-Übungsblatt: Pyramiden & Rechnen',
  header: {
    title: 'Mathe-Übungsblatt: Pyramiden & Schriftliches Rechnen',
    subtitle: 'Klasse 3b',
    show_name_field: true,
    show_date_field: true,
  },
  blocks: [
    {
      id: 'block-zm-1',
      type: 'zahlenmauer',
      x: 20.0,
      y: 40.0,
      width: 70.0,
      height: 45.0,
      scale: 1.0,
      params: {
        base_size: 4,
        difficulty: 'medium',
        seed: 42,
        show_numbering: true,
      },
    },
    {
      id: 'block-addsub-1',
      type: 'addsub',
      x: 110.0,
      y: 40.0,
      width: 40.0,
      height: 35.0,
      scale: 1.0,
      params: {
        operators: '+-',
        num_rows: 2,
        seed: 99,
        show_numbering: true,
      },
    },
  ],
  show_solutions: false,
};

export const App: React.FC = () => {
  const [catalog, setCatalog] = useState<CatalogExerciseItem[]>([]);
  const {
    sheet,
    selectedBlockId,
    selectedBlock,
    selectBlock,
    addBlock,
    updateBlock,
    updateBlockParams,
    moveBlock,
    commitMove,
    deleteBlock,
    duplicateBlock,
    updateHeader,
    toggleSolutions,
    setSheet,
    undo,
    redo,
    canUndo,
    canRedo,
  } = useSheetState(INITIAL_DEMO_SHEET);

  useEffect(() => {
    getCatalog()
      .then((data) => setCatalog(data))
      .catch((err) => console.warn('Could not fetch catalog from backend:', err));
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-100">
      {/* Top Toolbar */}
      <Toolbar
        sheet={sheet}
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={undo}
        onRedo={redo}
        onToggleSolutions={toggleSolutions}
        onLoadSheet={(newSheet) => setSheet(newSheet)}
      />

      {/* 3-Column Studio Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left: Exercise Palette */}
        <ExercisePalette onAddBlock={(type) => addBlock(type, 25, 45)} />

        {/* Center: A4 Interactive Canvas */}
        <A4Canvas
          sheet={sheet}
          selectedBlockId={selectedBlockId}
          onSelectBlock={selectBlock}
          onMoveBlock={moveBlock}
          onCommitMove={commitMove}
          onUpdateBlockDimensions={(id, width, height) => updateBlock(id, { width, height })}
        />

        {/* Right: Property Inspector */}
        <PropertyInspector
          selectedBlock={selectedBlock}
          catalog={catalog}
          header={
            sheet.header || {
              title: sheet.title,
              subtitle: '',
              show_name_field: true,
              show_date_field: true,
            }
          }
          onUpdateHeader={updateHeader}
          onUpdateBlock={updateBlock}
          onUpdateParams={updateBlockParams}
          onDeleteBlock={deleteBlock}
          onDuplicateBlock={duplicateBlock}
        />
      </div>
    </div>
  );
};

export default App;
