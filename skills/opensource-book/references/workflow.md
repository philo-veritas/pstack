# Workflow — Phase-by-Phase Reference

This document contains the detailed instructions for each phase of the book-writing workflow. Read the relevant section before executing that phase.

---

## Phase 0: Project Input

### Inputs
- GitHub repository (cloned to local path)
- Locked commit hash or tag
- Reader's initial interest dimensions (free-form, e.g., "I'm interested in the Agent scheduling mechanism and plugin system")

### Actions

1. **Record metadata**
   - Repository local path
   - Locked version (commit hash or tag)
   - Repository remote URL (for reader reference)

2. **Scan project**
   - List top-level directory structure (2-3 levels deep)
   - Identify primary programming language(s) and frameworks
   - Estimate project scale (file count, approximate lines of code)
   - Locate documentation artifacts: README, docs/, CONTRIBUTING, CHANGELOG, ADR (Architecture Decision Records), any design docs

3. **Assess documentation maturity**
   Rate the project's existing docs on a simple scale:
   - **Rich**: Comprehensive docs, architecture guides, API references
   - **Moderate**: Good README, some docs, but gaps in architecture explanation
   - **Sparse**: Minimal README, code is mostly self-documenting
   This rating helps calibrate how much the book needs to fill in vs. build upon existing docs.

### Output: Project Info Card

```markdown
# Project Info Card

- **Project**: [name]
- **Repository**: [remote URL]
- **Local Path**: [local path]
- **Locked Version**: [commit hash or tag]
- **Language(s)**: [e.g., TypeScript, Go]
- **Scale**: [file count, ~LOC]
- **Doc Maturity**: [Rich / Moderate / Sparse]
- **Key Documentation Found**: [list of doc files/directories]
- **Initial Interest Dimensions**: [reader's stated interests]
```

---

## Phase 1: Global Understanding

### Inputs
- Project Info Card (from Phase 0)
- Initial interest dimensions
- Access to deepwiki (`https://deepwiki.com/org/repo`)

### Actions

1. **Deepwiki information gathering**
   Use deepwiki's Q&A to efficiently collect:
   - High-level architecture overview
   - Core concepts and domain model
   - Key design decisions and trade-offs
   - Module/package relationships
   - Extension points and plugin mechanisms
   - Notable engineering patterns

   Suggested deepwiki questions:
   - "What is the overall architecture of this project?"
   - "What are the core abstractions and how do they relate?"
   - "What are the main design decisions and why were they made?"
   - "How does [initial interest dimension] work in this project?"
   - "What are the extension points or plugin mechanisms?"

2. **Source code justification**
   For every piece of information gathered from deepwiki, go back to the local source code and:
   - Verify accuracy — does the code actually reflect what deepwiki says?
   - Add specificity — which files, which functions, which patterns?
   - Fill gaps — what did deepwiki miss or oversimplify?

3. **Dynamic dimension discovery**
   While reading the source code for justification, watch for engineering knowledge dimensions that were not in the initial interest list. Examples:
   - An unusually elegant error handling strategy
   - A custom testing harness worth studying
   - A clever configuration management approach
   - An interesting approach to backward compatibility

   Record each discovered dimension with a brief note on why it's interesting.

4. **Synthesize**
   Combine deepwiki findings (after justification) with discovered dimensions into a coherent understanding of the project.

### Output: Global Understanding Document

```markdown
# Global Understanding: [Project Name]

## Architecture Overview
[High-level architecture, verified against source code]

## Core Modules
| Module | Purpose | Key Files | Notes |
|--------|---------|-----------|-------|
| ...    | ...     | ...       | ...   |

## Module Relationships
[How modules interact, dependency directions, communication patterns]

## Key Design Decisions
1. [Decision]: [rationale, source evidence]
2. ...

## Discovered Engineering Dimensions
| Dimension | Why It's Interesting | Key Source Locations |
|-----------|---------------------|-------------------|
| ...       | ...                 | ...               |

## Initial Interest Dimensions — Findings
[For each initial interest dimension, what was found]

## Open Questions
[Things that need deeper exploration in chapter writing]
```

### Important
- deepwiki is used ONLY in this phase. After this, all work is based on source code directly.
- If deepwiki is unavailable or the project isn't indexed, skip it and do the exploration entirely through source code reading.

---

## Phase 2: Reader Assessment

### Inputs
- Global Understanding Document (especially the Discovered Engineering Dimensions)

### Actions

1. **Design assessment questions**
   Create 8-15 questions covering the technical domains relevant to this project. Questions should:
   - Span different difficulty levels (basic concept → applied reasoning)
   - Cover both the project's primary language/framework and the discovered engineering dimensions
   - Be answerable in 1-3 sentences (not essay questions)
   - Include some scenario-based questions ("If you needed to X, how would you approach it?")

   Example question types:
   - "What is [concept]? Briefly explain." (knowledge check)
   - "What's the difference between [A] and [B]?" (distinction check)
   - "When would you use [pattern] vs [alternative]?" (judgment check)
   - "You see this code snippet — what's happening and why?" (reading check)

