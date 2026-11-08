# Frontend Code Architecture & Maintainability Guidelines
## Multi-Exercise Sheet Editor

> **Target Audience:** Maintainers and developers, especially those without extensive TypeScript background.  
> **Core Principle:** *Modularity is King.* Code must be simple to understand, modular to extend, completely tested, and resilient to changes.

---

## 1. Guiding Principles

1. **Keep TypeScript Simple and Explicit ("No Type Wizardry")**:
   - Write standard, readable TypeScript that looks like plain JavaScript with type hints.
   - **Do:** Use simple interfaces, type aliases, and optional fields (`field?: string`).
   - **Don't:** Use conditional types, mapped types, recursive generics, or `any` unless absolutely necessary.
   - If a type error is difficult to read or solve, write out the explicit structure rather than relying on complex type inference.

2. **Modularity via the Plugin / Registry Pattern**:
   - The core canvas, drag-and-drop system, and export toolbar must **never** hardcode exercise types (e.g. no `if (block.type === 'zahlenmauer')`).
   - Every exercise type is an isolated module conforming to a standard `ExercisePlugin` contract.
   - Adding a new exercise type requires creating one self-contained directory and registering it in a single central registry.

3. **Backend-Driven Flexibility**:
   - The backend is the source of truth for parameter schemas and geometry calculations.
   - New parameters added to Python algorithms automatically appear in the frontend UI without rewriting React components.

4. **100% Tested Core Interactions**:
   - All state management, coordinate math, plugin registration, and critical components must have automated Vitest + React Testing Library tests.

---

## 2. Directory Structure

```
web/
├── public/                 # Static assets (favicons, blank SVG icons)
├── src/
│   ├── api/                # API client calls (fetch/axios) to FastAPI backend
│   │   ├── client.ts       # Typed HTTP client
│   │   ├── catalog.ts      # GET /api/catalog
│   │   ├── render.ts       # POST /api/sheet/render, /api/sheet/pdf
│   │   └── sheets.ts       # CRUD /api/sheets (SQLite)
│   ├── components/         # Generic, reusable UI components
│   │   ├── Canvas/         # Interactive A4 SVG canvas viewer
│   │   │   ├── A4Canvas.tsx
│   │   │   ├── BlockOverlay.tsx   # Selection outline, drag handles
│   │   │   └── ZoomControls.tsx
│   │   ├── Header/         # Sheet title, date/name toggles
│   │   ├── Palette/        # Exercise picker sidebar
│   │   ├── Inspector/      # Dynamic block property editor
│   │   │   ├── PropertyInspector.tsx
│   │   │   └── FieldRenderers.tsx # Generic slider, number, select inputs
│   │   └── Toolbar/        # Export PDF, solution toggle, save/load
│   ├── exercises/          # PLUGINS: Isolated exercise definitions
│   │   ├── registry.ts     # Central registry of all exercise types
│   │   ├── zahlenmauer/    # Specific UI customizations for Zahlenmauer
│   │   ├── addsub/         # Specific UI customizations for AddSub
│   │   ├── mathrally/      # Specific UI customizations for Math Rally
│   │   └── custom_svg/     # Custom user SVG element / sticker plugin
│   ├── hooks/              # Custom React hooks (clean state isolation)
│   │   ├── useSheetState.ts   # Core state: blocks, selection, history (undo/redo)
│   │   ├── useDragPosition.ts # Screen px <-> A4 mm coordinate translation
│   │   └── useSheetExport.ts  # Download SVG/PDF actions
│   ├── types/              # Common data models matching FastAPI Pydantic schemas
│   │   ├── sheet.ts        # SheetSpec, ExerciseBlock, HeaderSpec
│   │   └── catalog.ts      # CatalogExerciseItem, CatalogParam
│   ├── App.tsx             # Main layout shell
│   └── main.tsx            # Vite entry point
├── tests/                  # Vitest unit & component test suite
│   ├── registry.test.ts
│   ├── coordinates.test.ts
│   ├── A4Canvas.test.tsx
│   └── PropertyInspector.test.tsx
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 3. The Exercise Plugin Architecture

To add or modify an exercise type, developers only interact with `src/exercises/`.

### 3.1 The `ExercisePlugin` Contract

```typescript
// src/exercises/types.ts
export interface ExercisePlugin {
  /** Unique key matching the backend ExerciseType enum (e.g. 'zahlenmauer') */
  type: string;

  /** Human-readable display name */
  name: string;

  /** Category for palette grouping ('Arithmetic', 'Puzzles', 'Custom') */
  category: string;

  /** Default width and height on canvas in millimeters */
  defaultSize: { width: number; height: number };

  /** Default exercise parameters */
  defaultParams: Record<string, any>;

  /** Optional icon or preview component */
  icon?: string;

  /**
   * Optional custom property editor component.
   * If omitted, a generic form is automatically generated from the backend parameter schema!
   */
  CustomInspector?: React.FC<ExerciseInspectorProps>;
}

