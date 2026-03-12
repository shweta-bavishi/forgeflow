# Workflow 11: Generate Test Plan

**Goal**: Automatically generate Zephyr test cases from Jira issue acceptance criteria. Maps each criterion to structured test cases with steps, expected results, and preconditions. Links test cases to source Jira issues.

**Trigger**: "Generate test plan for {JIRA-KEY}", "Create test cases for {JIRA-KEY}", "Generate Zephyr tests for epic {JIRA-KEY}", "Create QA tests for sprint stories"

**Agents**: Orchestrator → Test Agent, Jira Agent, Code Agent, Project Context Agent

**Time**: ~15-30 minutes (depends on scope: single story vs. epic vs. sprint)

## Phase 1: DETERMINE SCOPE

### Identify What to Generate Tests For

```
IF developer provides a single Jira key (e.g., "PROJ-123"):
  Call: get_jira_issue_detail(PROJ-123)

  IF issue type is Epic:
    → Call: search_jira_issues(JQL: '"Epic Link" = PROJ-123 OR parent = PROJ-123')
    → Fetch details for each child issue
    → Mode: EPIC (generate test suite per child story)

  IF issue type is Story / Task / Bug:
    → Mode: SINGLE (generate tests for this one issue)

  IF issue type is Sub-task:
    → Mode: SINGLE (generate tests for this sub-task only)

IF developer says "current sprint" or "this sprint":
  Call: get_project_sprints(project_key)
  → Find active sprint
  → IF no active sprint → ask: "No active sprint found. Which sprint?"
  Call: search_jira_issues(JQL: 'sprint = {sprintId} AND type in (Story, Bug, Task)')
  → Fetch details for each issue
  → Mode: SPRINT (group by epic/feature area)

IF developer provides multiple keys ("PROJ-101, PROJ-102, PROJ-103"):
  → Fetch each issue individually
  → Mode: BATCH (generate for each, present as grouped plan)
```

## Phase 2: ANALYZE REQUIREMENTS

### Extract Acceptance Criteria

```
FOR EACH issue in scope:

  STEP 1 — Fetch full details:
    Call: get_jira_issue_detail(issue_key)
    Extract:
      - Summary
      - Description (full text — search for criteria patterns)
      - Custom fields (dedicated acceptance criteria field if configured)
      - Issue type
      - Labels, components
      - Parent/epic context

  STEP 2 — Parse acceptance criteria:
    PATTERN SEARCH ORDER:
      1. Given/When/Then blocks → each block = 1 test case
      2. Lines starting with "should", "must", "can" → each = 1+ tests
      3. Numbered criteria (AC1:, AC-1:) → each = 1+ tests
      4. Bullet-list requirements → each bullet = 1 test
      5. No explicit criteria → derive from description
         → Flag: "⚠️ LOW CONFIDENCE — criteria inferred from description"

  STEP 3 — Identify functionality type:
    API endpoint → needs request/response tests, status codes
    UI feature → needs user interaction, visual, accessibility tests
    Data processing → needs input/output, edge case tests
    Integration → needs connectivity, retry, timeout tests
    Configuration → needs validation, default value tests

  STEP 4 — Check for existing tests:
    Call: search_jira_issues(JQL: 'type = Test AND issue in linkedIssues({issue_key})')
    → If tests already exist:
      → Show: "{N} tests already linked to {issue_key}"
      → Ask: "Skip, regenerate, or add missing tests?"
    → If no existing tests → proceed

  STEP 5 — Read project test patterns:
    Call: search_in_repository(config.coding_standards.test_pattern)
    → Find existing test files
    Call: get_file_content(one_test_file) — read one for convention matching
    → Extract: naming style, describe/it patterns, assertion library, setup/teardown patterns
```

## Phase 3: GENERATE TEST CASES

### Test Derivation Per Issue

