/**
 * src/hooks/useBlockPreviews.ts
 * Fetches and caches standalone SVG previews for exercise blocks.
 * Enables instant, interactive rendering of real exercise content directly on the canvas.
 */

import { useState, useEffect, useRef } from 'react';
import type { ExerciseBlockSpec } from '../types/models';
import { getBlockPreview } from '../api/client';

export interface BlockPreviewData {
  svgDataUrl: string;
  width: number;
  height: number;
}

function svgToDataUrl(svgString: string): string {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svgString)}`;
}

export function useBlockPreviews(
  blocks: ExerciseBlockSpec[],
  showSolutions: boolean,
  onDimensionsDiscovered?: (id: string, width: number, height: number) => void
) {
  const [previews, setPreviews] = useState<Record<string, BlockPreviewData>>({});
  const cacheRef = useRef<Record<string, BlockPreviewData>>({});

  useEffect(() => {
    let isCancelled = false;

    const fetchMissingPreviews = async () => {
      const updatedPreviews = { ...cacheRef.current };
      let changed = false;

      for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];
        const blockId = block.id || `block-${i}`;
        const cacheKey = `${block.type}-${showSolutions}-${JSON.stringify(block.params)}`;

        if (cacheRef.current[cacheKey]) {
          updatedPreviews[blockId] = cacheRef.current[cacheKey];
          continue;
        }

        try {
          const res = await getBlockPreview({
            type: block.type,
            params: block.params || {},
            show_solution: showSolutions,
          });

          const data: BlockPreviewData = {
            svgDataUrl: svgToDataUrl(res.svg),
            width: res.width,
            height: res.height,
          };

          cacheRef.current[cacheKey] = data;
          updatedPreviews[blockId] = data;
          changed = true;

          if (onDimensionsDiscovered && (!block.width || !block.height)) {
            onDimensionsDiscovered(blockId, res.width, res.height);
          }
        } catch (err) {
          console.warn(`Failed to preview block ${blockId}:`, err);
        }
      }

      if (!isCancelled) {
        setPreviews((prev) => (changed ? { ...prev, ...updatedPreviews } : updatedPreviews));
      }
    };

    fetchMissingPreviews();

    return () => {
      isCancelled = true;
    };
  }, [blocks, showSolutions, onDimensionsDiscovered]);

  return previews;
}

