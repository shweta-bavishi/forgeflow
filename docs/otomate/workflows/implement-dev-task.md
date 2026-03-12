# Workflow: Implement Dev Task

**Trigger:** "Implement {JIRA-KEY}", "Start working on {JIRA-KEY}", "Code {JIRA-KEY}"

## What It Does

Fetches a Jira task, analyzes project code, creates an implementation plan, generates production-ready code with tests, commits to a feature branch, and opens a merge request.

## How to Use

1. Say: **"Implement PROJ-123"**
2. Otomate fetches the task and analyzes your codebase
3. Presents file-by-file implementation plan
4. Review plan → approve → code generated
5. Review code → approve → MR created
6. Jira updated to "In Review"

## HITL Gates

1. Approve implementation plan
2. Review generated code (multi-round)
3. Approve push and MR creation

## MCP Tools Used

`get_jira_issue_detail`, `get_file_content`, `search_in_repository`, `commit_file_and_create_mr`, `update_jira_issue`

## Duration

~30-45 minutes (varies by task complexity)

## What It Creates

- Complete source files (controllers, services, entities, DTOs)
- Unit test files
- Feature branch
- Merge request with description template
- Jira status updates

## Next Steps

- Get MR reviewed and approved
- "Fix pipeline" if build fails
- "Fix sonar issues" if quality gate fails
- "Create release" when ready
