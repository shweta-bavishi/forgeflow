# Workflow 09: MR Auto-Review

**Goal**: Perform a comprehensive, multi-dimensional automated review of a Merge Request BEFORE human reviewers see it. Identify issues, verify standards compliance, check quality gates, assess test coverage, and post a structured review comment — saving human reviewer time and reducing review cycles.

**Trigger**: "Review my MR", "Auto-review MR !{id}", "Pre-review my changes", "Is my MR ready for review?"

**Agents**: Orchestrator → GitLab Agent, SonarQube Agent, Code Agent, Project Context Agent, Jira Agent

**Time**: ~15-25 minutes (analysis depth depends on MR size)

## Phase 1: IDENTIFY & FETCH MR

### Determine MR to Review

```
IF developer says "review my MR" (no ID):
  → Call: list_project_merge_requests(state="opened", author=current_user)
  → IF one open MR → confirm: "Found MR !{id}: '{title}'. Review this one?"
  → IF multiple open MRs → present list, ask developer to choose
  → IF no open MRs → "No open MRs found. Did you push your branch?"

IF developer provides MR ID (e.g., "review MR !142"):
  → Use MR !142 directly

IF developer says "pre-review my changes" (on a branch):
  → Try to find MR for the current branch
  → If no MR exists → "No MR found for this branch. Create one first, or want me to review the diff against {target_branch}?"
```

### Fetch MR Data

```
Call: review_merge_request(mr_id)
Extract:
  - Title, description, source branch → target branch
  - Changed files list with line counts (+add / -del)
  - Full diff content
  - Commit list and messages
  - Pipeline status
  - Approval status
  - Linked Jira key (from branch name pattern or MR description)

IF review_merge_request fails:
  → TRY: get_merge_request_details as fallback
  → FALLBACK: Ask developer for MR URL
  → ASK: "Cannot fetch MR data. Is the MR ID correct?"
```

## Phase 2: MULTI-DIMENSIONAL ANALYSIS

The Code Agent performs 6 review dimensions. Each finding is rated:
- 🔴 **BLOCKER** — Must fix before merging
- 🟡 **WARNING** — Should fix; review carefully
- 🟢 **OK** — Passes checks
- ℹ️ **INFO** — Informational; no action required

### Dimension 1: Standards Compliance

```
🎯 GOAL: Verify code follows project conventions

READ: coding_standards from otomate.config.yml

FOR EACH changed file:
  CHECK naming:
    - File name follows config.coding_standards.naming.files pattern?
    - Classes follow config.coding_standards.naming.classes?
    - Functions follow config.coding_standards.naming.functions?
    - Constants follow config.coding_standards.naming.constants?

  CHECK required patterns:
    - Error handling present? (try/catch, error callbacks)
    - Input validation present? (for endpoints, public methods)
    - JSDoc / docstrings on public methods?
    - Proper logging (not console.log in production)?

  CHECK forbidden patterns:
    FOR EACH pattern in config.auto_review.forbidden_patterns:
      - Search diff for: "console.log", "debugger", "TODO", "FIXME", "HACK"
      - If found → 🟡 WARNING: "Found '{pattern}' in {file}:{line}"

  CHECK import organization:
    - Imports sorted per project convention?
    - No circular imports introduced?

  CHECK consistency:
    Call: search_in_repository(similar_pattern)
    → Verify new code follows same patterns as existing code
    → If new code deviates → ℹ️ INFO: "Different pattern than {existing_file}"

AGGREGATION:
  IF any naming violations → 🟡 WARNING
  IF forbidden patterns found → 🟡 WARNING
  IF all checks pass → 🟢 OK
```

### Dimension 2: Architecture Compliance

```
🎯 GOAL: Verify files are in correct layers and dependencies flow correctly

READ: architecture from otomate.config.yml

FOR EACH new file:
  CHECK: Is it in the correct directory for its type?
    - Controller in config.architecture.layers[controllers].path?
    - Service in config.architecture.layers[services].path?
    - Repository in config.architecture.layers[repositories].path?
    → If misplaced → 🔴 BLOCKER: "Controller logic found in {wrong_path}"

FOR EACH changed file:
  CHECK dependency direction:
    - Controllers may import services ✓
    - Services may import repositories ✓
    - Repositories may import entities ✓
    - Controllers importing repositories directly → 🟡 WARNING: "Layer violation"
    - Services importing controllers → 🔴 BLOCKER: "Reverse dependency"

  CHECK module structure:
    - New functionality in existing module? → ✓
    - New module follows established pattern? → ✓
    - Cross-module dependencies introduced? → ℹ️ INFO

IF architecture not configured in config → ℹ️ INFO: "Architecture rules not configured; skipping"
```

