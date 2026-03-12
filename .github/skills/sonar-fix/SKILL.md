---
name: sonar-fix
description: "Analyze and fix SonarQube code quality issues. Categorizes issues by fixability, generates code fixes for auto-fixable issues, and creates fix MR to pass quality gate."
---

# Skill: Fix SonarQube Issues

Fetch SonarQube issues, categorize by fixability, generate fixes, and create a fix MR.

## Phase 1: FETCH SONAR DATA

```
Call: get_sonar_project_issues(config.sonarqube.project_key)
  → Fetch ALL issues with: severity, rule, file, line, message

Call: get_sonar_quality_gate_status(config.sonarqube.project_key)
  → Check: PASSED or FAILED, which conditions failed

Call: get_sonar_project_measures(config.sonarqube.project_key)
  → Metrics: coverage, duplications, complexity, debt
```

## Phase 2: CATEGORIZE ISSUES

```
AUTO-FIXABLE (agent can fix confidently):
  S2259 — Null pointer dereference → add null check
  S1128 — Unused imports → remove import
  S108  — Empty catch block → add error handling
  S2093 — Resource not closed → add try-with-resources / finally
  S1481 — Unused variable → remove or use
  S1186 — Empty method → add implementation or documentation
  Missing break in switch → add break statements

AGENT-ASSISTED (agent needs context):
  S3776 — Cognitive complexity too high → refactor method
  S1192 — Duplicated string literal → extract constant
  S1135 — TODO/FIXME in code → resolve or create Jira
  Security hotspots → assess and fix if true positive

MANUAL (developer must decide):
  Architecture violations → needs design discussion
  Complex design patterns → needs team consensus
  Database query optimization → needs performance analysis
  Business logic issues → needs domain knowledge
```

## Phase 3: PRIORITIZE

```
Order: severity × fixability

1. BLOCKER + AUTO-FIXABLE (fix immediately)
2. CRITICAL + AUTO-FIXABLE
3. BLOCKER + AGENT-ASSISTED
4. MAJOR + AUTO-FIXABLE
5. CRITICAL + AGENT-ASSISTED
6. MAJOR + AGENT-ASSISTED
7. Everything else
```

## Phase 4: PRESENT REPORT

```
## SonarQube Analysis

**Quality Gate:** {PASSED|FAILED}
**Total Issues:** {N} (Blocker: {n}, Critical: {n}, Major: {n}, Minor: {n})

### Auto-Fixable ({N} issues)
| # | File | Line | Rule | Severity | Fix |
|---|------|------|------|----------|-----|
| 1 | user.service.ts | 45 | S2259 | BLOCKER | Add null check |
| 2 | auth.controller.ts | 12 | S1128 | MINOR | Remove unused import |

### Agent-Assisted ({N} issues)
| # | File | Line | Rule | Severity | Approach |
|---|------|------|------|----------|----------|
| 1 | order.service.ts | 78 | S3776 | MAJOR | Refactor to reduce complexity |

### Manual ({N} issues)
{List with guidance for each}

### Estimated Impact
  Fixing auto-fixable issues resolves {N}/{total} issues
  Quality gate: {WILL PASS | STILL FAILING after fixes}
```

## Phase 5: 🚦 HITL GATE — Developer Selects Issues

```
Developer selects which issues to fix:
  - "Fix all auto-fixable"
  - "Fix specific issues: #1, #3, #5"
  - "Fix all except #7"
  - "Skip for now"
```

## Phase 6: GENERATE FIXES

```
FOR each approved fix:

  1. Read source file:
     Call: get_file_content(file_path)

  2. Generate fix:
     - Match project coding patterns
     - Preserve existing code structure
     - Add proper error handling
     - Maintain test compatibility

  3. Show before/after:
     BEFORE (line 45):
       const user = await this.repo.findOne(id);
       return user.name;  // ← S2259: null pointer

     AFTER (line 45):
       const user = await this.repo.findOne(id);
       if (!user) {
         throw new NotFoundException('User not found');
       }
       return user.name;
```

## Phase 7: 🚦 HITL GATE — Review Fixes

```
Developer reviews all generated fixes
Multi-round iteration until satisfied
```

## Phase 8: COMMIT & MR

```
Call: commit_file_and_create_mr(
  files: [all fixed files],
  branch: "chore/sonar-fixes-{date}",
  title: "fix(quality): Resolve {N} SonarQube issues",
  description: "Fixes {N} SonarQube issues:\n{issue list with rules}\n\nQuality gate: {expected impact}"
)
```

## Phase 9: VERIFY

```
After MR is merged (inform developer):
  Call: get_sonar_quality_gate_status(project_key)
  Show: gate status improvement

Note: SonarQube re-scan runs on next pipeline execution
```

## Error Handling

```
SonarQube unavailable → point to credential docs
No issues found → congratulate! Quality gate passing
Auto-fix breaks tests → revert fix, classify as AGENT-ASSISTED
Fix introduces new issues → detect and warn developer
```
