# Workflow 05: Fix Pipeline

**Goal**: Diagnose a failed Jenkins pipeline, identify root cause, propose fix, create fix branch, and open MR.

**Trigger**: "Fix pipeline", "Debug build failure", "Why is the pipeline failing?", "Debug Jenkins build {job} #{number}"

**Agents**: Orchestrator → Jenkins Agent, GitLab Agent, Code Agent, Jira Agent, Project Context Agent

**Time**: ~30 minutes (diagnosis + fix + MR)

## Phase 1: IDENTIFY THE BUILD

Jenkins Agent determines which build to diagnose:

### If developer specifies directly

```
Developer: "Debug Jenkins build my-awesome-api-build #42"
  → Use job_name: "my-awesome-api-build", build_number: 42
```

### If developer provides Jira key

```
Developer: "Why is PROJ-123 failing?"
  → Find branch associated with PROJ-123
  → Find pipeline on that branch
```

### If developer provides branch name

```
Developer: "Debug feature/PROJ-123-avatar build"
  → Find latest pipeline on that branch
```

### If ambiguous

```
Developer: "The pipeline is failing"
  → Ask: "Which pipeline? Provide job name and build number,
           or the Jira key, or the branch name"
```

## Phase 2: INVESTIGATE & DIAGNOSE

Jenkins Agent applies its error catalog:

### Fetch Build Information

```
Call: jenkins_get_build_status(job_name, build_number)
Extract:
  - Build status: SUCCESS / FAILURE
  - Failed stage: (build, test, deploy, lint, etc.)
  - Duration
  - Build parameters

Call: jenkins_get_console_text(job_name, build_number)
Extract:
  - Complete console log
  - Search for ERROR, FAIL, Exception
  - Extract first error (usually root cause)
```

### Investigate → Hypothesize → Verify → Recommend

```
INVESTIGATE:
  1. Which stage failed? (From build_status)
  2. What is the first error? (From console log)
  3. Are there stack traces? Extract file + line
  4. What exit code? (Usually in log)

HYPOTHESIZE:
  Match error against error catalog:
    If error matches known pattern → HIGH confidence diagnosis
    If error similar to known pattern → MEDIUM confidence
    If error is unique → LOW confidence, need investigation

VERIFY:
  If hypothesis involves:
    - Code: read src/file.ts at error line via GitLab
    - Dependencies: read package.json via GitLab
    - Configuration: read Jenkinsfile via GitLab
    - Build script: read build.sh via GitLab

RECOMMEND:
  Based on verified hypothesis:
    Root cause: [One sentence specific diagnosis]
    Why: [Explanation of what went wrong]
    Confidence: [HIGH / MEDIUM / LOW]
    Fix: [Specific actionable fix]
    Effort: [5 min / 30 min / 1 hour / complex investigation]
    Risk: [Low / Medium / High]
```

## Phase 3: PRESENT DIAGNOSIS

```
## Pipeline Failure Diagnosis

**Build**: {job_name} #{build_number}
**Status**: FAILED
**Failed Stage**: {stage_name}
**Date**: {date}

### Root Cause
{One sentence specific diagnosis}

### Confidence Level
HIGH / MEDIUM / LOW

### Evidence
{Relevant 10-20 log lines showing the error}

### Detailed Analysis
{Explanation of what went wrong and why}

Example:
  "The build failed because npm install encountered a version conflict
   for the 'express' package. The project requires express@4.17.1
   but npm found incompatible peer dependency requirements."

### Proposed Fix
Option 1: {Quick fix}
  Effort: 5 min
  Command: npm install --legacy-peer-deps
  Risk: Low (temporary workaround)

Option 2: {Better fix}
  Effort: 30 min
  Changes: Update package.json to resolve conflict
  Files: package.json
  Risk: Low (proper fix)

### Risk Assessment
{What could go wrong with the fix}
{How to mitigate}

### Additional Investigation (if needed)
{If unable to determine root cause}
"I see an error but need more context:
  - Have you changed dependencies recently?
  - Is this a new Node version?
  - Check if similar builds passed recently"
```

## Phase 4: CREATE FIX IMPLEMENTATION PLAN

Before making any code changes, generate a step-by-step fix plan as a todo list:

```
## Fix Implementation Plan for {job_name} #{build_number}

### Root Cause
{One sentence diagnosis}

### Fix Todo List
- [ ] 1. {Specific action — e.g., "Update express version in package.json from ^4.17.0 to ^4.18.0"}
       File: package.json (MODIFY line 15)
       Reason: Resolves peer dependency conflict
- [ ] 2. {Specific action — e.g., "Regenerate package-lock.json"}
       File: package-lock.json (REGENERATE)
- [ ] 3. {Specific action — e.g., "Fix null dereference in auth.controller.ts at line 42"}
       File: src/controllers/auth.controller.ts (MODIFY line 42)
       Before: return user.profile.name;
       After: return user?.profile?.name ?? 'Unknown';

### Expected Outcome
{stage_name} stage will pass because: {specific reason}

### Verification Steps
1. Trigger Jenkins build on fix branch
2. Verify {stage_name} stage passes
3. Confirm no regressions in other stages
```

## Phase 4b: 🚦 HITL GATE — Developer Approves Fix Plan

