---
name: release-note
description: "Generate and publish release notes to Confluence. Collects changes from Jira issues and GitLab commits, formats using template, and creates a Confluence page."
---

# Skill: Create Release Note

Collect changes from Jira and GitLab, generate formatted release notes, and publish to Confluence.

## Phase 1: DETERMINE VERSION

```
IF developer specifies version:
  → Use that version (e.g., "v1.2.0")

IF not specified:
  Call: get_ticket_history()
  → Find latest release ticket → extract version

  OR: Ask developer: "Which version? (e.g., v1.2.0)"
```

## Phase 2: COLLECT CHANGES

### From Jira

```
Call: search_jira_issues(
  jql: "project = {config.jira.project_key} AND fixVersion = {version}
        AND status = Done ORDER BY issuetype, priority"
)

FOR EACH issue found:
  Call: get_jira_issue_detail(issue_key)
  Extract: key, summary, type, priority, assignee, description
```

### From GitLab

```
Call: list_project_merge_requests(
  state: "merged",
  target_branch: config.gitlab.default_branch
)
→ Filter MRs for this version (by date range or tag comparison)

Extract: MR titles, authors, commit messages
```

## Phase 3: CATEGORIZE CHANGES

```
Group issues by type:

FEATURES (Story, Feature):
  - PROJ-101: Add user avatar upload
  - PROJ-102: Implement password reset

BUG FIXES (Bug):
  - PROJ-201: Fix login timeout issue
  - PROJ-202: Resolve pagination offset

IMPROVEMENTS (Task, Improvement):
  - PROJ-301: Optimize database queries
  - PROJ-302: Refactor auth middleware

BREAKING CHANGES:
  - Any issue labeled "breaking-change"
  - API endpoint changes, schema migrations

SECURITY FIXES:
  - Issues labeled "security"

DEPENDENCY UPDATES:
  - From commit messages or MR titles mentioning dependencies
```

## Phase 4: GENERATE RELEASE NOTE

```
Use template from: .github/skills/release-note/release-template.md

Fill in:
  - version, date, project_name
  - summary (2-3 sentence overview)
  - features (grouped Jira issues)
  - bugfixes
  - improvements
  - breaking_changes (with migration steps)
  - security_fixes (with severity)
  - dependencies
  - known_issues
  - contributors (from MR authors)

Format as Confluence-ready HTML
```

## Phase 5: 🚦 HITL GATE — Developer Reviews

```
Show rendered release note

Developer can:
  - Edit content (reword, add/remove items)
  - Adjust categorization
  - Add migration instructions
  - Add known issues
  - Modify formatting

Multi-round refinement
```

## Phase 6: PUBLISH TO CONFLUENCE

```
Call: create_confluence_page(
  space_key: config.confluence.space_key,
  parent_page_id: config.confluence.release_notes_parent_page_id,
  title: "Release Note — v{version} — {date}",
  content: rendered_release_note_html
)
```

## Phase 7: SUMMARY

```
✓ Release note published: {confluence_page_url}
  - {N} features, {M} bug fixes, {P} improvements
  - {K} breaking changes documented

→ Confluence page: {link}
→ Next: "Start planning for next sprint?"
```

## Error Handling

```
No Jira issues found → warn, generate from GitLab commits only
Confluence unavailable → show formatted release note for manual posting
Page creation fails → show content, guide manual creation
Version not found → ask developer for correct version
```
