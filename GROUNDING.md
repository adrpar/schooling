# Projekt Rechenrally — Grounding Document

> **Living document.** Updated as we make decisions together. Decisions are marked ✅ when settled.

---

## 1. Project Vision

A Python-based tool for generating unlimited, print-ready elementary school math exercise sheets as **SVG and PDF files**. The primary audience today is **teachers** who need fresh material without manual effort.

### Current scope (what we build now)
- One exercise type per page, generated via CLI.
- Output: A4 SVG → exported to PDF via Inkscape.
- Exercise types built entirely in SVG (programmatically constructed or via Inkscape-designed templates).

### Future scope (background context, not building yet)
- **Multi-exercise sheet editor** — drag/drop SVG areas, mix exercise types on one page (teacher-facing).
- **Student web portal** — self-serve page where students generate & download unlimited sheets.
- SVG remains the core rendering primitive throughout.

---

## 2. Codebase Map

### Repository root
```
Projekt Rechenrally/
├── img/                  # Inkscape-designed SVG templates (Rally1.svg, Rally2.svg)
├── core/                 # Shared domain types (Operator enum)
├── exercises/            # All exercise-type implementations
│   ├── mathrally/        # Exercise type: Math Rally (chain calculations)
│   ├── addsub/           # Exercise type: Written addition/subtraction (column form)
│   └── zahlenmauer/      # Exercise type: Zahlenmauer / Addition Pyramid
├── svg/                  # Shared SVG utilities (file I/O, layout engine, grid cells)
│   └── number_paper/     # Number-paper grid cells + written calculation box
├── cli/                  # Click CLI entry points (mathrally.py, addsub.py, zahlenmauer.py)
├── math_trainer.py       # Root CLI dispatcher — registers all sub-commands as `math-trainer`
└── tests/                # pytest suite (67 tests)
```

### Packages & dependency flow

```
math_trainer.py     ─→  cli/mathrally.py    ─→  exercises/mathrally/    ─→  svg/
                    │                                                    └── core/
                    ├── cli/addsub.py       ─→  exercises/addsub/       ─→  svg/
                    │                                                   │   └── number_paper/
                    │                                                   └── core/
                    └── cli/zahlenmauer.py  ─→  exercises/zahlenmauer/  ─→  svg/
```

---

## 3. Exercise Types

### 3.1 Math Rally (`exercises/mathrally/`)
**What it is:** A chain of arithmetic operations displayed in a pre-designed Inkscape SVG template. Each step shows an operator+operand arrow, with boxes for intermediate results. A *student* sheet (blanks) and a *solution* sheet are both generated.

| Component | File | Role |
|-----------|------|------|
| Algorithm | `exercises/mathrally/algorithm.py` | Generates a random chain of operations with seeded RNG. Validates no trivial cancellations and results stay in `[min, max]`. |
| Structural constants | `exercises/mathrally/mathrally.py` | `TEMPLATE_PATH` and `TEMPLATE_NAME` only. All tunable params are CLI options. |
| Template | `exercises/mathrally/template.py` | Loads an Inkscape SVG (default: `img/Rally1.svg`), injects values/operators into SVG text elements by ID convention (`value.N`, `operatorText.N`). Inherits from `CanvasExerciseTemplate`. |
| SVG templates | `img/Rally1.svg`, `img/Rally2.svg` | Inkscape-designed A4 layouts. IDs like `value.0`…`value.9` are the injection targets. |

**Architecture pattern:** "Template injection" — an Inkscape file holds the visual layout; Python finds elements by ID and sets their `.text`.

### 3.2 Written Add/Sub (`exercises/addsub/`)
**What it is:** Column-style written arithmetic (Schriftliche Rechenweise) — multiple exercises placed on an A4 page, each rendered as a grid of number-paper cells.

