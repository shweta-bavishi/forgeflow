# Workflow 06 — Sonar Fix

> Retrieves SonarQube quality issues, categorises them by fixability, generates code fixes for auto-fixable issues, and reports on those requiring manual attention.

---

## When to Use

- The SonarQube quality gate is failing or has new issues.
- You want to batch-fix common code quality issues automatically.
- You need a categorised report of what can and cannot be auto-fixed.

## Prerequisites

| Requirement | Details |
|---|---|
| SonarQube project | Accessible via `get_sonarqube_issues` |
| Config loaded | `sonarqube.project_key` in config |
| GitLab repo | For committing fixes |

## How to Trigger

```
@forgeflow fix sonar issues
```

Or filter by severity:

```
@forgeflow fix sonar blockers and criticals
```

## What Happens

### Phase 1 — Fetch Issues

The SonarQube Agent retrieves open issues using `get_sonarqube_issues`, filtered by the configured project key.

Issues are fetched in severity order: **Blocker → Critical → Major → Minor → Info**.

### Phase 2 — Categorise Issues

Each issue is classified into one of three categories:

| Category | Description | Examples |
|---|---|---|
| **AUTO-FIXABLE** | Can be fixed mechanically without changing logic | Null pointer checks (S2259), unused imports (S1128), empty blocks (S108), missing return types |
| **AGENT-ASSISTED** | Needs code restructuring; agent can propose a fix but human should review | Cognitive complexity (S3776), string duplication (S1192), long methods |
| **MANUAL** | Requires architectural or design decisions | Security vulnerabilities, major refactoring, design pattern changes |

### Phase 3 — Generate Fixes

For **AUTO-FIXABLE** issues:
- The Code Agent reads the affected file (`get_gitlab_file_content`).
- Generates the minimal fix (no unrelated refactoring).
- Validates the fix resolves the specific SonarQube rule.

For **AGENT-ASSISTED** issues:
- A suggested fix is generated but flagged for careful review.

For **MANUAL** issues:
- A description of the problem and recommended approach is provided (no code generated).

### Phase 4 — ⏸️ HITL: Approve Fixes

A categorised report is presented:

```
SonarQube Fix Report — my-service
═══════════════════════════════════

AUTO-FIXABLE (7 issues — ready to commit):
  ✅ S1128  src/utils/helpers.ts:14     Remove unused import 'lodash'
  ✅ S2259  src/services/auth.ts:42     Add null check before .email access
  ✅ S108   src/handlers/event.ts:88    Add comment or logic to empty catch block
  ...

AGENT-ASSISTED (3 issues — review suggested fixes):
  🔶 S3776  src/services/order.ts:120   Reduce cognitive complexity (18 → <15)
  🔶 S1192  src/constants.ts            Extract duplicated string "application/json"
  ...

MANUAL (2 issues — no auto-fix):
  🔴 S5131  src/api/query.ts:55         Potential SQL injection — parameterise query
  🔴 S1186  src/base/abstract.ts:10     Empty method in abstract class — design decision
```

You approve which fixes to apply.

### Phase 5 — Commit Fixes

Approved fixes are committed via `commit_file_and_create_mr` on a branch like `forgeflow/sonar-fixes-20260311`.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_sonarqube_issues` | Fetch quality issues |
| `get_sonarqube_quality_gate` | Check overall gate status |
| `get_sonarqube_measures` | Get metrics (coverage, duplications) |
| `get_gitlab_file_content` | Read affected source files |
| `commit_file_and_create_mr` | Commit fixes |

## Tips

- Run this workflow **after** Workflow 04 (implement) to catch issues before the MR is reviewed.
- Start with Blockers and Criticals — these typically fail the quality gate.
- AUTO-FIXABLE issues are safe to batch-approve; AGENT-ASSISTED fixes deserve individual review.
- If SonarQube rules are project-specific (custom quality profiles), some categorisations may be inaccurate — adjust in the HITL step.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| No issues returned | Wrong `sonarqube.project_key` or analysis hasn't run | Verify project key; trigger a SonarQube analysis first |
| Fix introduces new issues | Cascading change (e.g. removing import breaks another file) | Review the full diff at HITL; the self-review loop should catch this |
| Security issues misclassified as auto-fixable | Rule not in the manual-only list | Report it; update the SonarQube Agent's categorisation rules |
| Quality gate still fails after fixes | Remaining MANUAL issues or coverage threshold | Address manual issues separately; increase test coverage |
