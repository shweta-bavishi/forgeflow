# Workflow: Fix Pipeline

**Trigger:** "Fix pipeline", "Debug build failure", "Why is the pipeline failing?"

## What It Does

Fetches Jenkins build logs, diagnoses the root cause using an error catalog, generates a targeted code fix, and creates a fix MR.

## How to Use

1. Say: **"Fix pipeline"**
2. Otomate identifies the failed build and fetches console logs
3. Diagnoses: compilation, dependency, test, config, infra, or lint error
4. Presents diagnosis with root cause
5. Generates a **fix implementation plan** (todo list) with specific changes per file
6. Review fix plan → approve → **no code changes until plan is approved**
7. Fix code generated → review → approve → fix MR created

## HITL Gates

1. **Approve fix implementation plan (mandatory)** — step-by-step todo list of changes
2. Review generated fix code
3. Approve push and MR creation

## Error Categories

| Category | Auto-fixable | Example |
|----------|-------------|---------|
| Compilation | Yes | Syntax errors, missing imports |
| Dependency | Yes | Missing packages, version conflicts |
| Test | Mostly | Failing assertions |
| Configuration | Sometimes | Missing env vars |
| Infrastructure | No | OOM, timeout, network |
| Lint/Format | Yes | Style violations |

## MCP Tools Used

`jenkins_get_job_status`, `jenkins_get_build_status`, `jenkins_get_console_text`, `get_project_pipelines`, `get_file_content`, `search_in_repository`, `commit_file_and_create_mr`

## Duration

~15-30 minutes

## Next Steps

"Fix sonar issues" if quality gate still fails after pipeline fix.
