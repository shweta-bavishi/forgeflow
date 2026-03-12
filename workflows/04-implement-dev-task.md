# Workflow 04: Implement Dev Task

**Goal**: Fetch a Jira task, analyze project context, create implementation plan, write complete code, get review approval, commit, and open MR.

**Trigger**: "Implement {JIRA-KEY}", "Start working on {JIRA-KEY}", "Code {JIRA-KEY}"

**Agents**: Orchestrator → Jira Agent, GitLab Agent, Code Agent, Project Context Agent

**Time**: ~45 minutes (analysis + code generation + review + push)

## Phase 1: UNDERSTAND THE TASK

### Fetch Task Details

```
Call: get_jira_issue_detail(jira_key)
Extract:
  - Title, description
  - Acceptance criteria (as list)
  - Parent epic (context)
  - Linked issues (dependencies)
  - Priority, labels
  - Any comments or notes
```

### Load Project Context

From config + Code Agent analysis:
- Architecture layers and patterns
- Coding standards
- Technology stack
- Existing code patterns

### Analyze Relevant Code

Code Agent reads:
- Existing implementations in affected layers
- Similar features for reference
- Test examples
- Configuration patterns

**Purpose**: Generate code that matches project style and patterns

## Phase 2: CREATE IMPLEMENTATION PLAN

Code Agent produces detailed plan:

```
## Implementation Plan for PROJ-123: Avatar Upload Endpoint

### What We're Building
Enable users to upload custom avatar images with validation and compression.

### Acceptance Criteria (from Jira)
1. Users can upload image files via POST /users/:id/avatar
2. System validates file size < 5MB
3. Image automatically compressed to 300x300px
4. Avatar URL returned in response
5. Errors handled gracefully with clear messages

### Files to Create

#### src/controllers/avatar.controller.ts
Purpose: HTTP endpoint for avatar upload
Responsibility:
  - Route handler for POST /users/:id/avatar
  - Request validation with decorators
  - Call AvatarService
  - Return formatted response
Pattern: Follow UserController pattern (see src/controllers/user.controller.ts)
Import requirements: @nestjs/common, AvatarService

#### src/services/avatar.service.ts
Purpose: Business logic for avatar operations
Responsibility:
  - Validate file (size, type)
  - Compress image using sharp library
  - Store file to disk/cloud
  - Generate avatar URL
  - Handle errors
Pattern: Follow UserService pattern with dependency injection
Import requirements: @nestjs/common, AvatarRepository, image utilities

#### src/dto/upload-avatar.dto.ts
Purpose: Data transfer object for upload validation
Pattern: Use class-validator decorators (see other DTOs)

#### src/entities/avatar.entity.ts
Purpose: TypeORM entity for avatar metadata
Pattern: Follow User entity pattern

#### tests/avatar.service.spec.ts
Purpose: Unit tests for avatar service
Test cases:
  1. uploadAvatar validates file size
  2. uploadAvatar compresses image
  3. uploadAvatar persists metadata
  4. uploadAvatar returns avatar URL
  5. uploadAvatar throws error on invalid file
  6. deleteAvatar removes file and record

### Files to Modify

#### src/app.module.ts
Change: Register AvatarController and AvatarService as providers
Reason: Module must know about new injectable components

#### src/users/user.entity.ts
Change: Add optional avatarUrl field
Reason: User profile needs to know avatar URL

### Implementation Strategy

1. **Validation**: Use class-validator decorators on DTO
2. **Compression**: Use sharp library for image processing
3. **Storage**: Store files in /uploads/avatars/ directory
4. **Error Handling**: Custom exception for invalid files
5. **Testing**: Jest with mocking for sharp library

### Test Strategy

Test Case 1: File validation
  Arrange: Create test file > 5MB
  Act: Call uploadAvatar
  Assert: Throws InvalidFileException

Test Case 2: Compression
  Arrange: Create test image 1000x1000px
  Act: Call uploadAvatar
  Assert: Returns image 300x300px

Test Case 3: Persistence
  Arrange: Mock repository
  Act: Upload image
  Assert: Repository.save() called with avatar metadata

Test Case 4: URL generation
  Arrange: Upload avatar
  Act: Check response
  Assert: avatarUrl is present and valid format

### Risk & Mitigation

Risk: Image processing library (sharp) compatibility
  Mitigation: Add to package.json, test locally first

Risk: File system permissions for /uploads/
  Mitigation: Check permissions before deployment

Risk: Large file uploads timeout
  Mitigation: Set appropriate timeouts in NestJS config
```