### Dimension 3: Test Coverage

```
🎯 GOAL: Verify adequate test coverage for changes

Call: get_project_uncovered_lines(project_key) for changed files
Call: get_sonar_project_measures(project_key) for coverage metrics

CHECK — New source files have tests:
  FOR EACH new source file (not test file):
    → Search for corresponding test file matching config.coding_standards.test_pattern
    → If NO test file → 🔴 BLOCKER: "No tests for new file {file}"
    → If test file exists → 🟢 OK

CHECK — Test file naming:
  → Does test file name match convention from config?
  → Example: user.service.ts → user.service.spec.ts ✓

CHECK — Coverage threshold:
  → Is overall coverage >= config.coding_standards.coverage_threshold?
  → If below threshold → 🟡 WARNING: "Coverage {X}% below threshold {Y}%"
  → If above threshold → 🟢 OK

CHECK — New public methods/endpoints:
  → Are new public methods covered by tests?
  → If new endpoint without tests → 🔴 BLOCKER: "New endpoint POST /api/users without tests"

CHECK — Critical path coverage:
  → Error handling branches tested?
  → Edge cases considered?
  → If critical paths uncovered → 🟡 WARNING

IF SonarQube data unavailable → ℹ️ INFO: "Coverage data unavailable; skipping coverage check"
```

### Dimension 4: Quality Gate

```
🎯 GOAL: Check SonarQube quality gate status

Call: get_sonar_quality_gate_status(project_key)
Call: get_sonar_project_issues(project_key, filter="new_issues_only")

CHECK — Quality gate:
  IF gate PASSES → 🟢 OK
  IF gate FAILS → 🔴 BLOCKER: "Quality gate failing: {conditions}"

CHECK — New issues introduced by this MR:
  IF new BLOCKER/CRITICAL issues → 🔴 BLOCKER: "{N} new critical issues"
  IF new MAJOR issues → 🟡 WARNING: "{N} new major issues"
  IF no new issues → 🟢 OK

CHECK — Technical debt:
  IF debt increased significantly → 🟡 WARNING: "Technical debt increased by {hours}"

CHECK — Security hotspots:
  IF new security hotspots → 🟡 WARNING: "{N} new security hotspots to review"

IF SonarQube unavailable → ℹ️ INFO: "SonarQube unavailable; skipping quality gate check"
```

### Dimension 5: Jira Alignment

```
🎯 GOAL: Verify MR aligns with the linked Jira ticket

EXTRACT Jira key from:
  1. Branch name pattern (e.g., feature/PROJ-123-description → PROJ-123)
  2. MR description (search for PROJ-### pattern)
  3. Commit messages

IF Jira key found:
  Call: get_jira_issue_detail(jira_key)
  Extract: summary, description, acceptance criteria

  CHECK — MR references Jira:
    → MR description mentions Jira key? → ✓
    → If not → 🟡 WARNING: "MR description doesn't reference {JIRA-KEY}"

  CHECK — Changes align with Jira scope:
    → Do changed files relate to the ticket's domain?
    → Are unrelated files being modified? → 🟡 WARNING: "Scope creep: {file} seems unrelated to {JIRA-KEY}"

  CHECK — Acceptance criteria addressed:
    → Map each criterion to changed files/tests
    → If criterion appears unaddressed → ℹ️ INFO: "AC #{N} may not be covered by changes"
    → If all criteria have matching changes → 🟢 OK

IF Jira key NOT found:
  → ℹ️ INFO: "No linked Jira found. Consider adding ticket reference to MR description."
```

### Dimension 6: General Code Quality

