/**
 * src/components/Canvas/A4Canvas.tsx
 * Interactive A4 worksheet canvas supporting block dragging, selection, and live SVG preview.
 */

import React, { useRef, useState, useEffect } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { ExerciseBlockSpec, SheetSpec } from '../../types/models';
import { screenToCanvasMm, snapToGrid } from '../../utils/coordinates';
import { renderSheetSvg } from '../../api/client';

interface A4CanvasProps {
  sheet: SheetSpec;
  selectedBlockId: string | null;
  onSelectBlock: (id: string | null) => void;
  onMoveBlock: (id: string, x: number, y: number) => void;
  onCommitMove: () => void;
}

export const A4Canvas: React.FC<A4CanvasProps> = ({
  sheet,
  selectedBlockId,
  onSelectBlock,
  onMoveBlock,
  onCommitMove,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const [zoom, setZoom] = useState<number>(0.9);
  const [svgPreview, setSvgPreview] = useState<string>('');
  const [isRendering, setIsRendering] = useState<boolean>(false);

  // Dragging state
  const [draggingBlockId, setDraggingBlockId] = useState<string | null>(null);
  const dragStartRef = useRef<{ clientX: number; clientY: number; blockX: number; blockY: number } | null>(null);

  // Live SVG render preview from backend whenever sheet structure changes
  useEffect(() => {
    let active = true;
    const updatePreview = async () => {
      try {
        setIsRendering(true);
        const svgString = await renderSheetSvg(sheet);
        if (active) {
          setSvgPreview(svgString);
        }
      } catch (err) {
        // Backend might be offline or starting; fallback gracefully
      } finally {
        if (active) setIsRendering(false);
      }
    };

    const timeout = setTimeout(updatePreview, 150);
    return () => {
      active = false;
      clearTimeout(timeout);
    };
  }, [sheet]);

  // Pointer drag handling in mm space
  const handlePointerDown = (
    e: React.PointerEvent,
    block: ExerciseBlockSpec
  ) => {
    e.stopPropagation();
    onSelectBlock(block.id || null);

    setDraggingBlockId(block.id || null);
    dragStartRef.current = {
      clientX: e.clientX,
      clientY: e.clientY,
      blockX: block.x,
      blockY: block.y,
    };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!draggingBlockId || !dragStartRef.current || !svgRef.current) return;

    const deltaX = e.clientX - dragStartRef.current.clientX;
    const deltaY = e.clientY - dragStartRef.current.clientY;
    const { dxMm, dyMm } = screenToCanvasMm(deltaX, deltaY, svgRef.current);

    const targetX = snapToGrid(dragStartRef.current.blockX + dxMm, 2.5);
    const targetY = snapToGrid(dragStartRef.current.blockY + dyMm, 2.5);

    onMoveBlock(draggingBlockId, targetX, targetY);
  };

  const handlePointerUp = () => {
    if (draggingBlockId) {
      setDraggingBlockId(null);
      dragStartRef.current = null;
      onCommitMove();
    }
  };

  return (
    <div
      ref={containerRef}
      className="flex-1 bg-slate-200 relative overflow-auto flex items-center justify-center p-8 select-none"
      onClick={() => onSelectBlock(null)}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
    >
      {/* Zoom controls */}
      <div className="absolute bottom-5 right-5 z-20 bg-white/90 backdrop-blur rounded-lg shadow-md border border-slate-200 p-1 flex items-center gap-1">
        <button
          type="button"
          onClick={() => setZoom((z) => Math.max(0.4, z - 0.1))}
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700"
          title="Verkleinern"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-xs font-mono px-1 min-w-[40px] text-center">
          {Math.round(zoom * 100)}%
        </span>
        <button
          type="button"
          onClick={() => setZoom((z) => Math.min(2.0, z + 0.1))}
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700"
          title="Vergrößern"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => setZoom(0.9)}
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700 ml-1 border-l border-slate-200"
          title="Standardgröße"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* A4 Sheet Container */}
      <div
        style={{
          width: `${210 * 3.7795 * zoom}px`, // 1mm ~= 3.7795px at 96 DPI
          height: `${297 * 3.7795 * zoom}px`,
          transformOrigin: 'center center',
        }}
        className="relative bg-white shadow-2xl rounded-sm transition-transform border border-slate-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Rendered SVG Background */}
        {svgPreview && (
          <div
            className="absolute inset-0 pointer-events-none w-full h-full"
            dangerouslySetInnerHTML={{ __html: svgPreview }}
          />
        )}

        {/* Interactive SVG Overlay for Block Manipulation */}
        <svg
          ref={svgRef}
          viewBox="0 0 210 297"
          className="absolute inset-0 w-full h-full cursor-default"
          style={{ overflow: 'visible' }}
        >
          {sheet.blocks.map((block) => {
            const isSelected = block.id === selectedBlockId;
            const w = block.width || 50;
            const h = block.height || 40;

            return (
              <g
                key={block.id}
                transform={`translate(${block.x}, ${block.y})`}
                className="cursor-move"
                onPointerDown={(e) => handlePointerDown(e, block)}
              >
                {/* Hit test & Selection Outline */}
                <rect
                  x={0}
                  y={0}
                  width={w}
                  height={h}
                  fill={isSelected ? 'rgba(59, 130, 246, 0.08)' : 'transparent'}
                  stroke={isSelected ? '#2563eb' : 'transparent'}
                  strokeWidth={isSelected ? '0.75' : '0.5'}
                  strokeDasharray={isSelected ? '1.5 1.5' : undefined}
                  className="hover:stroke-blue-400 hover:stroke-[0.5]"
                  rx={1}
                />

                {/* Corner grab indicators when selected */}
                {isSelected && (
                  <>
                    <circle cx={0} cy={0} r={1.2} fill="#2563eb" />
                    <circle cx={w} cy={0} r={1.2} fill="#2563eb" />
                    <circle cx={0} cy={h} r={1.2} fill="#2563eb" />
                    <circle cx={w} cy={h} r={1.2} fill="#2563eb" />
                    <text
                      x={2}
                      y={-1.5}
                      fontSize="2.5"
                      fill="#2563eb"
                      fontFamily="sans-serif"
                      fontWeight="bold"
                    >
                      {block.type} ({Math.round(block.x)}, {Math.round(block.y)})
                    </text>
                  </>
                )}
              </g>
            );
          })}
        </svg>

        {isRendering && (
          <div className="absolute top-2 right-2 text-[10px] bg-slate-800/70 text-white px-2 py-0.5 rounded backdrop-blur">
            Aktualisiere...
          </div>
        )}
      </div>
    </div>
  );
};
