---
name: opensource-book
description: >
  Write a book that teaches readers an open-source project's source code and the engineering knowledge it embodies.
  Use this skill whenever the user wants to: create a book or guide for learning an open-source project,
  do a deep-dive write-up of a GitHub repository's architecture and design decisions, produce an mdBook-based
  technical book from source code analysis, or systematically document engineering patterns found in a codebase.
  Also trigger when the user says things like "help me write a book about this project", "I want to learn this
  repo by writing about it", "create a source code walkthrough book", "document the engineering knowledge in
  this codebase", or references an existing book project created by this skill. This skill covers the full
  lifecycle: project exploration, reader assessment, outline generation, chapter writing, and mdBook assembly.
---

# Open-Source Project Book Writer

Write a book that deeply explores an open-source project's source code and extracts the engineering knowledge within it. The book is both a learning artifact and a teaching artifact — writing it is how the reader (and author) truly understands the project.

The output is a Markdown-based ebook built with [mdBook](https://rust-lang.github.io/mdBook/).

## Core Principles

1. **Dimensions emerge from reading, not from templates.** The interesting engineering knowledge in a project is discovered during exploration, not prescribed upfront. A fixed dimension checklist produces documentation; dynamic discovery produces insight.
2. **Write like an engineer, not a textbook.** The tone is engineering notebook / technical blog — opinionated, exploratory, showing the "why" and the thought process, not just the "what."
3. **Source code is the ground truth.** External information (deepwiki, discussions) is a starting point, but every claim must be justified against actual code at a pinned version.
4. **Visuals serve understanding.** Diagrams, sequence charts, and architecture maps appear when they help the reader — never as decoration. Prefer HTML-coded diagrams; image generation prompts are an alternative.
5. **Lock the version, enable the future.** All source references include commit hash, file path, and line range, so readers can cross-reference and future editions can diff against updates.

---

## Workflow Overview

The book is produced in 6 phases. Each phase has defined inputs, actions, and outputs. Before starting, read `references/workflow.md` for the detailed phase-by-phase instructions.

```
Phase 0  Project Input ........... Capture repo, version, initial interests
Phase 1  Global Understanding .... Explore project, discover dimensions
Phase 2  Reader Assessment ....... Evaluate reader's knowledge gaps
Phase 3  Outline Generation ...... Produce and confirm the book skeleton
Phase 4  Chapter Writing ......... Write chapters with revision loop
Phase 5  Assembly ................ Build auxiliary sections + mdBook
```

### Quick Phase Summary

**Phase 0 — Project Input**
Receive the cloned repo path and the commit/tag to lock. Record the reader's initial interest dimensions (e.g., "Agent lifecycle", "plugin system"). Scan the project to produce a Project Info Card (language, scale, doc maturity).

**Phase 1 — Global Understanding**
Use deepwiki (`https://deepwiki.com/org/repo`) Q&A to efficiently gather high-level architecture info, then justify every finding against local source code. Dynamically discover engineering knowledge dimensions during this exploration. Produce a Global Understanding Document. deepwiki is used only in this phase.

**Phase 2 — Reader Assessment**
Design assessment questions based on the discovered dimensions. The reader answers them. Produce a Reader Profile that will influence content depth, prerequisite chapters, and chapter ordering.

**Phase 3 — Outline Generation**
Generate an outline draft using: initial interest dimensions + Global Understanding Document + Reader Profile. The reader reviews and adjusts. Each outline entry follows the format in `references/outline-spec.md`. The confirmed outline becomes SUMMARY.md.

**Phase 4 — Chapter Writing**
Write chapters one by one following the confirmed outline. Refer to `references/chapter-guide.md` for style, source citation format, and visual guidelines. If a new dimension is discovered mid-writing, trigger the **Outline Revision mechanism** (see below) before continuing.

**Phase 5 — Assembly**
Generate auxiliary sections (Project Overview ch.0, Glossary, Source File Index, Version Notes), assemble the full mdBook project, and verify the build.

---

## Outline Revision Mechanism

When a new engineering knowledge dimension is discovered during Phase 4:

1. Pause current chapter writing.
2. Propose an insertion plan: where the new chapter fits, what it covers, which existing chapters are affected.
3. Assess impact on the coherence of surrounding chapters (do transitions need updating? do cross-references break?).
4. Present the proposal to the reader for confirmation.
5. Upon approval, update SUMMARY.md and any affected chapter files, then resume writing.

The reader makes the final decision, but Claude owns the analysis and proposal.

---

## mdBook Project Structure

```
book-project/
├── book.toml
├── src/
│   ├── SUMMARY.md
│   ├── chapter-00-overview.md        # Project overview (generated in Phase 5)
│   ├── chapter-01-xxx.md             # Content chapters
│   ├── chapter-02-xxx.md
│   ├── ...
│   ├── glossary.md                   # Terminology definitions
│   ├── source-index.md               # Which source files appear in which chapters
│   └── version-notes.md              # Locked commit/tag, project version, writing date
└── assets/                           # Diagrams, generated images, etc.
```

---

## Reference Files

Read these before starting the corresponding phase:

| File | When to read | What it contains |
|------|-------------|-----------------|
| `references/workflow.md` | Before starting any phase | Detailed inputs, actions, outputs for each phase |
| `references/outline-spec.md` | Before Phase 3 | Outline entry format and chapter organization rules |
| `references/chapter-guide.md` | Before Phase 4 | Writing style, source citation format, visual guidelines, thought-question design |

---

## Getting Started

When the user triggers this skill, determine where they are in the workflow:

- **New project**: Start at Phase 0. Ask for the repo path, the commit/tag to lock, and their initial interest dimensions.
- **Resuming**: Identify which phase artifacts already exist (Project Info Card? Global Understanding Doc? Outline?) and resume from the next incomplete phase.
- **Specific phase**: If the user asks for a specific phase (e.g., "generate the outline"), check that prerequisite phases are complete, then proceed.

Always read `references/workflow.md` first to get the full phase details before executing any phase.