export interface ExerciseInspectorProps {
  params: Record<string, any>;
  onChange: (updatedParams: Record<string, any>) => void;
}
```

### 3.2 The Registry (`src/exercises/registry.ts`)

```typescript
import { ExercisePlugin } from './types';
import { zahlenmauerPlugin } from './zahlenmauer';
import { addSubPlugin } from './addsub';
import { mathRallyPlugin } from './mathrally';
import { customSvgPlugin } from './custom_svg';

export const exerciseRegistry: Record<string, ExercisePlugin> = {
  zahlenmauer: zahlenmauerPlugin,
  addsub: addSubPlugin,
  mathrally: mathRallyPlugin,
  custom_svg: customSvgPlugin,
};

export function getPlugin(type: string): ExercisePlugin | undefined {
  return exerciseRegistry[type];
}

export function getAllPlugins(): ExercisePlugin[] {
  return Object.values(exerciseRegistry);
}
```

---

## 4. Supporting Custom SVG Elements & User Templates

### 4.1 Custom SVG Element Plugin (`custom_svg`)
Teachers often want to insert custom diagrams, stickers, instructions, or reward icons onto a worksheet.
We treat `custom_svg` as a first-class exercise plugin:
- **Parameters**: `svgCode: string`, `label?: string`.
- **Backend handling**: The backend composer parses the raw SVG snippet and wraps it in a positioned `<g>` with bounding box calculation.
- **Frontend Inspector**: Provides an SVG code paste box or file uploader.

### 4.2 Custom Page Templates (Background Layouts)
Worksheets can use either the standard blank A4 canvas or a user-provided SVG template:
- `SheetSpec.template`: `null | string` (name or ID of template).
- Backend `/api/templates`:
  - Lists pre-installed templates (`Rally1.svg`, `Rally2.svg`, `blank_a4`).
  - Allows uploading a custom SVG template saved in SQLite or storage.
- When rendering, `SheetComposer` uses the chosen template as the canvas base.

---

## 5. Dynamic Parameter Editing ("Special Parameters")

Different exercises require distinct controls:
1. **Schema-Driven (Default)**:
   - For 90% of exercises, the frontend automatically builds input controls from the backend `CatalogExerciseParam` metadata:
     - `type: "int"` → Number stepper with `min`/`max`.
     - `type: "select"` → Dropdown menu.
     - `type: "bool"` → Toggle switch.
     - `type: "string"` → Text input.
2. **Specialized Custom Inspectors**:
   - If an exercise needs a custom interactive widget (e.g., clicking on specific bricks in a Zahlenmauer to toggle clue visibility, or a visual operator chip selector for AddSub), provide a `CustomInspector` in `src/exercises/<type>/Inspector.tsx`.
   - The registry automatically delegates to `CustomInspector` when present.

---

## 6. Coordinate Math & Canvas Mechanics

- **World Space (A4 Millimeters)**:
  - Page is 210mm wide × 297mm high.
  - All positions stored in `SheetSpec` are in millimeters (`x`, `y`).
- **Screen Space (Pixels)**:
  - SVG viewBox: `viewBox="0 0 210 297"`.
  - SVG element has CSS scaling (`preserveAspectRatio="xMidYMid meet"`).
- **Coordinate Conversion**:
  ```typescript
  // Simple, readable coordinate conversion utility
  export function screenToCanvasMm(
    screenDeltaX: number,
    screenDeltaY: number,
    svgElement: SVGSVGElement
  ): { dxMm: number; dyMm: number } {
    const rect = svgElement.getBoundingClientRect();
    const scaleFactor = 210 / rect.width; // 210 mm width
    return {
      dxMm: screenDeltaX * scaleFactor,
      dyMm: screenDeltaY * scaleFactor,
    };
  }
  ```

---

## 7. State Management Philosophy

- **Centralized Sheet Hook (`useSheetState`)**:
  - Keep state in one straightforward custom React hook instead of complex external Redux or MobX stores.
  - Actions: `addBlock(type, x, y)`, `updateBlock(id, changes)`, `deleteBlock(id)`, `selectBlock(id)`, `undo()`, `redo()`.
  - State is serializable directly to/from `SheetSpec` JSON.

---

## 8. Testing Strategy

1. **Unit Tests (`tests/*.test.ts`)**:
   - `registry.test.ts`: Asserts all plugins declare valid defaults and unique keys.
   - `coordinates.test.ts`: Verifies coordinate conversion and boundary clamping (cannot drag off page).
2. **Component Tests (`tests/*.test.tsx`)**:
   - `PropertyInspector.test.tsx`: Tests that changing a slider updates the block parameters.
   - `A4Canvas.test.tsx`: Tests block rendering and selection on click.
3. **API Integration Tests**:
   - Mock backend requests using `msw` (Mock Service Worker) to ensure the UI behaves properly when offline or on error.