2. **Present questions to reader**
   Give the reader all questions at once and let them answer.

3. **Analyze responses**
   For each engineering dimension, rate the reader's familiarity:
   - **Strong**: Can explain clearly, knows nuances
   - **Moderate**: Understands basics but gaps in depth
   - **Weak**: Limited or no familiarity
   - **Absent**: The dimension wasn't covered (need prerequisite chapter)

4. **Determine impact on book structure**
   Based on the assessment:
   - **Depth adjustment**: Strong areas can skip basics and go deep; weak areas need more scaffolding
   - **Prerequisite chapters**: If the reader is Weak/Absent on a foundational concept, consider adding a short background chapter
   - **Chapter ordering**: Start from the reader's stronger areas and progressively bridge to weaker ones, so early chapters build confidence

### Output: Reader Profile

```markdown
# Reader Profile

## Assessment Summary
| Dimension | Familiarity | Impact on Content |
|-----------|------------|------------------|
| [e.g., Event-driven architecture] | Moderate | Include brief primer, then go deep |
| [e.g., Go concurrency patterns] | Strong | Skip basics, focus on project-specific usage |
| ...       | ...        | ...              |

## Recommended Adjustments
- **Prerequisite chapters needed**: [list, if any]
- **Suggested reading order**: [start from X, then Y, because...]
- **Depth calibration**: [which topics go deep, which stay high-level]
```

---

## Phase 3: Outline Generation

### Inputs
- Initial interest dimensions (from Phase 0)
- Global Understanding Document (from Phase 1, including deepwiki-gathered + code-justified info)
- Reader Profile (from Phase 2)
- Project directory structure

### Actions

1. **Draft outline**
   Generate an outline that:
   - Organizes chapters primarily by concept (not by code module)
   - Orders chapters considering the reader's knowledge profile (stronger → weaker)
   - Ensures each chapter focuses on one concept (split large concepts)
   - Includes clear dependency links between chapters
   - See `outline-spec.md` for the required format of each outline entry

2. **Present to reader for review**
   The reader may:
   - Reorder chapters
   - Merge or split chapters
   - Add or remove topics
   - Adjust scope

3. **Finalize outline**
   Incorporate reader feedback and produce the confirmed outline, which becomes the initial SUMMARY.md.

### Output
- Confirmed book outline (see `outline-spec.md` for format)
- Initial `src/SUMMARY.md`

---

## Phase 4: Chapter Writing

### Inputs (per chapter)
- Confirmed outline entry for this chapter (concept, internal/external references)
- Source code files listed in the outline entry
- External reference research results (if any)

### Actions

1. **Research phase**
   - Read the internal reference source files thoroughly
   - Conduct external research if the outline specifies external references
   - Identify the key insight or argument for this chapter

2. **Write the chapter**
   Follow the style and format guidelines in `chapter-guide.md`. Key points:
   - Lead with an insight or question, not a definition
   - Show code that matters, explain why it matters
   - Use source citation format: `// path/to/file.ts#L42-L78 (commit-hash-short)`
   - Include diagrams/charts only when they genuinely aid understanding
   - End with thought-provoking questions that invite further exploration

3. **Check for new dimensions**
   If writing this chapter reveals a significant new engineering knowledge dimension:
   - Trigger the Outline Revision Mechanism (see SKILL.md)
   - Do NOT try to shoehorn the new dimension into the current chapter

4. **Self-review**
   Before presenting the chapter:
   - Verify all source citations point to real code at the locked version
   - Ensure the chapter stands on its own but connects to its prerequisites
   - Check that the tone is engineering-notebook, not textbook

### Output
- Chapter markdown file (`src/chapter-NN-slug.md`)

---

## Phase 5: Assembly

### Inputs
- All chapter files from Phase 4
- Project Info Card from Phase 0
- Global Understanding Document from Phase 1
- Confirmed outline

### Actions

1. **Generate auxiliary sections**

   **Project Overview (Chapter 0)**
   A bird's-eye view of the project: what it is, who it's for, its architecture at the highest level, and a reading guide for the book itself. This chapter should be readable by someone who has never seen the project.

   **Glossary**
   Collect all project-specific terms and engineering concepts introduced across chapters. Define each concisely. Organize alphabetically.

   **Source File Index**
   A cross-reference table: which source files were discussed in which chapters. Format:
   ```
   | Source File | Chapters |
   |-------------|----------|
   | src/agent/lifecycle.ts | Ch.3, Ch.7 |
   ```

   **Version Notes**
   Record:
   - Project name and version
   - Locked commit hash or tag
   - Date of writing
   - Note that code references correspond to this specific version

2. **Assemble mdBook project**
   - Create `book.toml` with project metadata
   - Finalize `src/SUMMARY.md` with all chapters and auxiliary sections
   - Place all chapter files in `src/`
   - Place diagram assets in `assets/`

3. **Verify**
   - Check all internal cross-references (chapter links, glossary links)
   - Verify SUMMARY.md matches actual file structure
   - If mdBook CLI is available, run `mdbook build` to verify

### Output
- Complete mdBook project directory, ready to build