| Component | File | Role |
|-----------|------|------|
| Algorithm | `exercises/addsub/algorithm.py` | Generates N exercises, each with M operand rows. Ensures no negative results for subtraction. |
| Legacy stub | `exercises/addsub/addsub.py` | Documentation stub only — `main()` and all config constants removed. Kept to avoid accidental import breaks. |
| Template | `exercises/addsub/template.py` | Creates a blank A4 canvas programmatically (via `CanvasExerciseTemplate`), generates `WrittenCalcExerciseBox` SVG groups, distributes them on the page. |
| Cell renderer | `svg/number_paper/paper_cell.py` | `NumericalPaperCell` — one grid square built from programmatic `lxml.etree` prototypes with `text-anchor: middle` centering. |
### 3.3 Zahlenmauer (`exercises/zahlenmauer/`)
**What it is:** Addition Pyramids / Number Walls (Zahlenmauer / Rechenmauer) — classic elementary school math puzzles where each brick is the sum of the two bricks directly underneath it. Features configurable base size, difficulty levels (`easy`, `medium`, `hard`), and guaranteed solvability verification via student-deduction simulation. Generates both student sheets (with blanks) and solution sheets (answers highlighted).

| Component | File | Role |
|-----------|------|------|
| Difficulty | `exercises/zahlenmauer/difficulty.py` | `Difficulty` enum (`EASY`, `MEDIUM`, `HARD`). |
| Algorithm & Solver | `exercises/zahlenmauer/algorithm.py` | `ZahlenmauerAlgorithm` (random full wall generation, upper bound apex checks), `ZahlenmauerSolver` (simulates step-by-step addition/subtraction and algebraic deduction), and mask generator. |
| Template | `exercises/zahlenmauer/template.py` | `ZahlenmauerTemplate` — builds staggered horizontal brickwork groups, sets fill/text colors for clues vs blanks vs solutions, and distributes multiple pyramids across the A4 canvas. |
| SVG blank | `exercises/zahlenmauer/drawing.svg` | A4 canvas with title, footer, and `drawingArea` rect. |

**Architecture pattern:** "Programmatic SVG construction with canvas template" — renders geometric brickwork into SVG elements and lays them out via the shared layout engine.

---

## 4. Shared Infrastructure (`svg/`)

| File | What it does |
|------|-------------|
| `svg_handler.py` | `NAMESPACE_MAP` — single canonical SVG namespace mapping. Completely encapsulates `lxml.etree`. `SvgElement` — clean Pythonic wrapper around SVG elements with DOM manipulation, builder methods (`create_child`), and XPath querying. `SvgDocument` — encapsulates SVG document loading, parsing, cloning, and writing. `SVGFile` & `SvgNode` — legacy adapters. `render_svg_to_pdf()` — calls Inkscape via `inkex.command` with auto-discovery on macOS/Linux. |
| `canvas_template.py` | `CanvasExerciseTemplate` — unified base class for all exercise templates (`AddSub`, `Zahlenmauer`, `RallyTemplate`). Dynamically creates A4 canvas SVG documents from code or loads template files, standardizes header/footer management, provides layout packing into `drawingArea`, and generic text/number helpers (`center_text_in_rect`, `center_text_in_circle`, `calc_adaptive_font_size`, `highlight_solution_box`). |
| `svg_groups.py` | `calculate_group_dimensions()` — recursive bounding-box calculation from transforms, supporting `<rect>`, `<line>`, `<circle>`, `<ellipse>`. `distribute_groups_in_drawing_area()` — row-based layout engine with justified spacing, cached bboxes, and overflow warnings. |
| `number_paper/paper_cell.py` | `NumericalPaperCell` — grid cell built from programmatic prototypes (`SvgElement`) with `text-anchor: middle` auto-centering. |
| `number_paper/written_calc_exercise_box.py` | Full column-calculation box assembled from cells and separator lines using `SvgElement`. Uses `Operator` from `core.operators` and `NAMESPACE_MAP` from `svg_handler`. |

---

## 4b. Shared Domain Types (`core/`)

