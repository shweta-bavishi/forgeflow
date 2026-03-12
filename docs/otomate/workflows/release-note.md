# Workflow: Create Release Note

**Trigger:** "Create release note for v{version}", "Publish release notes"

## What It Does

Collects changes from Jira issues and GitLab commits, categorizes them (features, bugs, improvements, breaking changes), formats using a template, and publishes to Confluence.

## How to Use

1. Say: **"Create release note for v1.2.0"**
2. Otomate collects all changes for this version from Jira and GitLab
3. Categorizes and formats the release note
4. Review content → approve → published to Confluence

## HITL Gates

1. Review rendered release note before publishing

## MCP Tools Used

`search_jira_issues`, `get_jira_issue_detail`, `list_project_merge_requests`, `create_confluence_page`, `get_confluence_page`

## Duration

~10-15 minutes

## What It Creates

Confluence page titled "Release Note — v{version} — {date}" under the configured parent page, with categorized changes, contributors, and known issues.

## Next Steps

Share the Confluence link with stakeholders.