## Phase 3: 🚦 HITL GATE — Developer Approves Plan

Developer reviews plan and can:

```
1. ADJUST scope
   "Don't compress for now, just store original file"
   Agent: [Updates plan]

2. REQUEST clarifications
   "Where should files be stored? Disk or S3?"
   Agent: [Explains approach, adjusts if needed]

3. POINT to reference code
   "Check src/documents/document.service.ts for upload pattern"
   Agent: [Reads file, incorporates pattern]

4. MODIFY requirements
   "Add watermark to avatar before storing"
   Agent: [Updates plan with new requirement]

5. APPROVE
   "Looks good, let's build it"
   Agent: Proceeds to code generation
```

## Phase 4: CREATE BRANCH

```
GitLab Agent creates branch following config pattern:

Branch name: feature/PROJ-123-avatar-upload
Base: develop (from config.gitlab.default_branch)

If branch already exists:
  Ask: "Branch exists. Use existing or create new?"
```

## Phase 5: IMPLEMENT CODE

Code Agent generates each file:

```
FOR each file in implementation plan:

1. Read existing similar file (for patterns)
   Example: Read src/controllers/user.controller.ts

2. Generate file following patterns:
   - Correct file structure
   - Proper imports
   - Error handling
   - Type definitions
   - JSDoc comments

3. Show to developer:
   - Complete file (not stubs)
   - Key sections highlighted
   - Explanation of approach
   - Reference to patterns used

EXAMPLE OUTPUT:

File: src/controllers/avatar.controller.ts
---
import { Controller, Post, UseGuards, Body, Param } from '@nestjs/common';
import { AvatarService } from '../services/avatar.service';
import { UploadAvatarDto } from '../dto/upload-avatar.dto';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';

/**
 * Controller for avatar upload and management
 * Handles user avatar uploads with validation and compression
 */
@Controller('users/:id/avatar')
@UseGuards(JwtAuthGuard)
export class AvatarController {
  constructor(private avatarService: AvatarService) {}

  /**
   * Upload user avatar
   * Validates file size and type, compresses image to 300x300px
   */
  @Post()
  async uploadAvatar(
    @Param('id') userId: string,
    @Body() dto: UploadAvatarDto
  ) {
    return await this.avatarService.uploadAvatar(userId, dto);
  }
}
---

This follows the pattern from UserController (see src/controllers/user.controller.ts)
- Uses @Controller, @Post decorators
- Uses JwtAuthGuard for authentication
- Dependency injection in constructor
- JSDoc comments on public methods
```

## Phase 6: 🚦 HITL GATE — Review Code Changes

Developer reviews each file:

```
1. CODE QUALITY
   Developer: "The error message is unclear"
   Agent: Updates error message

2. PATTERN MATCHING
   Developer: "This doesn't match our project style"
   Agent: Shows reference code, explains reasoning
   Agent: Can adjust if pattern incorrect

3. COMPLETENESS
   Developer: "Missing validation for file type"
   Agent: Adds file type validation
   Agent: Shows updated code

4. TESTS
   Developer: "Tests should cover this error case"
   Agent: Adds test case

Multi-round iteration until developer satisfied:
  Developer: "Looks good"
  Agent: Proceeds to commit
```

## Phase 7: UPDATE JIRA STATUS

