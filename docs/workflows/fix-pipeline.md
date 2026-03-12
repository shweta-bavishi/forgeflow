# Workflow 05 — Fix Pipeline

> Diagnoses a failed Jenkins pipeline, identifies the root cause using a built-in error catalogue, generates a fix, and optionally commits the fix.

---

## When to Use

- A Jenkins build or deployment pipeline has failed.
- You want automated root-cause analysis instead of manually reading logs.
- You want a suggested fix (and optionally an auto-committed patch).

## Prerequisites

| Requirement | Details |
|---|---|
| Jenkins job | Accessible via `get_jenkins_build_log` |
| Config loaded | `jenkins.base_url` and `jenkins.job_name` in config |
| GitLab repo | For committing fixes via `commit_file_and_create_mr` |

## How to Trigger

```
@otomate fix pipeline
```

Or with a specific build number:

```
@otomate diagnose jenkins build #142
```

## What Happens

### Phase 1 — Fetch Build Log

The Jenkins Agent retrieves the latest (or specified) build log using `get_jenkins_build_log`.

### Phase 2 — Error Catalogue Matching

The log is scanned against the built-in error catalogue (defined in the Jenkins Agent). Categories include:

| Category | Example Patterns |
|---|---|
| Dependency errors | `Could not resolve dependencies`, `ERESOLVE`, `Module not found` |
| Compilation errors | `TS2304`, `error TS`, `Cannot find name`, `SyntaxError` |
| Test failures | `FAIL src/`, `Test suite failed`, `expected X received Y` |
| Docker errors | `Cannot connect to Docker daemon`, `COPY failed`, `no space left` |
| Resource errors | `heap out of memory`, `ENOMEM`, `OOMKilled` |
| Permission errors | `EACCES`, `Permission denied`, `403 Forbidden` |
| Git errors | `fatal: could not read`, `merge conflict`, `detached HEAD` |
| Transient / flaky | `ETIMEDOUT`, `ECONNRESET`, `502 Bad Gateway` |

### Phase 3 — Root-Cause Analysis

Using the INVESTIGATE → HYPOTHESIZE → VERIFY → RECOMMEND loop:

1. **Investigate**: Extract the error message, stack trace, and failing stage.
2. **Hypothesize**: Match against known patterns; rank most likely cause.
3. **Verify**: Cross-reference with source code (via `get_gitlab_file_content`) to confirm the hypothesis.
4. **Recommend**: Propose a fix with specific file changes.

### Phase 4 — ⏸️ HITL: Approve Fix

The diagnosis and recommended fix are presented. You can:

- Accept the fix as-is.
- Modify the fix.
- Request further investigation.
- Mark as a transient failure (retry the build instead).

### Phase 5 — Apply Fix (Optional)

If approved, the Code Agent generates the fix and commits it via `commit_file_and_create_mr`.

For transient failures, the Jenkins Agent can re-trigger the build using `trigger_jenkins_build`.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_jenkins_build_log` | Fetch pipeline output |
| `get_jenkins_build_status` | Check build metadata |
| `trigger_jenkins_build` | Re-trigger after transient fix |
| `get_gitlab_file_content` | Read source files for verification |
| `commit_file_and_create_mr` | Commit the fix |

## Tips

- For **transient errors** (timeouts, 502s), a simple retry is often sufficient — no code fix needed.
- If the error doesn't match any catalogue entry, the agent falls back to general log analysis. Results may be less precise.
- Pipeline errors that stem from environment issues (Docker daemon down, disk full) can't be fixed via code — the agent will flag these for manual infrastructure action.
- For recurring failures, consider adding the pattern to the Jenkins Agent's error catalogue (see `docs/contributing.md`).

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Build log not found" | Wrong job name or build number | Verify `jenkins.job_name` in config |
| Diagnosis is vague | Error is not in the catalogue | Add the pattern to the Jenkins Agent's error catalogue |
| Fix doesn't compile | Context was insufficient | Provide more guidance at the HITL step |
| Re-trigger doesn't work | Jenkins token lacks Build permission | Check Jenkins API token scopes |
