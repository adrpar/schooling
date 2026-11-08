/**
 * src/hooks/useSheetState.ts
 * Centralized, undo-capable state management hook for worksheet layout and blocks.
 */

import { useState, useCallback } from 'react';
import type { ExerciseBlockSpec, ExerciseType, HeaderSpec, SheetSpec } from '../types/models';
import { getPlugin } from '../exercises/registry';
import { clampBlockPosition } from '../utils/coordinates';

function generateId(prefix: string = 'block'): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
}

export const DEFAULT_SHEET: SheetSpec = {
  id: 'sheet-new',
  title: 'Mathe-Übungsblatt',
  header: {
    title: 'Mathe-Übungsblatt',
    subtitle: 'Klasse 3',
    show_name_field: true,
    show_date_field: true,
  },
  blocks: [],
  show_solutions: false,
};

export function useSheetState(initialSheet: SheetSpec = DEFAULT_SHEET) {
  const [sheet, setSheetInternal] = useState<SheetSpec>(initialSheet);
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);

  // Undo / Redo stacks
  const [history, setHistory] = useState<SheetSpec[]>([]);
  const [future, setFuture] = useState<SheetSpec[]>([]);

  const pushState = useCallback((newSheet: SheetSpec) => {
    setHistory((prev) => [...prev.slice(-20), sheet]);
    setFuture([]);
    setSheetInternal(newSheet);
  }, [sheet]);

  const setSheet = useCallback((newSheet: SheetSpec) => {
    setHistory([]);
    setFuture([]);
    setSheetInternal(newSheet);
    setSelectedBlockId(null);
  }, []);

  const selectBlock = useCallback((id: string | null) => {
    setSelectedBlockId(id);
  }, []);

  const addBlock = useCallback(
    (type: string, x: number = 20, y: number = 40) => {
      const plugin = getPlugin(type);
      const defaultWidth = plugin?.defaultSize.width ?? 50;
      const defaultHeight = plugin?.defaultSize.height ?? 40;
      const defaultParams = plugin ? { ...plugin.defaultParams } : {};

      const clamped = clampBlockPosition(x, y, defaultWidth, defaultHeight);

      const newBlock: ExerciseBlockSpec = {
        id: generateId(type),
        type: type as ExerciseType,
        x: clamped.x,
        y: clamped.y,
        width: defaultWidth,
        height: defaultHeight,
        scale: 1.0,
        params: defaultParams,
      };

      const updated = {
        ...sheet,
        blocks: [...sheet.blocks, newBlock],
      };
      pushState(updated);
      setSelectedBlockId(newBlock.id || null);
    },
    [sheet, pushState]
  );

  const updateBlock = useCallback(
    (id: string, updates: Partial<ExerciseBlockSpec>) => {
      const updatedBlocks = sheet.blocks.map((block) => {
        if (block.id !== id) return block;
        return { ...block, ...updates };
      });
      pushState({ ...sheet, blocks: updatedBlocks });
    },
    [sheet, pushState]
  );

  const updateBlockParams = useCallback(
    (id: string, params: Record<string, any>) => {
      const updatedBlocks = sheet.blocks.map((block) => {
        if (block.id !== id) return block;
        return { ...block, params: { ...block.params, ...params } };
      });
      pushState({ ...sheet, blocks: updatedBlocks });
    },
    [sheet, pushState]
  );

  const moveBlock = useCallback(
    (id: string, x: number, y: number) => {
      const target = sheet.blocks.find((b) => b.id === id);
      if (!target) return;
      const w = target.width ?? 50;
      const h = target.height ?? 40;
      const clamped = clampBlockPosition(x, y, w, h);

      const updatedBlocks = sheet.blocks.map((block) => {
        if (block.id !== id) return block;
        return { ...block, x: clamped.x, y: clamped.y };
      });
      setSheetInternal({ ...sheet, blocks: updatedBlocks });
    },
    [sheet]
  );

  const commitMove = useCallback(() => {
    setHistory((prev) => [...prev.slice(-20), sheet]);
    setFuture([]);
  }, [sheet]);

  const deleteBlock = useCallback(
    (id: string) => {
      const updatedBlocks = sheet.blocks.filter((b) => b.id !== id);
      pushState({ ...sheet, blocks: updatedBlocks });
      if (selectedBlockId === id) {
        setSelectedBlockId(null);
      }
    },
    [sheet, selectedBlockId, pushState]
  );

  const duplicateBlock = useCallback(
    (id: string) => {
      const source = sheet.blocks.find((b) => b.id === id);
      if (!source) return;
      const newBlock: ExerciseBlockSpec = {
        ...source,
        id: generateId(source.type),
        x: Math.min(source.x + 10, 150),
        y: Math.min(source.y + 10, 240),
        params: { ...source.params },
      };
      pushState({ ...sheet, blocks: [...sheet.blocks, newBlock] });
      setSelectedBlockId(newBlock.id || null);
    },
    [sheet, pushState]
  );

  const updateHeader = useCallback(
    (headerUpdates: Partial<HeaderSpec>) => {
      const current: HeaderSpec = sheet.header || {
        title: sheet.title,
        subtitle: '',
        show_name_field: true,
        show_date_field: true,
      };
      pushState({
        ...sheet,
        header: { ...current, ...headerUpdates },
      });
    },
    [sheet, pushState]
  );

  const toggleSolutions = useCallback(() => {
    pushState({
      ...sheet,
      show_solutions: !sheet.show_solutions,
    });
  }, [sheet, pushState]);

  const undo = useCallback(() => {
    if (history.length === 0) return;
    const previous = history[history.length - 1];
    setHistory((prev) => prev.slice(0, prev.length - 1));
    setFuture((prev) => [sheet, ...prev]);
    setSheetInternal(previous);
  }, [history, sheet]);

  const redo = useCallback(() => {
    if (future.length === 0) return;
    const next = future[0];
    setFuture((prev) => prev.slice(1));
    setHistory((prev) => [...prev, sheet]);
    setSheetInternal(next);
  }, [future, sheet]);

  const selectedBlock = sheet.blocks.find((b) => b.id === selectedBlockId) || null;

  return {
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
    canUndo: history.length > 0,
    canRedo: future.length > 0,
  };
}
