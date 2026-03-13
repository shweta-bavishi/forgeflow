---
name: implement-dev-task
description: "Implement a Jira development task. Fetches task details, analyzes project code, creates implementation plan, generates production-ready code with tests, commits to branch, and opens merge request."
---

# Skill: Implement Dev Task

Fetch a Jira task, analyze code context, create an implementation plan, generate production-ready code, and open an MR.

## Phase 1: UNDERSTAND THE TASK

```
Call: get_jira_issue_detail(jira_key)
Extract:
  - Title, description
  - Acceptance criteria (as list)
  - Parent epic (context)
  - Linked issues (dependencies)
  - Priority, labels, comments

Load project context from otomate.config.yml:
  - Architecture layers and patterns
  - Coding standards and naming conventions
  - Technology stack details
```

## Phase 2: ANALYZE RELEVANT CODE

```
Read existing implementations in affected layers:

Call: get_file_content for similar files:
  - Existing controllers in src/controllers/
  - Existing services in src/services/
  - Existing entities in src/entities/
  - Test examples in tests/ or src/**/*.spec.ts

Call: search_in_repository for:
  - Related features and patterns
  - Import patterns to follow
  - Existing type definitions

Purpose: generate code that matches project style exactly
```

## Phase 3: RE-ANALYZE & CREATE IMPLEMENTATION PLAN

```
STEP 1 — Re-analyze codebase (even if Jira has a plan):
  The codebase may have changed since planning. Always verify:
  - Read current files in affected directories
  - Check for new patterns or conventions
  - Identify conflicts with recently merged code
  - Compare Jira plan (if exists) against actual codebase state

STEP 2 — Generate detailed implementation plan as TODO LIST:

## Implementation Plan for {JIRA-KEY}: {title}

### Acceptance Criteria
1. {criterion 1}
2. {criterion 2}

### Implementation Todo List
- [ ] 1. {Specific step — e.g., "Create UserEntity with TypeORM decorators"}
       Files: src/entities/{name}.entity.ts (CREATE)
       Pattern: follows {existing_entity} pattern
- [ ] 2. {Specific step — e.g., "Create UserRepository with CRUD methods"}
       Files: src/repositories/{name}.repository.ts (CREATE)
- [ ] 3. {Specific step — e.g., "Implement UserService with validation logic"}
       Files: src/services/{name}.service.ts (CREATE)
- [ ] 4. {Specific step — e.g., "Create controller with REST endpoints"}
       Files: src/controllers/{name}.controller.ts (CREATE)
- [ ] 5. {Specific step — e.g., "Create DTOs with class-validator decorators"}
       Files: src/dto/{name}.dto.ts (CREATE)
- [ ] 6. {Specific step — e.g., "Register providers in AppModule"}
       Files: src/app.module.ts (MODIFY)
- [ ] 7. {Specific step — e.g., "Write unit tests for service"}
       Files: tests/{name}.service.spec.ts (CREATE)

Each step specifies: what to do, which files, which pattern to follow.

### Implementation Strategy
{approach for core logic}

### Test Strategy
AC1 → test: 'should {behavior}'
AC2 → test: 'should {behavior}'

### Risks
{potential issues and mitigations}
```

## Phase 4: 🚦 HITL GATE — Developer Approves Implementation Plan

```
MANDATORY: Plan must be approved BEFORE any code is written.

Developer can:
  - Adjust scope ("skip compression for now")
  - Request clarification ("use S3, not local storage")
  - Point to reference code ("check document.service.ts")
  - Add requirements ("add watermark to image")
  - Add/remove/reorder steps in the todo list
  - Approve: "Looks good, let's build it"

Multi-round until developer approves the todo list.
The approved list becomes the implementation contract.
```

## Phase 5: IMPLEMENT CODE

```
FOR each file in plan:

  1. Read existing similar file:
     Call: get_file_content(reference_file_path)

  2. Generate file following patterns:
     - Correct naming (file, class, function)
     - JSDoc comments on public methods
     - Full type definitions
     - Project import style
     - Comprehensive error handling
     - Use scaffold templates (.hbs) when available:
       scaffolds/controller.hbs, scaffolds/service.hbs, etc.

  3. Present complete file (no stubs, no TODOs in core logic)
     Show: full code, key decisions, pattern references

GENERATE TESTS:
  For each acceptance criterion:
    - Independent test with AAA pattern
    - Descriptive name: 'should reject files larger than 5MB'
    - Mock external dependencies
    - Cover: happy path + error cases + edge cases
```

## Phase 6: 🚦 HITL GATE — Review Code Changes

```
Developer reviews each generated file:

  - Code quality feedback → agent updates code
  - Pattern mismatch → agent shows reference, adjusts
  - Missing features → agent adds implementation
  - Test gaps → agent adds test cases

Multi-round iteration until developer says "Looks good"
```

## Phase 7: UPDATE JIRA STATUS

```
Call: update_jira_issue(
  key: jira_key,
  transition: config.jira.statuses.in_progress
)

Add comment: "Branch: feature/{KEY}-{slug}\nImplementation started via Otomate"
```

## Phase 8: 🚦 HITL GATE — Approve Push & MR

```
Show summary:

  Files Created (N):
    + src/controllers/{name}.controller.ts (45 lines)
    + src/services/{name}.service.ts (78 lines)
    + tests/{name}.service.spec.ts (145 lines)

  Files Modified (M):
    ~ src/app.module.ts (3 lines added)

  Total: +303 lines, -5 lines

  MR Details:
    Branch: feature/{KEY}-{slug} → develop
    Title: {KEY}: {title}

  Should I push and open MR?
```

## Phase 9: COMMIT, PUSH & OPEN MR

```
Call: commit_file_and_create_mr(
  project_id: config.gitlab.project_id,
  files: [all generated/modified files],
  commit_message: config.gitlab.commit_message.pattern filled in,
  branch_name: "feature/{KEY}-{slug}",
  target_branch: config.gitlab.default_branch,
  mr_title: "{KEY}: {title}",
  mr_description: [from templates/mr-description.md template]
)

MR description includes:
  - Summary of changes
  - Linked Jira issue
  - Acceptance criteria checklist
  - Files changed list
  - Test plan
```

## Phase 10: UPDATE JIRA

```
Call: update_jira_issue(
  key: jira_key,
  transition: config.jira.statuses.in_review
)

Add comment: "MR: !{mr_id} — Ready for code review\nLink: {mr_url}"
```

## Error Handling

```
Task fetch fails → ask for correct key
Branch exists → ask: "Use existing or create new?"
Code doesn't match expectations → iterate in Phase 6
Push fails → show error, offer retry or manual push
MR creation fails → code still valid, guide manual MR creation
```
