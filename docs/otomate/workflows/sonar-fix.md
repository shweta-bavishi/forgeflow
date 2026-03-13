# Workflow: Fix SonarQube Issues

**Trigger:** "Fix sonar issues", "Resolve sonar report", "Help me pass quality gate"

## What It Does

Fetches SonarQube issues, categorizes them by fixability (auto-fixable, agent-assisted, manual), generates code fixes for selected issues, and creates a fix MR.

## How to Use

1. Say: **"Fix sonar issues"**
2. Otomate fetches all issues and quality gate status
3. Categorizes: auto-fixable vs needs-review vs manual
4. Select which issues to fix
5. Presents a **fix implementation plan** (todo list) with specific before/after for each issue
6. Review fix plan → approve → **no code changes until plan is approved**
7. Fix code generated → review → approve → fix MR created

## HITL Gates

1. Select which issues to fix
2. **Approve fix implementation plan (mandatory)** — step-by-step todo list of changes
3. Review generated fix code
4. Approve push and MR creation

## Issue Categories

| Type | Rule Examples | Fix Approach |
|------|-------------|-------------|
| Auto-fixable | S2259 (null pointer), S1128 (unused import), S108 (empty catch) | Agent fixes directly |
| Agent-assisted | S3776 (complexity), S1192 (duplicate string) | Agent proposes refactor |
| Manual | Architecture violations, design issues | Developer decision needed |

## MCP Tools Used

`get_sonar_project_issues`, `get_sonar_quality_gate_status`, `get_sonar_project_measures`, `get_project_uncovered_lines`, `get_file_content`, `commit_file_and_create_mr`

## Duration

~15-25 minutes

## Next Steps

After fixes merged, quality gate will re-run on next pipeline.