```
🎯 GOAL: Review the actual diff for code quality issues

Code Agent reviews the diff for:

LOGIC:
  - Potential bugs or logic errors
  - Missing edge case handling
  - Off-by-one errors
  - Incorrect boolean logic

ERROR HANDLING:
  - Uncaught exceptions
  - Missing try/catch for async operations
  - Generic catch blocks that swallow errors
  - Missing error responses for API endpoints

RESOURCES:
  - Unclosed connections, streams, file handles
  - Memory leaks (event listeners not removed)
  - Missing cleanup in finally blocks

CONCURRENCY:
  - Race conditions in async operations
  - Missing locks for shared state
  - Unhandled promise rejections

PERFORMANCE:
  - N+1 query patterns (loop with DB call inside)
  - Unnecessary iterations over large datasets
  - Missing pagination for list endpoints
  - Large payloads without streaming

SECURITY:
  - SQL injection (string concatenation in queries)
  - XSS (unsanitized user input in responses)
  - Missing auth checks on new endpoints
  - Hardcoded secrets or credentials
  - Insecure randomness for security-sensitive operations

CODE QUALITY:
  - Dead code or unreachable branches
  - Magic numbers / hardcoded values that should be constants
  - Overly complex functions (too many branches, deep nesting)
  - Copy-pasted code that should be extracted

LOGGING:
  - Sensitive data in logs (passwords, tokens, PII)
  - Too verbose (logging in hot loops)
  - Too sparse (no logging for error paths)

RATING:
  - Critical security/logic issues → 🔴 BLOCKER
  - Performance concerns → 🟡 WARNING
  - Style/quality suggestions → ℹ️ INFO
```

## Phase 3: PIPELINE CHECK

```
Call: get_project_pipelines(project_id) for this MR's branch

IF pipeline PASSED → 🟢 OK
IF pipeline FAILED:
  → 🔴 BLOCKER: "Pipeline failed at stage '{stage}'"
  → Suggest: "Run 'fix pipeline' workflow (05) to diagnose"
IF pipeline RUNNING → ℹ️ INFO: "Pipeline still running — final status pending"
IF pipeline NOT TRIGGERED → 🟡 WARNING: "No pipeline run found for this MR"
```

## Phase 4: GENERATE REVIEW REPORT

Assemble all dimension results into a structured report:

```
## 🔍 Otomate Auto-Review: MR !{id}

**{title}**
Branch: `{source}` → `{target}` | Files: {count} | Lines: +{add} -{del}
Linked Jira: {JIRA-KEY} — {jira_title}

---

### Summary
{1-2 sentence overall assessment based on findings}

**Verdict: ✅ READY FOR REVIEW / ⚠️ NEEDS ATTENTION / 🚫 NOT READY**

---

### 📋 Standards Compliance {🟢/🟡/🔴}
{findings with file:line references}

### 🏗️ Architecture Compliance {🟢/🟡/🔴}
{findings — layer violations, dependency direction}

### 🧪 Test Coverage {🟢/🟡/🔴}
{findings — coverage %, missing tests, uncovered lines}

### 🛡️ Quality Gate {🟢/🟡/🔴}
{findings — gate status, new issues, debt change}

### 📋 Jira Alignment {🟢/🟡/🔴}
{findings — criteria coverage, scope check}

### 💻 Code Quality {🟢/🟡/🔴}
{findings — specific issues with file:line references}

---

### 🎯 Action Items
{Numbered list of specific things to fix, ordered by severity:
  1. 🔴 {blocker description} — {file:line}
  2. 🟡 {warning description} — {file:line}
  ...}

### 💡 Suggestions (Optional)
{Non-blocking suggestions for improvement}

---
_Auto-reviewed by Otomate • {timestamp}_
```

### Verdict Logic

```
IF ANY 🔴 BLOCKER found:
  → Verdict = 🚫 NOT READY
  → Message: "{N} blocker(s) must be resolved before merging"

IF any 🟡 WARNING found but NO blockers:
  → Verdict = ⚠️ NEEDS ATTENTION
  → Message: "{N} warning(s) to review; no blockers"

IF all dimensions are 🟢 OK:
  → Verdict = ✅ READY FOR REVIEW
  → Message: "All checks passed. Ready for human review."

CALIBRATION:
  → Don't be overly strict — the goal is to HELP, not gatekeep
  → False positives erode trust
  → If unsure about a finding → mark as ℹ️ INFO, not 🔴 BLOCKER
  → Prioritize actionable feedback over exhaustive nitpicking
  → A review with 3 specific, actionable items beats one with 30 vague ones
```

## Phase 5: 🚦 HITL GATE — Approve Posting Review

