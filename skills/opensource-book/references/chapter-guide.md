# Chapter Writing Guide

This document defines the style, format, and conventions for writing book chapters.

---

## Writing Style

### Tone: Engineering Notebook / Technical Blog

The reader should feel like they're reading a senior engineer's thoughtful write-up, not a textbook or API reference. Characteristics:

- **Opinion-driven**: "This design choice is clever because..." or "The trade-off here is worth understanding..."
- **Process-visible**: Show the reasoning journey — "At first glance this looks like X, but looking deeper you'll notice Y"
- **Conversational but precise**: Informal doesn't mean imprecise. Technical claims must be backed by code evidence.
- **Discovery-oriented**: Frame sections as explorations, not definitions. "Let's trace what happens when..." rather than "The system consists of..."

### What to Avoid

- **Textbook structure**: Don't write "Background → Definition → Example → Exercise" in mechanical sequence.
- **Exhaustive enumeration**: Don't list every method in a class or every field in a config. Focus on what's interesting and why.
- **Hedging without substance**: "This is a complex topic" says nothing. Either explain the complexity or skip the sentence.
- **Describing what the reader can see**: If you show a code block, don't restate it line by line. Explain the insight the code reveals.

---

## Chapter Structure

There's no rigid template, but most chapters work well with this flow:

### 1. Opening Hook
Start with a question, a puzzle, or a real-world scenario that makes the reader care about this chapter's concept. Not a definition.

**Good**: "When an Agent crashes mid-execution, what happens to the work it was doing? The answer reveals a lot about how this project thinks about reliability."

**Bad**: "In this chapter, we will discuss the error handling system of the project."

### 2. Core Exploration
This is the main body. Walk through the concept by examining source code, explaining design decisions, and showing how pieces connect. Interleave code with narrative.

### 3. Reflection / Insight
Pull back from the code and articulate the engineering wisdom. What pattern is at work? Why is this approach better (or worse) than alternatives? What can the reader take away for their own work?

### 4. Thought Questions
End with 2-4 questions that invite the reader to explore further. These are not quizzes — they're genuine questions that extend the chapter's ideas.

**Good thought questions**:
- "What would change if this project needed to support [different requirement]?"
- "Compare this approach with how [other well-known project] handles the same problem."
- "The code uses [pattern] here. Can you find other places in the codebase where a similar pattern appears?"

---

## Source Code Citation

### Citation Format

Every source code reference must include:
- File path (relative to repo root)
- Line range
- Short commit hash (first 7 characters) or tag

Format: `// path/to/file.ext#L{start}-L{end} ({version})`

Example:
```
// src/agent/lifecycle.ts#L42-L78 (a1b2c3d)
```

Or with a tag:
```
// src/agent/lifecycle.ts#L42-L78 (v0.3.2)
```

### When to Use Direct Source vs Pseudocode

**Use direct source code when**:
- The exact syntax or API matters for understanding
- The code is elegant or idiomatic and that's part of the point
- The reader will want to look up this exact code in the repo
- The code is short enough (under ~30 lines) to read inline

**Use simplified pseudocode when**:
- The real code is verbose with boilerplate that distracts from the concept
- You need to show the essence of an algorithm without language-specific details
- The focus is on control flow or architecture, not implementation detail
- You're compositing logic from multiple files into one coherent picture

When using pseudocode, note it explicitly: *"Simplified from the actual implementation..."* and still cite which files the pseudocode is derived from.

### Referencing Multiple Versions

If comparing how a piece of code evolved:
```
// In v0.2.0: src/agent/lifecycle.ts#L30-L45 (tag: v0.2.0)
// In v0.3.2: src/agent/lifecycle.ts#L42-L78 (tag: v0.3.2)
```

---

## Visuals

### When to Use Visuals

Visuals are tools, not decoration. Use them when:
- Showing relationships between components (architecture diagrams)
- Illustrating sequences of events (sequence diagrams, flowcharts)
- Comparing structures (side-by-side diagrams)
- The spatial layout of something matters (memory layout, tree structures)

Don't create a diagram just because a section "feels like it should have one."

### Visual Production Methods

**Method 1: HTML/SVG code (preferred)**
Write the diagram directly in HTML or SVG, embedded in the markdown or as a separate file in `assets/`. This keeps diagrams version-controlled and editable.

For sequence diagrams, Mermaid syntax inside markdown code blocks is a good option if mdBook is configured with a Mermaid preprocessor.

**Method 2: Image generation prompt**
When a concept would benefit from a more illustrative or spatial visualization that's hard to do in code, provide a detailed prompt for image generation tools. Format:

```markdown
<!-- IMAGE: [description for generation]
Prompt: "A technical diagram showing [detailed description of what to visualize,
including layout, labels, colors, and relationships]"
-->
```

### Visual Placement

Place visuals immediately after the text that introduces the concept they illustrate. Don't front-load a chapter with diagrams before the reader has context.

---

## Cross-References

### Between Chapters
Use relative markdown links: `[see Chapter 3](chapter-03-agent-lifecycle.md)` or `[as discussed in the Agent Lifecycle chapter](chapter-03-agent-lifecycle.md#section-anchor)`.

### To Glossary
On first use of a project-specific term, link to the glossary: `[harness](glossary.md#harness)`.

### To Source File Index
When discussing a file for the first time in a chapter, the source file index will be auto-generated, so no manual cross-reference is needed. Just use the citation format consistently.

---

## Thought Question Design

Thought questions at the end of each chapter serve one purpose: **invite the reader to explore further on their own**.

### Good Patterns
- **Extension**: "What if the requirements changed? How would this design adapt?"
- **Comparison**: "How does this differ from how [other project] solves the same problem?"
- **Discovery**: "Can you find where else in the codebase this pattern appears?"
- **Critique**: "What are the downsides of this approach? When would it break down?"
- **Application**: "How would you apply this pattern in a project you're working on?"

### Bad Patterns
- Recall questions ("What is the name of the class that handles X?")
- Yes/no questions ("Does this project use dependency injection?")
- Questions answered in the chapter itself

Mark thought questions with a clear heading:

```markdown
## Think About It

1. [Question 1]
2. [Question 2]
3. [Question 3]
```
