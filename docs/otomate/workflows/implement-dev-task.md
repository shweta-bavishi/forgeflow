# Workflow: Implement Dev Task

**Trigger:** "Implement {JIRA-KEY}", "Start working on {JIRA-KEY}", "Code {JIRA-KEY}"

## What It Does

Fetches a Jira task, analyzes project code, creates an implementation plan, generates production-ready code with tests, commits to a feature branch, and opens a merge request.

## How to Use

1. Say: **"Implement PROJ-123"**
2. Otomate fetches the task and **re-analyzes your current codebase** (even if the Jira task already has an implementation plan — the codebase may have changed)
3. Presents a **detailed implementation plan as a todo list** — each step specifies the action, file, and pattern to follow
4. Review plan → modify if needed → approve → **no code is generated until plan is approved**
5. Code is generated following the approved todo list step-by-step
6. Review code → approve → MR created
7. Jira updated to "In Review"

## HITL Gates

1. **Approve implementation plan (mandatory)** — detailed todo list must be approved before ANY code is generated
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