```
Call: update_jira_issue(
  key: jira_key,
  transition: "in_progress"  # from config.jira.statuses
)

Add comment:
  "Branch: feature/PROJ-123-avatar-upload
   Implementation started via Otomate"
```

## Phase 8: 🚦 HITL GATE — Approve Push & MR

Show final summary:

```
## Summary of Changes

Files Created (6):
  + src/controllers/avatar.controller.ts (45 lines)
  + src/services/avatar.service.ts (78 lines)
  + src/dto/upload-avatar.dto.ts (12 lines)
  + src/entities/avatar.entity.ts (18 lines)
  + tests/avatar.service.spec.ts (145 lines)

Files Modified (2):
  ~ src/app.module.ts (3 lines added)
  ~ src/users/user.entity.ts (2 lines added)

Total: +303 lines, -5 lines

MR Details:
  Branch: feature/PROJ-123-avatar-upload → develop
  Title: PROJ-123: Add avatar upload endpoint
  Target: develop (auto-merge: yes, squash: yes)

Should I push and open MR?
```

## Phase 9: COMMIT, PUSH & OPEN MR

```
COMMIT:
  Call: commit_file_and_create_mr(
    project_id: from config,
    files: [all generated files],
    commit_message: "PROJ-123: Add avatar upload endpoint\n\n
                     - Implement POST /users/:id/avatar
                     - Add file validation (size, type)
                     - Compress image to 300x300px
                     - Add unit tests",
    branch_name: "feature/PROJ-123-avatar-upload",
    target_branch: "develop",
    mr_title: "PROJ-123: Add avatar upload endpoint",
    mr_description: [from templates/mr-description.md]
  )

MR DESCRIPTION:
  ## Summary
  Implements avatar upload endpoint with validation and compression.

  ## Linked Jira
  PROJ-123: Avatar Upload

  ## Acceptance Criteria
  - [ ] Users can upload avatar images
  - [ ] File size validated < 5MB
  - [ ] Image compressed to 300x300px
  - [ ] Avatar URL returned in response
  - [ ] Error handling implemented

  ## Files Changed
  6 created, 2 modified, +303 lines

  ## Test Plan
  - Run: npm test -- avatar.service.spec.ts
  - Expected: All 6 tests pass
  - Manual: POST /users/1/avatar with test image

  ## Pipeline Status
  [Link to pipeline in MR]
```

## Phase 10: UPDATE JIRA

```
Call: update_jira_issue(
  key: jira_key,
  transition: "in_review"  # from config.jira.statuses
)

Add comment:
  "MR: !{mr_number} — Avatar Upload Endpoint
   Ready for code review.
   Link: {mr_url}"
```

## Error Handling

### If task fetch fails

```
→ Stop, inform developer
→ Ask for correct issue key
```

### If branch creation fails

```
→ Try fallback (use main instead of develop)
→ Ask: "Should I use a different base branch?"
```

### If code generation doesn't match expectations

```
→ Multiple iterations in Phase 6
→ Don't force merge, iterate until satisfied
```

### If push fails

```
→ Show specific error
→ Offer troubleshooting: Check credentials, retry
→ Branch + code still valid, can create MR manually
```

### If MR creation fails

```
→ Branch and code are still available
→ Inform developer: "Code is ready, but MR creation failed"
→ Guide: "Manually create MR in GitLab UI"
→ Or: "Check credentials and retry"
```

## Success Criteria

✓ Task is fully analyzed before coding
✓ Implementation plan approved by developer
✓ Code is production-ready (no stubs)
✓ Code follows project patterns
✓ Tests cover acceptance criteria
✓ Code review happens before push
✓ MR is created with detailed description
✓ Jira is updated with links and status

---

**Duration**: 45 minutes (varies by task complexity)

**What It Creates**:
- Code files (controllers, services, tests)
- Git branch
- Merge Request
- Jira status updates

**Next Workflows**:
- Code review and merge (manual)
- 07-create-release-build (when ready to release)

**Related**: Code Agent, GitLab Agent, Jira Agent
