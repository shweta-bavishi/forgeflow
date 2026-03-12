# Workflow: Plan Dev Tasks

**Trigger:** "Plan dev tasks for {JIRA-KEY}", "Break down {JIRA-KEY}"

## What It Does

Breaks down a Jira epic into technical implementation tasks with story points, acceptance criteria, file changes, and dependencies.

## How to Use

1. Say: **"Plan dev tasks for PROJ-100"**
2. Otomate fetches the epic and analyzes your codebase
3. Presents task breakdown with points, files, dependencies
4. Review, modify, approve → tasks created in Jira with links

## HITL Gates

- Review task plan before Jira creation

## MCP Tools Used

`get_jira_issue_detail`, `search_jira_issues`, `get_jira_project_info`, `create_jira_issue`, `link_issues`, `move_issue_to_sprint`, `get_file_content`, `search_in_repository`

## Duration

~10-20 minutes

## Next Steps

"Implement PROJ-201" → start coding any of the created tasks.