```
FOR EACH issue in scope:

  FOR EACH acceptance criterion:

    GENERATE happy-path test:
      Name: "Verify {criterion works as expected}"
      Type: Functional
      Priority: Critical (for core criteria) / High (for secondary)
      Steps: Standard flow with valid data
      Expected: Success as described in criterion

    GENERATE negative test:
      Name: "Verify {criterion violation is handled correctly}"
      Type: Negative
      Priority: High
      Steps: Attempt to violate the criterion
      Expected: Appropriate error / rejection

    IF criterion involves numeric/size values:
      GENERATE boundary tests:
        - At minimum value → should succeed
        - Below minimum → should fail
        - At maximum value → should succeed
        - Above maximum → should fail
        - Zero / empty → appropriate handling
        Type: Boundary
        Priority: Medium

    IF criterion involves file handling:
      GENERATE file validation tests:
        - Each valid format → success
        - Invalid format → rejection with error message
        - Size at limit → success
        - Size over limit → rejection (correct status code)
        - Empty/corrupt file → rejection
        Type: Edge Case
        Priority: High

    IF criterion involves API endpoint:
      GENERATE HTTP tests:
        - Correct method → expected response
        - Wrong method → 405
        - Missing required fields → 400
        - Invalid field values → 422
        Type: Functional
        Priority: High

  GENERATE cross-cutting tests (per feature, not per criterion):

    IF feature requires authentication:
      - "Verify unauthenticated request returns 401"
      - "Verify unauthorized role returns 403"
      - "Verify expired token returns 401"
      Type: Security
      Priority: High

    IF feature modifies data:
      - "Verify data persists correctly after operation"
      - "Verify rollback on partial failure"
      Type: Integration
      Priority: Medium

  DEDUPLICATION:
    → If two criteria produce identical tests → combine
    → If existing linked test covers a criterion → skip + note
    → Flag any duplicates rather than silently removing
```

### Present Generated Test Plan

```
## Test Plan: {JIRA-KEY} — {title}

### Source Acceptance Criteria:
1. {criterion 1}
2. {criterion 2}
3. {criterion 3}

### Generated Test Cases:

| # | Test Name | Type | Priority | Source | Steps Summary |
|---|-----------|------|----------|-------|---------------|
| 1 | Verify JPG avatar upload succeeds | Functional | Critical | AC-1 | Upload valid JPG → 200 + URL |
| 2 | Verify PNG avatar upload succeeds | Functional | Critical | AC-1 | Upload valid PNG → 200 + URL |
| 3 | Reject GIF file upload | Negative | High | AC-2 | Upload GIF → 400 + error |
| 4 | Reject file > 5MB | Boundary | High | AC-2 | Upload 5.1MB → 413 |
| 5 | Accept file exactly 5MB | Boundary | Medium | AC-2 | Upload 5MB → 200 |
| 6 | Reject empty file upload | Edge Case | Medium | AC-2 | Upload 0-byte → 400 |
| 7 | Response contains valid URL | Functional | Critical | AC-3 | Upload → verify URL |
| 8 | Reject upload without auth | Security | High | Implied | No auth → 401 |
| 9 | Reject upload for other user | Security | High | Implied | Wrong user → 403 |

### Detailed Test Case Example:

**#1 — Verify JPG avatar upload succeeds**
  Objective: Confirm avatar upload endpoint accepts valid JPG images
  Preconditions:
    - User is authenticated
    - User account exists with ID {test_user_id}
  Steps:
    1. Prepare a valid JPG image file (100KB, 200x200px)
    2. Send POST request to /api/users/{test_user_id}/avatar (multipart/form-data)
    3. Observe response status code
    4. Observe response body
  Expected Results:
    - Step 3: Status code is 200
    - Step 4: Response body contains "avatarUrl" field with valid URL
  Test Data: test-avatar.jpg (100KB, 200x200px, valid JPEG)
  Priority: Critical
  Type: Functional

### Coverage Summary:
  Acceptance criteria covered: {N}/{total} (100%)
  Test cases: {total_tests}
    Functional: {N} | Negative: {N} | Boundary: {N}
    Security: {N} | Edge Case: {N} | Integration: {N}
```

## Phase 4: 🚦 HITL GATE — Review Test Plan

