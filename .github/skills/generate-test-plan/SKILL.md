---
name: generate-test-plan
description: "Generate Zephyr test cases from Jira acceptance criteria. Supports single stories, entire epics, or full sprints. Creates test cases linked to source Jira issues."
---

# Skill: Generate Test Plan

Extract acceptance criteria from Jira issues, generate structured test cases, and create them in Zephyr (with Jira subtask fallback).

## Phase 1: SCOPE DETERMINATION

```
IF single Jira key (Story/Task):
  → Process one issue

IF epic key:
  Call: search_jira_issues(jql="'Epic Link' = {epic_key}")
  → Process all child stories

IF "current sprint":
  Call: get_project_sprints(config.jira.project_key)
  → Pick active sprint
  Call: search_jira_issues(jql="sprint = {sprint_id} AND type in (Story, Task)")
  → Process all stories in sprint

IF multiple keys:
  → Process each
```

## Phase 2: REQUIREMENTS ANALYSIS

```
FOR EACH issue:

  Call: get_jira_issue_detail(issue_key)
  Extract acceptance criteria using these patterns:

  PATTERN 1 — Given/When/Then (BDD):
    "Given a logged-in user
     When they upload an image > 5MB
     Then the system rejects the upload"

  PATTERN 2 — Bullet list:
    - "Users can upload images"
    - "File size limited to 5MB"

  PATTERN 3 — Numbered criteria:
    1. Upload endpoint accepts PNG, JPG, GIF
    2. Files compressed to 300x300

  PATTERN 4 — Implicit (from description):
    Description mentions behavior → extract as implicit criteria

  Check existing tests:
    Call: search_jira_issues(jql="issue in linkedIssues({key}) AND type = Test")
    → Avoid duplicating existing test cases

  Read project test patterns:
    Call: get_file_content for existing test files
    Call: search_in_repository("describe.*{related_feature}")
    → Match test naming and structure patterns
```

## Phase 3: TEST CASE GENERATION

```
FOR EACH acceptance criterion:

  Generate test cases:

  HAPPY PATH (minimum 1 per criterion):
    Name: "Verify {feature} with valid {input}"
    Steps: specific actions with concrete test data
    Expected: clear pass/fail criteria

  NEGATIVE TEST (minimum 1 per criterion):
    Name: "Verify {feature} rejects {invalid_input}"
    Steps: attempt invalid operation
    Expected: appropriate error response

  BOUNDARY TEST (for input validation):
    Name: "Verify {feature} at boundary: {limit}"
    Steps: test at exact limit (5MB exactly, max length, etc.)
    Expected: accepted/rejected based on boundary

  SECURITY TEST (for auth features):
    Name: "Verify {feature} requires authentication"
    Steps: attempt without auth
    Expected: 401/403 response

  EDGE CASE (when applicable):
    Name: "Verify {feature} handles {edge_case}"
    Steps: unusual but valid scenario
    Expected: graceful handling

Each test case includes:
  - name: descriptive test name
  - objective: what is being verified
  - preconditions: required setup state
  - steps: numbered steps with specific data
  - expected_results: clear pass/fail criteria
  - priority: Critical | High | Medium | Low
  - type: Functional | Negative | Boundary | Security | Edge
```

### Special: Bug Test Cases

```
FOR bug issues:
  1. REPRODUCTION test: steps to reproduce the bug
  2. FIX VERIFICATION test: verify the fix works
  3. REGRESSION test: verify related features still work
```

## Phase 4: 🚦 HITL GATE — Developer Reviews

```
## Test Plan for {scope}

### {PROJ-101}: {story_title}

| # | Test Name | Type | Priority | Steps |
|---|-----------|------|----------|-------|
| 1 | Verify avatar upload with valid image | Functional | Critical | 5 |
| 2 | Verify upload rejects files > 5MB | Negative | High | 4 |
| 3 | Verify upload at exactly 5MB | Boundary | Medium | 4 |
| 4 | Verify upload requires auth | Security | High | 3 |

Total: {N} test cases ({functional}, {negative}, {boundary}, {security})

Developer can:
  - Add/remove test cases
  - Modify steps or expected results
  - Change priorities
  - Change test type
  - Request additional edge cases

Multi-round refinement until approved
```

## Phase 5: CREATE IN ZEPHYR

```
FOR EACH approved test case:

  PRIMARY — Zephyr:
    Call: create_zephyr_test(
      project_key: config.jira.project_key,
      summary: test.name,
      description: test.objective,
      test_steps: test.steps,
      expected_results: test.expected_results,
      priority: test.priority,
      labels: config.zephyr.labels
    )

    Call: link_issues(test_key, source_issue_key, config.zephyr.test_link_type)

  FALLBACK — Jira Subtasks (if Zephyr unavailable):
    Call: create_jira_subtask(
      parent_key: source_issue_key,
      summary: "[Test] " + test.name,
      description: formatted test steps and expected results
    )
```

## Phase 6: SUMMARY

```
✓ Created {N} test cases:
  - {TEST-001}: Verify avatar upload with valid image (Functional, Critical)
  - {TEST-002}: Verify upload rejects files > 5MB (Negative, High)
  ...

By type: {N} Functional, {M} Negative, {P} Boundary, {Q} Security, {R} Edge
Linked to: {source_issue_keys}

→ Next: "Generate tests for another story?"
```

## Error Handling

```
No acceptance criteria → warn, generate minimal tests from description
Zephyr unavailable → fall back to Jira subtasks
Test creation fails → show error, offer retry
Duplicate tests found → warn, skip or offer to update existing
Issue not found → ask for correct key
```
