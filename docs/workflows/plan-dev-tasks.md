# Workflow 03 — Plan Dev Tasks

> Breaks down a Jira Story into architecture-aligned development sub-tasks with detailed technical descriptions.

---

## When to Use

- A Story is ready for development and needs to be decomposed into actionable sub-tasks.
- You want sub-tasks that map to specific architecture layers (controller, service, repository, entity, test).
- You want each sub-task to include enough context for a developer (or the Code Agent) to implement without guesswork.

## Prerequisites

| Requirement | Details |
|---|---|
| Jira Story | Must exist and be accessible via `get_jira_issue` |
| Config loaded | `forgeflow.config.yml` with `architecture.layers` and `jira.project_key` |
| Architecture defined | Config must specify the project's layer structure |

## How to Trigger

```
@forgeflow plan tasks for PROJ-101
```

Or for multiple stories:

```
@forgeflow plan dev tasks for PROJ-101, PROJ-102, PROJ-103
```

## What Happens

### Phase 1 — Story Analysis

The Jira Agent fetches the story details (`get_jira_issue`), extracting:

- Summary and description
- Acceptance criteria
- Linked epics or parent issues
- Existing sub-tasks (to avoid duplication)

### Phase 2 — Architecture Mapping

The Code Agent maps the story's requirements to architecture layers defined in the config:

```yaml
# From forgeflow.config.yml
architecture:
  layers:
    - controller    # REST / GraphQL endpoints
    - service       # Business logic
    - repository    # Data access
    - entity        # Domain models / DB schemas
    - test          # Unit + integration tests
```

Each layer that needs changes gets a sub-task.

### Phase 3 — Sub-Task Generation

For each sub-task, the agent generates:

- **Summary**: `[Layer] Brief action description` (e.g. `[Service] Implement user registration logic`)
- **Description**: Technical specification including:
  - Files to create or modify
  - Method signatures / API contracts
  - Dependencies and imports
  - Edge cases to handle
  - Relevant patterns from existing codebase
- **Story points**: Estimated relative to layer complexity
- **Labels**: Layer name + any relevant tech tags

### Phase 4 — HITL Review

The sub-task plan is presented as a table:

```
Story: PROJ-101 — User Registration

| # | Layer      | Sub-Task                                 | Points |
|---|------------|------------------------------------------|--------|
| 1 | Entity     | Create User entity with validation       |    2   |
| 2 | Repository | Add UserRepository with CRUD + findByEmail |  2   |
| 3 | Service    | Implement registration with duplicate check |  3   |
| 4 | Controller | POST /api/users endpoint with DTO validation |  3   |
| 5 | Test       | Unit tests for service + integration for API |  3   |

Total: 13 points
```

You can adjust, merge, reorder, or remove sub-tasks before approval.

### Phase 5 — Jira Creation

After approval, the Jira Agent creates sub-tasks under the parent story using `create_jira_subtask`.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_jira_issue` | Fetch story details and existing sub-tasks |
| `get_jira_project_info` | Validate issue types and field configurations |
| `create_jira_subtask` | Create each sub-task under the parent story |

## Tips

- Define `architecture.layers` in your config — this is what drives the sub-task decomposition.
- For stories that only affect one layer (e.g. a pure UI change), the agent will skip irrelevant layers.
- If a story is too large (the agent generates 8+ sub-tasks), consider splitting the story first.
- Sub-task descriptions are intentionally verbose — they serve as implementation specs for Workflow 04.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Sub-tasks don't match project structure | `architecture.layers` not configured or wrong | Update the config to reflect actual project layout |
| Too many sub-tasks generated | Story is too broad | Split the story into smaller stories first |
| `create_jira_subtask` fails | Sub-task issue type not enabled in Jira project | Enable "Sub-task" issue type in Jira project settings |
| Missing technical detail in descriptions | Story description is vague | Enrich the story's acceptance criteria before running this workflow |