```
Show the complete test plan to developer (or QA lead).

Developer can:
  - Add missing tests: "Add a test for concurrent uploads"
  - Remove tests: "Remove test #6, we don't support empty files"
  - Change priority: "Change #8 to Critical"
  - Modify steps: "Update test data for #4 to use 6MB instead"
  - Add criteria: "Also test for SVG format rejection"
  - Reorder: "Move security tests to top"

SUPPORT MULTI-ROUND REFINEMENT:
  → After each change, re-present the updated plan
  → Ask: "Any other changes, or ready to create?"

IF developer is satisfied:
  → Proceed to Phase 5

IF developer wants to add acceptance criteria to Jira first:
  → Pause workflow
  → Resume after Jira is updated
```

## Phase 5: 🚦 HITL GATE — Confirm Zephyr Creation

```
Before creating any Zephyr issues, show final summary:

Ready to create {N} test cases in Zephyr:
  - {PROJ-101}: {X} tests (Functional: {a}, Negative: {b}, Security: {c})
  - {PROJ-102}: {Y} tests
  - {PROJ-103}: {Z} tests
  Total: {N} Zephyr Test issues

Each test will be:
  - Created as issue type: "{config.zephyr.test_issue_type}"
  - Labeled: {config.zephyr.labels}
  - Linked to source issue via "{config.zephyr.test_link_type}" link

Proceed?

WAIT for explicit approval.

IF developer says no → ask what to change
IF developer wants to export as text instead → output test cases as formatted text
```

## Phase 6: CREATE & LINK

### Execute Zephyr Test Creation

```
FOR EACH approved test case:

  STEP 1 — Build test issue data:
    Summary: {test name} (max 255 chars)
    Description: Full test case details:
      **Objective:** {objective}
      **Preconditions:** {preconditions}
      **Steps:**
        1. {step 1}
        2. {step 2}
        ...
      **Expected Results:**
        - Step 1: {expected}
        - Step 2: {expected}
        ...
      **Test Data:** {specific test data}
    Priority: {from test case}
    Labels: config.zephyr.labels
    Component: {from source Jira issue}

  STEP 2 — Create in Zephyr:
    Call: create_zephyr_test(test_data)

    → TRY: create_zephyr_test
    → FALLBACK: If Zephyr unavailable → create_jira_subtask(parent=source_issue, test_details)
    → ASK: If both fail → inform developer, offer text export

  STEP 3 — Link to source issue:
    Call: link_issues(
      issue_key_1: test_key,
      issue_key_2: source_issue_key,
      link_type: config.zephyr.test_link_type  // "Tests"
    )

    → TRY: link_issues
    → FALLBACK: Warn "Could not link — link type may not exist"
    → Continue with remaining tests

  STEP 4 — Report progress:
    ✓ Created TEST-001: Verify JPG avatar upload succeeds → linked to PROJ-1234
    ✓ Created TEST-002: Verify PNG avatar upload succeeds → linked to PROJ-1234
    ✗ Failed TEST-003: {error reason}
    ...

  ON PARTIAL FAILURE:
    → Continue creating remaining tests
    → Collect all successes and failures
    → Report at end: "{N}/{total} created successfully. {M} failed."
```

## Phase 7: SUMMARY

```
## Test Plan Generated

**Scope:** {epic/story/sprint} — {scope description}
**Total test cases:** {N}
  - Functional: {N}
  - Negative: {N}
  - Boundary: {N}
  - Security: {N}
  - Edge Case: {N}
  - Integration: {N}

**Coverage:**
  - Acceptance criteria covered: {N}/{total} (100%)
  - Stories with tests: {N}/{total}
  - Inferred criteria (low confidence): {N}

**Created Zephyr issues:** TEST-001 through TEST-{N}
  All linked to source Jira issues.

**Next Steps:**
  1. Review individual test cases in Jira
  2. Assign test cases to QA team members
  3. Execute test cases during QA phase
  4. Update test results in Zephyr
  5. Generate test execution report
```

## Error Handling

