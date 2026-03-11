# Workflow 04 — Implement Dev Task

> The flagship workflow. Takes a Jira sub-task, plans the implementation, writes production-quality code, and submits a merge request — all with approval gates at critical points.

---

## When to Use

- A Jira sub-task (or story) is ready for implementation.
- You want the Code Agent to analyse the codebase, write code, and raise an MR.
- You want to review and approve the plan and the final changes before they are pushed.

## Prerequisites

| Requirement | Details |
|---|---|
| Jira ticket | Sub-task or story accessible via `get_jira_issue` |
| Config loaded | Full `forgeflow.config.yml` with coding standards, GitLab, and Jira settings |
| Repository | Codebase accessible via GitLab MCP tools |

## How to Trigger

```
@forgeflow implement PROJ-101
```

Or with additional context:

```
@forgeflow implement PROJ-101 — focus on the service layer, skip controller for now
```

## What Happens — 10 Phases

### Phase 1 — Understand

- Fetches the Jira ticket (`get_jira_issue`): summary, description, acceptance criteria, parent story context.
- Reads linked tickets for broader context.

### Phase 2 — Analyse Codebase

- Scans the repository to find relevant existing code:
  - Similar modules / services (pattern reference)
  - Shared utilities, base classes, constants
  - Existing tests (to match style)
- Uses `get_gitlab_file_content` and `list_project_directory` to build a mental model of the codebase.

### Phase 3 — Plan Implementation

- Produces a detailed plan:
  - Files to create and modify
  - Method signatures and type definitions
  - Dependencies to import
  - Test cases to write
  - Edge cases and error handling strategy

### Phase 4 — ⏸️ HITL: Approve Plan

> **Approval gate.** The plan is presented to you. You must approve, request changes, or reject.

This is your chance to catch architectural mistakes *before* any code is written.

### Phase 5 — Branch & Implement

- Generates production-quality code following project conventions from the config:
  - Naming conventions, file structure, import ordering
  - Error handling patterns, logging standards
  - JSDoc / docstring comments
  - No `TODO` or placeholder code
- Uses scaffold templates (Handlebars) when creating new files matching configured patterns.

### Phase 6 — Self-Review

The Code Agent reviews its own output against:

- Acceptance criteria from the Jira ticket
- Coding standards from the config
- TypeScript strict-mode compliance (if applicable)
- Test coverage completeness

Issues found → auto-fix loop (max 2 iterations).

### Phase 7 — Update Jira (In Progress → In Review)

- Transitions the Jira ticket to "In Review" (or equivalent status).
- Adds a comment summarising what was implemented.

### Phase 8 — ⏸️ HITL: Approve Push

> **Approval gate.** The generated code is presented for review. You must approve before it is pushed.

You see:
- Full diff of all files
- Summary of changes
- Any self-review findings that were fixed

### Phase 9 — Commit & MR

- Commits all changes via `commit_file_and_create_mr`:
  - Creates the branch implicitly
  - Populates the MR description using `templates/mr-description.md`
  - Sets reviewers if configured in the config
- A single commit per sub-task (clean history).

### Phase 10 — Final Jira Update

- Adds the MR link to the Jira ticket.
- Adds a comment: "MR raised: <link>".

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_jira_issue` | Fetch ticket details |
| `get_gitlab_file_content` | Read existing source files |
| `list_project_directory` | Browse repo structure |
| `commit_file_and_create_mr` | Commit code + create MR |
| `update_jira_issue` | Transition ticket status |
| `add_jira_comment` | Add implementation summary + MR link |

## HITL Gates Summary

| Gate | Phase | What You Review | Risk if Skipped |
|---|---|---|---|
| Approve Plan | 4 | Implementation approach, file list, architecture decisions | Wrong approach → wasted code |
| Approve Push | 8 | Generated code diff, test coverage, quality | Bad code pushed to remote |

## Tips

- Provide clear acceptance criteria in the Jira ticket — the more specific, the better the generated code.
- If the Code Agent's plan looks wrong at Phase 4, reject and provide guidance. It is far cheaper to fix the plan than the code.
- For large implementations, break the story into sub-tasks first (Workflow 03) and implement each separately.
- The Code Agent respects `coding_standards` from the config — make sure naming conventions, error handling patterns, and import ordering are defined.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Code doesn't follow project patterns | Config `coding_standards` not set or incomplete | Add naming/import/error patterns to config |
| MR description is generic | Template not customised | Edit `templates/mr-description.md` |
| Jira transition fails | Workflow status names don't match Jira configuration | Check `jira.statuses` mapping in config |
| Large diff, hard to review | Implementing too much in one task | Split into smaller sub-tasks (Workflow 03) |
| `commit_file_and_create_mr` fails | Branch naming conflict or permission issue | Check GitLab token scopes (write_repository) |