| File | What it does |
|------|-------------|
| `core/operators.py` | `Operator` enum — single source of truth for `ADDITION`, `SUBTRACTION`, `MULTIPLICATION`, `DIVISION`. Imported by both exercise algorithms, templates, and tests. |
| `exercises/utils.py` | `operator_to_string()` — converts a list of `Operator` values to a display string (e.g. `[+, -]` → `'+-'`). |

---

## 5. CLI Layer (`cli/`)

All commands use **Click** and are registered under the `math-trainer` console script (entry point in `pyproject.toml` → `math_trainer:cli`).

Common options on all commands: `--output`, `--format` (`svg`/`pdf`/`both`), `--seed`.

| Command | File | Key options |
|---------|------|-------------|
| `addsub` | `cli/addsub.py` | `--num-exercises`, `--num-rows`, `--min-value`, `--max-value`, `--operators` |
| `mathrally` | `cli/mathrally.py` | `--solution`, `--template`, `--min-value`, `--max-value`, `--operators` |
| `zahlenmauer` | `cli/zahlenmauer.py` | `--solution`, `--base-size`, `--difficulty`, `--min-value`, `--max-value`, `--num-pyramids` |

PDF export: Inkscape is invoked via `inkex.command.inkscape()`. A temp SVG is written when `--format pdf` is requested without an explicit SVG output file.

---

## 6. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `lxml` | ≥5.3 | SVG XML parsing & construction |
| `inkex` | ≥1.4.1 | Inkscape Python API — PDF export via `inkex.command` |
| `click` | ≥8.1.8 | CLI argument parsing |
| `black` | ≥26.5 | Code formatter (dev group) |
| `pytest` | ≥9.1 | Test runner (dev group) |
| Python | ≥3.12 | Runtime |
| **Inkscape** (system) | — | PDF rendering (external binary dependency; auto-discovered from PATH or macOS `/Applications/Inkscape.app`) |

Package and project management is fully consolidated under **`uv`** via `pyproject.toml` and `uv.lock`.

---

## 7. Code Quality Observations & Improvement Flags

These are tracked here and will be addressed as we go. Each flag gets a status.

### 🔴 High Priority

| # | Issue | Location | Notes |
|---|-------|----------|-------|
| Q1 | ~~**Duplicated `Operator` enum**~~ | ~~`mathrally/algorithm.py` and `addSubWritten/algorithm.py`~~ | ✅ **Resolved.** Canonical `Operator` now lives in `core/operators.py` and is imported everywhere. |
| Q2 | ~~**Hardcoded config mixed into module files**~~ | ~~`exercises/addsub/addsub.py`, `exercises/mathrally/mathrally.py`~~ | ✅ **Resolved.** All tunable parameters (`SEED`, `MAX_VALUE`, `OPERATORS`, etc.) are now exposed as CLI options with documented defaults. Module files contain only structural constants. |
| Q3 | ~~**Template path hardcoded as relative string**~~ | ~~`addSubWritten/template.py` L16~~ | ✅ **Resolved.** `exercises/addsub/template.py` now uses `pathlib.Path(__file__).parent / "drawing.svg"`. |
| Q4 | ~~**`exercises/addsub/addsub.py` is both a config file and a legacy entry point**~~ | ~~`exercises/addsub/addsub.py`~~ | ✅ **Resolved.** `main()` and all hardcoded config constants removed. File is now a documentation stub. |
| Q5 | ~~**`debug print()` statements in algorithm**~~ | ~~`mathrally/algorithm.py`, `addSubWritten/algorithm.py`~~ | ✅ **Resolved.** Both algorithm files now use `logging.getLogger(__name__).debug(...)`. |
| Q19 | ~~**`RallyAlgorithm` start value ignores `min_value`**~~ | ~~`exercises/mathrally/algorithm.py`~~ | ✅ **Resolved.** Uses `self.rng.randrange(self.min_value, max(self.min_value + 1, self.max_value))`. |
| Q20 | ~~**`RallyAlgorithm` division produces `float`**~~ | ~~`exercises/mathrally/algorithm.py`~~ | ✅ **Resolved.** Uses integer division `//` ensuring all intermediate chain results are `int`. |
| Q21 | ~~**Global RNG pollution (`random.seed`)**~~ | ~~`exercises/mathrally/algorithm.py`, `exercises/addsub/algorithm.py`~~ | ✅ **Resolved.** Both algorithms now use an isolated `self.rng = random.Random(seed)` instance. |
| Q22 | ~~**`AddSubAlgorithm` subtraction logic overcomplicated + dead code**~~ | ~~`exercises/addsub/algorithm.py`~~ | ✅ **Resolved.** Dead code removed; simplified check to `values[0] - sum(values[1:]) >= 0` with no `deepcopy`. |
| Q23 | ~~**Premature infinite-loop bailout (`counter > 10`)**~~ | ~~Both algorithm modules~~ | ✅ **Resolved.** Increased attempt threshold to 100 with improved candidate generation. |

