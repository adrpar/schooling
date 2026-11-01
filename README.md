# Math Trainer — Projekt Rechenrally

A Python tool for generating unlimited, print-ready elementary school math exercise sheets as **SVG and PDF files**. Designed for teachers who need fresh material without manual effort.

---

## Installation

Install with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

After installation the `math-trainer` command is available inside the virtual environment:

```bash
# Activate the venv first, or prefix all commands with .venv/bin/
source .venv/bin/activate
math-trainer --help
```

---

## CLI Commands

All three commands share common `--output` and `--format` options and support `--seed` for reproducible sheets.

### Global usage

```
math-trainer [COMMAND] [OPTIONS]
```

---

### `addsub` — Written Addition / Subtraction (Schriftliche Rechnung)

Generates column-style written arithmetic worksheets on an A4 page.

```bash
math-trainer addsub [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output TEXT` | `addsub.svg` | Output SVG file name |
| `--format [svg\|pdf\|both]` | `both` | Output format |
| `--num-exercises INT` | `20` | Number of exercises per sheet |
| `--num-rows INT` | `2` | Operand rows per exercise (2 = standard addition/subtraction) |
| `--min-value INT` | `1` | Minimum operand value |
| `--max-value INT` | `9999` | Maximum operand / result value |
| `--operators TEXT` | `+-` | Operators as symbols, e.g. `+-`, `+*`, `+-*/` |
| `--seed INT` | *(random)* | Seed for reproducible output |

#### Examples

```bash
# 20 mixed add/sub exercises up to 999, PDF + SVG
math-trainer addsub --max-value 999 --format both --output sheet.svg

# 10 addition-only exercises, fixed seed for reproducibility
math-trainer addsub --num-exercises 10 --operators + --seed 42 --format svg

# Hard mixed sheet with all four operations
math-trainer addsub --operators "+-*/" --max-value 100 --num-rows 3
```

---

### `mathrally` — Math Rally (Rechenrally)

Generates a chain-calculation exercise (student sheet + solution sheet) from an Inkscape SVG template.

```bash
math-trainer mathrally [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output TEXT` | `rally.svg` | Output SVG for the student sheet |
| `--solution TEXT` | `rally_solution.svg` | Output SVG for the solution sheet |
| `--template TEXT` | `Rally1.svg` | Template file name or path (from `img/` or full path) |
| `--format [svg\|pdf\|both]` | `both` | Output format |
| `--min-value INT` | `1` | Minimum intermediate value in the chain |
| `--max-value INT` | `100` | Maximum intermediate value in the chain |
| `--operators TEXT` | `+-*/` | Operators as symbols, e.g. `+-`, `+*`, `+-*/` |
| `--seed INT` | *(random)* | Seed for reproducible output |

#### Examples

```bash
# Default rally (all four operators, Rally1.svg template)
math-trainer mathrally

# Addition/subtraction only, values 1–50, fixed seed
math-trainer mathrally --operators +- --max-value 50 --seed 123

# Use alternate template, SVG only
math-trainer mathrally --template Rally2.svg --format svg --output rally2.svg --solution rally2_sol.svg
```

---

### `zahlenmauer` — Number Wall / Addition Pyramid (Zahlenmauer)

Generates addition pyramid exercise sheets (student sheet + solution sheet).

```bash
math-trainer zahlenmauer [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output TEXT` | `zahlenmauer.svg` | Output SVG for the student sheet |
| `--solution TEXT` | `zahlenmauer_solution.svg` | Output SVG for the solution sheet |
| `--format [svg\|pdf\|both]` | `both` | Output format |
| `--base-size INT` | `4` | Bricks at the bottom row (3–10) |
| `--difficulty [easy\|medium\|hard]` | `medium` | How many bricks are revealed as clues |
| `--min-value INT` | `1` | Minimum base brick value |
| `--max-value INT` | *(auto)* | Maximum apex value; defaults to `max(100, 2^(base-1) * 10)` |
| `--num-pyramids INT` | *(auto)* | Pyramids per sheet; defaults to optimal count for `--base-size` |
| `--seed INT` | *(random)* | Seed for reproducible output |

#### Examples

```bash
# Default sheet: 4-brick base, medium difficulty
math-trainer zahlenmauer

# Large easy pyramid with fixed seed
math-trainer zahlenmauer --base-size 6 --difficulty easy --seed 99

# Small hard pyramid, SVG only
math-trainer zahlenmauer --base-size 3 --difficulty hard --format svg
```

---

## Prerequisites

This project requires **Inkscape** for SVG → PDF rendering.

### Installing Inkscape

1. Download from [inkscape.org](https://inkscape.org/release/).
2. Verify the installation:
   ```bash
   inkscape --version
   ```
3. If the command is not found, add Inkscape to your `PATH`:
   - **macOS**: Add to `~/.zshrc`:
     ```bash
     export PATH="/Applications/Inkscape.app/Contents/MacOS:$PATH"
     ```
   - **Windows**: Add the Inkscape install directory to the system `Path` variable.

---

## Developer Guide

### Running Tests

```bash
pytest
# or via uv:
uv run pytest
```

### Code Formatting

```bash
uv run black .
```

### Project Structure

```
Projekt Rechenrally/
├── img/                  # Inkscape SVG templates (Rally1.svg, Rally2.svg)
├── core/                 # Shared domain types (Operator enum)
├── exercises/
│   ├── addsub/           # Written add/sub exercise
│   ├── mathrally/        # Math Rally chain exercise
│   └── zahlenmauer/      # Addition Pyramid exercise
├── svg/                  # Shared SVG utilities (layout, styles, cell renderers)
│   └── number_paper/     # Grid cell + written calculation box
├── cli/                  # Click CLI entry points
├── math_trainer.py       # Root CLI dispatcher (math-trainer command)
└── tests/                # pytest test suite
```
