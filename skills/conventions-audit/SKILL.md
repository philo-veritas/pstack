---
name: conventions-audit
description: Audit, arbitrate, and distill the code-conventions section of CLAUDE.md / AGENTS.md against the project's actual code. Use this skill whenever the user wants to create, update, verify, refresh, or sync coding standards, code style rules, or conventions in CLAUDE.md, AGENTS.md, or any agent-config document — including requests like "extract conventions from this repo", "is my CLAUDE.md stale", "update the coding standards section", "what rules should I tell the agent about this codebase", or after a large refactor when agent-config docs may have drifted from reality. Also trigger when the user notices code and CLAUDE.md/AGENTS.md disagree and wants to know which side is right, or complains that an agent keeps making the same project-specific mistake.
---

# Conventions Audit

Arbitrate doc↔code consistency for the conventions section of CLAUDE.md / AGENTS.md: the agent forms an evidence-backed judgment from three sources — the doc, the code, and the ecosystem/upstream — and the user makes the final call. Keep only rules that change agent behavior; route everything else to deterministic enforcement or the trash.

## Core principle: the Surprise Test

A convention earns a line in CLAUDE.md/AGENTS.md **only if a competent agent, after reading 2–3 representative files, would still get it wrong**. This is behavioral calibration, not knowledge restatement.

Why this matters: agents already imitate surrounding code. Restating what the code visibly shows ("we use snake_case", "models live in `models/`") wastes context-window attention and creates a second source of truth that silently rots. The only rules worth their token cost are the ones the code *cannot teach by example*:

- **Deviations from ecosystem defaults** — choices a default-behavior agent would not make (e.g., "we deliberately avoid async ORM because of X").
- **Absence rules** — patterns that are forbidden, and therefore invisible in the code (e.g., "never import models directly in the service layer"). Absence cannot be inferred from reading code; this is the highest-value category.
- **Tribal knowledge** — the "why" behind counterintuitive structure, landmines, ordering constraints, things that broke before.

If a candidate rule fails the Surprise Test, drop it. Do not keep it "just in case".

## Two kinds of rot: facts vs conventions

Agent-config docs contain two distinct kinds of claims, and they rot differently:

- **Facts** — descriptive claims: entry points, package names, paths, run commands, ports, artifact names, framework versions. A fact has a single ground truth (the code), is mechanically verifiable, and when doc and code disagree, *the code is always right*. The fix is always "update the doc" — no human adjudication needed.
- **Conventions** — behavioral rules ("use X", "never Y"). When a declared convention conflicts with code, neither side is automatically right (see "Doc–code conflict arbitration" below).

During mining you will encounter facts drift for free; capture it in the dedicated "Facts drift" report section rather than discarding the observation. But facts drift is a secondary output: it does not count against the conventions budget, and fact-checking must not become the main job — if the user wants a full doc-accuracy audit, that is a broader harness audit, not this skill.

## Doc–code conflict arbitration (three evidence sources)

"Code does not follow the rule" is, by itself, a **zero-information observation**: it is equally consistent with "the doc rotted" and "the code is violating a correct rule". For conventions, code is NOT ground truth. Never classify a conflict from doc and code alone — bring in the third arbiter:

1. **Doc** — what the rule says, and whether its stated rationale still exists.
2. **Code** — what the repo actually does, and which direction recent commits move.
3. **Ecosystem / upstream** — what the relevant library or platform currently recommends. Check locally first: deprecation markers in the dependency source (`@Deprecated`, `DeprecationWarning`, doc comments — the jar/package is on disk, grep it), then changelogs and official docs (web search if needed).

The classic case: doc says "use `selectByIds()`, not `selectBatchIds()`", code uses `selectBatchIds()` widely. Doc-vs-code alone looks like rot. Upstream evidence (MyBatis-Plus deprecated `selectBatchIds`) flips the verdict: the doc is right, the code is legacy, and the correct action is to *sharpen* the rule ("New code must use selectByIds(); legacy usages migrate"), not remove it.

**Entry bar for "Stale"**: a conflicting rule may be classified Stale only with positive evidence that its *rationale died* — the dependency it governs is gone from the manifest, the infrastructure it references was deleted, upstream reversed the recommendation. Noncompliance alone never qualifies.

**Everything else goes to "Needs adjudication"** — and the agent must arrive with a verdict, not a shrug. After consulting all three sources, state a recommended resolution with its evidence ("Recommend: keep and sharpen — upstream deprecated Y in v3.5, see <evidence>"), so the user's decision collapses to accept/override instead of an open question. Only the user knows project intent; but making them do the research the agent could have done is a failure of the skill.

