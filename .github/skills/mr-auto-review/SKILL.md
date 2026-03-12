---
name: mr-auto-review
description: "Auto-review a merge request with 6-dimension analysis: standards compliance, architecture compliance, test coverage, quality gate, Jira alignment, and code quality. Posts structured review comment to MR."
---

# Skill: MR Auto-Review

Perform a structured 6-dimension review of a merge request, produce a severity-rated report, and optionally post as MR comment.

## Phase 1: IDENTIFY & FETCH MR

```
IF developer specifies MR ID:
  Call: review_merge_request(mr_id)

IF "review my MR" (no ID):
  Call: list_project_merge_requests(state="opened")
  → Show open MRs, ask developer to choose
  → Or auto-select if only one open MR by current user

Extract from MR:
  - Title, description, diff (changed files with content)
  - Commits (messages, authors)
  - Pipeline status
  - Approval status
  - Linked Jira key (from title pattern: PROJ-123: ...)
```

## Phase 2: MULTI-DIMENSIONAL ANALYSIS

### Dimension 1: Standards Compliance

```
CHECK against config.coding_standards:
  - File naming matches config.coding_standards.naming.files
  - Class/function/variable naming follows conventions
  - No forbidden patterns from config.auto_review.forbidden_patterns:
    console.log, debugger, TODO, FIXME, HACK
  - Import style consistent with existing code
  - JSDoc on new public methods
  - Formatting matches linter/formatter

Call: get_file_content for reference files in same directory
Rate: 🔴 BLOCKER | 🟡 WARNING | 🟢 OK
```

### Dimension 2: Architecture Compliance

```
CHECK against config.architecture:
  - Files in correct layers (controllers/, services/, etc.)
  - Dependency direction: controllers → services → repos → entities
  - VIOLATION: controllers importing repositories directly
  - VIOLATION: services importing controllers
  - New providers registered in module
  - No business logic in controllers
  - No HTTP concerns in services

Rate: 🔴 BLOCKER for violations | 🟢 OK otherwise
```

### Dimension 3: Test Coverage

```
CHECK:
  - New source files have test files matching config.coding_standards.test_pattern
  - New public methods have at least one test
  - Coverage threshold met: config.coding_standards.coverage_threshold

Call: get_project_uncovered_lines(config.sonarqube.project_key)
Call: search_in_repository for test files matching new source files

Rate: 🔴 BLOCKER if no tests | 🟡 WARNING if below threshold | 🟢 OK
```

### Dimension 4: Quality Gate

```
Call: get_sonar_quality_gate_status(config.sonarqube.project_key)
Call: get_sonar_project_issues(config.sonarqube.project_key) — new issues only

CHECK:
  - Gate status: PASSED / FAILED
  - New BLOCKER or CRITICAL issues introduced
  - Technical debt change
  - Security hotspots

Rate: 🔴 BLOCKER if gate fails | 🟡 WARNING for new issues | 🟢 OK
```

### Dimension 5: Jira Alignment

```
Extract Jira key from MR title/description
Call: get_jira_issue_detail(jira_key)

CHECK:
  - MR references valid Jira issue
  - Changes align with ticket scope (not over/under-scoped)
  - Acceptance criteria addressed by code changes
  - No unrelated changes (scope creep)
  - Jira status appropriate (should be "In Review")

Rate: 🟡 WARNING if no Jira ref | ℹ️ INFO for scope notes | 🟢 OK
```

### Dimension 6: Code Quality

```
Analyze diff for:
  - Logic errors (off-by-one, null dereference, infinite loops)
  - Error handling (empty catch, missing exception types)
  - Resource management (streams, connections not closed)
  - Performance:
    - N+1 query patterns
    - Unbounded collections
    - Missing pagination
    - Unnecessary computation in loops
  - Security:
    - SQL injection (non-parameterized queries)
    - XSS (unencoded output)
    - Hardcoded secrets
  - Dead code (unused imports, unreachable branches)
  - Magic numbers (unnamed constants)

Rate each finding: 🔴 BLOCKER | 🟡 WARNING | ℹ️ INFO
```

## Phase 3: PIPELINE CHECK

```
Call: get_project_pipelines(config.gitlab.project_id)
→ Find pipeline for MR source branch
→ Status: passed / failed / running
```

## Phase 4: GENERATE REVIEW REPORT

```
## MR Review: !{mr_id} — {title}

**Verdict:** {🚫 NOT READY | ⚠️ NEEDS ATTENTION | ✅ READY FOR REVIEW}
**Branch:** {source} → {target}
**Files:** {count} changed (+{added} -{removed})
**Pipeline:** {status}

### Standards Compliance: {emoji}
{findings or "No issues"}

### Architecture Compliance: {emoji}
{findings or "No issues"}

### Test Coverage: {emoji}
{coverage %, findings}

### Quality Gate: {emoji}
{gate status, new issues}

### Jira Alignment: {emoji}
{Jira ref, scope assessment}

### Code Quality: {emoji}
{findings by category}

---
### Action Items
{numbered list of blockers and warnings with file:line and fix suggestion}

### Suggestions
{info-level improvements}
```

### Verdict Logic

```
ANY 🔴 BLOCKER → 🚫 NOT READY
NO blockers, ANY 🟡 WARNING → ⚠️ NEEDS ATTENTION
ONLY 🟢 OK and ℹ️ INFO → ✅ READY FOR REVIEW
```

## Phase 5: 🚦 HITL GATE — Developer Reviews Report

```
Developer can:
  a) Post review as-is
  b) Edit findings (adjust severity, remove false positives)
  c) Fix issues → hand off to Otomate Code
  d) Skip posting (keep for reference)
```

## Phase 6: POST REVIEW

```
IF developer approves posting:
  Call: review_and_comment_mr(mr_id, review_content)
  OR: post_mr_review_comment(mr_id, comment_content)
```

## Phase 7: OFFER FOLLOW-UPS

```
IF issues found:
  - "Fix these issues?" → hand off to Otomate Code
  - "Generate missing tests?" → trigger generate-test-plan
  - "Fix sonar issues?" → trigger sonar-fix

IF pipeline failed:
  - "Diagnose pipeline?" → trigger fix-pipeline

IF MR looks good:
  - "Create release?" → trigger release-build
```

## Calibration Rules

```
HELP, don't gatekeep — assist developer, don't block
MINIMIZE false positives — read context before flagging
ACTIONABLE feedback — every finding includes how to fix
PROPORTIONAL severity — style issues are not BLOCKERs
GROUP related findings — don't repeat the same pattern 20 times
```