### 🟡 Medium Priority

| # | Issue | Location | Notes |
|---|-------|----------|-------|
| Q6 | ~~**Duplicated `NAMESPACE_MAP`**~~ | ~~`svg_handler.py`, `written_calc_exercise_box.py`, `paper_cell.py`~~ | ✅ **Resolved.** Defined as single module-level constant in `svg/svg_handler.py` and imported everywhere. |
| Q7 | ~~**`distribute_groups_in_drawing_area` silently drops exercises**~~ | ~~`svg/svg_groups.py`~~ | ✅ **Resolved.** Now logs a warning with count of dropped exercises when height is exceeded. |
| Q8 | ~~**`_get_operator_string` duplicated**~~ | ~~`mathrally/template.py`, `addSubWritten/template.py`~~ | ✅ **Resolved.** Extracted to `exercises/utils.py` as `operator_to_string()`. Both templates now call the shared function. |
| Q9 | ~~**`SVGFile.find_all_elements_by_attributes` crashes if element lacks the attribute**~~ | ~~`svg/svg_handler.py`~~ | ✅ **Resolved.** Added `if attribute in element.attrib` guard. |
| Q10 | ~~**`calculate_group_dimensions` only handles `translate()` transforms**~~ | ~~`svg/svg_groups.py`~~ | ✅ **Resolved.** Replaced regex parsing with `inkex.transforms.Transform` applying full affine transforms (`translate`, `rotate`, `scale`, `matrix`, `skew`) across nested groups and primitives. |
| Q11 | ~~**Multiple package management systems**~~ | ~~Root~~ | ✅ **Resolved.** Consolidated solely on `uv` + `pyproject.toml`. Removed Pipfile, Pipfile.lock, requirements.txt, setup.py. |
| Q12 | ~~**`tool>=0.8.0` in dependencies**~~ | ~~`pyproject.toml`~~ | ✅ **Resolved.** Removed unused `tool` dependency and its transitive packages. |
| Q13 | ~~**`__init__.py` contents**~~ | ~~`exercises/*/`, `core/`, `svg/`~~ | ✅ **Resolved.** Comprehensive public API docstrings and `__all__` exports documented across all packages. |
| Q24 | ~~**Ad-hoc operand generation for `*` and `/` in `RallyAlgorithm`**~~ | ~~`exercises/mathrally/algorithm.py`~~ | ✅ **Resolved.** Multiplication picks multipliers in `2..10`; division chooses from exact integer divisors of `curr_val`. |
| Q25 | ~~**`NumericalPaperCell` re-parses XML string on every cell instantiation**~~ | ~~`svg/number_paper/paper_cell.py`~~ | ✅ **Resolved.** Builds prototype elements programmatically once with `lxml.etree` and deep-copies per cell. |
| Q26 | ~~**`distribute_groups_in_drawing_area` redundant bbox calculations & duplicated code**~~ | ~~`svg/svg_groups.py`~~ | ✅ **Resolved.** Bboxes cached once per element; shared `_flush_row()` helper deduplicates row layout. |
| Q27 | ~~**`calculate_group_dimensions` ignores non-rect primitives**~~ | ~~`svg/svg_groups.py`~~ | ✅ **Resolved.** `_element_bbox()` handles `<line>` (x1/y1/x2/y2), `<circle>`, `<ellipse>`, and rects. |
| Q28 | ~~**Magic coordinate nudges in `NumericalPaperCell`**~~ | ~~`svg/number_paper/paper_cell.py`~~ | ✅ **Resolved.** Switched text to `text-anchor: middle` at cell center (`x=2.943`). Operators center automatically. |