```
Jira issue has no acceptance criteria:
  → Derive tests from description (MEDIUM confidence)
  → Warn: "⚠️ No explicit acceptance criteria. Tests are inferred. Review carefully."
  → Offer: "Add acceptance criteria to Jira first and re-run?"

create_zephyr_test fails:
  → TRY: create_zephyr_test
  → FALLBACK: create_jira_subtask with test case in description
  → ASK: "Zephyr unavailable. Created as Jira sub-task. OK?"

Epic has no child stories:
  → Treat the epic itself as the test source
  → Warn: "No child stories. Generating tests from epic directly."

No active sprint:
  → List available sprints
  → Ask: "Which sprint should I use?"

Duplicate test exists:
  → Show existing test
  → Ask: "Test already exists. Skip or regenerate?"
  → Skip by default to avoid duplicates

link_issues fails:
  → Warn: "Link type '{type}' may not exist in Jira."
  → Continue with remaining tests
  → Suggest: "Configure zephyr.test_link_type in forgeflow.config.yml"

Too many test cases generated (> 50):
  → Warn: "Generated {N} test cases — consider reviewing for duplicates"
  → Suggest: "Want to create in batches? (First 20, then next 20, etc.)"
```

## Special Cases

### Epic-Level Test Plans

```
IF generating for an epic:
  → Fetch all child stories
  → Generate tests per story
  → Present as grouped test plan:

  Test Plan: PROJ-100 (Epic: User Management)
  ├── PROJ-101 (Story: User Registration) — 8 tests
  ├── PROJ-102 (Story: User Login) — 6 tests
  ├── PROJ-103 (Story: Password Reset) — 7 tests
  └── PROJ-104 (Story: User Profile) — 5 tests
  Total: 26 tests

  → Add epic-level label for grouping: "epic-PROJ-100"
```

### Sprint-Level Test Plans

```
IF generating for a sprint:
  → Group by epic/feature area
  → Show coverage across the sprint

  Test Plan: Sprint 23 (Mar 1-15)
  ├── Epic: User Management (3 stories, 21 tests)
  ├── Epic: Analytics Dashboard (2 stories, 14 tests)
  └── Standalone: Bug Fix PROJ-150 (4 tests)
  Total: 39 tests
```

### Generating Tests for Bugs

```
IF issue type is Bug:
  → Generate:
    1. Reproduction test (verify the bug exists / existed)
    2. Fix verification test (verify the fix works)
    3. Regression test (verify related functionality still works)
  → Tests are typically higher priority (Critical/High)
```

## What NOT to Do

- ❌ Don't generate vague tests ("Verify it works correctly")
- ❌ Don't use placeholder test data ("TODO: fill in test data")
- ❌ Don't skip negative tests — they catch more bugs
- ❌ Don't create duplicate tests for the same criterion
- ❌ Don't create Zephyr issues without HITL approval
- ❌ Don't generate 100 tests for a simple story — be comprehensive but not exhaustive
- ❌ Don't assume acceptance criteria format — support multiple patterns
- ❌ Don't ignore security tests for authenticated features
- ❌ Don't mark inferred tests as high confidence
- ❌ Don't skip reading existing tests for pattern matching

## Success Criteria

✓ Every acceptance criterion has at least one happy-path and one negative test
✓ Boundary conditions tested for numeric/size constraints
✓ Security tests included for authenticated features
✓ Test cases have specific, actionable steps and concrete test data
✓ Tests follow project's existing naming conventions
✓ Duplicates identified and avoided
✓ All Zephyr tests linked to source Jira issues
✓ Developer reviews and approves before creation
✓ Coverage summary shows criteria → test mapping
✓ Partial failures don't block remaining test creation

---

**Duration**: 15-30 minutes (varies with scope)

**What It Creates**:
- Structured test plan document
- Zephyr Test issues in Jira (linked to source stories)
- Coverage summary

**Next Steps**:
- Assign tests to QA team
- Execute during QA phase
- Report results in Zephyr

**Related**: Test Agent, Jira Agent, Code Agent
