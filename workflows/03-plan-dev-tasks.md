# Workflow 03: Plan Dev Tasks

**Goal**: Break a Jira epic into detailed development tasks with comprehensive technical descriptions. Each task specifies files to create/modify and implementation patterns.

**Trigger**: "Plan dev tasks for {JIRA-KEY}", "Break down {EPIC-KEY}"

**Agents**: Orchestrator → Jira Agent, Code Agent, Project Context Agent

**Time**: ~20 minutes (analysis + approval + creation)

## Phase 1: GATHER CONTEXT

### Fetch Epic Details

```
Call: get_jira_issue_detail(epic_key)
Extract:
  - Epic description
  - Acceptance criteria
  - Linked child issues (if any)
  - Epic priority and labels
```

### Load Project Context

From config:
- Architecture layers
- Coding standards
- Technology stack
- Naming conventions

### Analyze Existing Code

Code Agent reads:
- Existing controller implementations
- Service patterns
- Repository implementations
- Test examples

**Purpose**: Understand patterns to follow when planning tasks

## Phase 2: ANALYZE & BREAK DOWN

This is where Code Agent excels. Analyze the epic technically:

### Understand Requirements

```
Example epic: "User Avatar Upload"
Description: "Enable users to upload and manage custom avatar images"

Acceptance Criteria:
  - Users can upload image files
  - System validates file size < 5MB
  - Image is automatically compressed to 300x300px
  - Avatar URL is returned and displayed on profile
```

### Map to Architecture Layers

```
For NestJS (clean architecture):

CONTROLLER LAYER:
  - POST /users/:id/avatar (upload endpoint)
  - DELETE /users/:id/avatar (delete endpoint)
  - GET /users/:id/avatar (fetch avatar)

SERVICE LAYER:
  - avatarService.uploadAvatar() - validate, compress, store
  - avatarService.deleteAvatar() - delete files
  - avatarService.getAvatarUrl() - fetch URL

REPOSITORY LAYER:
  - avatarRepository.save() - persist metadata
  - avatarRepository.delete() - delete records
  - avatarRepository.findById() - fetch records

ENTITY LAYER:
  - Avatar entity - avatar metadata model

DATA MODEL:
  - avatar table: id, userId, fileName, fileSize, uploadedAt
```

### Identify Task Decomposition

```
TASK 1: Set up Avatar module & service
  Files:
    - src/modules/avatar/avatar.module.ts (NEW)
    - src/services/avatar.service.ts (NEW)
    - src/repositories/avatar.repository.ts (NEW)
    - src/entities/avatar.entity.ts (NEW)
  Depends on: Nothing
  Effort: Small

TASK 2: Implement Avatar upload endpoint
  Files:
    - src/controllers/avatar.controller.ts (NEW)
    - src/dto/upload-avatar.dto.ts (NEW)
    - src/filters/avatar-error.filter.ts (NEW - custom exception handler)
  Depends on: TASK 1 (needs service)
  Effort: Medium

TASK 3: Add image compression logic
  Files:
    - src/services/avatar.service.ts (MODIFY - add compression)
    - src/utils/image.util.ts (NEW - compression helpers)
  Depends on: TASK 1 (needs service)
  Effort: Medium
  Notes: May require additional npm packages (sharp, etc.)

TASK 4: Implement avatar persistence
  Files:
    - src/repositories/avatar.repository.ts (MODIFY - add DB logic)
    - db/migrations/{date}_create_avatar_table.sql (NEW)
  Depends on: TASK 1
  Effort: Small

TASK 5: Add validation & security
  Files:
    - src/validators/avatar-upload.validator.ts (NEW)
    - src/guards/avatar-file.guard.ts (NEW)
    - src/services/avatar.service.ts (MODIFY - add validation)
  Depends on: TASK 1 (needs service)
  Effort: Small

TASK 6: Write unit tests
  Files:
    - tests/avatar.service.spec.ts (NEW)
    - tests/avatar.controller.spec.ts (NEW)
    - tests/avatar.repository.spec.ts (NEW)
  Depends on: All other tasks
  Effort: Medium

TASK 7: Write integration tests
  Files:
    - tests/avatar.e2e-spec.ts (NEW)
  Depends on: TASK 6
  Effort: Medium
```

### Create Detailed Task Descriptions

For each task, include:

