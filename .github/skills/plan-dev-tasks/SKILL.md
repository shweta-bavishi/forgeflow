---
name: plan-dev-tasks
description: "Plan development tasks for a Jira epic or story. Breaks down into technical implementation tasks with story points, acceptance criteria, file changes, and dependencies."
---

# Skill: Plan Dev Tasks

Break down a Jira epic into technical implementation tasks, each with story points, acceptance criteria, affected files, and dependencies.

## Phase 1: FETCH EPIC/STORY

```
Call: get_jira_issue_detail(jira_key)
Extract:
  - Summary, description, acceptance criteria
  - Child issues (if epic → list of stories)
  - Linked issues (dependencies, blockers)
  - Priority, labels, sprint

IF epic with children:
  → Fetch each child story: get_jira_issue_detail(child_key)
  → Plan tasks for each story

IF single story/task:
  → Plan tasks for this one issue
```

## Phase 2: ANALYZE CODEBASE

```
Read project structure and relevant code:

Call: get_file_content for existing files in affected layers:
  - src/controllers/* (HTTP handlers)
  - src/services/* (business logic)
  - src/entities/* (data models)

Call: search_in_repository for related patterns:
  - Existing implementations of similar features
  - Import patterns for dependencies
  - Test file patterns

Purpose: understand what exists, what needs creating, what needs modifying
```

## Phase 3: BREAK DOWN INTO TASKS

```
FOR EACH story in the epic:

  Map to implementation tasks:

  1. Entity/Model task:
     - Create/modify data models
     - Database migration if needed
     - Story points: 1-3

  2. Repository/Data Access task:
     - CRUD operations for new entities
     - Query methods
     - Story points: 2-3

  3. Service/Business Logic task:
     - Core business rules
     - Validation logic
     - Integration with other services
     - Story points: 3-5

  4. Controller/API task:
     - HTTP endpoints
     - Request/response DTOs
     - Input validation
     - Story points: 2-3

  5. Test task:
     - Unit tests for services
     - Integration tests for controllers
     - Story points: 2-5

  6. Configuration/Setup task (if needed):
     - Module registration
     - Environment variables
     - CI/CD changes
     - Story points: 1-2

  Define dependencies:
    Entity → Repository → Service → Controller → Tests
```

## Phase 4: PRESENT TASK PLAN

```
## Task Plan for {epic_key}: {epic_title}

### Story: {PROJ-101}: {story_title}

| # | Task | Points | Dependencies | Files |
|---|------|--------|-------------|-------|
| 1 | Create User entity | 2 | — | src/entities/user.entity.ts |
| 2 | Create UserRepository | 2 | Task 1 | src/repositories/user.repository.ts |
| 3 | Implement UserService | 5 | Tasks 1,2 | src/services/user.service.ts |
| 4 | Create UserController | 3 | Task 3 | src/controllers/user.controller.ts |
| 5 | Write unit tests | 3 | Tasks 1-4 | tests/user.service.spec.ts |
| 6 | Register in AppModule | 1 | Tasks 1-4 | src/app.module.ts |

Acceptance Criteria Coverage:
  AC1: "User can register" → Tasks 3,4
  AC2: "Email must be unique" → Tasks 2,3
  AC3: "Password hashed" → Task 3

Total: 6 tasks, 16 story points
```

## Phase 5: 🚦 HITL GATE — Developer Reviews

```
Developer can:
  - Add/remove tasks
  - Modify story points
  - Change task scope
  - Adjust dependencies
  - Re-prioritize
  - Split or merge tasks
  - Assign to specific team members

Multi-round refinement until approved
```

## Phase 6: CREATE IN JIRA

```
STEP 1 — Prerequisite:
  Call: get_jira_project_info(config.jira.project_key)

STEP 2 — Create tasks:
  FOR EACH approved task:
    Call: create_jira_issue(
      project_key: config.jira.project_key,
      issue_type: config.jira.task_issue_type,
      summary: task.title,
      description: task.description + acceptance_criteria + affected_files,
      story_points: task.points,
      labels: config.jira.labels
    )

STEP 3 — Link to parent:
  Call: link_issues(task_key, story_key, "is part of")

STEP 4 — Link dependencies:
  Call: link_issues(task_1, task_2, "is blocked by")

STEP 5 — Assign to sprint (if requested):
  Call: move_issue_to_sprint(task_key, sprint_id)
```

## Phase 7: SUMMARY

```
✓ Created {N} tasks for {epic_key}:
  - PROJ-201: Create User entity (2pts)
  - PROJ-202: Create UserRepository (2pts)
  - PROJ-203: Implement UserService (5pts)
  ...

✓ Total: {points} story points
✓ Dependencies linked
✓ Assigned to sprint: {sprint_name}

→ Next: "Implement PROJ-201?"
```

## Error Handling

```
Epic not found → ask for correct key
No acceptance criteria → warn, generate minimal tasks
Jira creation fails → show error, offer retry
Sprint not found → skip sprint assignment, note it
```
