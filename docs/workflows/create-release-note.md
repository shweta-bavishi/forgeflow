# Workflow 08 — Create Release Note

> Gathers release data from Jira and GitLab, fills the release note template, and publishes it to Confluence.

---

## When to Use

- A release build has been completed (Workflow 07).
- Stakeholders need a formatted release note on Confluence.
- You want the note auto-generated from actual ticket and commit data (not written from memory).

## Prerequisites

| Requirement | Details |
|---|---|
| Release completed | Jira tickets in "Done" / "Released" status for the version |
| Config loaded | `confluence.space_key`, `confluence.parent_page_id`, Jira and GitLab settings |
| Template | `templates/release-note.md` available |

## How to Trigger

```
@otomate create release note for v2.4.0
```

Or if tickets are tagged with a fix version:

```
@otomate generate release note — fixVersion = "2.4.0"
```

## What Happens

### Phase 1 — Gather Release Data

The agent collects data from multiple sources:

**From Jira** (`search_jira_issues`):
- All tickets with `fixVersion = "2.4.0"`
- Grouped by type: Features, Bug Fixes, Improvements, Tasks
- Ticket key, summary, assignee, status

**From GitLab** (`get_merge_request_details`, `create_release_from_history`):
- Merged MRs for the release
- Commit count and contributors
- Pipeline status for the release build

**From Config**:
- Project name, version
- Release date
- Environment / deployment targets

### Phase 2 — Template Population

The `templates/release-note.md` template is filled with the gathered data:

- **Header**: Project name, version, date
- **Highlights**: Top 3-5 features (most impactful)
- **Features table**: All new feature tickets with descriptions
- **Bug Fixes table**: All bug fix tickets
- **Improvements table**: Enhancements and refactoring
- **Breaking Changes**: Any tickets flagged with breaking-change labels
- **Known Issues**: Open tickets deferred from this release
- **Upgrade Instructions**: If applicable (DB migrations, config changes, etc.)
- **Contributors**: Developers who contributed to this release

### Phase 3 — ⏸️ HITL: Review Release Note

The full release note is presented for review. You can:

- Edit wording, especially the highlights section.
- Add context that the agent couldn't infer.
- Remove sensitive internal details before publishing.
- Adjust formatting.

### Phase 4 — Publish to Confluence

After approval, the Confluence Agent publishes using `create_confluence_page`:

- Creates the page under the configured parent page.
- Applies Confluence HTML formatting (tables, headings, callout panels).
- Adds labels: `release-note`, `v2.4.0`, project name.

### Phase 5 — Notification

A summary is provided with:

- Link to the Confluence page.
- Count of items included (features, bugs, improvements).
- List of contributors mentioned.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `search_jira_issues` | Find all tickets in the release |
| `get_jira_issue` | Fetch detailed ticket info |
| `get_merge_request_details` | Get MR data for the release |
| `create_release_from_history` | Compile commit history |
| `create_confluence_page` | Publish the release note |

## Example Output (Abbreviated)

```
📝 Release Note — MyService v2.4.0

Features (5):
  • PROJ-101  User authentication with OAuth2
  • PROJ-105  Dashboard analytics widgets
  • PROJ-110  CSV export for reports
  ...

Bug Fixes (3):
  • PROJ-112  Fix login redirect loop
  • PROJ-115  Correct timezone in audit logs
  ...

Contributors: @alice, @bob, @charlie

📄 Published to Confluence: https://wiki.company.com/display/PROJ/Release+v2.4.0
```

## Tips

- Ensure all release tickets have the correct `fixVersion` in Jira — this is how the agent finds them.
- Edit the highlights section during HITL review — the agent picks by story points, but you know which features stakeholders care about.
- For the first release note, customise `templates/release-note.md` to match your team's preferred format.
- If your Confluence space uses a specific page hierarchy, set `confluence.parent_page_id` to the "Releases" parent page.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Release note is empty | No tickets have the target `fixVersion` | Set fixVersion on Jira tickets before running |
| Missing contributors | MR authors not mapped to display names | Contributors are extracted from MR data; ensure GitLab profiles have display names |
| Confluence page creation fails | Wrong space key or parent page ID | Verify `confluence.space_key` and `confluence.parent_page_id` in config |
| Formatting looks wrong | Template has markdown but Confluence expects HTML | The agent converts markdown → Confluence storage format automatically |
| Duplicate release notes | Workflow run twice | Delete the duplicate page in Confluence; there is no delete tool in MCP |
