# Test Agent — Design Reference

> The Test Agent specializes in translating business requirements into structured, comprehensive Zephyr test cases linked to source Jira issues.

---

## Overview

| Property | Value |
|---|---|
| **File** | `agents/test-agent.md` |
| **Model Hint** | CAPABLE |
| **Used In** | Workflow 11 — Generate Test Plan |
| **Primary Tools** | Zephyr (2 tools), Jira (6 tools), GitLab (2 tools) |

## What It Does

The Test Agent thinks like a senior QA engineer:

1. **Extracts** acceptance criteria from Jira issues (supports multiple formats)
2. **Derives** comprehensive test cases: happy path, negative, boundary, security, edge cases
3. **Reads** existing test patterns in the codebase to match project conventions
4. **Deduplicates** — checks for existing linked tests to avoid redundancy
5. **Creates** Zephyr test issues with full detail (steps, data, preconditions)
6. **Links** every test to its source Jira issue

## Key Knowledge Areas

### Acceptance Criteria Extraction

The agent supports multiple criteria formats:
- **Given/When/Then** (BDD): Each block → 1 test case
- **Bullet lists** ("should", "must", "can"): Each bullet → test + negative test
- **Numbered criteria** (AC1, AC-1): Each → 1+ test cases
- **Implicit** (from description): Derived with LOW confidence warning

### Test Generation Patterns

| Criterion Type | Tests Generated |
|---|---|
| Each acceptance criterion | 1 happy-path + 1 negative (minimum) |
| Input validation | Boundary tests (min, max, empty, special chars) |
| API endpoint | HTTP method, status codes, request/response validation |
| Auth-protected feature | Valid creds, invalid creds, expired, missing, wrong role |
| Data modification | CRUD verification, integrity, cascade effects |
| File handling | Valid/invalid formats, size limits, empty/corrupt files |

### Test Case Structure

Every test case includes:
- **Test Name**: Specific, action-oriented ("Verify JPG upload succeeds")
- **Objective**: What the test proves
- **Preconditions**: What must be true before executing
- **Steps**: Numbered actions with specific data
- **Expected Results**: Per-step expected outcomes
- **Test Data**: Concrete values (never placeholders)
- **Priority**: Critical / High / Medium / Low
- **Type**: Functional / Negative / Boundary / Security / Edge Case / Integration

## MCP Tools

| Tool | Role in This Agent |
|---|---|
| `create_zephyr_test` | Create test cases |
| `update_zephyr_test` | Update existing tests |
| `get_jira_issue_detail` | Fetch acceptance criteria |
| `search_jira_issues` | Find children, existing tests, sprint issues |
| `create_jira_subtask` | Fallback when Zephyr unavailable |
| `link_issues` | Link tests to source issues |
| `get_project_sprints` | Find active sprint |
| `get_file_content` | Read existing test files for patterns |
| `search_in_repository` | Find test file conventions |

## Design Principles

- **Specific over vague**: Every test has concrete steps and data values
- **Comprehensive but not exhaustive**: Cover all criteria without generating 100 tests for a simple story
- **Convention-aware**: Reads existing tests to match project style
- **Deduplicated**: Checks for existing tests before creating new ones
- **Confidence-tagged**: Inferred tests are flagged as low confidence
- **Hierarchical**: Epic → Story → Test Case organization
- **Fallback-ready**: Zephyr → Jira sub-tasks → text export

## Scope Support

| Scope | Behavior |
|---|---|
| **Single Story** | Generate tests for one issue |
| **Epic** | Fetch all child stories, generate per story, organize as suite |
| **Sprint** | Find active sprint, group by epic/feature area |
| **Batch** | Multiple keys, each processed independently |
| **Bug** | Specialized: reproduction + fix verification + regression tests |

## Error Handling

| Error | Behavior |
|---|---|
| No acceptance criteria | Derives from description; warns about low confidence |
| Zephyr unavailable | Falls back to `create_jira_subtask` with test details |
| Duplicate test exists | Shows existing test; asks to skip or regenerate |
| No active sprint | Lists available sprints; asks developer to choose |
| Link type not configured | Warns; creates test without link; suggests config update |
| Too many tests (>50) | Warns; suggests batched creation |
