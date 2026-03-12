# Workflow: Fix Pipeline

**Trigger:** "Fix pipeline", "Debug build failure", "Why is the pipeline failing?"

## What It Does

Fetches Jenkins build logs, diagnoses the root cause using an error catalog, generates a targeted code fix, and creates a fix MR.

## How to Use

1. Say: **"Fix pipeline"**
2. Otomate identifies the failed build and fetches console logs
3. Diagnoses: compilation, dependency, test, config, infra, or lint error
4. Presents diagnosis with root cause and proposed fix
5. Review fix → approve → fix MR created

## HITL Gates

1. Approve fix approach
2. Review fix code

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
