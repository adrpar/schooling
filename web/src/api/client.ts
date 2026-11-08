/**
 * src/api/client.ts
 * Type-safe API client generated from the OpenAPI contract via openapi-fetch.
 */

import createClient from 'openapi-fetch';
import type { paths } from './generated/schema';
import type {
  BlockPreviewRequest,
  BlockPreviewResponse,
  CatalogExerciseItem,
  SheetSpec,
  SheetSummary,
} from '../types/models';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const rawClient = createClient<paths>({ baseUrl: API_BASE_URL });

/**
 * Fetch list of all available exercise types and their schema parameters.
 */
export async function getCatalog(): Promise<CatalogExerciseItem[]> {
  const { data, error } = await rawClient.GET('/api/catalog');
  if (error || !data) {
    throw new Error(`Failed to load catalog: ${JSON.stringify(error)}`);
  }
  return data;
}

/**
 * Generate preview SVG for a single exercise block.
 */
export async function getBlockPreview(
  request: BlockPreviewRequest
): Promise<BlockPreviewResponse> {
  const { data, error } = await rawClient.POST('/api/blocks/preview', {
    body: request,
  });
  if (error || !data) {
    throw new Error(`Failed to generate block preview: ${JSON.stringify(error)}`);
  }
  return data;
}

/**
 * Render complete worksheet as an SVG string.
 */
export async function renderSheetSvg(spec: SheetSpec): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/sheet/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(spec),
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Failed to render sheet: ${errText}`);
  }
  return await response.text();
}

/**
 * Export worksheet as PDF blob and trigger browser download.
 */
export async function exportSheetPdf(spec: SheetSpec): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/sheet/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(spec),
  });
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Failed to export PDF: ${errText}`);
  }
  return await response.blob();
}

/**
 * List all saved worksheets from SQLite storage.
 */
export async function listSavedSheets(): Promise<SheetSummary[]> {
  const { data, error } = await rawClient.GET('/api/sheets');
  if (error || !data) {
    throw new Error(`Failed to list sheets: ${JSON.stringify(error)}`);
  }
  return data;
}

/**
 * Save or update a worksheet in SQLite storage.
 */
export async function saveSheetSpec(spec: SheetSpec): Promise<SheetSpec> {
  const { data, error } = await rawClient.POST('/api/sheets', {
    body: spec,
  });
  if (error || !data) {
    throw new Error(`Failed to save sheet: ${JSON.stringify(error)}`);
  }
  return data;
}

/**
 * Load a worksheet specification by ID.
 */
export async function loadSheetSpec(sheetId: string): Promise<SheetSpec> {
  const { data, error } = await rawClient.GET('/api/sheets/{sheet_id}', {
    params: { path: { sheet_id: sheetId } },
  });
  if (error || !data) {
    throw new Error(`Failed to load sheet ${sheetId}: ${JSON.stringify(error)}`);
  }
  return data;
}

/**
 * Delete a worksheet specification by ID.
 */
export async function deleteSheetSpec(sheetId: string): Promise<boolean> {
  const { error } = await rawClient.DELETE('/api/sheets/{sheet_id}', {
    params: { path: { sheet_id: sheetId } },
  });
  if (error) {
    throw new Error(`Failed to delete sheet ${sheetId}: ${JSON.stringify(error)}`);
  }
  return true;
}
