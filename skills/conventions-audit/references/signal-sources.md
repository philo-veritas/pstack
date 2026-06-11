# Signal Sources for Surprise Mining

Detailed techniques per signal source. Read this before mining any repo larger than a toy project. The goal of every technique here is the same: find rules that fail to be self-evident from reading code.

## 1. Deviation scan (code vs. ecosystem baseline)

Sample strategically, not exhaustively:

- Read the 3–5 most-edited files (`git log --format= --name-only | sort | uniq -c | sort -rn | head`). High-churn files are where conventions are actually exercised and where agents will most likely work.
- Read one file per architectural layer (handler/service/repo, component/store/api, etc.).

For each sampled file, ask: *what would I have written differently by default?* Each difference is a candidate. Typical surprise categories by stack:

- **Python**: sync vs async choices, error-handling discipline (exceptions vs result types), typing strictness beyond what mypy config enforces, ORM usage boundaries.
- **TypeScript/JS**: state-management discipline, barrel-file policy, server/client boundary rules, error propagation style.
- **Go**: package-boundary rules, interface placement (consumer-side vs producer-side), context propagation rules.
- **Any stack**: transaction boundaries, where validation lives, logging discipline, dependency direction between layers.

Discard any difference that is mere personal taste with no project-specific reason — taste without a reason will not survive the Surprise Test's "why" requirement.

## 2. Absence probe

Absence is invisible in code, which is exactly why it must be documented when deliberate. Probe systematically:

- List the patterns/libraries the ecosystem default would reach for (e.g., for a Flask app: blueprints, SQLAlchemy relationships, Flask-Login; for React: context for global state, useEffect for data fetching).
- For each, grep the repo. If absent, check whether the absence is *deliberate*:
  - Is there a structural workaround that exists specifically to avoid it? (strong signal)
  - Does git history show it was removed? (`git log -S "<pattern>" --oneline` — strongest signal; the removal commit message often contains the why. Caveat: `-S` only matches strings that appeared in *code diffs*; if the pattern lived only in commit messages or config, the `--grep` revert sweep in section 3 is the complementary net.)
  - Or is the project just young/small and hasn't needed it yet? (not a convention — drop)
- Only deliberate absence with a recoverable reason becomes a rule. "We don't use X" without a why is noise; "Never use X because Y" is a top-budget rule.

## 3. Git history mining

Commands worth running:

```bash
# Reverts and corrections
git log --oneline --grep="revert" -i
git log --oneline --grep="don't\|do not\|stop\|again\|back to" -i

# Repeated fixes to the same file region (churn hotspots)
git log --format= --name-only | sort | uniq -c | sort -rn | head -20

# When a pattern was removed and why
git log -S "<removed_pattern>" --oneline
```

Interpretation rules:

- A revert pair (commit + revert) marks a decision point. Read both messages; the rule is usually articulated in the revert.
- The same fix appearing ≥2 times in history means neither the code nor any doc currently teaches the rule — prime candidate.
- Churn hotspots are where to spend extra reading time in the deviation scan.

If review comments are accessible (PR threads, review files in repo), repeated reviewer corrections are the single richest source — a human already did the surprise detection for you.

## 4. Enforcement gap analysis

Read every enforcement surface before writing a single doc line:

- Linters/formatters: ruff/flake8/eslint/biome/golangci-lint configs, .editorconfig
- Type checkers: mypy/tsconfig strictness flags
- Hooks: .pre-commit-config.yaml, husky, lefthook, Claude Code hooks (settings.json)
- CI: workflow files — what do the gates actually check?
- Import boundaries: import-linter, eslint-plugin-boundaries, depcruise configs

Three outcomes per candidate rule:

1. **Already enforced** → exclude from doc entirely. If the doc currently states it, mark stale-by-redundancy in the audit report.
2. **Enforceable but not enforced** → demotion candidate. Propose the exact config addition (write the actual TOML/JSON/YAML snippet, not a vague suggestion). Common demotions: import-direction rules → import-linter contract; banned APIs → lint `banned-api` rules; file/dir naming → pre-commit script.
3. **Not mechanically enforceable** → eligible for the doc, proceed to Surprise Test.

When in doubt whether something is enforceable, spend 2 minutes checking whether the project's existing linter has a rule for it before defaulting to documentation. The bar for "can't be enforced" should be high.