### 🟢 Low Priority / Nice to Have

| # | Issue | Location | Notes |
|---|-------|----------|-------|
| Q14 | ~~**No type hints**~~ | ~~All modules~~ | ✅ **Resolved.** Type annotations added across all domain, SVG, and CLI modules; `mypy` and `lxml-stubs` added to dev dependencies, passing with 0 errors and wired into CI. |
| Q15 | ~~**`_set_text(element, text)` uses `element[0]`**~~ | ~~`mathrally/template.py`~~ | ✅ **Resolved** (implicitly via refactoring). The old `_set_text` method was removed during the `RallyTemplate` refactor. |
| Q16 | **Test coverage is integration-only** | `tests/` | Expanded unit tests for algorithms, transforms, and SVG components; full suite now **71 tests**. |
| Q17 | ~~**Output SVG files checked into root**~~ | ~~Root~~ | ✅ **Resolved.** `.gitignore` ignores generated `*.svg`, `*.pdf`, and `output.png` while preserving template SVGs. |
| Q18 | ~~**Inline SVG string template in `paper_cell.py`**~~ | ~~`svg/number_paper/paper_cell.py`~~ | ✅ **Resolved.** Replaced by clean programmatic `lxml.etree` element creation. |

---

## 8. Architecture Decisions (Settled ✅ / Open ❓)

| # | Decision | Status | Notes |
|---|----------|--------|-------|
| D1 | SVG as the core rendering primitive, PDF via Inkscape | ✅ | Confirmed. Both exercise types use SVG. |
| D2 | Two flavours of SVG generation: *template injection* (Rally) vs *programmatic construction* (AddSub) | ✅ | Both approaches coexist. Template injection is better for visually rich layouts; programmatic is better for grid-based content. |
| D3 | A4 portrait as the standard page format | ✅ | All templates are 210×297mm. |
| D4 | Seeded RNG for reproducibility | ✅ | Both algorithms accept a seed, making sheets reproducible by seed+config. This is a key feature for teachers. |
| D5 | Where to define the shared `Operator` enum | ✅ | Lives in `core/operators.py`. Imported by all algorithm and template modules. |
| D6 | Package management: `uv` vs `pip` | ✅ | Settled on `uv` as the single package manager. `pyproject.toml` is canonical with `[dependency-groups]` for dev. |
| D7 | New exercise type structure | ✅ | All exercise types live under `exercises/<type>/`. Existing types (`mathrally`, `addsub`) moved. New types follow the same pattern. |
| D8 | CLI parameter exposure | ✅ | All exercise-specific params (`--seed`, `--min-value`, `--max-value`, `--operators`, `--num-exercises`, `--num-rows`, `--difficulty`, etc.) are now exposed as Click CLI options with sensible defaults. No external config file needed. |

---

## 9. Next Steps (Agreed Order of Work)

1. ✅ **Phase 0: Architecture & Structural Foundation**
   - Settle D5 & D7: create `core/operators.py` and `exercises/<type>/` structure.
   - Resolve Q1 (dedup Operator), Q3 (pathlib template), Q5 (logging), Q8 (shared operator string helper).
   - Resolve Inkscape auto-discovery on macOS & 100% test pass.
2. ✅ **Phase 1: Math Algorithms Clean-up & Hardening**
   - Resolved Q19, Q20, Q21, Q22, Q23, Q24.
   - Isolated RNG instances, int division, clean subtraction verification, increased attempt limits.
   - Added unit tests for bounds, int types, and RNG isolation (38/38 passing).
