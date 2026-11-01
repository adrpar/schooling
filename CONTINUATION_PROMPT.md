# Continuation Prompt — Projekt Rechenrally

Use this prompt to pick up where we left off in a new Antigravity IDE session.

---

## Paste this as your first message:

---

We are pair programming on **Projekt Rechenrally** — a Python tool for generating
printable elementary school math exercise sheets as SVG/PDF files, aimed at teachers.

Read `GROUNDING.md` in the project root first — it contains the full codebase map,
architecture decisions, and all flagged code quality issues.

### Where we are

We have done an initial exploration of the codebase. The project has two working exercise types:

1. **Math Rally** (`mathrally/`) — chain-calculation exercises using Inkscape SVG template injection.
2. **Written Add/Sub** (`addSubWritten/`) — column-form arithmetic built programmatically cell-by-cell from number-paper grid squares.

Shared infrastructure lives in `svg/` (SVG file I/O, layout engine, grid cells).
CLI entry points are in `cli/` using Click. PDF export goes through Inkscape via `inkex`.

### What we want to do next

We want to **build a new exercise type**. Before we do, we should resolve a few open
architectural questions from GROUNDING.md §8:

- **D5**: Where should the shared `Operator` enum live? (currently duplicated in both algorithm modules)
- **D7**: Should new exercise types get their own top-level directory (current pattern) or move to `exercises/<type>/`?

Then pick the cleanest code-quality fix to do *as we go* (see §7 in GROUNDING.md) — 
likely **Q1** (deduplicate Operator enum) and **Q5** (replace debug prints with logging)
before we add more code.

The working style is: discuss decisions before implementing, keep GROUNDING.md updated
as we settle things, and address quality flags incrementally as we touch related code.

---
