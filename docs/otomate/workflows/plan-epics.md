# Workflow: Plan Epics

**Trigger:** "Plan epics from Confluence page {URL/ID}", "Create epics from requirements"

## What It Does

Parses a Confluence requirements page, extracts feature areas as Jira epics with child stories, creates everything in Jira, and links back to Confluence.

## How to Use

1. Say: **"Plan epics from Confluence page 12345678"**
2. Otomate fetches and parses the requirements page
3. Presents proposed epics with stories and story points
4. Review, modify, approve → created in Jira
5. Confluence page updated with Jira links

## HITL Gates

- Review proposed epic plan before Jira creation

## MCP Tools Used

`get_confluence_page_full_content`, `get_page_children`, `get_jira_project_info`, `create_epic_with_issues`, `update_confluence_page`, `move_issue_to_sprint`

## Duration

~15-25 minutes (depends on requirements size)

## Next Steps

"Plan dev tasks for PROJ-100" → break each epic into implementation tasks.
