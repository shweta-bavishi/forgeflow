# Workflow: Generate Test Plan

**Trigger:** "Generate test plan for {KEY}", "Create test cases", "Generate Zephyr tests"

## What It Does

Extracts acceptance criteria from Jira issues, generates structured test cases (functional, negative, boundary, security, edge), and creates them in Zephyr (with Jira subtask fallback). Supports single stories, epics, or sprints.

## How to Use

1. Say: **"Generate test plan for PROJ-123"**
2. Otomate fetches issue details and extracts acceptance criteria
3. Generates test cases per criterion (happy path + negative + boundary)
4. Review test plan → approve → tests created in Zephyr
5. Each test linked to its source Jira issue

## Scope Options

| Scope | What It Processes |
|-------|-------------------|
| Single key | One story/task |
| Epic key | All stories under the epic |
| "Current sprint" | All stories in active sprint |
| Multiple keys | Each specified key |

## Test Types Generated

- **Functional** — Happy path verification
- **Negative** — Invalid input / error cases
- **Boundary** — At limits (exactly 5MB, max length)
- **Security** — Authentication / authorization
- **Edge Case** — Unusual but valid scenarios

## HITL Gates

1. Review test plan before creation (add/remove/modify tests)

## MCP Tools Used

`get_jira_issue_detail`, `search_jira_issues`, `get_project_sprints`, `create_zephyr_test`, `link_issues`, `create_jira_subtask`, `get_file_content`, `search_in_repository`

## Fallback

If Zephyr is not available, test cases are created as Jira subtasks under the source issue.

## Duration

~15-25 minutes (depends on number of criteria)
