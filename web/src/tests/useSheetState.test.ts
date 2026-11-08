import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSheetState } from '../hooks/useSheetState';

describe('useSheetState Hook', () => {
  it('initializes with default sheet and no selection', () => {
    const { result } = renderHook(() => useSheetState());
    expect(result.current.sheet.blocks).toEqual([]);
    expect(result.current.selectedBlockId).toBeNull();
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it('adds a block and selects it', () => {
    const { result } = renderHook(() => useSheetState());

    act(() => {
      result.current.addBlock('zahlenmauer', 30, 60);
    });

    expect(result.current.sheet.blocks.length).toBe(1);
    expect(result.current.sheet.blocks[0].type).toBe('zahlenmauer');
    expect(result.current.sheet.blocks[0].x).toBe(30);
    expect(result.current.sheet.blocks[0].y).toBe(60);
    expect(result.current.selectedBlockId).toBe(result.current.sheet.blocks[0].id);
    expect(result.current.canUndo).toBe(true);
  });

  it('supports undo and redo', () => {
    const { result } = renderHook(() => useSheetState());

    act(() => {
      result.current.addBlock('zahlenmauer', 30, 60);
    });
    expect(result.current.sheet.blocks.length).toBe(1);

    act(() => {
      result.current.undo();
    });
    expect(result.current.sheet.blocks.length).toBe(0);
    expect(result.current.canRedo).toBe(true);

    act(() => {
      result.current.redo();
    });
    expect(result.current.sheet.blocks.length).toBe(1);
  });

  it('updates block parameters and position', () => {
    const { result } = renderHook(() => useSheetState());

    act(() => {
      result.current.addBlock('zahlenmauer', 20, 40);
    });
    const blockId = result.current.sheet.blocks[0].id!;

    act(() => {
      result.current.updateBlockParams(blockId, { base_size: 5 });
    });
    expect(result.current.sheet.blocks[0].params['base_size']).toBe(5);

    act(() => {
      result.current.moveBlock(blockId, 50, 80);
    });
    expect(result.current.sheet.blocks[0].x).toBe(50);
    expect(result.current.sheet.blocks[0].y).toBe(80);
  });

  it('deletes block and clears selection', () => {
    const { result } = renderHook(() => useSheetState());

    act(() => {
      result.current.addBlock('addsub', 20, 40);
    });
    const blockId = result.current.sheet.blocks[0].id!;

    act(() => {
      result.current.deleteBlock(blockId);
    });
    expect(result.current.sheet.blocks.length).toBe(0);
    expect(result.current.selectedBlockId).toBeNull();
  });
});
