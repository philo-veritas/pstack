# Outline Specification

This document defines the format and rules for the book outline.

---

## Chapter Entry Format

Every chapter in the outline must include these fields:

```markdown
## Chapter N: [Title]

- **Core Concept**: The single concept this chapter explains thoroughly.
  If you can't state it in one sentence, the chapter scope is too broad — split it.
- **Internal References**: Source code files relevant to this chapter.
  List file paths relative to the repo root.
  ```
  - src/agent/lifecycle.ts
  - src/agent/types.ts
  - src/scheduler/queue.ts
  ```
- **External References**: Topics to search/research outside the codebase.
  These become research tasks before writing the chapter.
  ```
  - Actor model concurrency pattern
  - Comparison with Temporal.io workflow approach
  ```
- **Prerequisites**: Which chapters the reader should have read first.
  Use chapter numbers. `None` if this is a standalone entry point.
  ```
  - Chapter 2 (core abstractions)
  - Chapter 4 (event system basics)
  ```
- **Key Questions**: 1-3 questions this chapter answers.
  These guide the writing and become the chapter's implicit promise to the reader.
  ```
  - Why does the project use a custom scheduler instead of a standard job queue?
  - How does the lifecycle state machine handle failure recovery?
  ```
```

---

## Organization Rules

### Concept-first, code-second
Chapters are organized around concepts, not around code directories. A chapter on "Error Recovery Strategy" might touch files from 5 different modules — that's fine. The reader cares about the concept, not the folder layout.

### One concept per chapter
Each chapter should have a clearly stated core concept. If a chapter draft covers two distinct ideas, split it. Conversely, if two outline entries are really the same concept, merge them.

### Reading order = learning path
Chapter ordering should respect two constraints:
1. **Prerequisite dependencies**: A chapter must come after its prerequisites.
2. **Reader profile**: Among chapters at the same dependency level, order them from the reader's stronger areas to weaker areas, building confidence before tackling unfamiliar ground.

### Concept size calibration
There's no fixed page count, but a useful heuristic: if a chapter would require more than ~30 minutes of focused reading, the concept might be too large. Consider splitting into:
- A "foundations" chapter covering the core idea
- A "deep dive" chapter covering advanced aspects or edge cases

---

## SUMMARY.md Generation

The confirmed outline translates directly to SUMMARY.md:

```markdown
# Summary

[Project Overview](chapter-00-overview.md)

---

[Chapter 1: Title](chapter-01-slug.md)
[Chapter 2: Title](chapter-02-slug.md)
[Chapter 3: Title](chapter-03-slug.md)

---

[Glossary](glossary.md)
[Source File Index](source-index.md)
[Version Notes](version-notes.md)
```

File naming convention: `chapter-NN-slug.md` where `slug` is a short kebab-case identifier derived from the chapter title (e.g., `chapter-03-agent-lifecycle.md`).
