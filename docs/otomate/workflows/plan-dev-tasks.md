# Workflow: Plan Dev Tasks

**Trigger:** "Plan dev tasks for {JIRA-KEY}", "Break down {JIRA-KEY}"

## What It Does

Breaks down a Jira epic into technical implementation tasks with story points, acceptance criteria, file changes, and dependencies.

## How to Use

1. Say: **"Plan dev tasks for PROJ-100"**
2. Otomate fetches the epic and analyzes your codebase
3. Presents task breakdown with points, files, dependencies
4. Review, modify, approve → tasks created in Jira with links
5. Each Jira task includes a **step-by-step implementation plan** (todo list) in its description

## What Goes Into Each Jira Task

Every dev task created by this workflow includes in its description:
- **What to implement** — functional description
- **Files to create/modify** — specific file paths
- **Implementation plan** — step-by-step todo list (the blueprint for coding)
- **Implementation patterns** — which existing code to follow
- **Acceptance criteria** — developer-facing checklist
- **Dependencies and risks**

## HITL Gates

- Review task plan before Jira creation

## MCP Tools Used

`get_jira_issue_detail`, `search_jira_issues`, `get_jira_project_info`, `create_jira_issue`, `link_issues`, `move_issue_to_sprint`, `get_file_content`, `search_in_repository`

## Duration

~10-20 minutes

## Next Steps

"Implement PROJ-201" → start coding any of the created tasks.