```
Developer reviews the fix implementation plan (todo list) and can:

1. ACCEPT plan as proposed
   → Proceed to create branch and implement

2. REQUEST more investigation
   "Can you check if this happened before?"
   → Run more diagnostics, update plan

3. PROVIDE context
   "We just upgraded Node to 18"
   → Use context to improve diagnosis, update plan

4. MODIFY plan
   "Also update the CI config"
   → Add/change steps in the todo list

5. DECLINE fix
   "I'll fix this manually"
   → Stop workflow gracefully

IMPORTANT: No code changes until the fix plan is approved.
```

## Phase 5: CREATE FIX BRANCH

```
GitLab Agent creates branch:
  Branch name: fix/PROJ-123-pipeline-failure
             or fix/{job-name}-{issue-type}

If branch already exists:
  Ask: "Branch exists. Use existing or create new?"
```

## Phase 6: IMPLEMENT FIX

Code Agent or manual fix depending on type:

```
Example fixes:

FIX TYPE 1: Dependency version conflict
  File: package.json
  Change: Update version ranges to resolve conflict
  Before: "express": "^4.17.0"
  After: "express": "^4.18.0"

FIX TYPE 2: Missing dependency
  File: package.json
  Change: Add missing package
  Add: "sharp": "^0.32.0"

FIX TYPE 3: Jenkinsfile configuration
  File: Jenkinsfile
  Change: Increase memory limit
  Before: nodejs memory: 512m
  After: nodejs memory: 2048m

FIX TYPE 4: Code issue (null pointer, syntax error)
  File: src/file.ts at line {line}
  Change: Add null check
  Before: return object.property;
  After: return object?.property;

For each fix:
  Show: Before/After code
  Explain: Why this fixes the issue
```

## Phase 7: 🚦 HITL GATE — Review Fix Code

```
Developer reviews fix and can:

1. APPROVE
   "Looks good, commit it"

2. REQUEST changes
   "This fix is too hacky, do it properly"
   Agent: Updates fix

3. SKIP fix
   "I'll handle this differently"
   Agent: Stop workflow
```

## Phase 8: 🚦 HITL GATE — Approve Push & MR

```
Show summary:
  Files changed: {N}
  Branch: fix/PROJ-123-pipeline-failure
  MR target: develop

Confirmation: "Push and create MR?"
```

## Phase 9: COMMIT, PUSH & OPEN MR

```
Call: commit_file_and_create_mr(
  files: [fixed files],
  commit_message: "PROJ-123: fix pipeline failure\n\n
                   - Root cause: {diagnosis}
                   - Fix: {what was changed}
                   - Issue: {job_name} #{build_number}",
  branch_name: "fix/PROJ-123-pipeline-failure",
  mr_description: [From template]
)

MR DESCRIPTION includes:
  - Link to Jenkins build that failed
  - Root cause diagnosis
  - Fix explanation
  - How to verify fix works
```

## Phase 10: SUGGEST VERIFICATION

```
Recommend to developer:
  1. Trigger Jenkins build on this branch
  2. Verify build passes
  3. Request approval for merge
  4. Once approved, merge to develop

Note: Can't auto-trigger Jenkins (no tool available)
      Developer must trigger via Jenkins UI or CLI
```

## Error Handling

### If build not found

```
→ Suggest: Check job name and build number
→ Ask: Use jenkins_list_jobs to find available jobs?
```

### If log parsing fails

```
→ Show: Raw log excerpt
→ Ask: Help me understand this error?
```

### If diagnosis is uncertain

```
→ Show confidence level clearly
→ If LOW confidence: Suggest options, don't commit to one
→ Say: "I see an error but need more context..."
```

### If fix type is unknown

```
→ Ask developer for guidance
→ "This error is outside my known patterns.
   Can you explain what the fix should be?"
```

## Special Cases

### Flaky / Intermittent Failures

```
If error might be transient:
  → Suggest: "This might be transient. Try re-running build first"
  → Offer: teach_schedule_jenkins_build for retry
  → If recurring: Then investigate root cause
```

### External Service Failures

```
If error is "service unavailable", "timeout", "connection refused":
  → Diagnosis: External dependency issue
  → Recommend: "This is likely external. Check if {service} is up"
  → Fix: Usually no code change needed (wait for service recovery)
  → Or: Add retries/timeout handling in code
```

## Success Criteria

✓ Root cause is identified with clear confidence level
✓ Diagnosis explains WHY the build failed
✓ Fix implementation plan (todo list) presented to developer BEFORE any code changes
✓ Developer approves fix plan before implementation begins
✓ Fix is specific and actionable
✓ Developer approves code changes before committing
✓ MR is created with diagnosis details and completed fix plan
✓ Effort estimate is realistic
✓ Risk is honestly assessed

---

**Duration**: 30 minutes (diagnosis + fix + MR)

**What It Creates**:
- Git branch with fix
- Merge Request
- Clear diagnosis documentation

**Next Steps**:
- Developer triggers Jenkins build on fix branch
- After passing: Merge to develop
- Resume 04-implement-dev-task or other workflows

**Related**: Jenkins Agent, GitLab Agent, Code Agent

**Limitation**: Cannot auto-trigger Jenkins builds (must be manual via UI/CLI)