```
## TASK: {Task Name}

### What to Implement
{Specific functionality}

### Files to Create/Modify
- src/controllers/avatar.controller.ts (CREATE)
- src/services/avatar.service.ts (MODIFY)
- ...

### Architectural Layer
Controller, Service, Repository, Entity

### Implementation Patterns
Reference existing code: "Follow pattern from src/controllers/user.controller.ts"

### Acceptance Criteria (Developer Perspective)
- [ ] Endpoint accepts multipart/form-data with file
- [ ] Validates file size < 5MB
- [ ] Returns 400 if file too large
- [ ] Successfully compresses and stores file
- [ ] Returns avatar URL in response
- [ ] Tests cover happy path and error cases

### Dependencies
- Blocks: {Other task keys}
- Blocked by: {Other task keys}
- Requires: npm packages (sharp, multer, etc.)

### Estimated Story Points
5 points (based on complexity)

### Risk & Mitigation
Risk: Image compression library compatibility
Mitigation: Add sharp as dependency, test on target Node version
```

## Phase 3: PRESENT BREAKDOWN

Show detailed table:

```
| # | Task Name | Layer | Points | Dependencies |
|----|-----------|-------|--------|--------------|
| 1  | Setup Avatar module | Service | 3 | None |
| 2  | Implement upload endpoint | Controller | 5 | Task 1 |
| 3  | Add image compression | Service | 5 | Task 1 |
| 4  | Avatar persistence | Repository | 3 | Task 1 |
| 5  | Validation & security | Service | 3 | Task 1 |
| 6  | Unit tests | Testing | 5 | All |
| 7  | Integration tests | Testing | 5 | Task 6 |

TOTAL: 29 points

IMPLEMENTATION ORDER:
  1. Task 1 (foundation)
  2. Tasks 2, 3, 4, 5 in parallel (after Task 1)
  3. Task 6 (after tasks 2-5)
  4. Task 7 (after Task 6)

SUGGESTED SPRINT DISTRIBUTION:
  Sprint 1: Task 1, 2, 3 (13 points)
  Sprint 2: Task 4, 5, 6 (11 points)
  Sprint 3: Task 7 (5 points)
```

## Phase 4: 🚦 HITL GATE — Developer Approves Tasks

Developer reviews and can:

```
1. MODIFY task scope
   "Task 2 is too big, split into upload and validation"

2. ADJUST story points
   "This should be 8 points, not 5"

3. ADD dependencies
   "Task 3 must happen before Task 2"

4. ADD/REMOVE tasks
   "We should also add Task 8: API documentation"

5. CLARIFY requirements
   "What about error handling for corrupted files?"
   Agent: [Explains approach, can update task description]

6. CHANGE order
   "Do tests earlier, not last"

Multi-round refinement until developer is satisfied
```

## Phase 5: CREATE JIRA TASKS

For each approved task:

### Prerequisites

```
Call: get_jira_project_info(project_key)
  - Verify issue types and custom fields
```

### Create Issues

```
For each task:
  Call: create_jira_issue(
    project_key: from config,
    issue_type: "Task" (or "Story" from config),
    summary: "{Epic-KEY-X}: {Task name}",
    description: [Full task description from Phase 2],
    story_points: calculated from task description,
    priority: from epic priority
  )

Link to epic:
  Call: link_issues(epic_key, new_issue_key, "relates to")

Link dependencies:
  If Task A blocks Task B:
    Call: link_issues(task_a_key, task_b_key, "Blocks")
```

### Report Created Tasks

```
✓ Created {N} tasks:
  PROJ-101: Avatar module setup (3 points)
  PROJ-102: Upload endpoint (5 points)
  PROJ-103: Image compression (5 points)
  ...

Linked to epic: PROJ-100
Dependencies configured: {N} links created

NEXT STEPS:
  1. Review tasks in Jira
  2. Assign tasks to developers
  3. Start implementation (04-implement-dev-task workflow)
```

## Error Handling

### If epic not found

```
→ Ask: "What is the correct epic key? (e.g., PROJ-100)"
```

### If Jira creation fails

```
→ Show: Which tasks succeeded, which failed
→ Offer: Retry, create manually, or continue
```

### If code analysis hits unexpected patterns

```
→ Ask: "I found this pattern in your code. Should I follow it?"
→ Or: "Should I create new patterns, or follow existing code?"
```

## Success Criteria

✓ Epic is broken into logically independent tasks
✓ Each task has detailed technical description
✓ Dependencies are clearly identified
✓ Files to create/modify are specified
✓ Story points are realistic
✓ Developer approves before Jira creation
✓ Jira tasks are linked to epic and to each other

---

**Duration**: 20 minutes

**What It Creates**: Jira tasks linked to epic

**Next Workflow**: 04-implement-dev-task (implement individual tasks)

**Related**: Code Agent, Jira Agent, Project Context Agent
