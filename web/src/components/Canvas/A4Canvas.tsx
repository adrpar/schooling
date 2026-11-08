/**
 * src/components/Canvas/A4Canvas.tsx
 * Interactive A4 worksheet canvas rendering live SVG exercise graphics directly inside draggable blocks.
 */

import React, { useRef, useState, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { ExerciseBlockSpec, SheetSpec } from '../../types/models';
import { screenToCanvasMm, snapToGrid } from '../../utils/coordinates';
import { useBlockPreviews } from '../../hooks/useBlockPreviews';

interface A4CanvasProps {
  sheet: SheetSpec;
  selectedBlockId: string | null;
  onSelectBlock: (id: string | null) => void;
  onMoveBlock: (id: string, x: number, y: number) => void;
  onCommitMove: () => void;
  onUpdateBlockDimensions?: (id: string, width: number, height: number) => void;
}

export const A4Canvas: React.FC<A4CanvasProps> = ({
  sheet,
  selectedBlockId,
  onSelectBlock,
  onMoveBlock,
  onCommitMove,
  onUpdateBlockDimensions,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const [zoom, setZoom] = useState<number>(0.9);

  // Live standalone SVG previews for each block
  const handleDimensions = useCallback(
    (id: string, width: number, height: number) => {
      if (onUpdateBlockDimensions) {
        onUpdateBlockDimensions(id, width, height);
      }
    },
    [onUpdateBlockDimensions]
  );

  const previews = useBlockPreviews(
    sheet.blocks,
    Boolean(sheet.show_solutions),
    handleDimensions
  );

  // Dragging state
  const [draggingBlockId, setDraggingBlockId] = useState<string | null>(null);
  const dragStartRef = useRef<{ clientX: number; clientY: number; blockX: number; blockY: number } | null>(null);

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

  const header = sheet.header || {
    title: sheet.title,
    subtitle: '',
    show_name_field: true,
    show_date_field: true,
  };

  return (
    <div
      ref={containerRef}
      className="flex-1 bg-slate-200 relative overflow-auto flex items-center justify-center p-8 select-none"
      onClick={() => onSelectBlock(null)}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
    >
      {/* Floating Zoom Controls */}
      <div className="absolute bottom-5 right-5 z-20 bg-white/95 backdrop-blur rounded-lg shadow-md border border-slate-200 p-1 flex items-center gap-1">
        <button
          type="button"
          onClick={() => setZoom((z) => Math.max(0.4, Number((z - 0.1).toFixed(1))))}
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700"
          title="Verkleinern"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-xs font-mono px-1 min-w-[42px] text-center text-slate-700">
          {Math.round(zoom * 100)}%
        </span>
        <button
          type="button"
          onClick={() => setZoom((z) => Math.min(2.0, Number((z + 0.1).toFixed(1))))}
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
          width: `${210 * 3.7795 * zoom}px`, // 1mm = 3.7795px at 96 DPI
          height: `${297 * 3.7795 * zoom}px`,
        }}
        className="relative bg-white shadow-2xl rounded-sm transition-all border border-slate-300"
        onClick={(e) => e.stopPropagation()}
      >
        <svg
          ref={svgRef}
          viewBox="0 0 210 297"
          className="w-full h-full block cursor-default"
        >
          {/* Paper Background */}
          <rect x={0} y={0} width={210} height={297} fill="#ffffff" />

          {/* Printable Area Margins Guide (14mm left/right, 32mm top, 21mm bottom) */}
          <rect
            x={14}
            y={32}
            width={182}
            height={244}
            fill="none"
            stroke="#e2e8f0"
            strokeDasharray="2 2"
            strokeWidth="0.3"
            pointerEvents="none"
          />

          {/* Worksheet Header */}
          <g id="sheetHeader" className="pointer-events-none select-none">
            <text
              x={14}
              y={17}
              fontSize="5.2"
              fontWeight="bold"
              fill="#0f172a"
              fontFamily="system-ui, sans-serif"
            >
              {header.title || sheet.title}
            </text>

            {header.subtitle && (
              <text
                x={14}
                y={23.5}
                fontSize="3.2"
                fill="#64748b"
                fontFamily="system-ui, sans-serif"
              >
                {header.subtitle}
              </text>
            )}

            {header.show_name_field && (
              <text
                x={140}
                y={17}
                fontSize="3.2"
                fill="#475569"
                fontFamily="system-ui, sans-serif"
              >
                Name: ______________________
              </text>
            )}

            {header.show_date_field && (
              <text
                x={140}
                y={23.5}
                fontSize="3.2"
                fill="#475569"
                fontFamily="system-ui, sans-serif"
              >
                Datum: ______________________
              </text>
            )}

            {/* Separator line below header */}
            <line
              x1={14}
              y1={27}
              x2={196}
              y2={27}
              stroke="#cbd5e1"
              strokeWidth="0.4"
            />
          </g>

          {/* Exercise Blocks with Live SVG Visuals */}
          {sheet.blocks.map((block) => {
            const isSelected = block.id === selectedBlockId;
            const preview = block.id ? previews[block.id] : undefined;
            const w = preview?.width || block.width || 50;
            const h = preview?.height || block.height || 40;

            return (
              <g
                key={block.id}
                transform={`translate(${block.x}, ${block.y})`}
                className="cursor-move"
                onPointerDown={(e) => handlePointerDown(e, block)}
              >
                {/* Real Exercise SVG Graphic */}
                {preview?.svgDataUrl ? (
                  <image
                    href={preview.svgDataUrl}
                    x={0}
                    y={0}
                    width={w}
                    height={h}
                    preserveAspectRatio="xMinYMin meet"
                    className="pointer-events-none select-none"
                  />
                ) : (
                  <g className="pointer-events-none">
                    <rect
                      x={0}
                      y={0}
                      width={w}
                      height={h}
                      fill="#f8fafc"
                      stroke="#cbd5e1"
                      strokeDasharray="1 1"
                      strokeWidth="0.3"
                      rx={1}
                    />
                    <text
                      x={w / 2}
                      y={h / 2}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize="2.5"
                      fill="#94a3b8"
                      fontFamily="system-ui, sans-serif"
                    >
                      Lade {block.type}...
                    </text>
                  </g>
                )}

                {/* Interactive Selection Box / Hit Area */}
                <rect
                  x={0}
                  y={0}
                  width={w}
                  height={h}
                  fill={isSelected ? 'rgba(59, 130, 246, 0.05)' : 'transparent'}
                  stroke={isSelected ? '#2563eb' : '#cbd5e1'}
                  strokeWidth={isSelected ? '0.6' : '0.25'}
                  strokeDasharray={isSelected ? '2 1.5' : '1.5 1.5'}
                  className="hover:stroke-blue-400 hover:stroke-[0.4] transition-colors"
                  rx={1}
                />

                {/* Selection Badges and Corner Handles */}
                {isSelected && (
                  <g className="pointer-events-none select-none">
                    {/* Corner Handles */}
                    <rect x={-1} y={-1} width={2} height={2} fill="#2563eb" />
                    <rect x={w - 1} y={-1} width={2} height={2} fill="#2563eb" />
                    <rect x={-1} y={h - 1} width={2} height={2} fill="#2563eb" />
                    <rect x={w - 1} y={h - 1} width={2} height={2} fill="#2563eb" />

                    {/* Block Info Badge */}
                    <g transform="translate(0, -3.5)">
                      <rect
                        x={0}
                        y={0}
                        width={Math.min(w, 35)}
                        height={3.2}
                        rx={0.6}
                        fill="#2563eb"
                      />
                      <text
                        x={1.5}
                        y={2.2}
                        fontSize="2.0"
                        fill="#ffffff"
                        fontWeight="bold"
                        fontFamily="system-ui, sans-serif"
                      >
                        {block.type} ({Math.round(block.x)}, {Math.round(block.y)})
                      </text>
                    </g>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