## Security escalation

Any finding with security implications — committed credentials or secrets, vulnerable patterns, permission landmines — goes into a separate **Escalations** section of the report, handled out-of-band from doc editing. Never offer "reword the doc to acknowledge the problem" as a resolution: weakening the documented rule to match an unsafe reality inverts the purpose of the audit. State the finding, its location, and the remediation direction (rotate credentials, move to env/secret manager, etc.), and leave the documented rule intact or strengthened.

## Mode selection

Check whether the target doc (CLAUDE.md, AGENTS.md, or both) already contains a conventions/coding-standards section:

- **Audit mode** (section exists — the common case): produce a diff report across these categories: stale rules, needs-adjudication conflicts, missing rules (undocumented surprises), demotion candidates, facts drift, and escalations. Present the report before editing anything.
- **Generate mode** (no section yet): run the full pipeline below and propose a new section, plus any enforcement-config changes.

If both CLAUDE.md and AGENTS.md exist, respect the project's existing split (typically: global behavioral calibration in CLAUDE.md, project/agent-specific operating rules in AGENTS.md). Never duplicate a rule across both — pick the file where an agent will actually encounter it at the right moment.

## Pipeline

### Phase 1 — Establish the ecosystem baseline

Identify language, framework, and toolchain (read manifest files: pyproject.toml, package.json, go.mod, etc.). Then explicitly write down, in your working notes, what a *default-behavior agent* would assume for this stack: idiomatic patterns, common libraries, standard layouts. This baseline is what "surprise" is measured against. Without it, everything looks like a convention.

### Phase 2 — Mine surprises

Work through the signal sources in priority order. Detailed heuristics and per-source techniques are in `references/signal-sources.md` — read it before mining a non-trivial repo.

1. **Deviation scan**: diff actual code patterns against the Phase 1 baseline. Only deviations are candidates.
2. **Absence probe**: for each "obvious" pattern the ecosystem would expect, check whether the repo conspicuously avoids it. Confirmed avoidance (especially with structural workarounds) is a strong candidate.
3. **Git history**: reverts, repeated near-identical fixes, commit messages containing "don't", "stop", "revert", "again". A correction that happened twice will happen a third time — to the agent.
4. **Existing enforcement gap**: read lint/format/CI configs. Anything already enforced deterministically is *excluded* from the doc (the tool will catch it; the doc line is redundant). Anything the configs *almost* enforce is a demotion candidate.

For every candidate, record: the rule, the evidence (file paths / commits), and why a default agent would violate it.

### Phase 3 — Enforcement triage

Route every candidate through this decision tree, in order:

1. **Mechanically checkable?** (lint rule, formatter option, import-boundary check, pre-commit hook, CI step) → propose the config/hook change. Do NOT put it in the doc. Deterministic enforcement beats behavioral instruction every time it's available.
2. **Behavioral and surprising?** (passes the Surprise Test, cannot be mechanically checked) → candidate for the doc. Write it with its *why* in one breath: a rule with a reason is followed; a bare imperative is pattern-matched and forgotten.
3. **Neither?** → drop, and say so in the report. Visible drops build user trust in the triage.

Borderline case: a rule that is *partially* checkable (e.g., "prefer X over Y except in migration scripts") — enforce the checkable core mechanically, document only the exception.

### Phase 4 — Budget and ranking

Hard budget: the conventions section is **≤ 20 lines** (count bullet lines, not headers). If candidates exceed budget, rank by `violation cost × violation probability`:

- violation cost: what breaks if an agent violates this? (data corruption / legal risk > broken build > style churn)
- violation probability: how strongly does the ecosystem default pull toward the violation?

Cut from the bottom. If a cut rule feels painful to lose, that is a signal it belongs in a hook, not that the budget should grow.

### Phase 5 — Output

**Audit mode** — present this report first, apply edits only after user confirmation:

```markdown
# Conventions Audit: <project>

## Stale (rationale verifiably dead — dependency removed, infra deleted, upstream reversed)
- <rule> — rationale-death evidence: <files/commits/manifest>. Action: remove / rewrite.

## Needs adjudication (doc–code conflict; agent verdict attached)
- <rule> — doc/code/upstream evidence. **Recommend: <verdict>** (<key evidence>). If overridden: <the other rewrite>.

## Missing (surprise in code, absent from doc)
- <rule> + why — evidence. Proposed line: "<exact doc line>"

## Demote to enforcement (emitted as ordered task list — not executed in this pass)
- <rule> → <concrete config diff: .eslintrc / ruff.toml / pre-commit hook>. Order: enforcement lands and passes first, doc line deleted second.

## Facts drift (descriptive claims out of sync — code is ground truth, fix is mechanical)
- <claim in doc> → <reality> — evidence. Action: update doc line.

## Escalations (security-sensitive — resolve out-of-band, never by rewording the doc)
- <finding> — location. Remediation direction: <rotate / move to secret manager / ...>.

## Dropped candidates (failed Surprise Test)
- <rule> — inferable from code, not documenting.

## Budget check: <N>/20 lines after changes (facts drift and escalations excluded from budget).

## Decision sheet
Will apply unless you veto: [Stale #..., Facts drift #..., Missing #... (wording above)]
Need your call: [Adjudication #1: accept recommendation? y/n] [Demote #1..N: opt in per item]
Acknowledge: [Escalations — handled outside this audit]
```

**Generate mode** — propose the new section using this shape for each rule:

```markdown
- <imperative rule> — <one-clause why>. (<scope, if not global>)
```

Example: `- Never import models in the service layer — services must stay storage-agnostic for the planned split. (src/services/**)`

Plus a separate "Enforcement changes" list with concrete config diffs for everything triaged to tooling.

## After the report: the decision protocol

The report is not the end of the skill — it opens a human-in-the-loop gate. Run it like this:

**1. End the report with the decision sheet** (template above). Defaults by category, chosen so the user answers only real questions:

| Category | Default | Why |
|---|---|---|
| Facts drift | apply unless vetoed | code is ground truth, no discretion |
| Stale | apply unless vetoed | entry bar already requires rationale-death evidence |
| Missing | apply unless vetoed, full wording shown | wording is the user's hand-tuned territory — show every proposed line verbatim |
| Needs adjudication | **no default** — accept/override the recommendation | designed to need a human |
| Demote | **no default** — opt-in per item | touches the toolchain, can break CI |
| Escalations | never handled here — acknowledge only | out-of-band by definition |
| Dropped | no action | disclosure only |

Silence on a defaulted item means consent; the user's minimum interaction is answering the adjudication and demote questions.

**2. Apply in this order, after the user responds:**

1. Doc edits (facts drift, stale, missing, accepted adjudications) — one commit, surgical diffs, never wholesale regeneration.
2. Opted-in demotions — *enforcement first, deletion second*: land the lint/hook/CI config, run it against the existing codebase, and only after it passes delete the now-redundant doc line. Reversing the order opens a window where the rule is enforced by nothing. If existing code violates the new check (common — that's often why the rule existed), report it: the options are warning-level/baseline-exempt rollout or a migration task, never silently forcing CI red. Each demotion is its own commit (independently revertable).
3. This skill emits demotion configs as an ordered task list with exact diffs; whether to execute them in-session or hand them to a review flow is the user's call per the decision sheet.

**3. Adjudication decisions are persisted in the wording itself, not in side-car state.** An accepted "keep and sharpen" verdict produces a doc line like "New code must use X; legacy Y usages migrate per <plan>" — which no longer textually conflicts with legacy code, so the next audit run will not re-raise it. No decisions.json, nothing extra to rot. Unresolved escalations *will* resurface on every run; that is correct behavior, not a bug.

**4. Close the loop**: show the final doc diff and the recomputed budget count as the last frame. The user's final impression should be *what changed*, not "done".

## Anti-patterns

- **Restating the visible**: naming style, directory layout, library choices that match ecosystem defaults. The agent sees these.
- **Unbounded sections**: every line added makes the previous lines less likely to be obeyed (attention is finite). The budget is part of the design, not an inconvenience.
- **Bare imperatives**: "Always use X" without why. Explain the reason or route to a hook.
- **One-shot mindset**: this skill's steady state is re-running audit mode after major changes. Prefer surgical diffs over wholesale regeneration — regeneration destroys hand-tuned wording the user added.
- **Defaulting to "remove" on conflict**: noncompliant code is a zero-information observation, not proof of rot. Removing the rule silently converts the agent-config doc from steering wheel to rear-view mirror. Arbitrate with upstream evidence; route to adjudication.
- **Symmetric options without a verdict**: handing the user "(a) or (b)?" without doing the upstream research first offloads the agent's job onto the human. Always attach a recommended resolution with evidence.
- **Resolving security findings by weakening the doc**: "rewrite the rule to admit legacy secrets exist" is not remediation. Escalate; keep the rule strict.
- **Editing without showing the report**: in audit mode, the report comes first. The user owns the doc; the skill proposes.