```
Show developer the complete review report.

ASK: "Here's the auto-review. Would you like to:
  1. Post this review as a comment on the MR
  2. Edit before posting
  3. Fix the issues first and re-review later
  4. Don't post (just for my reference)"

IF developer chooses "Edit":
  → Let them modify findings
  → They may disagree with some findings — let them remove or change severity
  → Re-generate the report with modifications

IF developer chooses "Fix first":
  → Save the review for reference
  → Offer to help fix specific issues

IMPORTANT:
  → NEVER post a review without developer approval
  → Developer might disagree with findings — that's OK
  → The review is a draft until approved
```

## Phase 6: POST REVIEW (If Approved)

```
IF developer approves posting:

  PREFERRED — Use review_and_comment_mr:
    Call: review_and_comment_mr(mr_id, review_content)
    → Posts the full review as an MR comment in one call
    → Includes diff context and line references

  ALTERNATIVE — Use post_mr_review_comment:
    Call: post_mr_review_comment(mr_id, comment_body)
    → Use when review_merge_request was already called in Phase 1
    → Posts the formatted review as a comment

  VERIFY:
    → Confirm comment was posted successfully
    → Show developer: "Review posted to MR !{id}"

  IF posting fails:
    → TRY: Retry once
    → FALLBACK: Offer to copy review to clipboard
    → ASK: "Could not post comment. Want me to try again or show you the text to paste manually?"
```

## Phase 7: OFFER FOLLOW-UP ACTIONS

```
Based on findings, offer relevant next steps:

IF sonar issues found:
  → "Want me to fix the sonar issues? (Workflow 06)"

IF missing tests:
  → "Want me to generate test stubs for the untested code?"

IF MR description missing Jira link:
  → "Want me to update the MR description with the Jira reference?"

IF pipeline failed:
  → "Want me to diagnose the pipeline failure? (Workflow 05)"

IF all clear:
  → "MR looks good! Ready for human review. Anything else?"

IF developer wants to fix and re-review:
  → Remember the review findings
  → After fixes: "Ready for re-review? I'll run the checks again."
```

## Error Handling

```
MR not found:
  → Ask: "MR !{id} not found. Check the ID or provide the full URL."

SonarQube unavailable:
  → Skip quality gate dimension
  → Note: "⚠️ SonarQube data unavailable — quality gate and coverage checks skipped"
  → Continue with other dimensions

Jira not linked:
  → Skip Jira alignment dimension
  → Note: "ℹ️ No Jira linked — alignment check skipped"

Pipeline hasn't run:
  → Note: "ℹ️ Pipeline not yet triggered — results pending"
  → Don't block the review

Review finds zero issues:
  → Still show the report (confirmation is valuable)
  → Verdict: ✅ READY FOR REVIEW
  → "All checks passed! No issues found."

Large MR (> 50 files):
  → Warn: "This is a large MR ({N} files). Review may take longer."
  → Focus on most critical files first
  → Suggest: "Consider splitting into smaller MRs for easier review"
```

## What NOT to Do

- ❌ Don't post review comments without developer approval
- ❌ Don't be overly pedantic — focus on meaningful issues
- ❌ Don't block review because one dimension has no data
- ❌ Don't classify uncertain findings as BLOCKER — use INFO
- ❌ Don't ignore security issues even if MR is small
- ❌ Don't skip the review if the MR "looks simple"
- ❌ Don't merge or approve the MR — only review and comment
- ❌ Don't generate a review longer than the code change itself

## Success Criteria

✓ All 6 review dimensions are evaluated (or noted as skipped with reason)
✓ Findings are specific: file name, line number, concrete issue
✓ Verdict is accurate and calibrated (not too strict, not too lenient)
✓ Action items are prioritized and actionable
✓ Developer reviews and approves before posting
✓ Review saves human reviewer time by catching obvious issues
✓ False positive rate stays low (trust is maintained)
✓ Follow-up actions are offered based on findings

---

**Duration**: 15-25 minutes (varies with MR size)

**What It Creates**:
- Structured review report with 6 dimensions
- MR comment (if approved by developer)
- Action items list for remediation

**Next Steps**:
- Fix identified issues
- Re-run auto-review after fixes
- Request human review once auto-review passes

**Related**: Code Agent, GitLab Agent, SonarQube Agent, Jira Agent

**Model Hint**: MOST_CAPABLE (deep code analysis and reasoning)
