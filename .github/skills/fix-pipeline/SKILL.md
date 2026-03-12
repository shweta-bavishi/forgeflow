---
name: fix-pipeline
description: "Diagnose and fix CI/CD pipeline failures. Fetches Jenkins build logs, identifies root cause from error catalog, generates targeted code fixes, and creates fix MR."
---

# Skill: Fix Pipeline

Diagnose a failed CI/CD pipeline, identify root cause from build logs, generate a fix, and create a fix MR.

## Phase 1: IDENTIFY PIPELINE

```
Determine which pipeline failed:

IF developer specifies job/build:
  → Use that directly

IF ambiguous:
  Call: jenkins_get_job_status(config.jenkins.job_name)
  → Get latest failed build number

  Call: get_project_pipelines(config.gitlab.project_id)
  → Show recent pipeline runs with status

  Ask: "Which pipeline? a) Latest failed build  b) Specific job  c) Specific build #"
```

## Phase 2: FETCH LOGS

```
Call: jenkins_get_build_status(job_name, build_number)
Extract: stage that failed, duration, overall result

Call: jenkins_get_console_text(job_name, build_number)
Extract: error messages, stack traces, failed commands
  → This is the PRIMARY diagnosis source
  → Parse the full console output for error patterns
```

## Phase 3: DIAGNOSE

```
Apply error catalog to classify failure:

COMPILATION ERRORS (syntax, type, import):
  Pattern: "error TS2304", "Cannot find module", "SyntaxError"
  Fix: Code Agent corrects source files
  Confidence: HIGH (usually auto-fixable)

DEPENDENCY ERRORS (missing deps, version conflicts):
  Pattern: "Cannot resolve", "ERESOLVE", "version conflict"
  Fix: Update package.json/pom.xml, run install
  Confidence: HIGH

TEST FAILURES (failing tests):
  Pattern: "FAIL", "Expected.*but received", "AssertionError"
  Fix: Analyze test + source code, fix logic
  Confidence: MEDIUM (may need developer input)

CONFIGURATION ERRORS (env vars, config):
  Pattern: "undefined env", "config not found", "missing variable"
  Fix: Update config files or document needed env vars
  Confidence: MEDIUM

INFRASTRUCTURE ERRORS (timeout, OOM, network):
  Pattern: "ENOMEM", "timeout", "ECONNREFUSED"
  Fix: Cannot auto-fix — guide developer to manual resolution
  Confidence: LOW (needs infra team)

LINT/FORMAT ERRORS (style violations):
  Pattern: "eslint", "prettier", "checkstyle"
  Fix: Run formatter/linter auto-fix
  Confidence: HIGH (usually auto-fixable)
```

## Phase 4: ANALYZE SOURCE CODE

```
Call: get_file_content for each affected file from error log

Understand:
  - What the code is trying to do
  - Why it's failing
  - What the correct fix would be

For test failures:
  Read both test file and source file
  Determine if test is wrong or source is wrong
```

## Phase 5: PRESENT DIAGNOSIS

```
## Pipeline Diagnosis

**Job:** {job_name} #{build_number}
**Stage Failed:** {stage_name}
**Category:** {COMPILATION | DEPENDENCY | TEST | CONFIG | INFRA | LINT}

### Root Cause
{Clear explanation of why the build failed}

### Error Details
{Relevant error message from console log}

### Affected Files
{List of files that need fixing}

### Proposed Fix
{Description of what needs to change}
```

## Phase 6: 🚦 HITL GATE — Developer Approves Approach

```
Developer reviews diagnosis and proposed fix
Can: approve, suggest alternative, point to relevant code, skip
```

## Phase 7: GENERATE FIX

```
FOR each affected file:
  Call: get_file_content(file_path) — read current state
  Generate fix following project patterns
  Show before/after with explanation
```

## Phase 8: 🚦 HITL GATE — Review Fix Code

```
Developer reviews generated fix code
Multi-round iteration until satisfied
```

## Phase 9: COMMIT & MR

```
Call: commit_file_and_create_mr(
  files: [fixed files],
  branch: "fix/{JIRA-KEY}-pipeline-fix" or "fix/pipeline-{date}",
  title: "fix: {brief description of fix}",
  description: "Pipeline fix for #{build_number}\n\nRoot cause: {diagnosis}\nFix: {what changed}"
)

Show MR link to developer
```

## Error Handling

```
Jenkins unavailable → check GitLab pipelines instead
No recent builds → ask developer which build to diagnose
Infrastructure issue → guide manual fix, cannot auto-resolve
Multiple failures → diagnose most critical first, then offer to fix others
```
