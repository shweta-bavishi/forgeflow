# Workflow 02 — Plan Epics

> Parses a Confluence requirements page and creates Jira Epics with linked Stories in a single batch operation.

---

## When to Use

- A product or business analyst has published requirements on a Confluence page.
- You need to translate those requirements into a structured Jira backlog (Epics → Stories).
- You want to avoid manually creating dozens of tickets one by one.

## Prerequisites

| Requirement | Details |
|---|---|
| Confluence page | Page must exist and be accessible via `get_confluence_page_full_content` |
| Jira project | Must be accessible; `get_jira_project_info` must return valid metadata |
| Config | `otomate.config.yml` loaded with `jira.project_key` and `confluence.space_key` |

## How to Trigger

```
@otomate plan epics from confluence page 123456
```

Or provide the page title:

```
@otomate create epics from "Q3 Feature Requirements"
```

## What Happens

### Phase 1 — Confluence Content Retrieval

The Confluence Agent fetches the page using `get_confluence_page_full_content` (not the summary endpoint).  The raw HTML is parsed into a structured document, identifying:

- Headings (H1/H2/H3) → Epic candidates
- Bullet lists under headings → Story candidates
- Tables → Acceptance criteria or data mappings
- Callout panels → Constraints, assumptions, non-functional requirements

### Phase 2 — Requirement Structuring

The parsed content is organised into a hierarchy:

```
Epic: User Authentication
  ├─ Story: Implement login with email/password
  ├─ Story: Add OAuth2 social login (Google, GitHub)
  ├─ Story: Build password reset flow
  └─ Story: Add MFA (TOTP) support

Epic: Dashboard Analytics
  ├─ Story: Real-time event counter widget
  ├─ Story: Historical trend chart (7d / 30d / 90d)
  └─ Story: Export analytics as CSV
```

Each story includes:
- **Summary** — concise title
- **Description** — acceptance criteria extracted from the page
- **Story points** — estimated if the config enables it
- **Labels** — derived from page metadata or heading context

### Phase 3 — HITL Review

The full Epic → Story tree is presented for review.  You can:

- Rename, merge, or split stories.
- Adjust story point estimates.
- Remove items that are out of scope.
- Add stories the page didn't explicitly mention.

### Phase 4 — Jira Creation

After approval, the Jira Agent uses `create_epic_with_issues` to create each Epic and its child Stories in a **single API call per epic** (avoiding N+1 requests).

### Phase 5 — Summary

A confirmation table is printed with links to every created ticket.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_confluence_page_full_content` | Fetch raw HTML of requirements page |
| `get_jira_project_info` | Validate project metadata before creation |
| `create_epic_with_issues` | Batch-create Epic + child Stories |

## Tips

- Use **`get_confluence_page_full_content`** (not `get_confluence_page`). The summary endpoint truncates content and drops tables/lists.
- Well-structured Confluence pages (clear headings, consistent bullet formats) produce better results.
- If the page is very long, consider splitting into multiple workflow runs — one per section.
- Review story descriptions carefully; the agent infers acceptance criteria but may miss nuance.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Stories have vague descriptions | Confluence page uses prose instead of structured lists | Rewrite the page with clearer bullet-point requirements, or edit stories in the HITL step |
| `create_epic_with_issues` fails | Jira field configuration mismatch (required custom fields) | Check `get_jira_project_info` output for required fields; update config |
| Duplicate epics created | Workflow run twice on the same page | Delete duplicates manually in Jira; the MCP server has no delete-issue tool |
| Page not found | Wrong page ID or insufficient Confluence permissions | Verify page ID and token scopes |