3. ✅ **Phase 2: SVG Layout & Cell Engine Streamlining**
   - Resolved Q6, Q7, Q9, Q18, Q25, Q26, Q27, Q28.
   - Programmatic cell prototyping, text centering without offsets, cached bbox calculations, non-rect support, overflow logging.
4. ✅ **Phase 3: Design & Build Next Exercise Type (Zahlenmauer)**
   - Added `exercises/zahlenmauer/` with `Difficulty` enum (`easy`, `medium`, `hard`).
   - Implemented full pyramid generator, deduction-based solvability solver, and difficulty-guided masking.
   - Built programmatic SVG staggered brickwork template and integrated with A4 layout engine.
   - Added `cli/zahlenmauer.py` registered in `math_trainer.py`.
   - Added unit and CLI test suite (67/67 tests passing after Phase 4).
5. ✅ **Phase 4: CLI Configuration & Packaging Polish**
   - ✅ Q2: All tunable params (`--seed`, `--min-value`, `--max-value`, `--operators`, `--num-exercises`, `--num-rows`, `--difficulty`, etc.) exposed as Click CLI options.
   - ✅ Q4: Legacy `main()` and hardcoded config constants removed from `exercises/addsub/addsub.py`.
   - ✅ Q15: `_set_text()` confirmed removed (implicitly resolved during `RallyTemplate` refactor).
   - ✅ D8: Settled — CLI options with documented defaults are the config layer; no config file needed.
   - ✅ `math-trainer` registered as a `[project.scripts]` console entry point in `pyproject.toml`.
   - ✅ Renamed `math-trainer.py` → `math_trainer.py` for Python importability.
   - ✅ README fully rewritten: option tables and examples for all three commands.
   - ✅ All 67 tests passing.
6. ✅ **Phase 5: Code Quality — Type Hints & API Documentation**
   - ✅ Q10: Full SVG transform matrix support in `calculate_group_dimensions` (`translate`, `rotate`, `scale`, `matrix`, `skew`).
   - ✅ Q13: Documented public API across `exercises/`, `exercises/*/`, `core/`, and `svg/` `__init__.py` files.
   - ✅ Q14: Added comprehensive type annotations across `core/`, `exercises/`, `svg/`, `cli/`, `math_trainer.py`. Added `mypy` & `lxml-stubs` to dev dependencies with 0 type errors, and wired `mypy` type checking into GitHub Actions CI.
   - ✅ Suite expanded to 71 tests, all passing.
7. **Phase 6: Multi-Exercise Sheet Editor (MVP)** *(in progress)*
   - ✅ Backend: FastAPI app in `server/app.py` with multi-block A4 composer (`server/composer.py`).
   - ✅ Persistence: SQLite database (`server/db.py`) storing sheet specifications with full CRUD endpoints.
   - ✅ Endpoints: `/api/catalog`, `/api/blocks/preview`, `/api/sheet/render`, `/api/sheet/pdf`, `/api/sheets`.
   - ✅ Testing: 78 tests passing (including 7 backend integration tests).
   - ✅ Guidelines: Comprehensive frontend architecture and maintainability guidelines in `docs/frontend_architecture_guidelines.md`.
   - 🔄 Next: Frontend implementation in `web/` using React, Vite, TypeScript, and the modular Exercise Plugin architecture.

---

## 10. Glossary

| Term | Meaning |
|------|---------|
| **Rechenrally** | "Math Rally" — a chain-calculation exercise where students compute step-by-step |
| **Schriftliche Rechnung** | "Written calculation" — column-form arithmetic (the `addSubWritten` exercise type) |
| **Number paper** | Grid paper where each cell is a fixed-size square for one digit |
| **Template injection** | Pattern where an Inkscape SVG file is loaded and text elements are replaced by ID |
| **Programmatic SVG** | Pattern where SVG elements are created from scratch using `lxml.etree` |
| **Seed** | Random seed passed to `random.seed()` — same seed + same config = identical exercise sheet |
