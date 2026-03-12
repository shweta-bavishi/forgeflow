# Workflow 11 — Generate Test Plan

> Automatically generates Zephyr test cases from Jira acceptance criteria. Supports single stories, entire epics, or full sprints. Links every test case back to its source Jira issue.

---

## When to Use

- A story or epic has acceptance criteria and needs structured QA test cases.
- You want to generate test cases for an entire sprint's worth of stories at once.
- Your team uses Zephyr for test management and wants automated test creation.
- A QA engineer needs a starting point for test case design.

## Prerequisites

| Requirement | Details |
|---|---|
| Jira issues | Stories/epics/tasks with acceptance criteria in descriptions |
| Zephyr (recommended) | Zephyr test management configured in Jira |
| Config loaded | `zephyr.test_issue_type`, `zephyr.test_link_type` |
| Fallback | If Zephyr unavailable, creates Jira sub-tasks instead |

## How to Trigger

For a single story:

```
@otomate generate test plan for PROJ-123
```

For an entire epic:

```
@otomate create test cases for epic PROJ-100
```

For the current sprint:

```
@otomate generate test plan for this sprint
```

## What Happens

### Phase 1 — Scope Determination

| Input | Behavior |
|---|---|
| Single Jira key (Story/Task) | Generate tests for that one issue |
| Single Jira key (Epic) | Fetch all child stories, generate tests per story |
| "Current sprint" | Find active sprint, fetch all stories, group by epic |
| Multiple keys | Generate for each, present as grouped plan |

### Phase 2 — Requirements Analysis

For each issue, the Test Agent:

1. **Extracts acceptance criteria** — supports Given/When/Then, bullet lists, numbered criteria
2. **Identifies functionality type** — API endpoint, UI feature, data processing, etc.
3. **Checks for existing tests** — avoids creating duplicates
4. **Reads project test patterns** — matches naming conventions from existing test files

### Phase 3 — Test Case Generation

For each acceptance criterion, the agent generates:

| Test Type | What It Tests | Example |
|---|---|---|
| **Happy Path** | Criterion works as described | "Verify JPG upload returns URL" |
| **Negative** | Violation is handled correctly | "Verify GIF upload is rejected" |
| **Boundary** | Edge values and limits | "Verify file exactly 5MB accepted" |
| **Security** | Auth and authorization | "Verify unauthenticated upload returns 401" |
| **Edge Case** | Unusual but valid inputs | "Verify empty file upload is rejected" |

Each test case includes:
- Objective, preconditions, steps, expected results
- Specific test data (not placeholders)
- Priority (Critical / High / Medium / Low)
- Source criterion reference

### Phase 4 — HITL Review

You review the complete test plan and can:
- Add missing test cases
- Remove irrelevant tests
- Change priority levels
- Modify test steps or data
- Multiple rounds of refinement supported

### Phase 5 — Zephyr Creation

After approval, test cases are created in Zephyr (or as Jira sub-tasks as fallback) and linked to their source issues.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_jira_issue_detail` | Fetch acceptance criteria |
| `search_jira_issues` | Find epic children, existing tests, sprint stories |
| `get_project_sprints` | Find active sprint |
| `create_zephyr_test` | Create test cases in Zephyr |
| `update_zephyr_test` | Update test cases |
| `link_issues` | Link tests to source issues |
| `create_jira_subtask` | Fallback when Zephyr unavailable |
| `get_file_content` | Read existing tests for convention matching |
| `search_in_repository` | Find test file patterns |

## Example Output

```
Test Plan: PROJ-123 — User Avatar Upload

Source Acceptance Criteria:
  1. POST /api/users/:id/avatar accepts image upload
  2. Validates file type (jpg, png) and size (<5MB)
  3. Returns avatar URL in response

Generated: 9 test cases
  Functional: 3 | Negative: 2 | Boundary: 2 | Security: 2

| # | Test Name                          | Type     | Priority |
|---|------------------------------------|----------|----------|
| 1 | Verify JPG avatar upload succeeds  | Func     | Critical |
| 2 | Verify PNG avatar upload succeeds  | Func     | Critical |
| 3 | Reject GIF file upload             | Negative | High     |
| 4 | Reject file > 5MB                  | Boundary | High     |
| 5 | Accept file exactly 5MB            | Boundary | Medium   |
| 6 | Reject empty file upload           | Edge     | Medium   |
| 7 | Response contains valid avatar URL | Func     | Critical |
| 8 | Reject upload without auth         | Security | High     |
| 9 | Reject upload for other user       | Security | High     |

Created in Zephyr: TEST-001 through TEST-009
All linked to PROJ-123 via "Tests" link.
```

## Tips

- **Well-written acceptance criteria produce better tests.** Given/When/Then format works best.
- **For epics**, the workflow generates tests per child story — organized as a test suite hierarchy.
- **Inferred tests** (when criteria aren't explicit) are flagged with a confidence warning. Review them carefully.
- **Existing tests** are detected via Jira links — duplicates are skipped by default.
- **Bug tickets** get specialized tests: reproduction, fix verification, and regression tests.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "No acceptance criteria found" | Jira description lacks structured criteria | Add Given/When/Then or bullet-point criteria to the Jira issue |
| Tests are too generic | Description is vague | Enrich the story with specific requirements |
| Zephyr creation fails | Zephyr not configured or test issue type missing | Configure `zephyr.test_issue_type` in config; falls back to sub-tasks |
| Link type not found | "Tests" link type doesn't exist in Jira | Configure `zephyr.test_link_type` to match your Jira setup |
| Too many tests generated | Story has many criteria or is too broad | Split the story or review and remove redundant tests at HITL step |
| Duplicate tests created | Ran workflow twice | Check for existing linked tests; workflow detects and skips by default |
